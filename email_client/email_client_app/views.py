from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
import smtplib
import ssl
from email.message import EmailMessage
import os
from email.parser import BytesParser
import imaplib

# Create your views here.
def test_view(request):
    return HttpResponse('Email App is working!')

def index(request):
    return render(request, 'email_client_app/index.html')

def send_email(request):
    if request.method == 'POST':
        # Debug input
        # print("Raw receiver:", request.POST.get('receiver', ''))
        # print("Raw CC:", request.POST.get('cc', ''))

        receivers = [r.strip() for r in request.POST.get('receiver', '').split(',') if r.strip()]
        cc = [c.strip() for c in request.POST.get('cc', '').split(',') if c.strip()]
        
        # print("Processed receivers:", receivers)
        # print("Processed CC:", cc)

        subject = request.POST.get('subject', '')
        body = request.POST.get('body', '')
        attachment = request.FILES.get('attachment')

        if not receivers:  # Ensure at least one valid receiver
            return JsonResponse({'status': 'error', 'message': 'No valid recipients provided'}, status=400)

        # Create email message
        em = EmailMessage()
        em['From'] = settings.EMAIL_SENDER
        em['To'] = ', '.join(receivers)
        if cc:
            em['Cc'] = ', '.join(cc)
        em['Subject'] = subject
        em.set_content(body)

        if attachment:
            file_data = attachment.read()
            file_name = attachment.name
            em.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

        # Send email
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, context=context) as smtp:
                smtp.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
                smtp.sendmail(settings.EMAIL_SENDER, receivers + cc, em.as_string())
            return JsonResponse({'status': 'success', 'message': 'Email sent successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def get_inbox(request):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
    mail.select("inbox")

    # Get unread count
    status, unread = mail.search(None, "UNSEEN")
    unread_count = len(unread[0].split()) if status == 'OK' and unread[0] else 0

    # Get all inbox emails (limit to last 10)
    status, messages = mail.search(None, "ALL")
    if status != 'OK' or not messages[0]:
        mail.logout()
        return JsonResponse({'emails': [], 'unread_count': unread_count})

    email_ids = messages[0].split()[-10:]  # Last 10 emails
    emails = []

    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(FLAGS RFC822)")
        if status != 'OK' or not msg_data[0]:
            continue
        raw_email = msg_data[0][1]  # Email content
        flags = msg_data[0][0]  # Flags like b'1 (FLAGS (\Seen))'
        email_message = BytesParser().parsebytes(raw_email)
        is_unread = b"\\Seen" not in flags
        emails.append({
            'sender': email_message['from'],
            'subject': email_message['subject'] or '(No Subject)',
            # 'snippet': (email_message.get_payload(0).get_payload()[:50].strip() if isinstance(email_message.get_payload(), list) else email_message.get_payload()[:50].strip()) if email_message.get_payload() else '',
            'time': email_message['date'] or 'Unknown',
            'unread': is_unread
        })

    mail.logout()
    return JsonResponse({'emails': emails, 'unread_count': unread_count})