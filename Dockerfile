FROM python:3.11

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the required files
COPY requirements.txt .
COPY *.py .
COPY *.db .

# Expose the default Streamlit port
EXPOSE 8502

# Command to run the application
CMD ["streamlit", "run", "flashcards.py"]
