# Mental Health Text Analysis Pipeline
  
[🇺🇸 English](README.md) | [🇷🇺 Русский](README_RU.md)

### MindAnalyzer: AI-Powered Emotional State Analysis

## Status: ✅ Operational | Basic functionality complete | Active development

## 📖 About The Project
A web application for emotional state text analysis.
The system detects emotional tone, cognitive patterns, and extracts key entities from user text. 

**Key Features:**

🔐 **JWT Token Authentication** - Secure user sessions

🗄️ **Encrypted Database Storage** - Fernet encryption for sensitive data

🤖 **AI-powered text analysis** using YandexGPT

🌐 **Bilingual interface** (English/Russian)

🎯 **Emotion and cognitive pattern detection**

⚠️ **Ethical disclaimer** and safety measures

📊 **Specialist dashboard** with analytics

💾 **SQLite/PostgreSQL ready** database architecture

## 🏗️ Project Structure

```bash
mental-health-text-analysis-pipeline/ 

├── instance/                       # Database directory
│   └── mental_health_analysis.db   # Database file
├── data/                           # Test datasets
│   ├── golden_standard_en.json
│   └── golden_standard_ru.json
├── prompts/                        # AI prompts directory
│   ├── system_prompt_en.md
│   ├── system_prompt_ru.md
│   ├── few_shot_examples_en.md
│   └── few_shot_examples_ru.md
├── src/                            # Source code
│   ├── __init__.py                 # Python package
│   ├── api/                        # API module
│   │   ├── __init__.py
│   │   ├── models.py               # Pydantic models
│   │   └── yandex_gpt.py           # YandexGPT client
│   │
│   ├── auth/                       # Authentication module
│   │   ├── __init__.py
│   │   ├── utils.py                # JWT utilities
│   │   └── routes.py               # Auth endpoints
│   │
│   ├── models/                     # Database models
│   │   ├── __init__.py
│   │   └── sql_models.py           # SQLAlchemy models
│   │
│   ├── dashboard/                  # Dashboard module
│   │   ├── __init__.py
│   │   └── app.py                  # Streamlit application
│   │
│   └── static/                     # Frontend assets
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
├── templates/                      # HTML templates
│   └── index.html
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── test_api.py                 # API tests
│   ├── test_models.py              # Model tests
│   └── test_prompt_assembly.py     # Prompt tests
│
├── app.py                          # Main Flask server
│
├── extensions.py                   # Extensions (db)
├── debug_jwt.py                    # JWT debug utility
├── .env                            # Environment variables
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Dependencies
├── LICENSE                         # License file
├── README.md                       # English documentation
└── README_RU.md                    # Russian documentation  
```

## 🚀 Current Progress

### ✅ Completed: 

**Security & Authentication:**

- JWT token-based authentication system

- Password hashing with Werkzeug security

- Encrypted database storage (Fernet encryption)

- Protected API endpoints with token validation

- Secure environment configuration

**Database Architecture:**

- SQLAlchemy ORM with proper initialization

- User and AnalysisResult models with relationships

- Automated table creation and migrations

- Data encryption at rest for sensitive content

**Core Functionality:**

- System prompts (RU/EN versions)

- Few-shot examples (RU/EN versions)

- Golden standard dataset (20 test cases RU/EN)

- Flask API with complete REST endpoints

- Frontend UI with real-time language switching

- YandexGPT integration with error handling

- Pydantic validation for robust data handling

**Professional Features:**

- Ethical disclaimer system with bilingual support

- Modern CSS design with responsive layout

- Specialist analytics dashboard (Streamlit)

- Role-based access control foundation

## 🔐 Security Features Implemented

- JWT Authentication - Secure token-based sessions

- Password Hashing - bcrypt-based password security

- Data Encryption - Fernet encryption for sensitive text

- Input Validation - Pydantic request validation

- Environment Variables - Secure configuration management

- CORS Protection - Configured for production security

### 🔄 In Progress:  

- Telegram bot implementation 

## 🧪 Testing

```bash
# Run prompt assembly tests
python tests/test_prompt_assembly.py

# Run authentication tests
python tests/test_api.py

# Run JWT functionality tests  
python tests/test_jwt.py
```

## 🛠️ Tech Stack

**Backend:** Python 3.12, Flask, SQLAlchemy, Pydantic

**Authentication:** JWT, Werkzeug Security, Fernet Encryption

**AI:** YandexGPT API, Custom prompt engineering

**Frontend:** JavaScript, HTML5, CSS3

**Dashboard:** Streamlit, Plotly, Pandas

**Database:** SQLite (PostgreSQL ready)

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
# JWT_SECRET=your-super-secret-jwt-key
# ENCRYPTION_KEY=your-encryption-key-here
```

## Database Setup

The application will automatically create a database in the `instance/` folder.
For custom configuration, you can specify an absolute path in .env (optional):
```bash
DATABASE_URL=sqlite:///C:/path/to/your/project/instance/mental_health_analysis.db
```


4. **Run the application:**

```bash
python app.py
```

**In the data folder you will find the test_cases.md file with ready-to-use examples for testing.**

You can use these examples to test the application functionality, or provide your own text samples.

5. **Open in browser:**

```text
http://localhost:5000
```
**Dashboard:** 

```text
streamlit run src/dashboard/app.py
```
## ⚠️ Important Notice
MindAnalyser is a self-reflection aid tool. It does not provide diagnoses, is not a medical service, and is not a substitute for professional consultation with a psychologist or psychotherapist. Use only under specialist supervision.

## 📋 Next Steps  

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