from datetime import datetime
from io import BytesIO

from picamera import PiCamera
from PIL import Image

MEDIA_DIR = '/home/oudeis/timelapse_media'

with PiCamera() as camera:
    stream = BytesIO()
    camera.capture(stream, format='jpeg')
    stream.seek(0)
    with Image.open(stream) as image:
        pixels = image.getdata()
        black_thresh = 50
        nblack = 0

        for pixel in pixels:
            if sum(pixel) < black_thresh:
                nblack += 1

        print(f"{nblack} black pixels out of {len(pixels)}")
        if (nblack / float(len(pixels))) > 0.5:
            print("mostly black")

        # TODO - If not mostly black, write to file
        # file_name = f"{datetime.now().strftime('%Y-%m-%d_%H%M')}.jpeg"
        # image.save(f"{MEDIA_DIR}/{file_name}")

# TODO - Make for folder for every 24 hours
# Generate a video for every folder
# Delete folders older than X days

