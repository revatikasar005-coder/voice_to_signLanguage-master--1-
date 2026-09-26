import fetchLink
from pytube import YouTube
from conf import SAMPLE_INPUTS,SAMPLE_OUTPUTS
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips
import os
import re,wget
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


def downloader(word):
    original_cwd = os.getcwd()
    try:
        for w in word.split():
            link = fetchLink.getLink(w)
            print("**********", link, "***********")
            if link == 0:
                clips = []
                for l in w:
                    filename = f"{l}.mp4"
                    filepath = os.path.join(SAMPLE_INPUTS, "alphabets", filename)
                    if not os.path.exists(filepath):
                        raise FileNotFoundError(f"Missing alphabet clip: {filepath}")
                    clips.append(VideoFileClip(filepath))
                clip = concatenate_videoclips(clips, method='compose')
                os.makedirs(SAMPLE_INPUTS, exist_ok=True)
                os.chdir(SAMPLE_INPUTS)
                filename = f"{w}.mp4"
                clip.write_videofile(filename)
            elif re.match(r'^(https?://)?(www\.youtube\.com|youtu\.?be)/.+$', link):
                yt = YouTube(link)
                yt.streams.first().download(output_path=SAMPLE_INPUTS)
            else:
                os.makedirs(SAMPLE_INPUTS, exist_ok=True)
                wget.download(link, out=SAMPLE_INPUTS)
    finally:
        os.chdir(original_cwd)