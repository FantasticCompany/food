FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Sugeridos por Streamlit para server
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Railway asigna PORT; ponemos fallback para local
ENV PORT=8080
EXPOSE 8080

# ⚠️ Clave: ejecuta con bash y borra la variable conflictiva
CMD bash -lc "unset STREAMLIT_SERVER_PORT; streamlit run app.py --server.port=${PORT:-8080} --server.address=0.0.0.0"
