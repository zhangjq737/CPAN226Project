// email_client_app/static/email_client_app/js/email.js

// UI Helper Functions
const UI = {
    showLoadingIndicator() {
        const emailList = document.getElementById('email-list');
        emailList.innerHTML = '';

        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'loading-indicator';
        loadingDiv.className = 'flex justify-center items-center py-10';

        const spinner = document.createElement('div');
        spinner.className = 'animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500';

        const loadingText = document.createElement('span');
        loadingText.className = 'ml-3 text-gray-600';
        loadingText.textContent = 'Loading emails...';

        loadingDiv.appendChild(spinner);
        loadingDiv.appendChild(loadingText);
        emailList.appendChild(loadingDiv);
    },

    hideLoadingIndicator() {
        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
    },

    setActiveNavigation(activeId) {
        const navItems = document.querySelectorAll('nav a');
        navItems.forEach(item => {
            item.classList.remove('bg-primary-50', 'text-primary-700');
            item.classList.add('text-gray-700', 'hover:bg-gray-100', 'hover:text-gray-900');
        });

        const activeItem = document.getElementById(activeId);
        if (activeItem) {
            activeItem.classList.remove('text-gray-700', 'hover:bg-gray-100', 'hover:text-gray-900');
            activeItem.classList.add('bg-primary-50', 'text-primary-700');
        }
    },

    createEmailListItem(email, folder) {
        const li = document.createElement('li');
        li.className = `cursor-pointer hover:bg-gray-50 transition-colors duration-150 ${email.unread ? 'bg-blue-50' : ''}`;
        li.dataset.id = email.id;
        li.dataset.folder = folder;

        const row = document.createElement('div');
        row.className = "flex px-6 py-3 items-center";

        const cells = [
            { content: email.sender, className: "w-1/4 font-medium truncate" },
            { content: email.subject, className: "w-1/3 truncate" },
            { content: email.snippet, className: "w-1/4 text-gray-500 truncate" },
            { content: email.time, className: "w-1/6 text-right text-sm text-gray-500" }
        ];

        cells.forEach(cell => {
            const div = document.createElement('div');
            div.className = cell.className;
            div.textContent = cell.content;
            row.appendChild(div);
        });

        li.appendChild(row);
        return li;
    }
};

// Email Operations
const EmailOperations = {
    async loadEmails(endpoint, folder, options = {}) {
        UI.showLoadingIndicator();
        try {
            UI.setActiveNavigation(options.activeButton);
            const response = await fetch(endpoint);
            const data = await response.json();
            const emailList = document.getElementById('email-list');
            emailList.innerHTML = '';

            data.emails.forEach(email => {
                const li = UI.createEmailListItem(email, folder);
                emailList.insertBefore(li, emailList.firstChild);
            });

            if (options.updateCount) {
                const countElement = document.getElementById(options.countElement);
                if (countElement) {
                    countElement.textContent = data[options.countProperty];
                }
            }
        } catch (error) {
            console.error(`Error loading ${folder}:`, error);
            document.getElementById('email-list').innerHTML =
                '<div class="p-4 text-red-500">Failed to load emails. Please try again.</div>';
        } finally {
            UI.hideLoadingIndicator();
        }
    },

    async sendEmail(form) {
        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        try {
            const response = await fetch("/send-email/", {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            const data = await response.json();

            if (data.status === 'success') {
                alert(data.message);
                document.getElementById('composeModal').classList.add('hidden');
                form.reset();
                this.loadEmails('/sent/', '[Gmail]/Sent Mail', { activeButton: 'sentBtn' });
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            alert('Error sending email: ' + error);
        }
    },

    async saveDraft(form) {
        const draftData = {
            receiver: form.receiver.value,
            subject: form.subject.value,
            body: form.body.value,
            cc: form.cc.value
        };

        try {
            const response = await fetch('/save-draft/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(draftData)
            });
            const data = await response.json();

            if (data.status === 'success') {
                document.getElementById('composeModal').classList.add('hidden');
                form.reset();
                this.loadEmails('/drafts/', '[Gmail]/Drafts', {
                    activeButton: 'draftsBtn',
                    updateCount: true,
                    countElement: 'draft-count',
                    countProperty: 'draft_count'
                });
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error details:', error);
            alert('Error saving draft: ' + error);
        }
    }
};

// Initialize Application
document.addEventListener('DOMContentLoaded', function () {
    // Initial load
    EmailOperations.loadEmails('/inbox/', 'INBOX', {
        activeButton: 'inboxBtn',
        updateCount: true,
        countElement: 'unread-count',
        countProperty: 'unread_count'
    });

    // Setup navigation events
    const navigationHandlers = {
        'inboxBtn': () => EmailOperations.loadEmails('/inbox/', 'INBOX', {
            activeButton: 'inboxBtn',
            updateCount: true,
            countElement: 'unread-count',
            countProperty: 'unread_count'
        }),
        'sentBtn': () => EmailOperations.loadEmails('/sent/', '[Gmail]/Sent Mail', {
            activeButton: 'sentBtn'
        }),
        'draftsBtn': () => EmailOperations.loadEmails('/drafts/', '[Gmail]/Drafts', {
            activeButton: 'draftsBtn',
            updateCount: true,
            countElement: 'draft-count',
            countProperty: 'draft_count'
        })
    };

    Object.entries(navigationHandlers).forEach(([id, handler]) => {
        document.getElementById(id).addEventListener('click', (e) => {
            e.preventDefault();
            handler();
        });
    });

    // Setup compose modal events
    const composeForm = document.getElementById('composeForm');
    document.getElementById('sendEmail').addEventListener('click', () =>
        EmailOperations.sendEmail(composeForm));
    document.getElementById('saveDraft').addEventListener('click', () =>
        EmailOperations.saveDraft(composeForm));
    document.getElementById('deleteDraft').addEventListener('click', () => {
        if (confirm("Are you sure you want to discard this draft?")) {
            composeForm.reset();
            document.getElementById('composeModal').classList.add('hidden');
        }
    });

    // Setup email details handler
    document.getElementById('email-list').addEventListener('click', function (e) {
        const emailItem = e.target.closest('li');
        if (emailItem?.dataset.id && emailItem?.dataset.folder) {
            fetch(`/get_email_detail/?id=${encodeURIComponent(emailItem.dataset.id)}&folder=${encodeURIComponent(emailItem.dataset.folder)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.email) {
                        window.showEmailDetails(data.email);
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error fetching email details:', error);
                    alert('Failed to load email details.');
                });
        }
    });
});