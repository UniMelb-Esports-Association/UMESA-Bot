FROM python:3.11-slim-bookworm

RUN apt update 
RUN apt install -y git

RUN git clone https://github.com/UniMelb-Esports-Association/UMESA-Bot.git
RUN pip3 install discord.py python-dotenv requests

COPY cog/ticket/ticket_data.json UMESA-Bot/cog/ticket/
COPY cog/ticket/clip_questions.json UMESA-Bot/cog/ticket/
COPY data.json UMESA-Bot/
COPY .env UMESA-Bot/
CMD cd UMESA-Bot && python3 main.py