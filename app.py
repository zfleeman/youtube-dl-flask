import yt_dlp
from datetime import datetime
from flask import Flask, request, send_file, redirect

app = Flask(__name__)


def url_help(url: str):
    symbols = {"+": "%2B", " ": "%20"}

    for k, v in symbols.items():
        url = url.replace(k, v)

    return url


@app.route("/")
def index():
    return """
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
                        <form action="/process", method="post">
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
            """


@app.route("/process", methods=["POST"])
def dl_form():
    url = request.form["url"]
    video_or_audio = request.form["video_or_audio"]
    quality = request.form.get("quality", "good")

    dt = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M")

    bv = "bv[ext=mp4][vcodec^=av]"
    ba = "ba[ext=m4a][acodec^=mp4a]"

    ydl_opts = {
        "restrictfilenames": True,
        "format": f"{bv}+{ba}",
        "outtmpl": "output/" + dt + "_%(title)s.%(ext)s",
    }

    if video_or_audio == "a":
        ydl_opts.update({"format": f"{ba}"})

    if video_or_audio == "v":
        ydl_opts.update({"format": f"{bv}"})

    if video_or_audio == "kitchen_sink":
        ydl_opts.update({"format": f"{bv},{ba},{bv}+{ba}"})

    if quality == "bad":
        ydl_opts["format"] = f"{bv}[height<=480]+{ba}"

    print("\n\n{}\n\n".format(ydl_opts))

    ydl = yt_dlp.YoutubeDL(params=ydl_opts)
    info_dict = ydl.extract_info(url, download=False)
    ydl.download([url])

    fname = url_help(ydl.prepare_filename(info_dict))

    return redirect("/download?filename=" + fname)


@app.route("/download", methods=["GET"])
def get_file():
    return send_file(request.args["filename"], as_attachment=True)


if __name__ == "__main__":
    app.run("0.0.0.0", port=5111, debug=True)
