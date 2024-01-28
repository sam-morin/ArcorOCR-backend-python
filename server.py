# backend/app.py

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

create_upload_folder()

@app.route('/upload', methods=['POST'])
def upload_file():
    create_upload_folder()

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Perform OCRmyPDF conversion
            output_filename = filename.split('.')[0] + '_ArcorOCR.pdf'
            output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

            subprocess.run(['ocrmypdf', '--optimize', '0', '--redo-ocr', filepath, output_filepath])
            # subprocess.run(['ocrmypdf', '--optimize', '0', '--force-ocr', filepath, output_filepath])

            return send_file(output_filepath, as_attachment=True, download_name=output_filename)
        finally:
            # Delete the original and converted files after sending
            os.remove(filepath)
            os.remove(output_filepath)
    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/upload/remove', methods=['POST'])
def upload_file_remove_ocr():
    create_upload_folder()

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Perform OCRmyPDF conversion
            output_filename = filename.split('.')[0] + '_ArcorOCR.pdf'
            output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

            subprocess.run(['ocrmypdf', '--tesseract-timeout', '0', '--force-ocr', filepath, output_filepath])
            # subprocess.run(['ocrmypdf', '--optimize', '0', '--force-ocr', filepath, output_filepath])

            return send_file(output_filepath, as_attachment=True, download_name=output_filename)
        finally:
            # Delete the original and converted files after sending
            os.remove(filepath)
            os.remove(output_filepath)
    return jsonify({'error': 'Invalid file format'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5002')

