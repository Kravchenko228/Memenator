# Use the official Python image
FROM python:3.12-slim

# Set environment variables to prevent buffering and ensure Python runs in production mode
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to install dependencies
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the project files to the working directory inside the container
COPY . /app/

# Expose the port on which Django will run (8000)
EXPOSE 8000

# Command to run Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
