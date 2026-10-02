# Etiqueta: APP_CHANGO_DOCKERFILE_02102026
# Proyecto: app chango
# Arquitectura: Python 3.10 Slim Production Container

FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias esenciales de sistema si fuera necesario
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requerimientos Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente completo del microkernel
COPY . .

# Exponer puerto de la API FastAPI
EXPOSE 8000

# Comando de ejecución por defecto del contenedor
CMD ["uvicorn", "api.main_api:app", "--host", "0.0.0.0", "--port", "8000"]
