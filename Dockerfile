# telegram_bot/Dockerfile
FROM python:3.12-slim

# Sécurité : pas de root
RUN useradd -m -u 1001 botuser

WORKDIR /app

# Copie deps en premier (layer cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code
COPY . .

# Change vers user non-root
USER botuser

# Healthcheck : vérifie que le bot répond
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('https://api.telegram.org')" || exit 1

CMD ["python", "bot.py"]
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                                                                                                                                                           
~                                                    
