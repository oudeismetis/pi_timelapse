#!/bin/bash
time=$(date +"%Y-%m-%d_%H%M")
raspistill -o /home/pi/timelapse/$time.jpeg
