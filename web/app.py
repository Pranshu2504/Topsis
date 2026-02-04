from flask import Flask, request, render_template
import os
import re
import pandas as pd
import smtplib
from email.message import EmailMessage
from topsis_core import run_topsis

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/topsis", methods=["POST"])
def topsis_service():
    if "file" not in request.files:
        return "File not provided"

    file = request.files["file"]
    weights = request.form.get("weights")
    impacts = request.form.get("impacts")
    email = request.form.get("email")

    if not re.match(EMAIL_REGEX, email):
        return "Invalid email format"

    try:
        weights = [float(w) for w in weights.split(",")]
        impacts = impacts.split(",")
    except:
        return "Weights must be numeric and comma separated"

    if len(weights) != len(impacts):
        return "Number of weights must be equal to number of impacts"

    if not all(i in ["+", "-"] for i in impacts):
        return "Impacts must be either + or -"

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        if file.filename.lower().endswith(".csv"):
            df = pd.read_csv(filepath)
        elif file.filename.lower().endswith(".xlsx"):
            df = pd.read_excel(filepath)
        else:
            return "Unsupported file format"
    except Exception as e:
        return f"Error reading file: {e}"

    try:
        result_df = run_topsis(df, weights, impacts)
    except ValueError as e:
        return str(e)

    output_path = filepath.rsplit(".", 1)[0] + "_result.csv"
    result_df.to_csv(output_path, index=False)

    try:
        send_email(email, output_path)
    except Exception as e:
        return f"Error sending email: {e}"

    return "Result sent to email successfully"

def send_email(receiver, attachment_path):
    msg = EmailMessage()
    msg["Subject"] = "TOPSIS Result"
    msg["From"] = "your_email@gmail.com"
    msg["To"] = receiver
    msg.set_content("Please find the attached TOPSIS result file.")

    with open(attachment_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="octet-stream",
            filename="result.csv"
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("your_email@gmail.com", "APP_PASSWORD")
        server.send_message(msg)

if __name__ == "__main__":
    app.run(debug=True)
