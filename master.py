import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import datetime
from openai import OpenAI
from constant import prompt
import pandas as pd
from io import StringIO
from datetime import date, time
import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from constant import apikey

# # Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def get_g_mails(mail_type, EMAIL_ACCOUNT, APP_PASSWORD):
    IMAP_SERVER = "imap.gmail.com"

    # -------- helper: decode subject text --------
    def decode_text(text):
        if not text:
            return ""
        decoded, encoding = decode_header(text)[0]
        if isinstance(decoded, bytes):
            return decoded.decode(encoding if encoding else "utf-8", errors="ignore")
        return decoded

    # -------- helper: extract email body --------
    def get_body(msg):
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            if msg.get_content_type() == "text/plain":
                body = msg.get_payload(decode=True).decode(errors="ignore")
        return body.strip()

    # -------- helper: fetch emails from folder --------
    def fetch_emails(folder, label, date_str):
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, APP_PASSWORD)
        mail.select(folder)

        status, data = mail.search(None, f'(ON "{date_str}")')
        email_ids = data[0].split()

        mail_list = []
        for i, eid in enumerate(email_ids, 1):
            status, msg_data = mail.fetch(eid, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            subject = decode_text(msg.get("Subject"))
            from_ = msg.get("From")
            to_ = msg.get("To")
            date_obj = parsedate_to_datetime(msg.get("Date"))
            date_formatted = date_obj.strftime("%Y-%m-%d %H:%M")

            body = get_body(msg)

            mail_dict = {
                "from": from_,
                "to": to_,
                "date": date_formatted,
                "subject": subject,
                "body": body
            }

            mail_list.append(mail_dict)

        mail.logout()
        return mail_list

    # -------- main logic (unchanged) --------
    # date_str = datetime.date.today().strftime("%d-%b-%Y")
    date_str = "21-Feb-2026"

    if mail_type == "receive":
        return fetch_emails("inbox", "Received", date_str)

    elif mail_type == "sent":
        return fetch_emails('"[Gmail]/Sent Mail"', "Sent", date_str)

def get_zoho_mails(mail_type, EMAIL_ACCOUNT, APP_PASSWORD):
    IMAP_SERVER = "imap.zoho.com"
    # -------- helper: decode subject text --------
    def decode_text(text):
        if not text:
            return ""
        decoded, encoding = decode_header(text)[0]
        if isinstance(decoded, bytes):
            return decoded.decode(encoding if encoding else "utf-8", errors="ignore")
        return decoded

    # -------- helper: extract email body --------
    def get_body(msg):
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            if msg.get_content_type() == "text/plain":
                body = msg.get_payload(decode=True).decode(errors="ignore")
        return body.strip()

    # -------- helper: fetch emails from folder --------
    def fetch_emails(folder, label, date_str):
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, APP_PASSWORD)
        mail.select(folder)

        status, data = mail.search(None, f'(ON "{date_str}")')
        email_ids = data[0].split()

        mail_list = []
        for i, eid in enumerate(email_ids, 1):
            status, msg_data = mail.fetch(eid, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            subject = decode_text(msg.get("Subject"))
            from_ = msg.get("From")
            to_ = msg.get("To")
            date_obj = parsedate_to_datetime(msg.get("Date"))
            date_formatted = date_obj.strftime("%Y-%m-%d %H:%M")

            body = get_body(msg)

            mail_dict = {
                "from": from_,
                "to": to_,
                "date": date_formatted,
                "subject": subject,
                "body": body
            }

            mail_list.append(mail_dict)

        mail.logout()
        return mail_list

    # -------- main logic (unchanged) --------
    date_str = datetime.date.today().strftime("%d-%b-%Y")
    # date_str = "21-Feb-2026"

    if mail_type == "receive":
        return fetch_emails("INBOX", "Received", date_str)

    elif mail_type == "sent":
        return fetch_emails("Sent", "Sent", date_str)

def generate_mail_csv(mail_json):
    client = OpenAI(
      base_url="https://openrouter.ai/api/v1",
      api_key= apikey,
    )

    completion = client.chat.completions.create(
      extra_headers={
        "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
      },
      model="openai/gpt-oss-120b:free",
      messages=[
        {
          "role": "user",
          "content": prompt + str(mail_json)
        }
      ]
    )

    return completion.choices[0].message.content






def save_csv_and_excel(csv_string):
    if not csv_string or csv_string.strip() == "":
        print(f"No data found for the emails. Skipping...")
    else:
        df = pd.read_csv(StringIO(csv_string))

        # Inspect the data
        print(df.head())

        # Save to CSV file
        global csv_file
        csv_file = "emails.csv"
        global excel_file
        excel_file = "emails.xlsx"

        df.to_csv(csv_file, index=False, encoding="utf-8")
        df.to_excel(excel_file, index=False)





def available_task_list(file_paths):
    # Read and combine multiple CSV files
    dataframes = []
    for path in file_paths:
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip().str.lower()
        dataframes.append(df)

    df = pd.concat(dataframes, ignore_index=True)

    # Clean task_name
    df["task_name"] = df["task_name"].astype(str).str.strip()

    # Keep only rows where task exists
    tasks_df = df[
        (df["task_name"] != "0") &
        (df["task_name"] != "") &
        (~df["task_name"].isna())
    ]

    # -------- Future-proof logic --------
    # If status column exists → use it
    if "status" in tasks_df.columns:
        tasks_df["status"] = tasks_df["status"].astype(str).str.lower().str.strip()

        pending_df = tasks_df[tasks_df["status"].isin(["pending", "incomplete"])]
        completed_df = tasks_df[tasks_df["status"].isin(["completed", "done"])]

    else:
        # No status column → all tasks are pending
        pending_df = tasks_df
        completed_df = pd.DataFrame(columns=tasks_df.columns)

    # Counts
    pending_count = len(pending_df)
    completed_count = len(completed_df)

    # Lists
    pending_tasks = pending_df["task_name"].to_list()
    completed_tasks = completed_df["task_name"].to_list()

    # -------- Email Format --------
    email_body = []
    email_body.append("Task Summary Report")
    email_body.append("=" * 25)
    email_body.append(f"Total Pending Tasks: {pending_count}")
    email_body.append(f"Total Completed Tasks: {completed_count}")
    email_body.append("")

    email_body.append("Pending Tasks:")
    if pending_tasks:
        for i, task in enumerate(pending_tasks, 1):
            email_body.append(f"{i}. {task}")
    else:
        email_body.append("No pending tasks.")

    email_body.append("")
    email_body.append("Completed Tasks:")
    if completed_tasks:
        for i, task in enumerate(completed_tasks, 1):
            email_body.append(f"{i}. {task}")
    else:
        email_body.append("No completed tasks.")

    return "\n".join(email_body)


def send_email_with_attachments(to, body, file_paths):
    creds = None

    # Load saved login token
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Build Gmail service
    service = build('gmail', 'v1', credentials=creds)

    sender = ""
    subject = "This day email analysis"

    # Create email
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    # Add body
    message.attach(MIMEText(body, 'plain'))

    # Attach multiple files
    for file_path in file_paths:
        if os.path.exists(file_path):
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(file_path)}'
            )
            message.attach(part)
        else:
            print(f"Attachment not found: {file_path}")

    # Encode and send
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    sent = service.users().messages().send(
        userId="me",
        body={'raw': raw_message}
    ).execute()

    print("Email sent! Message ID:", sent['id'])



email_account = 
app_password = 

# email_account = 
# app_password =
# recive =  get_zoho_mails("receive", email_account, app_password)
# sent =  get_zoho_mails("sent", email_account, app_password)


recive =  get_g_mails("receive", email_account, app_password)
sent =  get_g_mails("sent", email_account, app_password)
print(recive)
print(sent)

if recive == [] and sent == []:
    print("something went wrong 1!!!")
    csv_ = (generate_mail_csv(mail_json = sent))
elif recive == []:
    csv_ = (generate_mail_csv(mail_json = sent))
elif recive != [] and sent != []:
    csv_ = (generate_mail_csv(mail_json = recive+sent))
elif sent == []:
    csv_ = (generate_mail_csv(mail_json = recive))

else:
    print("something went wrong 2!!!")

print(csv_)

save_csv_and_excel(csv_string=csv_)
task_list = available_task_list(file_paths = ["emails.csv"])
print(task_list)
send_email_with_attachments(
    to="",
    body = f"Hello! here is your todays mail analysis:\n{task_list}",
    file_paths=[
        "emails.csv",
        "emails.xlsx"
    ]
)


print("you did it!!!")