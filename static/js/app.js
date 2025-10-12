let authToken = localStorage.getItem('authToken');
let currentUser = null;

const translations = {
    'en': {
        'subtitle': 'Explore your emotions and cognitive patterns',
        'textLabel': 'Share your thoughts:',
        'textPlaceholder': 'I\'ve been feeling... ✍️',
        'authLanguageLabel': 'Language:',
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
        'welcome': 'Welcome, ',
        'authLoading': 'Processing...',
        'networkError': 'Network error. Please check your connection.',
        'sessionExpired': 'Session expired. Please login again.',
        'fillAllFields': 'Please fill all fields',
        'fillUsernamePassword': 'Please fill username and password',
        'validEmail': 'Please enter a valid email'
    },
    'ru': {
        'subtitle': 'Исследуйте свои эмоции и когнитивные паттерны',
        'textLabel': 'Поделитесь мыслями:',
        'textPlaceholder': 'Я чувствую... ✍️',
        'authLanguageLabel': 'Язык:',
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
        'welcome': 'Добро пожаловать, ',
        'authLoading': 'Обработка...',
        'networkError': 'Проблемы с соединением. Проверьте интернет.',
        'sessionExpired': 'Сессия истекла. Пожалуйста, войдите снова.',
        'fillAllFields': 'Пожалуйста, заполните все поля',
        'fillUsernamePassword': 'Пожалуйста, заполните имя пользователя и пароль',
        'validEmail': 'Пожалуйста, введите корректный email'
    }
};

class LanguageManager {
    constructor() {
        this.supportedLanguages = ['ru', 'en'];
        this.defaultLanguage = 'ru';
    }

    detectBrowserLanguage() {
        const savedLang = this.getSavedLanguage();
        if (savedLang) return savedLang;

        const browserLanguages = this.getBrowserLanguages();
        
        for (let lang of browserLanguages) {
            const primaryLang = lang.split('-')[0].toLowerCase();
            if (this.supportedLanguages.includes(primaryLang)) {
                return primaryLang;
            }
        }

        return this.defaultLanguage;
    }

    getBrowserLanguages() {
        const languages = [];
        
        if (navigator.languages) {
            languages.push(...navigator.languages);
        }
        
        if (navigator.language) {
            languages.push(navigator.language);
        }
        
        if (navigator.userLanguage) {
            languages.push(navigator.userLanguage);
        }
        
        return [...new Set(languages)];
    }

    saveLanguagePreference(lang) {
        try {
            localStorage.setItem('userLanguage', lang);
            sessionStorage.setItem('currentLanguage', lang);
        } catch (e) {
            console.warn('Cannot save language preference:', e);
        }
    }

    getSavedLanguage() {
        try {
            return localStorage.getItem('userLanguage') || sessionStorage.getItem('currentLanguage');
        } catch (e) {
            return null;
        }
    }

    applyLanguage(lang) {
        const finalLang = this.supportedLanguages.includes(lang) ? lang : this.defaultLanguage;
        
        document.getElementById('language').value = finalLang;
        document.getElementById('authLanguage').value = finalLang;
        
        this.saveLanguagePreference(finalLang);
        
        updateLanguage();
        
        return finalLang;
    }
}

const languageManager = new LanguageManager();

function initializeLanguage() {
    const detectedLang = languageManager.detectBrowserLanguage();
    languageManager.applyLanguage(detectedLang);
}

function setAuthButtonLoading(button, isLoading) {
    const lang = document.getElementById('authLanguage').value;
    const t = translations[lang];
    
    if (isLoading) {
        button.dataset.originalText = button.textContent;
        button.textContent = t.authLoading;
        button.disabled = true;
    } else {
        button.textContent = button.dataset.originalText || 
                           (button.id === 'loginButton' ? t.loginButton : t.registerButton);
        button.disabled = false;
    }
}

class ApiClient {
    constructor() {
        this.baseUrl = '';
    }

    async request(endpoint, options = {}) {
        const lang = document.getElementById('language').value;
        const t = translations[lang];
        
        try {
            const response = await fetch(endpoint, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
            });

            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error(t.sessionExpired);
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error(t.networkError);
            }
            throw error;
        }
    }

    async authenticatedRequest(endpoint, options = {}) {
        return this.request(endpoint, {
            ...options,
            headers: {
                'Authorization': `Bearer ${authToken}`,
                ...options.headers,
            },
        });
    }
}

const apiClient = new ApiClient();

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function toggleAuthForms() {
    const isLoggedIn = authToken !== null;
    document.getElementById('authSection').style.display = isLoggedIn ? 'none' : 'block';
    document.getElementById('analysisSection').style.display = isLoggedIn ? 'block' : 'none';

    if (!isLoggedIn) {
        const mainLang = document.getElementById('language').value;
        document.getElementById('authLanguage').value = mainLang;
    }
    
    if (isLoggedIn && currentUser) {
        const greeting = translations[document.getElementById('language').value].welcome;
        document.getElementById('userGreeting').textContent = greeting + currentUser.username;
    } else {
        document.getElementById('userGreeting').textContent = '';
    }
}

async function register(username, email, password) {
    const registerBtn = document.getElementById('registerButton');
    setAuthButtonLoading(registerBtn, true);

    try {
        const language = document.getElementById('authLanguage').value;
        const data = await apiClient.request('/api/auth/register', {
            method: 'POST', 
            body: JSON.stringify({ username, email, password, language })
        });
        
        authToken = data.token;
        currentUser = data.user;
        localStorage.setItem('authToken', authToken);
        toggleAuthForms();
        return data;
    } finally {
        setAuthButtonLoading(registerBtn, false);
    }
}

async function login(username, password) {
    const loginBtn = document.getElementById('loginButton');
    setAuthButtonLoading(loginBtn, true);

    try {
        const language = document.getElementById('authLanguage').value;
        const data = await apiClient.request('/api/auth/login', {
            method: 'POST', 
            body: JSON.stringify({ username, password, language })
        });
        
        authToken = data.token;
        currentUser = data.user;
        localStorage.setItem('authToken', authToken);
        toggleAuthForms();
        return data;
    } finally {
        setAuthButtonLoading(loginBtn, false);
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
    const lang = document.getElementById('authLanguage').value;
    const t = translations[lang];
    
    if (!username || !email || !password) {
        alert(t.fillAllFields);
        return;
    }
    
    if (!validateEmail(email)) {
        alert(t.validEmail);
        return;
    }
    
    register(username, email, password).catch(error => {
        alert(error.message);
    });
}

function handleLogin() {
    const username = document.getElementById('authUsername').value;
    const password = document.getElementById('authPassword').value;
    const lang = document.getElementById('authLanguage').value;
    const t = translations[lang];
    
    if (!username || !password) {
        alert(t.fillUsernamePassword);
        return;
    }
    
    login(username, password).catch(error => {
        alert(error.message);
    });
}

function handleLogout() {
    logout();
}

function updateLanguage() {
    const lang = document.getElementById('language').value;
    const t = translations[lang];

    document.querySelectorAll('[data-translate-placeholder]').forEach(element => {
        const key = element.getAttribute('data-translate-placeholder');
        if (t[key]) {
            element.placeholder = t[key];
        }
    });
    
    Object.keys(t).forEach(key => {
        const element = document.querySelector(`[data-translate="${key}"]`);
        if (element) {
            element.textContent = t[key];
        }
    });
    
    document.getElementById('disclaimer-en').style.display = (lang === 'en') ? 'block' : 'none';
    document.getElementById('disclaimer-ru').style.display = (lang === 'ru') ? 'block' : 'none'; 
    
    if (currentUser) {
        document.getElementById('userGreeting').textContent = t.welcome + currentUser.username;
    }
}

document.getElementById('authLanguage').addEventListener('change', function() {
    const newLang = this.value;
    languageManager.applyLanguage(newLang);
});

document.getElementById('language').addEventListener('change', function() {
    const newLang = this.value;
    languageManager.applyLanguage(newLang);
});

document.getElementById('analysisForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!authToken) {
        const lang = document.getElementById('language').value;
        const t = translations[lang];
        alert(t.sessionExpired);
        return;
    }

    const form = e.target;
    const resultDiv = document.getElementById('result');
    const button = form.querySelector('button');
    const lang = document.getElementById('language').value;
    const t = translations[lang];
    
    button.textContent = t.loading;
    button.disabled = true;
    resultDiv.innerHTML = `<div class="loading">${t.loading}</div>`;
    
    try {
        const formData = new FormData(form);
        const data = await apiClient.authenticatedRequest('/api/analyze', {
            method: 'POST', 
            body: JSON.stringify({
                text: formData.get('text'),
                language: lang
            })
        }); 
        
        resultDiv.innerHTML = `
            <div class="result-item"><div class="result-label">${t.sentiment}</div><div>${data.sentiment}</div></div>
            <div class="result-item"><div class="result-label">${t.confidence}</div><div>${(data.confidence_score * 100).toFixed(1)}%</div></div>
            <div class="result-item"><div class="result-label">${t.emotions}</div><div>${data.entities.emotions.join(', ') || t.none}</div></div>
            <div class="result-item"><div class="result-label">${t.skills}</div><div>${data.entities.skills.join(', ') || t.none}</div></div>
            <div class="result-item"><div class="result-label">${t.patterns}</div><div>${data.distortions.join(', ') || t.none}</div></div>
        `;
        
    } catch (error) {
        console.error('API Error:', error);

        if (error.message.includes(t.sessionExpired)) {
            logout();
            alert(t.sessionExpired);
            return;
        }
        
        resultDiv.innerHTML = `<div class="error"><strong>${t.error}</strong> ${error.message}</div>`;
    } finally {
        button.textContent = t.submitButton;
        button.disabled = false;
    }
});

document.addEventListener('DOMContentLoaded', () => {
    initializeLanguage();
    toggleAuthForms();
    
    document.getElementById('loginButton').setAttribute('data-translate', 'loginButton');
    document.getElementById('registerButton').setAttribute('data-translate', 'registerButton');
    document.getElementById('logoutButton').setAttribute('data-translate', 'logoutButton');
});