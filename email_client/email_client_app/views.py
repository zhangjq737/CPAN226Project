from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import smtplib
import ssl
from email.message import EmailMessage
from email.parser import BytesParser
import imaplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Helper function to get email snippet (unchanged)
def get_email_snippet(email_message, max_length):
    try:
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    content = part.get_payload(decode=True)
                    if content:
                        if isinstance(content, bytes):
                            text = content.decode('utf-8', errors='replace')
                        else:
                            text = str(content)
                        return text[:max_length].strip()
            return str(email_message.get_payload(0))[:max_length].strip()
        else:
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

# Existing views (unchanged)
def test_view(request):
    return HttpResponse('Email App is working!')

def index(request):
    return render(request, 'email_client_app/index.html', {
        'settings': settings,
        'email_sender': settings.EMAIL_SENDER
    })

def send_email(request):
    if request.method == 'POST':
        receivers = [r.strip() for r in request.POST.get('receiver', '').split(',') if r.strip()]
        cc = [c.strip() for c in request.POST.get('cc', '').split(',') if c.strip()]
        subject = request.POST.get('subject', '')
        body = request.POST.get('body', '')
        attachment = request.FILES.get('attachment')

        if not receivers:
            return JsonResponse({'status': 'error', 'message': 'No valid recipients provided'}, status=400)

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

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, context=context) as smtp:
                smtp.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
                smtp.sendmail(settings.EMAIL_SENDER, receivers + cc, em.as_string())
            return JsonResponse({'status': 'success', 'message': 'Email sent successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# Modified get_inbox to include email ID
def get_inbox(request):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
    mail.select("INBOX")

    status, unread = mail.search(None, "UNSEEN")
    unread_count = len(unread[0].split()) if status == 'OK' and unread[0] else 0

    status, messages = mail.search(None, "ALL")
    if status != 'OK' or not messages[0]:
        mail.logout()
        return JsonResponse({'emails': [], 'unread_count': unread_count})

    email_ids = messages[0].split()[-50:]
    emails = []

    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(FLAGS RFC822)")
        if status != 'OK' or not msg_data[0]:
            continue
        raw_email = msg_data[0][1]
        flags = msg_data[0][0]
        email_message = BytesParser().parsebytes(raw_email)
        is_unread = b"\\Seen" not in flags
        emails.append({
            'id': email_id.decode(),  # Added email ID
            'sender': email_message['from'],
            'subject': email_message['subject'] or '(No Subject)',
            'snippet': get_email_snippet(email_message, 50),
            'time': email_message['date'] or 'Unknown',
            'unread': is_unread
        })

    mail.logout()
    return JsonResponse({'emails': emails, 'unread_count': unread_count})

# Modified get_sent to include email ID
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
            'id': email_id.decode(),  # Added email ID
            'sender': email_message['from'],
            'subject': email_message['subject'] or '(No Subject)',
            'snippet': get_email_snippet(email_message, 50),
            'time': email_message['date'] or 'Unknown'
        })

    mail.logout()
    return JsonResponse({'emails': emails})

# Modified get_drafts to include email ID
def get_drafts(request):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
    mail.select(r'"[Gmail]/Drafts"')

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
            'id': email_id.decode(),  # Added email ID
            'sender': email_message['from'],
            'subject': email_message['subject'] or '(No Subject)',
            'snippet': get_email_snippet(email_message, 50),
            'time': email_message['date'] or 'Unknown'
        })

    draft_count = len(email_ids)
    mail.logout()
    return JsonResponse({'emails': emails, 'draft_count': draft_count})

# New view to get full email details
def get_email_detail(request):
    if request.method == 'GET':
        email_id = request.GET.get('id')
        folder = request.GET.get('folder', 'INBOX')  # Default to INBOX

        if not email_id:
            return JsonResponse({'status': 'error', 'message': 'No email ID provided'}, status=400)

        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
        mail.select(f'"{folder}"')

        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status != 'OK' or not msg_data[0]:
            mail.logout()
            return JsonResponse({'status': 'error', 'message': 'Email not found'}, status=404)

        raw_email = msg_data[0][1]
        email_message = BytesParser().parsebytes(raw_email)

        email_data = {
            'sender': email_message['from'],
            'receiver': email_message['to'],
            'cc': email_message['cc'],
            'subject': email_message['subject'] or '(No Subject)',
            'body': get_full_email_body(email_message),
            'time': email_message['date'] or 'Unknown',
            'attachment': None  # Add attachment handling if needed
        }

        mail.logout()
        return JsonResponse({'email': email_data})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# New helper function to get the full email body
def get_full_email_body(email_message):
    # If it’s a single-part email (not multipart)
    if not email_message.is_multipart():
        content = email_message.get_payload(decode=True)
        if content is None:
            return ''
        return content.decode('utf-8', errors='replace') if isinstance(content, bytes) else str(content)
    
    # For multipart emails, walk through all parts
    html_content = None
    plain_content = None
    for part in email_message.walk():
        content_type = part.get_content_type()
        if content_type == 'text/html':
            content = part.get_payload(decode=True)
            if content:
                html_content = content.decode('utf-8', errors='replace') if isinstance(content, bytes) else str(content)
        elif content_type == 'text/plain' and not html_content:  # Fallback only if no HTML
            content = part.get_payload(decode=True)
            if content:
                plain_content = content.decode('utf-8', errors='replace') if isinstance(content, bytes) else str(content)
    
    # Return HTML if available, otherwise plain text
    return html_content if html_content else plain_content if plain_content else ''

def save_draft_to_imap(receiver, subject, body, cc=None):
    try:
        # Establish IMAP connection and save draft
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
        
        mail.select(r'"[Gmail]/Drafts"')  
        
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_SENDER
        msg['To'] = receiver
        if cc:
            msg['Cc'] = cc
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        msg_data = msg.as_bytes()
        status, response = mail.append(r'"[Gmail]/Drafts"', '\\Draft', None, msg_data)

        if status == 'OK':
            return {"status": "success", "message": "Draft saved successfully!"}
        else:
            return {"status": "error", "message": f"Failed to save draft: {response}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
# @csrf_exempt
def save_draft(request):
    if request.method == 'POST':
        try:
            # Check if the content type is application/json
            if request.content_type == 'application/json':
                data = json.loads(request.body.decode('utf-8'))
                receiver = data.get('receiver', '')
                subject = data.get('subject', '')
                body = data.get('body', '')
                cc = data.get('cc', '')
            else:
                # Fall back to form data
                receiver = request.POST.get('receiver', '')
                subject = request.POST.get('subject', '')
                body = request.POST.get('body', '')
                cc = request.POST.get('cc', '')
            
            result = save_draft_to_imap(receiver, subject, body, cc)
            return JsonResponse(result)
        except Exception as e:
            import traceback
            print(traceback.format_exc())  
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid method"})