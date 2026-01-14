FROM python:3.12-slim 

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y wget

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install -r requirements.txt

WORKDIR /workspace

COPY app/ app/
COPY data/ data/
# Copy juste pour les test le répertoire tes, a enlever
COPY test/ test/

EXPOSE 8080