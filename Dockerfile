# Use the official Alpine image as the base image
FROM alpine:latest

# Set the working directory in the container
WORKDIR /app

# Install Python, pip, and other dependencies
RUN apk update && \
    apk add --no-cache python3 py3-pip tesseract-ocr ghostscript && \
    python3 -m ensurepip && \
    pip3 install --no-cache --upgrade pip

# Print Ghostscript version
RUN gs --version

# Install Tesseract OCR Python bindings
RUN pip3 install --no-cache-dir pytesseract

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any other dependencies from requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Expose the port that your app will run on
EXPOSE 5002

# Define environment variable
ENV FLASK_APP=server.py

# Run Gunicorn with the app as the entry point
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5002", "server:app", "--timeout", "300"]
