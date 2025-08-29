# Mental Health Text Analysis Pipeline

### MindAnalyzer: AI-Powered Emotional State Analysis

## Status: ✅ Operational | Basic functionality complete | Active development

## 📖 About The Project
A web application for emotional state text analysis.
The system detects emotional tone, cognitive patterns, and extracts key entities from user text. 

Key Features:

🤖 AI-powered text analysis using YandexGPT

🌐 Bilingual interface (English/Russian)

🎯 Emotion and cognitive pattern detection

⚠️ Ethical disclaimer and safety measures

💾 Ready for database integration

## 🏗️ Project Structure

```bash
mental-health-text-analysis-pipeline/
├── app.py                      # Flask server (main application)
├── templates/
│   └── index.html 
├── static/
│   ├── css/style.css 
│   └── js/app.js           
├── src/
│   └── api/
│       ├── models.py          # Pydantic request/response models
│       └── yandex_gpt.py      # YandexGPT API client implementation
├── prompts/                   # LLM prompts for RU/EN languages
│   ├── system_prompt_en.txt
│   ├── system_prompt_ru.txt
│   ├── few_shot_examples_en.txt
│   └── few_shot_examples_ru.txt
├── data/                      # Test datasets
│   ├── golden_standard_en.json
│   └── golden_standard_ru.json
├── tests/                     # Test suite
├── .env 
├── venv/ 
├── .gitignore
├── LICENSE
└── README.md
```

## 🚀 Current Progress

### ✅ Completed:

- System prompts (RU/EN versions)
- Few-shot examples (RU/EN versions) 
- Golden standard dataset (20 test cases RU/EN)
- Prompt assembly integration tests
- Flask API with POST /api/analyze endpoint
- Frontend UI with real-time language switching (EN/RU)
- YandexGPT integration with comprehensive error handling
- Pydantic validation for robust request/response handling
- Ethical disclaimer system with bilingual support
- Modern CSS design with gradients and responsive layout

### 🔄 In Progress:

- SQLite database integration with SQLAlchemy ORM

- Streamlit dashboard for specialist analytics

- Telegram bot implementation

- API key authentication system for specialists

## 🧪 Testing

```bash
# Run prompt assembly tests
python tests/test_prompt_assembly.py
```

## 🛠️ Tech Stack

Python 3.12.10

Flask - Web framework

Pydantic - Data validation

YandexGPT API - ML model integration

Streamlit - Analytics dashboard

JavaScript - Frontend interactivity and API communication

## 🚀 Quick Start

### Prerequisites
- **Yandex Cloud account** with access to YandexGPT API
- **API Key** and **Folder ID** from Yandex Cloud Console
- **Python 3.10+**

### Installation & Setup
1. **Clone repository:**
```bash
git clone https://github.com/AdeleVer/mental-health-text-analysis.git
cd mental-health-text-analysis
```
2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Configure environment:**

```bash
cp .env.example .env

# Edit .env file with your credentials:
# YANDEX_API_KEY=your_actual_api_key_here
# YANDEX_FOLDER_ID=your_actual_folder_id_here
```

4. **Run the application:**

```bash
python app.py
```

5. **Open in browser:**

```text
http://localhost:5000
```

## ⚠️ Important Notice
MindAnalyser is a self-reflection aid tool. It does not provide diagnoses, is not a medical service, and is not a substitute for professional consultation with a psychologist or psychotherapist. Use only under specialist supervision.

## 📋 Next Steps

- Database integration (SQLite + SQLAlchemy)

- Specialist analytics dashboard (Streamlit)

- Telegram bot for mobile access

- API authentication and user management

- Export functionality (CSV/JSON reports)

- Advanced data visualizations

- Docker containerization

- Deployment ready configuration


## 👩‍💻 Author
AdeleVer - Prompt Engineering Specialist

GitHub: AdeleVer

Project: Mental Health Text Analysis Pipeline

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.