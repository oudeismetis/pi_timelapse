from datetime import datetime
from io import BytesIO
from os.path import exists, expanduser
from subprocess import check_call
from time import sleep

from picamera import PiCamera
from PIL import Image

MEDIA_DIR = "/timelapse_media"
CAPTURE_FREQUENCY = 300  # numbers of seconds to wait before capturing a new image


def setup_folders():
    if not exists(MEDIA_DIR):
        check_call(["sudo", "mkdir", expanduser(MEDIA_DIR)])
        # add write permissions for all
        check_call(["sudo", "chmod", "a+w", expanduser(MEDIA_DIR)])

def is_mostly_dark(image):
    pixels = image.getdata()
    black_thresh = 50
    nblack = 0

    for pixel in pixels:
        if sum(pixel) < black_thresh:
            nblack += 1

    print(f"{nblack} black pixels out of {len(pixels)}")
    return (nblack / float(len(pixels))) > 0.5


def capture_image(camera):
    stream = BytesIO()
    camera.capture(stream, format="jpeg")
    stream.seek(0)
    with Image.open(stream) as image:
        if is_mostly_dark(image):
            # Nighttime so don't bother saving it
            print("mostly black")
        else:
            # TODO - If not mostly black, write to file
            pass
        file_name = f"{datetime.now().strftime('%Y-%m-%d_%H%M')}.jpeg"
        image.save(f"{MEDIA_DIR}/{file_name}")


def main():
    setup_folders()
    with PiCamera() as camera:
        camera.resolution = (1280, 720)
        try:
            while True:
                start = datetime.now()
                capture_image(camera)
                # To capture somewhat consistently, subtract our run time
                duration = datetime.now() - start
                sleep(CAPTURE_FREQUENCY - duration.seconds)
        except Exception as e:
            print(f"failure from main loop, shutting down. {e}")


# TODO - Make for folder for every 24 hours
# Generate a video for every folder
# Delete folders older than X days

if __name__ == "__main__":
    main()
