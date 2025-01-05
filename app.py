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
        # "listformats": True,
        "restrictfilenames": True,
        "format": format_options.get(video_or_audio),
        "outtmpl": f"output/{dt}_%(title)s.%(ext)s"
    }

    if quality == "bad":
        ydl_opts["format"] = f"{video_filter}[height<=480]+{audio_filter}"

    print(f"\n\n{ydl_opts}\n\n")

    try:
        ydl = yt_dlp.YoutubeDL(params=ydl_opts)
        video_info = ydl.extract_info(url, download=False)
        video_info["audio_formats"] = [
            format for format in video_info.get("formats", []) if format["resolution"] == "audio only"
        ]
        video_info["video_formats"] = [
            format
            for format in video_info.get("formats", [])
            if format["resolution"] != "audio only" and format["ext"] != "mhtml"
        ]

        video_info["clean_name"] = ydl.prepare_filename(video_info)

        # get "selected" formats
        format_ids = video_info["format_id"].split("+")

        for video_format in video_info["video_formats"]:
            if format_ids[0] == video_format["format_id"] and video_format["audio_ext"] == "none":
                print(f"video format: {video_format}")
                break
        for audio_format in video_info["audio_formats"] and video_format["video_ext"] == "none":
            if format_ids[1] == audio_format["format_id"]:
                print(f"audio format: {audio_format}")
                break
  
        # print(f"vcodec: {vcodec}")
        # print(f"acodec: {acodec}")


        formats = video_info.get("formats", [])
        ydl.download([url])


        # Debug print the formats
        # print("Available formats:")
        # for f in selected_formats:
        #     print(f"{f}")
    except Exception as e:
        return f"An error occurred: {e}", 500
    
    # ydl.download([url])

    # if selected_formats:
    #     for f in selected_formats:
    #         print(f"ID: {f['format_id']}, Info: {f}")

    return render_template("form.html", video_info=video_info)


@app.route("/download", methods=["GET"])
def get_file():
    return send_file(request.args["filename"], as_attachment=True)


if __name__ == "__main__":
    app.run("0.0.0.0", port=5111, debug=True)
