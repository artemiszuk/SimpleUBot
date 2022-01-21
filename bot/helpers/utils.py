import os
import pathlib
import random
import ffmpeg

def extension(fpath):
    return str(pathlib.Path(fpath).suffix)

def progress(current, total):
    bar = ""
    current = int(current / 10)
    for i in range(0, 10):
        if i < current:
            bar += "█"
        else:
            bar += "░"
    return f"[{bar}]"

async def get_details(filepath):
    mydict = dict()
    probe = ffmpeg.probe(filepath)
    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None
    )
    mydict["width"] = int(video_stream["width"])
    mydict["height"] = int(video_stream["height"])
    mydict["duration"] = probe["format"]["duration"]
    filename = os.path.basename(filepath)
    mydict["tname"] = filename[0 : filename.index(".")] + ".jpeg"
    (
        ffmpeg.input(filepath, ss=random.randrange(0, int(float(mydict["duration"]))))
        .filter("scale", mydict["width"], -1)
        .output(mydict["tname"], vframes=1)
        .run()
    )
    return mydict