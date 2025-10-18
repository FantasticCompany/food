# Base image
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# (Railway inyecta PORT automáticamente)
EXPOSE 8080
ENV PORT=8080

# <-- usar bash -lc para que se expanda $PORT
CMD ["bash","-lc","streamlit run app.py --server.port $PORT --server.address 0.0.0.0"]
