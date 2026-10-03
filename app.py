import logging
import os
import sys

from flask import Flask, jsonify, redirect, render_template, render_template_string, request, url_for

from flask import __version__ as flask_version

from database import fetch_feedback, save_feedback


app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def get_setting(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


@app.route("/")
def home():
    logger.info("Homepage requested")

    config = {
        "environment": get_setting("APP_ENVIRONMENT", "Development"),
        "version": get_setting("APP_VERSION", "1.1"),
        "message": get_setting(
            "APP_MESSAGE", "Application V1.1 is running successfully."
        ),
    }

    try:
        feedback_items = fetch_feedback()
        feedback_error = None
    except ValueError as exc:
        logger.warning("Feedback data unavailable: %s", exc)
        feedback_items = []
        feedback_error = "Database configuration is missing. Set SQL_SERVER, SQL_USER, SQL_PASSWORD, and SQL_DATABASE to enable Cloud Feedback."
    except Exception as exc:
        logger.exception("Unable to fetch feedback data")
        feedback_items = []
        feedback_error = "We couldn't load feedback right now. Please try again later."

    return render_template(
        "index.html",
        app_name="CloudDeploy Dashboard",
        subtitle="From Code to Cloud",
        environment=config["environment"],
        version=config["version"],
        message=config["message"],
        platform="Python + Flask",
        hosting="Azure App Service",
        feedback_items=feedback_items,
        feedback_error=feedback_error,
        validation_error=None,
        form_name="",
        form_message="",
    )


@app.route("/feedback", methods=["POST"])
def feedback():
    name = (request.form.get("name") or "").strip()
    message = (request.form.get("message") or "").strip()

    try:
        feedback_items = fetch_feedback()
    except ValueError as exc:
        logger.warning("Feedback data unavailable: %s", exc)
        feedback_items = []
    except Exception:
        logger.exception("Unable to fetch feedback data")
        feedback_items = []

    validation_error = None
    if not name:
        validation_error = "Name is required."
    elif len(name) > 100:
        validation_error = "Name must be 100 characters or less."

    if not message:
        validation_error = "Message is required."
    elif len(message) > 500:
        validation_error = "Message must be 500 characters or less."

    if validation_error:
        return render_template(
            "index.html",
            app_name="CloudDeploy Dashboard",
            subtitle="From Code to Cloud",
            environment=get_setting("APP_ENVIRONMENT", "Development"),
            version=get_setting("APP_VERSION", "1.0"),
            message=get_setting("APP_MESSAGE", "Application is running successfully."),
            platform="Python + Flask",
            hosting="Azure App Service",
            feedback_items=feedback_items,
            feedback_error=None,
            validation_error=validation_error,
            form_name=name,
            form_message=message,
        )

    try:
        save_feedback(name, message)
        return redirect(url_for("home"))
    except ValueError as exc:
        logger.warning("Feedback submission validation error: %s", exc)
        return render_template(
            "index.html",
            app_name="CloudDeploy Dashboard",
            subtitle="From Code to Cloud",
            environment=get_setting("APP_ENVIRONMENT", "Development"),
            version=get_setting("APP_VERSION", "1.0"),
            message=get_setting("APP_MESSAGE", "Application is running successfully."),
            platform="Python + Flask",
            hosting="Azure App Service",
            feedback_items=feedback_items,
            feedback_error=str(exc),
            validation_error=None,
            form_name=name,
            form_message=message,
        )
    except Exception:
        logger.exception("Unable to save feedback data")
        return render_template(
            "index.html",
            app_name="CloudDeploy Dashboard",
            subtitle="From Code to Cloud",
            environment=get_setting("APP_ENVIRONMENT", "Development"),
            version=get_setting("APP_VERSION", "1.0"),
            message=get_setting("APP_MESSAGE", "Application is running successfully."),
            platform="Python + Flask",
            hosting="Azure App Service",
            feedback_items=feedback_items,
            feedback_error="We couldn't submit your feedback right now. Please try again later.",
            validation_error=None,
            form_name=name,
            form_message=message,
        )


@app.route("/health")
def health():
    logger.info("Health check requested")
    return jsonify({"status": "healthy"})


@app.route("/about")
def about():
    logger.info("About page requested")

    environment = get_setting("APP_ENVIRONMENT", "Development")
    version = get_setting("APP_VERSION", "1.0")

    return render_template_string(
        """
        <!doctype html>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>About | CloudDeploy Dashboard</title>
                <style>
                    body {
                        margin: 0;
                        font-family: Arial, sans-serif;
                        background: linear-gradient(135deg, #0f172a 0%, #111827 100%);
                        color: #e5e7eb;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        min-height: 100vh;
                    }
                    .card {
                        width: min(720px, 90vw);
                        background: rgba(15, 23, 42, 0.9);
                        border: 1px solid rgba(148, 163, 184, 0.25);
                        border-radius: 18px;
                        padding: 32px;
                        box-shadow: 0 18px 48px rgba(15, 23, 42, 0.55);
                    }
                    h1 {
                        margin-top: 0;
                        font-size: 2rem;
                    }
                    .meta {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 16px;
                        margin-top: 25px;
                    }
                    .item {
                        background: rgba(15, 118, 110, 0.12);
                        border: 1px solid rgba(94, 234, 212, 0.2);
                        border-radius: 12px;
                        padding: 16px;
                    }
                    .label {
                        color: #94a3b8;
                        font-size: 0.8rem;
                        text-transform: uppercase;
                        letter-spacing: 0.08em;
                        margin-bottom: 6px;
                    }
                    .value {
                        font-size: 1.1rem;
                        font-weight: 700;
                    }
                    a {
                        display: inline-block;
                        margin-top: 24px;
                        color: #67e8f9;
                        text-decoration: none;
                        font-weight: 600;
                    }
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>CloudDeploy Dashboard</h1>
                    <div class="meta">
                        <div class="item">
                            <div class="label">Application Name</div>
                            <div class="value">CloudDeploy Dashboard</div>
                        </div>
                        <div class="item">
                            <div class="label">Python Version</div>
                            <div class="value">{{ python_version }}</div>
                        </div>
                        <div class="item">
                            <div class="label">Flask Version</div>
                            <div class="value">{{ flask_version }}</div>
                        </div>
                        <div class="item">
                            <div class="label">Environment</div>
                            <div class="value">{{ environment }}</div>
                        </div>
                        <div class="item">
                            <div class="label">Application Version</div>
                            <div class="value">{{ version }}</div>
                        </div>
                        <div class="item">
                            <div class="label">Hosting Platform</div>
                            <div class="value">Azure App Service</div>
                        </div>
                    </div>
                    <a href="/">← Back to dashboard</a>
                </div>
            </body>
        </html>
        """,
        python_version=sys.version.split()[0],
        flask_version=flask_version,
        environment=environment,
        version=version,
    )


@app.errorhandler(404)
def page_not_found(error):
    return render_template_string(
        """
        <!doctype html>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>404 | CloudDeploy Dashboard</title>
                <style>
                    body {
                        margin: 0;
                        font-family: Arial, sans-serif;
                        background: #0f172a;
                        color: #e2e8f0;
                        display: grid;
                        place-items: center;
                        min-height: 100vh;
                    }
                    .box {
                        text-align: center;
                        background: #111827;
                        border: 1px solid #334155;
                        border-radius: 16px;
                        padding: 36px 48px;
                    }
                    h1 { font-size: 3rem; margin: 0 0 12px; }
                    p { color: #94a3b8; }
                    a { color: #67e8f9; text-decoration: none; }
                </style>
            </head>
            <body>
                <div class="box">
                    <h1>404</h1>
                    <p>The page you requested does not exist.</p>
                    <a href="/">Return to CloudDeploy Dashboard</a>
                </div>
            </body>
        </html>
        """
    ), 404


logger.info("Application started")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
