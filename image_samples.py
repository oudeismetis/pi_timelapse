import logging
from os import listdir, makedirs
from os.path import exists, isdir
import shutil

import click

# python image_samples.py get-daily-images <camera_name>

logger = logging.getLogger(__name__)


@click.group()
def cli():
    logging.basicConfig(level=logging.INFO)
    logger.info('starting')

@cli.command()
@click.argument('camera_name')
def get_daily_images(camera_name):
    # for each day of image files
    dest = f"daily_images/{camera_name}"
    for day in listdir(f"dumps/{camera_name}"):
        if isdir(f"dumps/{camera_name}/{day}"):
            file_names = listdir(f"dumps/{camera_name}/{day}")
            if file_names:
                sample_file = file_names[len(file_names)//2]
                src = f"dumps/{camera_name}/{day}/{sample_file}"
                shutil.copyfile(src, f"{dest}/{sample_file}")


def get_sorted_list(filenames):
    def sort_key(e):
        return e.split("_")[1].split(".jpeg")[0]
    filenames.sort(key=sort_key)
    return filenames


def is_5_min_apart(filename_1, filename_2):
    return int(filename_2.split("_")[1].split(".jpeg")[0]) - int(filename_1.split("_")[1].split(".jpeg")[0]) == 5


def copy_file_to_folder(src_folder, dest_folder, filename):
    if not exists(dest_folder):
        makedirs(dest_folder)
    shutil.copyfile(f"{src_folder}/{filename}", f"{dest_folder}/{filename}")


def find_group_for_image(src_folder, dest_root, filename):
    file_date = filename.split("_")[0]
    dest_contents = [f"{dest_root}/{x}" for x in listdir(dest_root)]
    dest_folders = [x for x in dest_contents if isdir(x) and file_date in x]
    added_to_existing = False
    for dest_folder in dest_folders:
        existing_files = get_sorted_list(listdir(dest_folder))
        if existing_files and is_5_min_apart(existing_files[-1], filename):
            copy_file_to_folder(src_folder, dest_folder, filename)
            added_to_existing = True
            break
    if not added_to_existing:
        copy_file_to_folder(src_folder, f"{dest_root}/{file_date}_{len(dest_folders) + 1}", filename)


def _group_folder_by_timestamp(folder):
    if not isdir(folder):
        raise Exception("Not a directory")
    logger.info(f"Working on folder {folder}")
    dest_root = "grouped_images"
    _, camera, working_day = folder.split("/")
    filenames = get_sorted_list([x for x in listdir(folder) if x.endswith(".jpeg")])
    for filename in filenames:
        find_group_for_image(folder, f"{dest_root}/{camera}", filename)


@cli.command()
@click.argument('folder')
def group_folder_by_timestamp(folder):
    _group_folder_by_timestamp(folder)


@cli.command()
@click.argument('camera_name')
def group_all_folders_by_timestamp(camera_name):
    for folder in listdir(f"dumps/{camera_name}"):
        full_path = f"dumps/{camera_name}/{folder}"
        if isdir(full_path):
            _group_folder_by_timestamp(full_path)


if __name__ == "__main__":
    cli()
