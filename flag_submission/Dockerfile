# Use a lightweight Python image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the flag submission API code into the container
COPY flag_submission.py /app/flag_submission.py
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the API port
EXPOSE 8080

# Run the Flask API
CMD ["python", "flag_submission.py"]
