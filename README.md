# IntelliPlan - Smart Study Planning Assistant

A privacy-focused web application to help students manage their studies effectively with intelligent planning and AI-powered assistance.

## Features

- Google Authentication
- Personal Study Dashboard
- CRUD Study Plan Management
- AI-powered Study Assistant (IntelliChat)
- Privacy-First Design (No trackers or analytics)

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with the following variables:
   ```
   SECRET_KEY=your_django_secret_key
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   OPENAI_API_KEY=your_openai_api_key
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
intelliplan/
├── manage.py
├── intelliplan/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── authentication/
│   ├── dashboard/
│   ├── study_plan/
│   └── intellichat/
├── static/
│   ├── css/
│   └── js/
└── templates/
    ├── base.html
    ├── dashboard/
    ├── study_plan/
    └── intellichat/
``` 