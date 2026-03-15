// API Base URL
const API_URL = 'http://127.0.0.1:8000/api';
let currentToken = localStorage.getItem('token');
let isLoginMode = true;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
});

// Auth Functions
function checkAuth() {
    if (currentToken) {
        showAuthenticatedUI();
    } else {
        showGuestUI();
    }
}

function showLogin() {
    isLoginMode = true;
    document.getElementById('modalTitle').textContent = 'Вход';
    document.getElementById('authSubmitBtn').textContent = 'Войти';
    document.getElementById('switchText').textContent = 'Нет аккаунта?';
    document.getElementById('switchLink').textContent = 'Зарегистрироваться';
    document.getElementById('authModal').style.display = 'block';
}

function showRegister() {
    isLoginMode = false;
    document.getElementById('modalTitle').textContent = 'Регистрация';
    document.getElementById('authSubmitBtn').textContent = 'Зарегистрироваться';
    document.getElementById('switchText').textContent = 'Уже есть аккаунт?';
    document.getElementById('switchLink').textContent = 'Войти';
    document.getElementById('authModal').style.display = 'block';
}

function switchAuthMode() {
    if (isLoginMode) {
        showRegister();
    } else {
        showLogin();
    }
}

function closeModal() {
    document.getElementById('authModal').style.display = 'none';
}

async function handleAuth(event) {
    event.preventDefault();
    
    const email = document.getElementById('authEmail').value;
    const password = document.getElementById('authPassword').value;
    
    try {
        if (isLoginMode) {
            // Login
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);
            
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData
            });
            
            if (!response.ok) throw new Error('Ошибка входа');
            
            const data = await response.json();
            currentToken = data.access_token;
            localStorage.setItem('token', currentToken);
            
            closeModal();
            showAuthenticatedUI();
            loadMyLinks();
        } else {
            // Register
            const response = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            
            if (!response.ok) throw new Error('Ошибка регистрации');
            
            alert('Регистрация успешна! Теперь войдите.');
            showLogin();
        }
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
}

function logout() {
    currentToken = null;
    localStorage.removeItem('token');
    showGuestUI();
    document.getElementById('myLinksSection').style.display = 'none';
}

function showAuthenticatedUI() {
    document.getElementById('authButtons').style.display = 'none';
    document.getElementById('userInfo').style.display = 'flex';
    document.getElementById('userEmail').textContent = 'user@email.com'; // Можно получить из токена
    document.getElementById('myLinksSection').style.display = 'block';
}

function showGuestUI() {
    document.getElementById('authButtons').style.display = 'flex';
    document.getElementById('userInfo').style.display = 'none';
}

// Main Function: Shorten URL
async function shortenUrl() {
    const urlInput = document.getElementById('urlInput');
    const originalUrl = urlInput.value.trim();
    
    if (!originalUrl) {
        alert('Пожалуйста, введите URL');
        return;
    }
    
    // Add https:// if not present
    let url = originalUrl;
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://' + url;
    }
    
    try {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // Add auth if available
        if (currentToken) {
            headers['Authorization'] = `Bearer ${currentToken}`;
        }
        
        const response = await fetch(`${API_URL}/links/shorten`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ original_url: url })
        });
        
        if (!response.ok) {
            throw new Error('Ошибка при создании ссылки');
        }
        
        const data = await response.json();
        showResult(data);
        
        // Load my links if authenticated
        if (currentToken) {
            loadMyLinks();
        }
        
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
}

function showResult(data) {
    const resultContainer = document.getElementById('resultContainer');
    const shortUrl = document.getElementById('shortUrl');
    const createdAt = document.getElementById('createdAt');
    const clickCount = document.getElementById('clickCount');
    
    shortUrl.href = data.short_url;
    shortUrl.textContent = data.short_url;
    
    // Format date
    const date = new Date(data.created_at);
    createdAt.textContent = date.toLocaleString('ru-RU');
    
    clickCount.textContent = data.click_count || 0;
    
    resultContainer.style.display = 'block';
    
    // Scroll to result
    resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function copyToClipboard() {
    const shortUrl = document.getElementById('shortUrl').textContent;
    
    navigator.clipboard.writeText(shortUrl).then(() => {
        alert('Ссылка скопирована!');
    }).catch(err => {
        // Fallback
        const textArea = document.createElement('textarea');
        textArea.value = shortUrl;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert('Ссылка скопирована!');
    });
}

// Load My Links
async function loadMyLinks() {
    if (!currentToken) return;
    
    try {
        const response = await fetch(`${API_URL}/links/my`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (!response.ok) throw new Error('Ошибка загрузки ссылок');
        
        const links = await response.json();
        displayMyLinks(links);
        
    } catch (error) {
        console.error('Error loading links:', error);
    }
}

function displayMyLinks(links) {
    const container = document.getElementById('linksList');
    
    if (links.length === 0) {
        container.innerHTML = '<p style="color: #999; text-align: center;">У вас пока нет ссылок</p>';
        return;
    }
    
    container.innerHTML = links.map(link => `
        <div class="link-item">
            <a href="${link.short_url}" target="_blank">${link.short_url}</a>
            <p>Оригинал: ${link.original_url}</p>
            <p>📊 Переходов: ${link.click_count || 0} | 📅 ${new Date(link.created_at).toLocaleString('ru-RU')}</p>
        </div>
    `).join('');
    
    document.getElementById('myLinksSection').style.display = 'block';
}

// Close modal on outside click
window.onclick = function(event) {
    const modal = document.getElementById('authModal');
    if (event.target === modal) {
        closeModal();
    }
}