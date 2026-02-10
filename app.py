from flask import Flask, render_template, request, send_file
from groq import Groq
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import io

load_dotenv(dotenv_path=".env", override=True)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)

def generate_resume(data):
    prompt = f"""
Create a professional, ATS-friendly resume for the role of {data['role']}.

Candidate Name: {data['name']}
Education: {data['education']}
Skills: {data['skills']}
Projects: {data['projects']}

Tailor the resume specifically for a {data['role']} position.
"""

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


@app.route("/", methods=["GET", "POST"])
def index():
    resume = ""

    if request.method == "POST":
        data = {
            "name": request.form["name"],
            "education": request.form["education"],
            "skills": request.form["skills"],
            "projects": request.form["projects"],
            "role": request.form["role"]
        }

        resume = generate_resume(data)

    return render_template("index.html", resume=resume)


@app.route("/download", methods=["POST"])
def download_pdf():
    resume_text = request.form["resume"]

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    text = pdf.beginText(40, 800)

    for line in resume_text.split("\n"):
        text.textLine(line)

    pdf.drawText(text)
    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Resume.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

