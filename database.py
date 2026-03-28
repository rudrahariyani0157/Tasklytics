import csv

# Writing data
def appden_data(receiver_gmail,usagemail, credits, email_service_type):
    # receiver_gmail = input("R Email: ")
    # usagemail = input("U Email: ")
    # credits = input("Credits: ")
    # email_service_type = input("Service type: ")

    with open('database.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        # writer.writerow(['Email ID', 'App Password'])
        writer.writerow([receiver_gmail, usagemail, credits, email_service_type])

    # Reading data
def print_data():
    with open('database.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)

    with open('database.csv', 'r') as file:
        reader = csv.reader(file)
        # next(reader)  # Skip header row
        
        for row in reader:
            rm = row[0]
            um = row[1]
            cre = row[2]
            st = row[3]
            print("Reciving Gmail ID:", rm)
            print("Using Mail", um)
            print("App Password:", cre)
            print("Servise type: ", st)

def find_data(query):

    with open('database.csv', 'r') as file:
        reader = csv.reader(file)
        # next(reader)  # Skip header row
        
        for row in reader:
            if query == row[0]:
                return True
            else:
                return False