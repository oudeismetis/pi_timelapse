# Timelapse video for Raspberry Pi

1. use raspberry pi installer. Lite 32 version. Setting wifi setting before writing helps
1. sudo apt install python3-pip
1. pip3 install -r requirements.txt
1. sudo apt install libopenjp2-7  # PIL error
1. sudo raspi-config  # enable camera
1. python3 -u timelapse.py
1. Install quickly:
```
curl -L https://github.com/oudeismetis/pi_timelapse/raw/main/install.sh | sh
```

```
ffmpeg -framerate 24 -pattern_type glob -i "dumps/06_28/*.jpeg" -s:v 1440x1080 -c:v libx264 -crf 17 -pix_fmt yuv420p videos/06_28_timelapse.mp4
```

## Concat all the days
https://stackoverflow.com/questions/7333232/how-to-concatenate-two-mp4-files-using-ffmpeg

my_list.txt looks something like:
```
file '/Users/oudeis/dev/pi_timelapse/videos/06_28_timelapse.mp4'
file '/Users/oudeis/dev/pi_timelapse/videos/07_10_timelapse.mp4'
```
then you can run:
```
ffmpeg -f concat -safe 0 -i my_list.txt -c copy videos/exp_merge.mp4
```

## Power Saver: (~180mA)

### TODO
I wonder if you can use another Pi and a short ethernet cable to SSH directly onto a Pi?
If so, that would make disabling of all the below settings much more practical as you'd still have a way in to disable them when needed.

Alternatively, build some sort of "solar button".
When we detect that it's very dark outside via inspecting camera images, trigger a shutdown of the OS.
Have a tiny light sensor pointed at the sky. When it detects enough light, trigger the pi back on.
This could be a physical button trigger, but I believe you can also power on the pi via wire

### Disable USB (100mA)
resets on reboot.
Disable and enable would be:
```
echo '1-1' |sudo tee /sys/bus/usb/drivers/usb/unbind
echo '1-1' |sudo tee /sys/bus/usb/drivers/usb/bind
```

### Disable HDMI (30mA)
resets on reboot.
Disable and enable would be:
```
sudo /opt/vc/bin/tvservice -o
sudo /opt/vc/bin/tvservice -p
```

### Disable Wifi/Bluetooth (40mA)
Change is permenant unless lines are removed
Edit `/boot/config.txt`
```
[all]
dtoverlay=disable-wifi
dtoverlay=disable-bt
```

### Disable LEDs (10mA)
Most of these changes work for the Pi3, though some are Pi4 specific. Pi2 has very different settings
Change is permenant unless lines are removed
Edit `/boot/config.txt`
```
[pi4]
# Disable the PWR LED
dtparam=pwr_led_trigger=none
dtparam=pwr_led_activelow=off
# Disable the Activity LED
dtparam=act_led_trigger=none
dtparam=act_led_activelow=off
# Disable ethernet port LEDs
dtparam=eth_led0=4
dtparam=eth_led1=4
disable_camera_led=1
```


Resources:
1. https://maker.pro/raspberry-pi/projects/how-to-build-a-time-lapse-camera-using-a-raspberry-pi-zero-w
1. https://stackoverflow.com/questions/7333232/how-to-concatenate-two-mp4-files-using-ffmpeg
1. https://blues.io/blog/tips-tricks-optimizing-raspberry-pi-power/
