# Mental Health Text Analysis Pipeline

**Status:** 🚧 In Development | Active development phase

## 📖 About The Project

A pipeline for analyzing mental state through text messages. The system detects emotional tone, cognitive distortions, and extracts key entities from user text using YandexGPT API.

## 🏗️ Project Structure

```bash
mental-health-text-analysis-pipeline/
├── 📁 src/ # Source code
│ ├── 📁 api/ # Flask backend API
│ └── 📁 dashboard/ # Streamlit dashboard
├── 📁 data/ # Datasets and golden standards
│ ├── golden_standard_ru.json
│ └── golden_standard_en.json
├── 📁 prompts/ # LLM prompts
│ ├── system_prompt_ru.txt
│ ├── system_prompt_en.txt
│ ├── few_shot_examples_ru.txt
│ └── few_shot_examples_en.txt
├── 📁 tests/ # Test files
│ └── test_prompt_assembly.py
├── 📁 venv/ # Virtual environment
├── .gitignore
├── LICENSE
└── README.md
```

## 🚀 Current Progress

### ✅ Completed:
- Project structure setup
- System prompts (RU/EN versions)
- Few-shot examples (RU/EN versions) 
- Golden standard dataset (20 test cases RU/EN)
- Prompt assembly integration tests

### 🔄 In Progress:
- YandexGPT API integration
- Flask API development
- Pydantic validation models

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

Docker - Containerization

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

4. **Run tests:**

To run the test suite, use the following command:

```bash
python tests/test_prompt_assembly.py
```
Requirements: Make sure pytest is installed in your virtual environment:

```bash
pip install pytest
```
5. **API Configuration**
- To get your Yandex Cloud credentials:

- Create service account in Yandex Cloud Console

- Assign ai.languageModels.user role

- Create API Key for the service account

- Copy Folder ID from your catalog page

## 📋 Next Steps
- Implement YandexGPT API client

- Create Flask API endpoints

- Add data validation with Pydantic

- Develop Streamlit dashboard

- Add comprehensive test suite


## 👩‍💻 Автор
AdeleVer - Prompt Engineering Specialist

GitHub: AdeleVer

Project: Mental Health Text Analysis Pipeline

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.