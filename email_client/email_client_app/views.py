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

# Add this function after the imports and before other functions

def get_imap_connection(folder=None):
    """
    Helper function to establish IMAP connection and optionally select a folder
    Returns: (connection, status) tuple
    """
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
        if folder:
            mail.select(f'"{folder}"')
        return mail, True
    except Exception as e:
        return None, str(e)

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

# Modified get_inbox to use get_imap_connection
def get_inbox(request):
    mail, status = get_imap_connection("INBOX")
    if not isinstance(status, bool):
        return JsonResponse({'status': 'error', 'message': status}, status=500)

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
            'id': email_id.decode(),
            'sender': email_message['from'],
            'subject': email_message['subject'] or '(No Subject)',
            'snippet': get_email_snippet(email_message, 50),
            'time': email_message['date'] or 'Unknown',
            'unread': is_unread
        })

    mail.logout()
    return JsonResponse({'emails': emails, 'unread_count': unread_count})

# Modified get_sent to use get_imap_connection
def get_sent(request):
    mail, status = get_imap_connection("[Gmail]/Sent Mail")
    if not isinstance(status, bool):
        return JsonResponse({'status': 'error', 'message': status}, status=500)

    status, messages = mail.search(None, "ALL")
    if status != 'OK' or not messages[0]:
        mail.logout()
        return JsonResponse({'emails': []})

    email_ids = messages[0].split()[-20:]
    emails = []

    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status != 'OK' or not msg_data[0]:
            continue
        raw_email = msg_data[0][1]
        email_message = BytesParser().parsebytes(raw_email)
        emails.append({
            'id': email_id.decode(),
            'sender': email_message['from'],
            'subject': email_message['subject'] or '(No Subject)',
            'snippet': get_email_snippet(email_message, 50),
            'time': email_message['date'] or 'Unknown'
        })

    mail.logout()
    return JsonResponse({'emails': emails})

# Modified get_drafts to use get_imap_connection
def get_drafts(request):
    mail, status = get_imap_connection("[Gmail]/Drafts")
    if not isinstance(status, bool):
        return JsonResponse({'status': 'error', 'message': status}, status=500)

    status, messages = mail.search(None, "ALL")
    if status != 'OK' or not messages[0]:
        mail.logout()
        return JsonResponse({'emails': [], 'draft_count': 0})

    email_ids = messages[0].split()[-20:]
    emails = []

    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status != 'OK' or not msg_data[0]:
            continue
        raw_email = msg_data[0][1]
        email_message = BytesParser().parsebytes(raw_email)
        emails.append({
            'id': email_id.decode(),
            'sender': email_message['from'],
            'subject': email_message['subject'] or '(No Subject)',
            'snippet': get_email_snippet(email_message, 50),
            'time': email_message['date'] or 'Unknown'
        })

    draft_count = len(email_ids)
    mail.logout()
    return JsonResponse({'emails': emails, 'draft_count': draft_count})

# Modified get_email_detail to use get_imap_connection
def get_email_detail(request):
    if request.method == 'GET':
        email_id = request.GET.get('id')
        folder = request.GET.get('folder', 'INBOX')

        if not email_id:
            return JsonResponse({'status': 'error', 'message': 'No email ID provided'}, status=400)

        mail, status = get_imap_connection(folder)
        if not isinstance(status, bool):
            return JsonResponse({'status': 'error', 'message': status}, status=500)

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
            'attachment': None
        }

        mail.logout()
        return JsonResponse({'email': email_data})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# New helper function to get the full email body
def get_full_email_body(email_message):
    if not email_message.is_multipart():
        content = email_message.get_payload(decode=True)
        if content is None:
            return ''
        return content.decode('utf-8', errors='replace') if isinstance(content, bytes) else str(content)
    
    html_content = None
    plain_content = None
    for part in email_message.walk():
        content_type = part.get_content_type()
        if content_type == 'text/html':
            content = part.get_payload(decode=True)
            if content:
                html_content = content.decode('utf-8', errors='replace') if isinstance(content, bytes) else str(content)
        elif content_type == 'text/plain' and not html_content:
            content = part.get_payload(decode=True)
            if content:
                plain_content = content.decode('utf-8', errors='replace') if isinstance(content, bytes) else str(content)
    
    return html_content if html_content else plain_content if plain_content else ''

# Modified save_draft_to_imap to use get_imap_connection
def save_draft_to_imap(receiver, subject, body, cc=None):
    try:
        mail, status = get_imap_connection("[Gmail]/Drafts")
        if not isinstance(status, bool):
            return {"status": "error", "message": status}

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
            if request.content_type == 'application/json':
                data = json.loads(request.body.decode('utf-8'))
                receiver = data.get('receiver', '')
                subject = data.get('subject', '')
                body = data.get('body', '')
                cc = data.get('cc', '')
            else:
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

# Function to render the Home Page. Displays a welcome message and provides a link to compose a new email.
def home_view(request):
    context = {
        'title': 'Home Page - Django Email App',
        'welcome_message': 'Welcome to the Django Email Application!',
        'instructions': [
            'Click the "+ Compose" button on the Main Email Dashboard Page to start writing your email.',
            'You can:',
            '1. Add a subject and message',
            '2. Send to one or more recipients (supports CC)',
            '3. Attach files',
            '4. Send your email instantly!',
            '5. Use the sidebar to navigate your Inbox, Sent, and Draft folders.',
            '6. Unread and unsent messages will be indicated clearly.',
            '7. Your communication is now simple, fast, and organized — all in one place!',
        ]
    }
    return render(request, 'email_client_app/home.html', context)

# Function to render the About Page. Provides information about the project and contributors.
def about_view(request):
    context = {
        'title': 'About Page - Django Email App',
        'project_description': 'This application allows the email sender, which is the user, to compose and send emails using a clean, web-based interface.',
        'features': [
            '1. Compose and Send Emails with a modern interface',
            '2. Add one or more recipients, including CC support',
            '3. Attach files to your messages',
            "4. Use the '+ Compose' button for quick access to email creation",
            '5. Navigate between Inbox, Sent, and Draft folders easily',
            '6. View email counts for unread (Inbox) or unsent (Drafts) messages',
            '7. Compatible with Gmail servers for real-time email communication',
            '8. Fully responsive design built with React-Bootstrap',
            '9. Secure backend integration using Django (Python), SMTP (Simple Mail Transfer Protocol), and IMAP (Internet Message Access Protocol)'
        ],
        'purpose': "This app was built to simplify email communication and offer core features in a clean layout, whether you're sending to a single recipient or multiple contacts.",
        'group_members': [
            '1. Ekroop Hundal-Vatcher (n01632322)',
            '2. Ritik Patel (n01565101)',
            '3. Jason Zhang (n01677466)'
        ]
    }
    return render(request, 'email_client_app/about.html', context)