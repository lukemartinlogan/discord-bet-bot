FROM python:3.8-slim-buster

WORKDIR /gamble

COPY requirements.txt .
COPY .env .
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
