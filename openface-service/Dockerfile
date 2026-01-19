FROM bolympio/openface:latest

RUN apt-get update && apt-get install -y build-essential

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

WORKDIR /app

COPY ./app .

EXPOSE 8081


