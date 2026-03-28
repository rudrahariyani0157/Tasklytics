from django.shortcuts import render, redirect
from database import appden_data, find_data

def landingpage(request):
    return render(request, 'landingpage.html')

def register_view(request):
    if request.method == "POST":
        get_gmail_id = request.POST.get("get_gmail_id")
        analysis_email = request.POST.get("analysis_email")
        app_password = request.POST.get("app_password")
        mail_type = request.POST.get("mail_type")

        if find_data(get_gmail_id) == True:
            return render(request, "userexist.html")

        else:
            appden_data(get_gmail_id, analysis_email, app_password, mail_type) 
            return render(request, 'userappended.html')

        # Print to terminal
        # print("Gmail ID:", get_gmail_id)
        # print("Analysis Email:", analysis_email)
        # print("App Password:", app_password)
        # print("Mail Type:", mail_type)
        

    return render(request, 'register.html')

def settings_view(request):
    return render(request, 'settings.html')

def userexist(request):
    return render(request, 'userexist.html')