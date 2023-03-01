# Use the official Python image as the base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the working directory
COPY . /app

# Set sqlite airbite-server.db to writable
RUN ls -la
RUN chmod 777 airbite-server.db

# Set port 3721 to be exposed
EXPOSE 3721/tcp

# Define the entry point for the container
CMD ["python", "server.py"]