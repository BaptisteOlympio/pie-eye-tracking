FROM openface:latest

# # # ## ================== Python layer ====================================

RUN apt-get update && apt-get install -y build-essential

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

RUN mkdir -p /workspace

WORKDIR /app

COPY ./app .

EXPOSE 8081


