# AI Resume Analyzer (corrected starter copy)

## 1. Create and activate a Python environment (Windows PowerShell)
From this project folder (`AI_resume_analyzer_corrected`):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, you can use Command Prompt and run `.venv\Scripts\activate.bat`.

## 2. Configure environment settings
Copy `backend\.env.example` to `backend\.env`, then edit `backend\.env`. Replace the secret-key placeholder and set your MySQL login password. Do not share or commit `backend\.env`.

Generate a Flask secret key by running:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Paste the generated value after `SECRET_KEY=`. Set `DB_PASSWORD` to the password you use for your MySQL `root` login. You can leave `GEMINI_API_KEY` and `GEMINI_MODEL` blank at first; the app then uses basic fallback suggestions. To enable Gemini, fill both with your own API key and a model identifier currently supported by your API account.

## 3. Create database tables
Open MySQL Command Line Client and run the schema file using its full path, for example:

```sql
SOURCE C:/path/to/AI_resume_analyzer_corrected/backend/schema.sql;
```

Replace the example path with the actual path on your computer. Confirm the tables with:

```sql
USE resume_analyzer;
SHOW TABLES;
```

You should see `users` and `analyses`.

## 4. Run the application
From the project root, after configuration and database creation:

```powershell
python backend/app.py
```

Open `http://127.0.0.1:5000`. Keep the terminal open while testing.

## Notes
- This starter accepts text-readable PDFs; scanned-image PDFs need OCR support, which is not included.
- The match score is a simple weighted skill coverage estimate, not an actual proprietary ATS score.
- `debug=True` is intended only for local development. Turn debug mode off and add production security controls before deployment.

## Environment setup

1. Install dependencies with `pip install -r requirements.txt`.
2. Copy `backend/.env.example` to `backend/.env`.
3. Fill in your own local database credentials and API keys in `backend/.env`. Do not commit that file.
4. Start the backend using `python backend/app.py` from the project root, or follow the project-specific run instructions above.

The `.env.example` file contains blank values intentionally. Never put real API keys or passwords in example files or commit history.
