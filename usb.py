import logging
from os import listdir
from os.path import exists, expanduser, isdir, isfile
from subprocess import CalledProcessError, check_call

from pyudev import Context, Monitor

logger = logging.getLogger(__name__)

# Python Interactive Debugging
# logger.setLevel(logging.DEBUG)
# console_handler = logging.StreamHandler()
# console_handler.setFormatter(logging.Formatter("%(message)s"))
# logger.addHandler(console_handler)

MEDIA_DIR = '/timelapse_media'
SKIP_EXISTING_FOLDERS = True
USB_MOUNT_DIR = '/timelapse_usb'
USB_DIR = USB_MOUNT_DIR + '/timelapse'


def _copy_files(folder, root=''):
    for filename in listdir(folder):
        full_path = f'{folder}/{filename}'
        if isdir(full_path):
            dest = f'{USB_DIR}/{folder.replace(root, "")}/{filename}'
            if SKIP_EXISTING_FOLDERS and isdir(dest):
                logger.info(f'Skipping {full_path} | SKIP_EXISTING_FOLDERS is enabled')
            else:
                logger.info(f'Drilling down into folder {full_path}')
                _copy_files(full_path, root)
        elif isfile(full_path):
            # Destination on the USB shouldn't include folders above our root
            dest = f'{USB_DIR}/{full_path.replace(root, "").strip("/")}'
            logger.info(f'Moving {full_path} to {dest}')
            # TODO test via su to the user running the process
            try:
                check_call(['sudo', 'cp', full_path, dest])
            except CalledProcessError as e:
                logger.error(f'Error while copying file {e}')
            # TODO if is_old > delete


def _process_usb(device):
    device_name = device.device_node  # gets name e.g. /dev/sda1
    # TODO - simple security?
    # if device.get('ID_FS_LABEL', '').lower() == 'missed':
    try:
        # if mount folder exists, always delete folder and create again
        if exists(USB_MOUNT_DIR):
            check_call(['sudo', 'rm', '-rf', expanduser(USB_MOUNT_DIR)])
        check_call(['sudo', 'mkdir', expanduser(USB_MOUNT_DIR)])
        check_call(['sudo', 'mount', device_name, expanduser(USB_MOUNT_DIR)])
        # mk dir on usb if doesn't exist
        if not exists(USB_DIR):
            check_call(['sudo', 'mkdir', expanduser(USB_DIR)])
    except CalledProcessError as e:
        logger.error(f'error: {e}')
    else:
        logger.info('==============')
        logger.info('Writing files to attached USB device')
        _copy_files(MEDIA_DIR, MEDIA_DIR)
        logger.info('Done copying files')
    finally:
        check_call(['sudo', 'umount', USB_MOUNT_DIR], timeout=60)
        check_call(['sudo', 'eject', device_name], timeout=60)
        logger.info(f'USB {device_name} ejected')


def main():
    logger.basicConfig(level=logging.INFO)
    logger.info('starting timelapse-usb')

    context = Context()
    monitor = Monitor.from_netlink(context)
    monitor.filter_by(subsystem='block', device_type='partition')
    monitor.start()

    for device in iter(monitor.poll, None):
        if device.action == 'add':
            _process_usb(device)
    logger.info('timelapse-usb ready')


if __name__ == '__main__':
    main()
