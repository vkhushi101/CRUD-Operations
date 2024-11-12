# Uses an official Python runtime as a parent image
FROM python:3.13-slim

# Sets the working directory in the container
WORKDIR /app

# Copies the current dir contents into the container at /app
COPY . /app

# # Installs packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Exposes port 8080 to the outside world
EXPOSE 8080

# Define environment variables for Flask
ENV FLASK_APP=src.app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

# Copies the setup.sh script into the container
COPY ./setup.sh /app/setup.sh

# Makes sure the script is executable
RUN chmod +x /app/setup.sh

# Set the CMD to run the setup.sh script - sets up the Database, runs all Database migrations, and spins up the Flask application when the container launches
CMD ["/app/setup.sh"]