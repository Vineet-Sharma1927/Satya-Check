# Use a lightweight Python base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV (GL libraries)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (to cache dependencies)
COPY requirements.txt .

# Install Python dependencies (Torch is heavy, so we limit CPU version to save space)
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Copy the rest of the app
COPY . .

# Expose the port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]