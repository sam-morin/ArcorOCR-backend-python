from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

limiter = Limiter(get_remote_address, app=app, default_limits=["250 per day", "70 per hour", "4 per minute"], strategy='fixed-window-elastic-expiry')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        
create_upload_folder()


def perform_ocr(file, removal=False):
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

            if removal:
                subprocess.run(['ocrmypdf', '--tesseract-timeout', '0', '--force-ocr', filepath, output_filepath])
            else:
                subprocess.run(['ocrmypdf', '--optimize', '0', '--redo-ocr', filepath, output_filepath])

            return send_file(output_filepath, as_attachment=True, download_name=output_filename)
        finally:
            # Delete the original and converted files after sending
            os.remove(filepath)
            os.remove(output_filepath)


@app.route('/upload', methods=['POST'])
@limiter.limit("4 per minute")
def upload_file():
    create_upload_folder()

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    return perform_ocr(file, removal=False)


@app.route('/upload/remove', methods=['POST'])
@limiter.limit("4 per minute")
def upload_file_remove_ocr():
    create_upload_folder()

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    return perform_ocr(file, removal=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5002')
