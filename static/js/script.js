// ===========================
//       DOM Elements
// ===========================
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const removeBtn = document.getElementById('removeBtn');
const previewContainer = document.getElementById('previewContainer');
const imagePreview = document.getElementById('imagePreview');
const resultsSection = document.getElementById('resultsSection');
const predictionsContainer = document.getElementById('predictionsContainer');
const loadingContainer = document.getElementById('loadingContainer');
const emptyState = document.getElementById('emptyState');
const dropZoneContent = document.querySelector('.drop-zone-content');
const darkModeToggle = document.getElementById('darkModeToggle');

// ===========================
//           State
// ===========================
let selectedFile = null;

// ===========================
//      Dark Mode Toggle
// ===========================
darkModeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode ? 'true' : 'false');
    
    showNotification(
        isDarkMode ? 'Dark mode activated! 🌙' : 'Light mode activated! ☀️',
        'info'
    );
});

window.addEventListener('DOMContentLoaded', () => {
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode === 'true') {
        document.body.classList.add('dark-mode');
    }
});

// ===========================
//    File Upload Handling
// ===========================

browseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
});

dropZone.addEventListener('click', (e) => {
    if (!previewContainer.style.display || previewContainer.style.display === 'none') {
        fileInput.click();
    }
});

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('drag-over');
    
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        handleFile(file);
    } else {
        showNotification('Please drop an image file! 🖼️', 'error');
    }
});

// ===========================
//       File Processing
// ===========================
function handleFile(file) {
    selectedFile = file;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        dropZoneContent.style.display = 'none';
        previewContainer.style.display = 'flex';
        analyzeBtn.disabled = false;
        
        resultsSection.style.display = 'none';
        emptyState.style.display = 'block';
        
        showNotification('Image loaded! Ready to analyze! 🎉', 'success');
    };
    reader.readAsDataURL(file);
}

removeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    selectedFile = null;
    fileInput.value = '';
    dropZoneContent.style.display = 'block';
    previewContainer.style.display = 'none';
    analyzeBtn.disabled = true;
    resultsSection.style.display = 'none';
    emptyState.style.display = 'block';
    
    showNotification('Image removed!', 'info');
});

// ===========================
//       Image Analysis
// ===========================
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    // Show loading state
    loadingContainer.style.display = 'block';
    resultsSection.style.display = 'none';
    emptyState.style.display = 'none';
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data.predictions);
            showNotification('Analysis complete! ✨', 'success');
        } else {
            showNotification('Oops! ' + (data.error || 'Unknown error'), 'error');
            emptyState.style.display = 'block';
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to analyze image. Please try again! 😅', 'error');
        emptyState.style.display = 'block';
    } finally {
        loadingContainer.style.display = 'none';
    }
});

// ===========================
//      Display Results
// ===========================
function displayResults(predictions) {
    predictionsContainer.innerHTML = '';
    
    predictions.forEach((pred, index) => {
        const card = document.createElement('div');
        card.className = 'prediction-card';
        
        card.innerHTML = `
            <div class="prediction-emoji">${pred.emoji}</div>
            <div class="prediction-info">
                <div class="prediction-label">${pred.label}</div>
                <div class="confidence-bar-container">
                    <div class="confidence-bar" style="width: 0%;" data-width="${pred.confidence}"></div>
                    <div class="confidence-text">${pred.confidence}%</div>
                </div>
            </div>
        `;
        
        predictionsContainer.appendChild(card);
        
        setTimeout(() => {
            const bar = card.querySelector('.confidence-bar');
            bar.style.width = bar.dataset.width + '%';
        }, 100 + (index * 100));
    });
    
    resultsSection.style.display = 'block';
    emptyState.style.display = 'none';
}

// ===========================
//     Notification System
// ===========================
function showNotification(message, type = 'info') {
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notif => notif.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const emoji = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    
    notification.innerHTML = `
        <span class="notification-emoji">${emoji}</span>
        <span class="notification-text">${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    requestAnimationFrame(() => {
        notification.classList.add('show');
    });
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ===============================
// Notification Styles (Injected)
// ===============================
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    .notification {
        position: fixed;
        top: 70px;
        right: -400px;
        background: white;
        border: 2px solid var(--color-border, #D1D9E6);
        border-radius: 12px;
        padding: 12px 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        gap: 10px;
        font-family: 'Grandstander', cursive;
        font-weight: 600;
        font-size: 0.95rem;
        z-index: 10001;
        transition: right 0.3s ease;
        max-width: 320px;
    }
    
    .notification.show {
        right: 16px;
    }
    
    .notification-success {
        background: #9DB6A5;
        color: white;
        border-color: #8AA595;
    }
    
    .notification-error {
        background: #E07A5F;
        color: white;
        border-color: #D4674F;
    }
    
    .notification-info {
        background: #7C9CBF;
        color: white;
        border-color: #6A8BAF;
    }
    
    .notification-emoji {
        font-size: 1.2rem;
        flex-shrink: 0;
    }
    
    .notification-text {
        flex: 1;
    }
    
    body.dark-mode .notification {
        border-color: #4B5563;
    }
    
    body.dark-mode .notification-success {
        background: #8AA595;
    }
    
    body.dark-mode .notification-error {
        background: #D4674F;
    }
    
    body.dark-mode .notification-info {
        background: #6A8BAF;
    }
    
    @media (max-width: 768px) {
        .notification {
            font-size: 0.85rem;
            padding: 10px 16px;
            max-width: 280px;
            top: 60px;
        }
        
        .notification.show {
            right: 12px;
        }
        
        .notification-emoji {
            font-size: 1.1rem;
        }
    }
`;

document.head.appendChild(notificationStyles);
