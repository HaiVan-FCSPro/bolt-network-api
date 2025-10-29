# === Dockerfile for BOLT Network API ===

# 1. Base Image: Use an official Python runtime as a parent image
# Using slim-bullseye for a smaller image size
FROM python:3.12-slim-bullseye

# 2. Set Environment Variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures Python output is sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED 1

# 3. Set Work Directory: Create and set the working directory in the container
WORKDIR /app

# 4. Install Dependencies
# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .
# Install packages specified in requirements.txt
# --no-cache-dir reduces image size
# --upgrade pip ensures we have the latest pip
RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

# 5. Copy Application Code
# Copy the rest of the application code into the working directory
COPY . .
# Note: Ensure your .env file is present here or managed via environment variables later

# 6. Expose Port: Make port 8000 available to the world outside this container
EXPOSE 8000

# 7. Run Command: Define the command to run the application using uvicorn
# Use 0.0.0.0 to make it accessible outside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
