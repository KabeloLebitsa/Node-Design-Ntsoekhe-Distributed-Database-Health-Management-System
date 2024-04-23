FROM python:3.9-alpine

# Set the working directory
WORKDIR /app

# Copy requirements.txt file
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your SQLite database file into the container
COPY . .
# Expose the port on which the API will run
EXPOSE 80

# Command to run when the container starts
CMD ["python", "app/app.py", "--host=0.0.0.0"]