# Use the official Ubuntu image as the base image
FROM ubuntu:latest

# Set the working directory in the container
WORKDIR /app

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Tesseract OCR and dependencies
RUN apt-get update && \
    apt-get install -y tesseract-ocr ghostscript && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Print Ghostscript version
RUN gs --version

# Install Tesseract OCR Python bindings
RUN pip3 install --no-cache-dir pytesseract

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any other dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Expose the port that your app will run on
EXPOSE 5002

# Define environment variable
ENV FLASK_APP=server.py

# Run Gunicorn with the app as the entry point
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5002", "server:app", "--timeout", "300"]