FROM openface:latest

# # # ## ================== Python layer ====================================

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

RUN mkdir -p /workspace

WORKDIR /app

COPY ./app .

EXPOSE 8081


