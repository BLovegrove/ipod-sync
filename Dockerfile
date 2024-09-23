FROM python:3.12

WORKDIR /app

COPY . .

RUN apt-get update \
    && apt-get install -qq -y python3-pip ffmpeg --no-install-recommends\
    && apt-get clean\
    && pip install coloredlogs

CMD ["python","-m","convert"]