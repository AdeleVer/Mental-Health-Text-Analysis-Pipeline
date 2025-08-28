const translations = {
    'en': {
        'subtitle': 'AI-powered mental health text analysis',
        'textLabel': 'Share your thoughts:',
        'textPlaceholder': 'I\'ve been feeling... ✍️',
        'languageLabel': 'Language:',
        'submitButton': 'Analyze Text',
        'loading': 'Analysis in progress...',
        'sentiment': 'Sentiment:',
        'confidence': 'Confidence:',
        'emotions': 'Emotions:',
        'patterns': 'Cognitive Patterns:',
        'none': 'None detected',
        'error': 'Error:'
    },
    'ru': {
        'subtitle': 'Анализ психического здоровья с помощью ИИ',
        'textLabel': 'Поделитесь мыслями:',
        'textPlaceholder': 'Я чувствую... ✍️',
        'languageLabel': 'Язык:',
        'submitButton': 'Анализировать текст',
        'loading': 'Анализ выполняется...',
        'sentiment': 'Настроение:',
        'confidence': 'Уверенность:',
        'emotions': 'Эмоции:',
        'patterns': 'Когнитивные искажения:',
        'none': 'Не обнаружено',
        'error': 'Ошибка:'
    }
};

function updateLanguage() {
    const lang = document.getElementById('language').value;
    const t = translations[lang];
    document.getElementById('subtitle').textContent = t.subtitle;
    document.getElementById('textLabel').textContent = t.textLabel;
    document.getElementById('text').placeholder = t.textPlaceholder;
    document.getElementById('languageLabel').textContent = t.languageLabel;
    document.getElementById('submitButton').textContent = t.submitButton;
}

document.getElementById('language').addEventListener('change', updateLanguage);
updateLanguage();

document.getElementById('analysisForm').addEventListener('submit', async (e) => {
    e.preventDefault();
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
            headers: { 'Content-Type': 'application/json' },
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
            <div class="result-item"><div class="result-label">${t.patterns}</div><div>${data.distortions.join(', ') || t.none}</div></div>
        `;
        
    } catch (error) {
        resultDiv.innerHTML = `<div class="error"><strong>${t.error}</strong> ${error.message}</div>`;
    } finally {
        button.textContent = t.submitButton;
        button.disabled = false;
    }
});