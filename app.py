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

format_options = {
    "va": f"{video_filter}+{audio_filter}",
    "a": f"{audio_filter}",
    "v": f"{video_filter}",
    "kitchen_sink": f"{video_filter},{audio_filter},{video_filter}+{audio_filter}",
}


@app.route("/")
def index():

    # get yt-dlp's current version
    env_version = version("yt-dlp")

    # poll the web and get the most recent version for an "OUTDATED" warning
    response = requests.get("https://pypi.org/pypi/yt-dlp/json")
    if response.ok:
        data = response.json()
        pypi_version = data["info"]["version"]
    else:
        pypi_version = "UNABLE TO RETRIEVE VERSION FROM PYPI"

    return render_template("form.html", env_version=env_version, pypi_version=pypi_version)


@app.route("/process", methods=["POST"])
def dl_form():
    # get information from the form
    url = request.form["url"]
    video_or_audio = request.form["video_or_audio"]
    auto_dl = request.form.get("auto_dl") == "dl"
    video_format_id = request.form.get("video_format_id")
    audio_format_id = request.form.get("audio_format_id")

    # create the all-important ydl params
    dt = datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M")
    ydl_opts = {
        # "listformats": True,
        "restrictfilenames": True,
        "outtmpl": f"output/{dt}_%(title)s.%(ext)s",
    }

    # fill in the format in the ydl_opts dictionary from the webform or the application defaults (best video and audio)
    if video_format_id or audio_format_id:
        if video_format_id and audio_format_id:
            format_id = f"{video_format_id}+{audio_format_id}"
        else:
            format_id = video_format_id or audio_format_id
        ydl_opts["format"] = format_id

    else:
        ydl_opts["format"] = format_options.get(video_or_audio)

    try:
        ydl = yt_dlp.YoutubeDL(params=ydl_opts)

        # the video_info dictionary is used to populate the webform and to get information about our video
        video_info = ydl.extract_info(url, download=False)
        video_info["auto_dl"] = auto_dl

        # gather up the audio/video formats for later display
        video_info["audio_formats"] = [
            format for format in video_info.get("formats", []) if format["vcodec"] == "none"
        ]
        video_info["video_formats"] = [
            format
            for format in video_info.get("formats", [])
            if format["vcodec"] != "none" and format["acodec"] == "none"
        ]

        # clean up our file name a bit
        video_info["clean_name"] = quote(ydl.prepare_filename(video_info))

        # get "selected" formats from the info dict
        selected_format_ids = set(video_info["format_id"].split("+"))

        # create a small list for later html formatting
        video_info["selected_ids"] = [
            format["format_id"] for format in video_info["formats"]
            if format["format_id"] in selected_format_ids
        ]

        # initiate the download if the checkbox is selected
        if auto_dl:
            print(ydl_opts)
            ydl.download([url])
            return send_file(video_info["clean_name"], as_attachment=True)

    except Exception as e:
        return f"An error occurred: {e}", 500

    return render_template("form.html", video_info=video_info, url=url)


if __name__ == "__main__":
    app.run("0.0.0.0", port=5111, debug=True)
