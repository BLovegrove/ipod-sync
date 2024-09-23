FROM python:3.12

WORKDIR /app

COPY . .

RUN apt-get update \
    && apt-get install -qq -y ffmpeg --no-install-recommends\
    && apt-get clean\
    && apt-get install python3-pip && pip install coloredlogs

CMD ["python","-m","convert"]