# Timelapse video for Raspberry Pi

https://maker.pro/raspberry-pi/projects/how-to-build-a-time-lapse-camera-using-a-raspberry-pi-zero-w

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
