FROM python:3.8-slim-buster

WORKDIR /bet

COPY requirements.txt .
COPY .env .
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python", "bet-bot.py"]
