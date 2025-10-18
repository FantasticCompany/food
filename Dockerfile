FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Esta línea asegura que Streamlit use el puerto dinámico de Railway
CMD python -c "import os; port=os.environ.get('PORT', 8080); os.system(f'streamlit run app.py --server.port {port} --server.address 0.0.0.0')"
