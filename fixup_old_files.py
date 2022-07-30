import logging
from os import listdir, system
from os.path import exists, expanduser, isdir, isfile
from subprocess import check_call

import click
from PIL import Image

logger = logging.getLogger(__name__)

ROOT = "/Users/edromano/dev/pi_timelapse"
VIDEO_ROOT = "/Users/edromano/dev/pi_timelapse/video_chunks"


@click.group()
def cli():
    logging.basicConfig(level=logging.INFO)
    logger.info('starting')


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

    # logger.info(f"{nblack} black pixels out of {len(pixels)}")
    return (nblack / float(len(pixels))) > 0.75


def remove_dark_images(folder):
    for filename in listdir(folder):
        full_path = f'{folder}/{filename}'
        if isdir(full_path):
            logger.info(f'working on folder {filename}')
            remove_dark_images(full_path)
        else:
            try:
                with Image.open(full_path) as image:
                    if is_mostly_dark(image):
                        check_call(["sudo", "rm", expanduser(full_path)])
            except Exception:
                logger.info(f"Error while processing: {filename}")
                check_call(["sudo", "rm", expanduser(full_path)])


@cli.command()
@click.argument('folder')
def create_video(folder):
    sub_dir = 'front' if '/front/' in folder else 'rear'
    filename = folder.split("/")[-1]
    if isdir(folder):
        logger.info(f'working on folder {filename}')
        args1 = "-framerate 24 -pattern_type glob"
        args2 = "-s:v 1440x1080 -c:v libx264 -crf 17 -pix_fmt yuv420p"
        video_cmd = f'ffmpeg {args1} -i "{folder}/*.jpeg" {args2} {VIDEO_ROOT}/{sub_dir}/{filename}.mp4'
        system(video_cmd)


@cli.command()
@click.argument('camera_name')
def merge_videos(camera_name):
    with open(f"/tmp/{camera_name}_chunks.txt", "w") as f:
        for video_name in listdir(f"{VIDEO_ROOT}/{camera_name}/"):
            f.write(f"file '{VIDEO_ROOT}/{camera_name}/{video_name}'\n")
        video_cmd = f'ffmpeg -f concat -safe 0 -i /tmp/{camera_name}_chunks.txt -c copy {ROOT}/videos/{camera_name}.mp4'
        # SOOOO annoying. For some reason this ffmpeg command can't run from python
        logger.info(f"Run: {video_cmd}")


def group_by_date(folder):
    for filename in listdir(folder):
        full_path = f'{folder}/{filename}'
        if isfile(full_path):
            new_folder = filename.split('_')[0]
            dest = f'{ROOT}/dumps/grouped/{new_folder}'
            setup_folder(dest)
            check_call(['sudo', 'cp', full_path, f'{dest}/{filename}'])


@cli.command()
@click.option('--dest_folder', type=str)
@click.argument('src_root')
def get_usb_dump(dest_folder, src_root):
    # rear or front
    # /Volumes/{usb_name}/timelapse
    logger.info(f"Updating {dest_folder} for {src_root}")
    dest_root = f"{ROOT}/dumps/{dest_folder}"
    for folder in listdir(src_root):
        dest_folder = f"{dest_root}/{folder}"
        src_folder = f"{src_root}/{folder}"
        if not exists(dest_folder):
            check_call(["mkdir", dest_folder])
        for file in listdir(src_folder):
            check_call(['mv', "-f", f"{src_folder}/{file}", f'{dest_folder}/{file}'])


if __name__ == '__main__':
    cli()
