let authToken = localStorage.getItem('authToken');
let currentUser = null;

const translations = {
    'en': {
        'subtitle': 'Explore your emotions and cognitive patterns',
        'textLabel': 'Share your thoughts:',
        'textPlaceholder': 'I\'ve been feeling... ✍️',
        'languageLabel': 'Language:',
        'submitButton': 'Analyze Text',
        'loading': 'Analysis in progress...',
        'sentiment': 'Sentiment:',
        'confidence': 'AI-model Confidence Score:',
        'emotions': 'Emotions:',
        'skills': 'Skills:',
        'patterns': 'Cognitive Patterns:',
        'none': 'None detected',
        'error': 'Error:',
        'loginTitle': 'Login / Register',
        'usernamePlaceholder': 'Username',
        'emailPlaceholder': 'Email (for registration)',
        'passwordPlaceholder': 'Password',
        'loginButton': 'Login',
        'registerButton': 'Register',
        'logoutButton': 'Logout',
        'welcome': 'Welcome, '
    },
    'ru': {
        'subtitle': 'Исследуйте свои эмоции и когнитивные паттерны',
        'textLabel': 'Поделитесь мыслями:',
        'textPlaceholder': 'Я чувствую... ✍️',
        'languageLabel': 'Язык:',
        'submitButton': 'Анализировать текст',
        'loading': 'Анализ выполняется...',
        'sentiment': 'Настроение:',
        'confidence': 'Оценка уверенности AI-модели:',
        'emotions': 'Эмоции:',
        'skills': 'Навыки:',
        'patterns': 'Когнитивные искажения:',
        'none': 'Не обнаружено',
        'error': 'Ошибка:',
        'loginTitle': 'Вход / Регистрация',
        'usernamePlaceholder': 'Имя пользователя',
        'emailPlaceholder': 'Email (для регистрации)',
        'passwordPlaceholder': 'Пароль',
        'loginButton': 'Войти',
        'registerButton': 'Зарегистрироваться',
        'logoutButton': 'Выйти',
        'welcome': 'Добро пожаловать, '
    }
};

function toggleAuthForms() {
    const isLoggedIn = authToken !== null;
    document.getElementById('authSection').style.display = isLoggedIn ? 'none' : 'block';
    document.getElementById('analysisSection').style.display = isLoggedIn ? 'block' : 'none';
    
    if (isLoggedIn && currentUser) {
        document.getElementById('userGreeting').textContent = translations[document.getElementById('language').value].welcome + currentUser.username;
    }
}

async function register(username, email, password) {
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        const data = await response.json();
        if (response.ok) {
            authToken = data.token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            toggleAuthForms();
            return data;
        } else {
            throw new Error(data.error || 'Registration failed');
        }
    } catch (error) {
        console.error('Registration error:', error);
        throw error;
    }
}

async function login(username, password) {
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (response.ok) {
            authToken = data.token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            toggleAuthForms();
            return data;
        } else {
            throw new Error(data.error || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    toggleAuthForms();
}

function handleRegister() {
    const username = document.getElementById('authUsername').value;
    const email = document.getElementById('authEmail').value;
    const password = document.getElementById('authPassword').value;
    
    if (!username || !email || !password) {
        alert('Please fill all fields');
        return;
    }
    
    register(username, email, password)
        .catch(error => alert(error.message));
}

function handleLogin() {
    const username = document.getElementById('authUsername').value;
    const password = document.getElementById('authPassword').value;
    
    if (!username || !password) {
        alert('Please fill username and password');
        return;
    }
    
    login(username, password)
        .catch(error => alert(error.message));
}

function handleLogout() {
    logout();
}

function updateLanguage() {
    const lang = document.getElementById('language').value;
    const t = translations[lang];
    document.getElementById('subtitle').textContent = t.subtitle;
    document.getElementById('textLabel').textContent = t.textLabel;
    document.getElementById('text').placeholder = t.textPlaceholder;
    document.getElementById('languageLabel').textContent = t.languageLabel;
    document.getElementById('submitButton').textContent = t.submitButton;
    document.getElementById('disclaimer-en').style.display = (lang === 'en') ? 'block' : 'none';
    document.getElementById('disclaimer-ru').style.display = (lang === 'ru') ? 'block' : 'none';
    document.getElementById('authTitle').textContent = t.loginTitle;
    document.getElementById('authUsername').placeholder = t.usernamePlaceholder;
    document.getElementById('authEmail').placeholder = t.emailPlaceholder;
    document.getElementById('authPassword').placeholder = t.passwordPlaceholder;
    document.getElementById('loginButton').textContent = t.loginButton;
    document.getElementById('registerButton').textContent = t.registerButton;
    document.getElementById('logoutButton').textContent = t.logoutButton;
    
    if (currentUser) {
        document.getElementById('userGreeting').textContent = t.welcome + currentUser.username;
    }
}

document.getElementById('language').addEventListener('change', updateLanguage);
updateLanguage();

document.getElementById('analysisForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!authToken) {
        alert('Please login first');
        return;
    }

    const form = e.target;
    const resultDiv = document.getElementById('result');
    const button = form.querySelector('button');
    const lang = document.getElementById('language').value;
    const t = translations[lang];
    
    button.textContent = lang === 'ru' ? 'Анализируем...' : 'Analyzing...';
    button.disabled = true;
    resultDiv.innerHTML = `<div class="loading">${t.loading}</div>`;
    
    try {
        const formData = new FormData(form);
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                text: formData.get('text'),
                language: lang
            })
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.details || 'Analysis failed');
        
        resultDiv.innerHTML = `
            <div class="result-item"><div class="result-label">${t.sentiment}</div><div>${data.sentiment}</div></div>
            <div class="result-item"><div class="result-label">${t.confidence}</div><div>${(data.confidence_score * 100).toFixed(1)}%</div></div>
            <div class="result-item"><div class="result-label">${t.emotions}</div><div>${data.entities.emotions.join(', ') || t.none}</div></div>
            <div class="result-item"><div class="result-label">${t.skills}</div><div>${data.entities.skills.join(', ') || t.none}</div></div>
            <div class="result-item"><div class="result-label">${t.patterns}</div><div>${data.distortions.join(', ') || t.none}</div></div>
        `;
        
    } catch (error) {
        if (error.message.includes('401') || error.message.includes('token')) {
            logout();
            alert('Session expired. Please login again.');
        }
        resultDiv.innerHTML = `<div class="error"><strong>${t.error}</strong> ${error.message}</div>`;
    } finally {
        button.textContent = t.submitButton;
        button.disabled = false;
    }
});

document.addEventListener('DOMContentLoaded', () => {
    toggleAuthForms();
});