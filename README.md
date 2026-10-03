# CloudDeploy Dashboard

This is a tiny Flask application designed as a simple Azure App Service demo. It is intentionally small and focused so the Azure platform, environment variables, logs, and deployment flow stay easy to explain in a YouTube video.

## Project structure

```text
azure-appservice-demo/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── .gitignore
└── README.md
```

## Python requirement

This app is designed for Python 3.12.

## Install dependencies

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run locally

### Flask development server

The app is intentionally simple and starts with a normal default configuration.

```bash
export APP_ENVIRONMENT=Development
export APP_VERSION=1.0
export APP_MESSAGE="Application is running successfully."
python app.py
```

On Windows PowerShell:

```powershell
$env:APP_ENVIRONMENT = "Development"
$env:APP_VERSION = "1.0"
$env:APP_MESSAGE = "Application is running successfully."
python app.py
```

Then open:

```text
http://localhost:8000
```

## Run with Gunicorn

```bash
export APP_ENVIRONMENT=Development
export APP_VERSION=1.0
export APP_MESSAGE="Application is running successfully."
gunicorn --bind 0.0.0.0:8000 app:app
```

On Windows PowerShell:

```powershell
$env:APP_ENVIRONMENT = "Development"
$env:APP_VERSION = "1.0"
$env:APP_MESSAGE = "Application is running successfully."
gunicorn --bind 0.0.0.0:8000 app:app
```

## Environment variables

The app reads configuration from environment variables:

```text
APP_ENVIRONMENT=Development
APP_VERSION=1.0
APP_MESSAGE=Application is running successfully.
SQL_CONNECTION_STRING=Driver={ODBC Driver 18 for SQL Server};Server=tcp:<server-name>.database.windows.net,1433;Database=dhruvfeedbackdb;Uid=<username>;Pwd=<password>;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;
```

If a variable is missing, the app uses a safe default value for the app-level settings. The SQL connection string must be configured for the feedback feature to work.

## Azure App Service deployment

This app is made to be deployed to Azure App Service on Linux. It does not require a database, credentials, or Azure SDK. It simply exposes a Flask app and relies on App Service environment settings for configuration.

Typical flow for the demo video:

1. Create an Azure App Service
2. Create or attach an App Service Plan
3. Deploy the app from GitHub or ZIP deployment
4. Set configuration in App Service → Configuration → Application settings
5. Restart the app to see the updated values
6. Review logs in App Service log stream and monitoring tools

## Recommended Azure startup command

Use this for Azure App Service:

```bash
gunicorn --bind=0.0.0.0 --timeout 600 app:app
```

Why this command works:

- `--bind=0.0.0.0` makes the app listen on all interfaces, which is required in Azure containers and App Service hosts.
- Azure provides the port through the runtime environment, so the app should not hard-code `localhost`.
- `--timeout 600` gives the app enough time for slower startup or deployment operations.
- `app:app` ensures Gunicorn loads the Flask application instance named `app` from `app.py`.

## Azure App Service environment variables

Use simple app settings in Azure App Service:

```text
APP_ENVIRONMENT=Azure
APP_VERSION=1.0
APP_MESSAGE=Application is running successfully.
```

These values can be changed without modifying the code, which makes the app easy to explain in a cloud demo.

## Health endpoint

The `/health` route is a JSON API endpoint, not a page. It returns:

```json
{"status": "healthy"}
```
