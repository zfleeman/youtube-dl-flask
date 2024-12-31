from datetime import datetime
from importlib.metadata import version
import os
from urllib.parse import quote

import requests
from flask import Flask, request, send_file, redirect, render_template
import yt_dlp

app = Flask(__name__)

video_filter = os.getenv("VIDEO_FILTER", "bv[ext=mp4][vcodec^=avc]")
audio_filter = os.getenv("AUDIO_FILTER", "ba[ext=m4a][acodec^=mp4a]")


@app.route("/")
def index():
    env_version = version("yt-dlp")

    response = requests.get("https://pypi.org/pypi/yt-dlp/json")
    if response.ok:
        data = response.json()
        pypi_version = data["info"]["version"]
    else:
        pypi_version = "UNABLE TO RETRIEVE VERSION FROM PYPI"

    return render_template("form.html", env_version=env_version, pypi_version=pypi_version)


@app.route("/process", methods=["POST"])
def dl_form():
    url = request.form["url"]
    video_or_audio = request.form["video_or_audio"]
    quality = request.form.get("quality", "good")

    dt = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M")

    format_options = {
        "va": f"{video_filter}+{audio_filter}",
        "a": f"{audio_filter}",
        "v": f"{video_filter}",
        "kitchen_sink": f"{video_filter},{audio_filter},{video_filter}+{audio_filter}",
    }

    ydl_opts = {
        "restrictfilenames": True,
        "format": format_options.get(video_or_audio),
        "outtmpl": f"output/{dt}_%(title)s.%(ext)s",
    }

    if quality == "bad":
        ydl_opts["format"] = f"{video_filter}[height<=480]+{audio_filter}"

    print(f"\n\n{ydl_opts}\n\n")

    try:
        ydl = yt_dlp.YoutubeDL(params=ydl_opts)
        info_dict = ydl.extract_info(url, download=False)
        ydl.download([url])
    except Exception as e:
        return f"An error occurred: {e}", 500

    fname = quote(ydl.prepare_filename(info_dict), safe="")

    return redirect("/download?filename=" + fname)


@app.route("/download", methods=["GET"])
def get_file():
    return send_file(request.args["filename"], as_attachment=True)


if __name__ == "__main__":
    app.run("0.0.0.0", port=5111, debug=True)
