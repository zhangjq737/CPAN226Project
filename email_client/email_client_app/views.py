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

# (\HasNoChildren) "/" "Health"
# (\HasNoChildren) "/" "INBOX"
# (\HasNoChildren) "/" "Notes"
# (\HasChildren \Noselect) "/" "[Gmail]"
# (\All \HasNoChildren) "/" "[Gmail]/All Mail"
# (\Drafts \HasNoChildren) "/" "[Gmail]/Drafts"
# (\HasNoChildren \Important) "/" "[Gmail]/Important"
# (\HasNoChildren \Sent) "/" "[Gmail]/Sent Mail"
# (\HasNoChildren \Junk) "/" "[Gmail]/Spam"
# (\Flagged \HasNoChildren) "/" "[Gmail]/Starred"
# (\HasNoChildren \Trash) "/" "[Gmail]/Trash"
# (\HasChildren \Noselect) "/" "[Imap]"

# Create your views here.
def test_view(request):
    return HttpResponse('Email App is working!')

def index(request):
    return render(request, 'email_client_app/index.html', {
        'settings': settings,  # Already passing settings
        'email_sender': settings.EMAIL_SENDER  # Explicitly pass EMAIL_SENDER
    })

def send_email(request):
    if request.method == 'POST':
        receivers = [r.strip() for r in request.POST.get('receiver', '').split(',') if r.strip()]
        cc = [c.strip() for c in request.POST.get('cc', '').split(',') if c.strip()]

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
    mail.select("INBOX")

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
            'snippet': get_email_snippet(email_message, 50),
            'time': email_message['date'] or 'Unknown',
            'unread': is_unread
        })

    mail.logout()
    return JsonResponse({'emails': emails, 'unread_count': unread_count})

def get_sent(request):    
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
    mail.select(r'"[Gmail]/Sent Mail"')

    status, messages = mail.search(None, "ALL")
    if status != 'OK' or not messages[0]:
        mail.logout()
        return JsonResponse({'emails': []})

    email_ids = messages[0].split()[-10:]
    emails = []

    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status != 'OK' or not msg_data[0]:
            continue
        raw_email = msg_data[0][1]
        email_message = BytesParser().parsebytes(raw_email)
        emails.append({
            'sender': email_message['from'],
            'subject': email_message['subject'] or '(No Subject)',
            'snippet': get_email_snippet(email_message, 50),
            'time': email_message['date'] or 'Unknown'
        })

    mail.logout()
    return JsonResponse({'emails': emails})

def get_drafts(request):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
    mail.select(r'"[Gmail]/Drafts"')  # Gmail drafts folder

    # Get all draft emails (limit to last 10)
    status, messages = mail.search(None, "ALL")
    if status != 'OK' or not messages[0]:
        mail.logout()
        return JsonResponse({'emails': [], 'draft_count': 0})

    email_ids = messages[0].split()[-10:]
    emails = []

    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status != 'OK' or not msg_data[0]:
            continue
        raw_email = msg_data[0][1]
        email_message = BytesParser().parsebytes(raw_email)
        emails.append({
            'sender': email_message['from'],
            'subject': email_message['subject'] or '(No Subject)',
            'snippet': get_email_snippet(email_message, 50),
            'time': email_message['date'] or 'Unknown'
        })

    draft_count = len(email_ids)  # Total drafts shown
    mail.logout()
    return JsonResponse({'emails': emails, 'draft_count': draft_count})

def get_email_snippet(email_message, max_length):
    try:
        # Simple approach for text extraction
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    content = part.get_payload(decode=True)
                    if content:
                        try:
                            if isinstance(content, bytes):
                                text = content.decode('utf-8', errors='replace')
                            else:
                                text = str(content)
                            return text[:max_length].strip()
                        except:
                            pass
            # Fallback to first part if no text/plain
            return str(email_message.get_payload(0))[:max_length].strip()
        else:
            # For non-multipart emails
            content = email_message.get_payload(decode=True)
            if content is None:
                return ''
            if isinstance(content, bytes):
                text = content.decode('utf-8', errors='replace')
            else:
                text = str(content)
            return text[:max_length].strip()
    except Exception as e:
        print(f"Error in snippet extraction: {e}")
        return ''