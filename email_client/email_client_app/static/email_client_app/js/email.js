// email_client_app/static/email_client_app/js/email.js
function showLoadingIndicator() {
    const emailList = document.getElementById('email-list');
    emailList.innerHTML = '';
    
    // Create loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading-indicator';
    loadingDiv.className = 'flex justify-center items-center py-10';
    
    // Create spinning circle animation
    const spinner = document.createElement('div');
    spinner.className = 'animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500';
    
    // Add loading text
    const loadingText = document.createElement('span');
    loadingText.className = 'ml-3 text-gray-600';
    loadingText.textContent = 'Loading emails...';
    
    // Assemble the loading indicator
    loadingDiv.appendChild(spinner);
    loadingDiv.appendChild(loadingText);
    
    // Add to email list container
    emailList.appendChild(loadingDiv);
}

function hideLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

function loadInbox() {
    showLoadingIndicator();
    
    fetch("/inbox/")
        .then(response => response.json())
        .then(data => {
            const emailList = document.getElementById('email-list');
            const unreadCount = document.getElementById('unread-count');
            emailList.innerHTML = '';
            
            data.emails.forEach(email => {
                const li = document.createElement('li');
                li.className = `cursor-pointer hover:bg-gray-50 transition-colors duration-150 ${email.unread ? 'bg-blue-50' : ''}`;
                
                // Create a single flex container for the entire row
                const row = document.createElement('div');
                row.className = "flex px-6 py-3 items-center";
                
                // Create and append each cell
                const senderCell = document.createElement('div');
                senderCell.className = "w-1/4 font-medium truncate";
                senderCell.textContent = email.sender;
                
                const subjectCell = document.createElement('div');
                subjectCell.className = "w-1/3 truncate";
                subjectCell.textContent = email.subject;
                
                const snippetCell = document.createElement('div');
                snippetCell.className = "w-1/4 text-gray-500 truncate";
                snippetCell.textContent = email.snippet;
                
                const timeCell = document.createElement('div');
                timeCell.className = "w-1/6 text-right text-sm text-gray-500";
                timeCell.textContent = email.time;
                
                // Append all cells to the row
                row.appendChild(senderCell);
                row.appendChild(subjectCell);
                row.appendChild(snippetCell);
                row.appendChild(timeCell);
                
                // Append the row to the list item
                li.appendChild(row);
                
                // Insert at the beginning of the list to keep newest emails on top
                emailList.insertBefore(li, emailList.firstChild);
            });
            
            unreadCount.textContent = data.unread_count;
            
            // Set active navigation
            setActiveNavigation('inboxBtn');
        })
        .catch(error => {
            console.error('Error loading inbox:', error);
            // Show error message in the list
            const emailList = document.getElementById('email-list');
            emailList.innerHTML = '<div class="p-4 text-red-500">Failed to load emails. Please try again.</div>';
        })
        .finally(() => {
            hideLoadingIndicator();
        });
}

function loadSent() {
    showLoadingIndicator();
    
    fetch("/sent/")
        .then(response => response.json())
        .then(data => {
            const emailList = document.getElementById('email-list');
            emailList.innerHTML = '';
            
            data.emails.forEach(email => {
                const li = document.createElement('li');
                li.className = 'cursor-pointer hover:bg-gray-50 transition-colors duration-150';
                
                // Create a single flex container for the entire row
                const row = document.createElement('div');
                row.className = "flex px-6 py-3 items-center";
                
                // Create and append each cell
                const senderCell = document.createElement('div');
                senderCell.className = "w-1/4 font-medium truncate";
                senderCell.textContent = email.sender;
                
                const subjectCell = document.createElement('div');
                subjectCell.className = "w-1/3 truncate";
                subjectCell.textContent = email.subject;
                
                const snippetCell = document.createElement('div');
                snippetCell.className = "w-1/4 text-gray-500 truncate";
                snippetCell.textContent = email.snippet;
                
                const timeCell = document.createElement('div');
                timeCell.className = "w-1/6 text-right text-sm text-gray-500";
                timeCell.textContent = email.time;
                
                // Append all cells to the row
                row.appendChild(senderCell);
                row.appendChild(subjectCell);
                row.appendChild(snippetCell);
                row.appendChild(timeCell);
                
                // Append the row to the list item
                li.appendChild(row);
                
                // Insert at the beginning of the list to keep newest emails on top
                emailList.insertBefore(li, emailList.firstChild);
            });
            
            // Set active navigation
            setActiveNavigation('sentBtn');
        })
        .catch(error => {
            console.error('Error loading sent:', error);
            // Show error message in the list
            const emailList = document.getElementById('email-list');
            emailList.innerHTML = '<div class="p-4 text-red-500">Failed to load emails. Please try again.</div>';
        })
        .finally(() => {
            hideLoadingIndicator();
        });
}

function loadDrafts() {
    showLoadingIndicator();
    
    fetch("/drafts/")
        .then(response => response.json())
        .then(data => {
            const emailList = document.getElementById('email-list');
            const draftCount = document.getElementById('draft-count');
            emailList.innerHTML = '';
            
            data.emails.forEach(email => {
                const li = document.createElement('li');
                li.className = 'cursor-pointer hover:bg-gray-50 transition-colors duration-150';
                
                // Create a single flex container for the entire row
                const row = document.createElement('div');
                row.className = "flex px-6 py-3 items-center";
                
                // Create and append each cell
                const senderCell = document.createElement('div');
                senderCell.className = "w-1/4 font-medium truncate";
                senderCell.textContent = email.sender;
                
                const subjectCell = document.createElement('div');
                subjectCell.className = "w-1/3 truncate";
                subjectCell.textContent = email.subject;
                
                const snippetCell = document.createElement('div');
                snippetCell.className = "w-1/4 text-gray-500 truncate";
                snippetCell.textContent = email.snippet;
                
                const timeCell = document.createElement('div');
                timeCell.className = "w-1/6 text-right text-sm text-gray-500";
                timeCell.textContent = email.time;
                
                // Append all cells to the row
                row.appendChild(senderCell);
                row.appendChild(subjectCell);
                row.appendChild(snippetCell);
                row.appendChild(timeCell);
                
                // Append the row to the list item
                li.appendChild(row);
                
                // Insert at the beginning of the list to keep newest emails on top
                emailList.insertBefore(li, emailList.firstChild);
            });
            
            draftCount.textContent = data.draft_count;
            
            // Set active navigation
            setActiveNavigation('draftsBtn');
        })
        .catch(error => {
            console.error('Error loading drafts:', error);
            // Show error message in the list
            const emailList = document.getElementById('email-list');
            emailList.innerHTML = '<div class="p-4 text-red-500">Failed to load emails. Please try again.</div>';
        })
        .finally(() => {
            hideLoadingIndicator();
        });
}

// Function to set active navigation item
function setActiveNavigation(activeId) {
    // Remove active class from all navigation items
    const navItems = document.querySelectorAll('nav a');
    navItems.forEach(item => {
        item.classList.remove('bg-primary-50', 'text-primary-700');
        item.classList.add('text-gray-700', 'hover:bg-gray-100', 'hover:text-gray-900');
    });
    
    // Add active class to selected item
    const activeItem = document.getElementById(activeId);
    if (activeItem) {
        activeItem.classList.remove('text-gray-700', 'hover:bg-gray-100', 'hover:text-gray-900');
        activeItem.classList.add('bg-primary-50', 'text-primary-700');
    }
}

// Handle modal functionality
function setupComposeModal() {
    const modal = document.getElementById('composeModal');
    const openButton = document.getElementById('compose');
    const closeButtons = modal.querySelectorAll('[data-bs-dismiss="modal"]');
    
    // Open modal
    if (openButton) {
        openButton.addEventListener('click', function() {
            modal.classList.remove('hidden');
        });
    }
    
    // Close modal
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            modal.classList.add('hidden');
        });
    });
    
    // Close when clicking outside
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.classList.add('hidden');
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Initial load
    loadInbox();
    
    // Setup navigation events
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
    
    // Setup modal
    setupComposeModal();
    
    // Email sending functionality
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
                // Hide modal
                document.getElementById('composeModal').classList.add('hidden');
                // Clear form
                form.reset();
                // Reload appropriate list
                loadSent();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => alert('Error sending email: ' + error));
    });
    
    // Add save draft functionality
    document.getElementById('saveDraft').addEventListener('click', function() {
        const form = document.getElementById('composeForm');
        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch("/save-draft/", {
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
                alert(data.message || 'Draft saved successfully');
                // Hide modal
                document.getElementById('composeModal').classList.add('hidden');
                // Update draft count if available
                if (data.draft_count) {
                    document.getElementById('draft-count').textContent = data.draft_count;
                }
                // If we're in the drafts view, refresh it
                if (document.getElementById('draftsBtn').classList.contains('bg-primary-50')) {
                    loadDrafts();
                }
            } else {
                alert('Error: ' + (data.message || 'Failed to save draft'));
            }
        })
        .catch(error => alert('Error saving draft: ' + error));
    });
});