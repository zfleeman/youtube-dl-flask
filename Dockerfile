FROM python:3.11-alpine
WORKDIR /usr/app/
COPY . .
RUN apk add --no-cache g++ ffmpeg
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
WORKDIR /usr/app/
EXPOSE 5111
CMD ["python","/usr/app/app.py"]