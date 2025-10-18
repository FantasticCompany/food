FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ajustes recomendados para Streamlit en server
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_HEADLESS=true

# Puerto (fallback) y exposición
ENV PORT=8080
EXPOSE 8080

# 🔒 Fuerza puerto correcto y evita que una var externa rompa el arranque
# (si existiera STREAMLIT_SERVER_PORT con "$PORT", la sobreescribimos con un número)
CMD ["bash","-lc","export STREAMLIT_SERVER_PORT=${PORT:-8080}; streamlit run app.py --server.port $STREAMLIT_SERVER_PORT --server.address 0.0.0.0"]
