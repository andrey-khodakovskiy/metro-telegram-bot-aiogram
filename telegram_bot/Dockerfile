FROM python:3.8.6
WORKDIR /telegram-bot
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD python metro_bot.py