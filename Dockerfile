# Base image
FROM python:3.11-slim

# Working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose the port Railway assigns
ENV PORT=8080
EXPOSE 8080

# Command to run Streamlit (note the use of $PORT properly expanded by shell)
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
