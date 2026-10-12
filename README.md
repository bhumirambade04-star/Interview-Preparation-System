# Interview Preparation System

A student-friendly final-year BSc Computer Science project built with **Python Flask, HTML, CSS, and SQLite**.

## Features
- User registration and login (passwords are hashed)
- Dashboard with quiz attempts and average score
- Technical MCQ practice for Python, Java, DBMS, and OOP
- HR interview questions with sample guidance
- Resume checklist
- Interview preparation tips
- Quiz results and progress history
- SQLite database is created automatically on first run

## Requirements
- Python 3.10 or newer
- Visual Studio Code (recommended)

## Run on Windows
1. Extract the ZIP to a folder.
2. Open that folder in VS Code (`File > Open Folder`).
3. Open Terminal (`Terminal > New Terminal`).
4. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   ```
5. Activate it:
   ```bash
   .venv\Scripts\activate
   ```
   If PowerShell blocks activation, use Command Prompt terminal or run `python -m pip install -r requirements.txt` directly.
6. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
7. Start the application:
   ```bash
   python app.py
   ```
8. Open **http://127.0.0.1:5000** in your browser.

The database file `interview_prep.db` is generated automatically in the project folder after the first run. Keep it private because it contains account records.

## Project structure
```
Interview_Preparation_System/
├── app.py
├── requirements.txt
├── README.md
├── interview_prep.db        # generated when the app runs
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── practice.html
│   ├── quiz_result.html
│   ├── hr_questions.html
│   ├── resume.html
│   └── tips.html
└── static/
    └── style.css
```

## Notes
- This is a local college-project starter, not a production deployment. Before public hosting, set a strong `SECRET_KEY`, disable debug mode, use HTTPS, and configure a production database.
- GitHub Pages hosts static files only; it cannot run this Flask backend directly.
