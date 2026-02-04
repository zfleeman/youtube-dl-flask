FROM python:3-alpine
WORKDIR /usr/app/
COPY . .
RUN apk add --no-cache g++ ffmpeg
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
WORKDIR /usr/app/
ENV VIDEO_FILTER=bv[ext=mp4][vcodec^=avc]
ENV AUDIO_FILTER=ba[ext=m4a][acodec^=mp4a]
EXPOSE 5111
CMD ["python","/usr/app/app.py"]
