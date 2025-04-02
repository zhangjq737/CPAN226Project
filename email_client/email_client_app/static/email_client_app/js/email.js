// email_client_app/static/email_client_app/js/email.js
function loadInbox() {
    fetch("/inbox/")
        .then(response => response.json())
        .then(data => {
            const emailList = document.getElementById('email-list');
            const unreadCount = document.getElementById('unread-count');
            emailList.innerHTML = '';
            data.emails.forEach(email => {
                const li = document.createElement('li');
                li.className = `email-item list-group-item ${email.unread ? 'unread' : ''}`;
                li.innerHTML = `
                    <div class="row">
                        <div class="col-3">${email.sender}</div>
                        <div class="col-4">${email.subject}</div>
                        <div class="col-3">${email.snippet}</div>
                        <div class="col-2 text-end">${email.time}</div>
                    </div>
                `;
                emailList.insertBefore(li, emailList.firstChild);
            });
            unreadCount.textContent = data.unread_count;
        })
        .catch(error => console.error('Error loading inbox:', error));
}

function loadSent() {
    fetch("/sent/")
        .then(response => response.json())
        .then(data => {
            const emailList = document.getElementById('email-list');
            emailList.innerHTML = '';
            data.emails.forEach(email => {
                const li = document.createElement('li');
                li.className = 'email-item list-group-item';
                li.innerHTML = `
                    <div class="row">
                        <div class="col-3">${email.sender}</div>
                        <div class="col-4">${email.subject}</div>
                        <div class="col-3">${email.snippet}</div>
                        <div class="col-2 text-end">${email.time}</div>
                    </div>
                `;
                emailList.insertBefore(li, emailList.firstChild);
            });
        })
        .catch(error => console.error('Error loading sent:', error));
}

function loadDrafts() {
    fetch("/drafts/")
        .then(response => response.json())
        .then(data => {
            const emailList = document.getElementById('email-list');
            const draftCount = document.getElementById('draft-count');
            emailList.innerHTML = '';
            data.emails.forEach(email => {
                const li = document.createElement('li');
                li.className = 'email-item list-group-item';
                li.innerHTML = `
                    <div class="row">
                        <div class="col-3">${email.sender}</div>
                        <div class="col-4">${email.subject}</div>
                        <div class="col-3">${email.snippet}</div>
                        <div class="col-2 text-end">${email.time}</div>
                    </div>
                `;
                emailList.insertBefore(li, emailList.firstChild);
            });
            draftCount.textContent = data.draft_count;
        })
        .catch(error => console.error('Error loading drafts:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    loadInbox();
    document.getElementById('inboxBtn').addEventListener('click', function(e) {
        e.preventDefault();
        loadInbox();
    });
    document.getElementById('sentBtn').addEventListener('click', function(e) {
        e.preventDefault();
        loadSent();
    });
    document.getElementById('draftsBtn').addEventListener('click', function(e) {
        e.preventDefault();
        loadDrafts();
    });
    // document.getElementById('compose').addEventListener('click', function() {
    //     document.getElementById('sender').value = '{{ settings.EMAIL_SENDER }}';
    // });
    document.getElementById('sendEmail').addEventListener('click', function() {
        const form = document.getElementById('composeForm');
        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch("/send-email/", {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
                bootstrap.Modal.getInstance(document.getElementById('composeModal')).hide();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => alert('Error sending email: ' + error));
    });
});