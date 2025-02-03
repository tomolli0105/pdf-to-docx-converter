from flask import Flask, request, send_from_directory, jsonify
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "No file selected"}), 400

    filename = secure_filename(file.filename)
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    docx_path = os.path.join(OUTPUT_FOLDER, filename.replace(".pdf", ".docx"))

    file.save(pdf_path)

    try:
        subprocess.run(["python", "pipeline.py", pdf_path, docx_path], check=True)
        return jsonify({"status": "success", "url": f"/outputs/{os.path.basename(docx_path)}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/outputs/<filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
