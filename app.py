import youtube_dl
from datetime import datetime
from flask import Flask, request, redirect
from celery import Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


app = Flask(__name__)

app.config.update(
    CELERY_BROKER_URL='redis://192.168.1.7:6379',
    CELERY_RESULT_BACKEND='redis://192.168.1.7:6379'
)
celery = make_celery(app)

@app.route("/")
def index():
    return '''
            <!doctype html>
            <html lang="en">
                <head>
                    <!-- Required meta tags -->
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

                    <!-- Bootstrap CSS -->
                    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">

                    <title>YTDL</title>
                </head>
                <body>
                    <div class="container-fluid">
                        <h1>ZF's YT DL-er</h1>
                        <form action="/download", method="post">
                            <label>
                                YouTube Link:<br />
                                <input type="text" name="url" />
                            </label>
                            <br />
                            <input type="radio" id="va" name="video_or_audio" value="va" checked />
                            <label for="va">Video and Audio</label><br>
                            <input type="radio" id="a" name="video_or_audio" value="a" />
                            <label for="a">Audio</label><br>
                            <input type="radio" id="v" name="video_or_audio" value="v" />
                            <label for="v">Video</label><br>
                            <input type="radio" id="kitchen_sink" name="video_or_audio" value="kitchen_sink" />
                            <label for="kitchen_sink">Three Files</label><br>
                            <input type="checkbox" id="quality" name="quality" value="bad">
                            <label for="quality">Lower Quality</label><br>
                            <input type="submit" value="Submit" />
                        </form>
                    </div>

                    <!-- Optional JavaScript -->
                    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
                    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
                    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
                </body>
            </html>
            '''

@celery.task()
def download(ydl_opts, url):
    ydl = youtube_dl.YoutubeDL(params=ydl_opts)
    ydl.download([url])


@app.route("/download", methods=['POST'])
def dl_form():
    url = request.form['url']
    video_or_audio = request.form['video_or_audio']
    quality = request.form.get('quality', 'good')

    dt = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M")

    ydl_opts = {
        'restrictfilenames':True,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]',
        'outtmpl': 'output/' + dt + '_%(title)s.f%(format_id)s.%(ext)s'
    }

    if video_or_audio == 'a':
        ydl_opts.update({'format':'bestaudio[ext=m4a]'})

    if video_or_audio == 'v':
        ydl_opts.update({'format':'bestvideo[ext=mp4]'})

    if video_or_audio == 'kitchen_sink':
        ydl_opts.update({'format':'bestvideo[ext=mp4],bestaudio[ext=m4a],bestvideo[ext=mp4]+bestaudio[ext=m4a]'})

    if quality == 'bad':
        ydl_opts['format'] = ydl_opts['format'].replace('bestvideo','bestvideo[height <= 480]')

    print('\n\n{}\n\n'.format(ydl_opts))

    result = download.delay(ydl_opts, url)
    return redirect("/")
