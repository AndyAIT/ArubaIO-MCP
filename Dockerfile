# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir fastmcp httpx python-dotenv

# Create a non-root user
RUN useradd -m appuser
USER appuser

# Expose the port the app runs on
EXPOSE 8830

# Define environment variable file
ENV_FILE=.env

# Run the app when the container launches
CMD ["python", "server.py"]
