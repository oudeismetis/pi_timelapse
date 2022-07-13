import logging
from datetime import datetime
from io import BytesIO
from os.path import exists, expanduser
from subprocess import check_call
from time import sleep

from picamera import PiCamera
from PIL import Image

logger = logging.getLogger(__name__)

MEDIA_DIR = "/timelapse_media"
CAPTURE_FREQUENCY = 300  # numbers of seconds to wait before capturing a new image


def setup_folder(folder_path):
    if not exists(folder_path):
        check_call(["sudo", "mkdir", expanduser(folder_path)])
        # add write permissions for all
        check_call(["sudo", "chmod", "a+w", expanduser(folder_path)])


def is_mostly_dark(image):
    pixels = image.getdata()
    black_thresh = 50
    nblack = 0

    # start = datetime.now()
    for pixel in pixels:
        if sum(pixel) < black_thresh:
            nblack += 1
    # duration = datetime.now() - start
    # ~2 seconds. Not worth optimizing
    # logger.info(f"Nighttime detection took: {duration}s")

    logger.info(f"{nblack} black pixels out of {len(pixels)}")
    return (nblack / float(len(pixels))) > 0.75


def capture_image(camera):
    stream = BytesIO()
    camera.capture(stream, format="jpeg")
    stream.seek(0)
    with Image.open(stream) as image:
        if not is_mostly_dark(image):
            folder = datetime.now().strftime("%Y-%m-%d")
            setup_folder(f"{MEDIA_DIR}/{folder}")
            file_name = datetime.now().strftime("%Y-%m-%d_%H%M")
            image.save(f"{MEDIA_DIR}/{folder}/{file_name}.jpeg")


def main():
    logging.basicConfig(level=logging.INFO)
    setup_folder(MEDIA_DIR)
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
            logger.error(f"failure from main loop, shutting down. {e}")


# TODO - Make for folder for every 24 hours
# Generate a video for every folder
# Delete folders older than X days

if __name__ == "__main__":
    main()
