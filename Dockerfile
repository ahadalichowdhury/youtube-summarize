# Use an official Python image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the application code to the container
COPY . .

# Expose the port on which the app will run
EXPOSE 5000


# Run the Flask application
CMD ["python", "index.py"]
