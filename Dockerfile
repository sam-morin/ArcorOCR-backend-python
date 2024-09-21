# Use the official Alpine image as the base image
FROM alpine:latest

# Set the working directory in the container
WORKDIR /app

# Install Python, pip, and other dependencies
RUN apk update && \
    apk add --no-cache python3 py3-pip tesseract-ocr ghostscript && \
    python3 -m venv /app/venv

# Activate the virtual environment and install dependencies
RUN source /app/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install --no-cache-dir pytesseract

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any other dependencies from requirements.txt inside the virtual environment
RUN source /app/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Expose the port that your app will run on
EXPOSE 5002

# Define environment variable
ENV FLASK_APP=server.py

# Activate the virtual environment when running the application
CMD ["/app/venv/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:5002", "server:app", "--timeout", "300"]
