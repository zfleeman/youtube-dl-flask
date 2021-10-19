FROM python:3-alpine
RUN pip install --upgrade youtube-dl
RUN pip install flask
RUN apk add --no-cache ffmpeg
WORKDIR /usr/app/
COPY app.py .
EXPOSE 5111
CMD ["python","/usr/app/app.py"]