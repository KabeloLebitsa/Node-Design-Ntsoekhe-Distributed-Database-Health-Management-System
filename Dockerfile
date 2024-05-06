FROM python:3.9-alpine

# Set the working directory
WORKDIR /app

# Copy only the requirements.txt first to leverage Docker cache
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the port on which the API will run
#EXPOSE 8081 8082 8083 8084 8085

# Command to run when the container starts
CMD ["python", "app/app.py", "--host=0.0.0.0"]