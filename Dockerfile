# Usar imagen base de Python 3.13 slim
FROM python:3.13-slim

# Definir arquitectura como argumento de build
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Instalar dependencias del sistema y Microsoft ODBC Driver
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    gnupg2 \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.asc.gpg \
    && if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
         echo "deb [arch=arm64] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list; \
       else \
         echo "deb [arch=amd64] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list; \
       fi \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Evitar advertencia de pip corriendo como root
ENV PIP_ROOT_USER_ACTION=ignore

# Copiar archivos de dependencias de Python
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación Python
COPY ./app /app/app

# Copiar frontend ya construido (build se hace en CI/CD)
COPY ./ezekl-budget-ionic/www /app/ezekl-budget-ionic/www

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Exponer puerto (configurable via ENV)
EXPOSE ${PORT:-8001}

# Variables de entorno por defecto
ENV PORT=8001

# Healthcheck para Docker
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8001}/api/health || exit 1

# Comando para ejecutar la aplicación
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}