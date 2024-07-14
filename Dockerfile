FROM python:3.11-slim-bookworm

RUN apt update 
RUN apt install -y git

RUN git clone https://github.com/UniMelb-Esports-Association/UMESA-Bot.git
RUN pip3 install discord.py python-dotenv requests

COPY data.json /UMESA-Bot/data.json
COPY env /UMESA-Bot/.env

CMD cd UMESA-Bot && python3 main.py
