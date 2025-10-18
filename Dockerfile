FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
ENV PORT=8080

# ✅ Comando corregido
CMD python -c "import os; os.system(f'streamlit run app.py --server.port={os.environ.get(\"PORT\", 8080)} --server.address=0.0.0.0')"
