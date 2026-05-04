import os
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
# Since server.py is in backend/, we need to tell Flask where the templates and static folders are.
# By default, Flask looks for templates and static in the same directory as the script.
# We'll set them to the root directory relative to this script.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "sync-pillar-secret-key-change-in-production")

# Email configuration
MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_RECEIVER = os.environ.get("MAIL_RECEIVER")


def send_email(name, user_email, project_type, message_body):
    """Sends an email with the contact form details."""
    if not all([MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD, MAIL_RECEIVER]):
        print("Email configuration is incomplete. Skipping email send.")
        return "Email configuration is incomplete in .env file."

    msg = EmailMessage()
    msg['Subject'] = f"New Quote Request from {name} - {project_type}"
    msg['From'] = MAIL_USERNAME
    msg['To'] = MAIL_RECEIVER
    
    # Alternatively, you could use user_email for Reply-To
    msg.add_header('reply-to', user_email)

    content = f"""
New quote request received.

Name: {name}
Email: {user_email}
Project Type: {project_type}

Message/Scope:
{message_body}
"""
    msg.set_content(content)

    try:
        # Use TLS
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return str(e)


# ─── Page Routes ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Landing page."""
    return render_template("index.html", active_page="home")


@app.route("/services")
def services():
    """Services page."""
    return render_template("services.html", active_page="services")


@app.route("/contact")
def contact():
    """Contact / Get a Quote page."""
    return render_template("contact.html", active_page="contact")


# ─── API Routes ─────────────────────────────────────────────────────────────────

@app.route("/api/contact", methods=["POST"])
def submit_contact():
    """Handle contact form submission."""
    # Support both form-encoded and JSON
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    full_name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    project_type = data.get("project_type", "SaaS").strip()
    message = data.get("message", "").strip()

    # Validation
    errors = []
    if not full_name:
        errors.append("Full name is required.")
    if not email or "@" not in email:
        errors.append("A valid email is required.")
    if not message:
        errors.append("Project scope & objectives are required.")

    if errors:
        if request.is_json:
            return jsonify({"success": False, "errors": errors}), 400
        for error in errors:
            flash(error, "error")
        return redirect(url_for("contact"))

    # Send the email
    email_sent = send_email(full_name, email, project_type, message)
    
    if request.is_json:
        if email_sent is True:
            return jsonify({"success": True, "message": "Quote request received!"})
        else:
            return jsonify({"success": False, "errors": [f"Failed to send email: {email_sent}"]}), 500

    if email_sent is True:
        flash("Your quote request has been submitted successfully! We'll respond within 24 hours.", "success")
    else:
        flash(f"There was an issue sending your request: {email_sent}", "error")
        
    return redirect(url_for("contact"))


# ─── Run ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
