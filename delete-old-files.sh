#!/bin/bash

MEDIA_PATH=/timelapse_media/*

# create crontab to look for media files that are
# older than 7 days(mtime +6 is 7 days ago) and deletes it.
find $MEDIA_PATH -type d -mtime +6 -delete

DATE_TIME=`date`
echo Done $DATE_TIME
