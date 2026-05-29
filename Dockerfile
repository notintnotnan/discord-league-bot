FROM python:3.14

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /bot

RUN useradd --create-home --shell /bin/bash discordbot 

COPY requirements.txt .

RUN pip install --no-cache -r requirements.txt

COPY . .

RUN chown -R discordbot /bot

USER discordbot

CMD ["python", "bot.py"]