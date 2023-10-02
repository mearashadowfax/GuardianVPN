FROM python:3.11-slim

LABEL description="A Telegram bot that delivers VPN configuration files straight to your device at the touch of a button"

COPY bot.py .
COPY en_strings.json .
COPY ru_strings.json .
COPY fr_strings.json .
COPY es_strings.json .
COPY de_strings.json .
COPY requirements.txt .

#Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "bot.py" ]
