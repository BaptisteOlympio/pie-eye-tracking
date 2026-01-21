FROM bolympio/openface:latest

RUN apt-get update && apt-get install -y build-essential

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

<<<<<<< HEAD
RUN apt-get install -y iputils-ping

WORKDIR /workspace
=======
WORKDIR /app

COPY ./app .
>>>>>>> main

EXPOSE 8081


