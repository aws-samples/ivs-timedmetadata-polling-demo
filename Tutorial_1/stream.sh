#!/usr/bin/env bash

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

PROJECT_INGESTSERVER="CHANGEME!!"
PROJECT_STREAMKEY="CHANGEME!!"

STREAM_FILE="norisleepingmusic2_720p.mp4"
STREAM_DOWNLOAD="https://rodeolabz-us-east-1.s3.us-east-1.amazonaws.com/ivs-timedmetadata-polling-demo/${STREAM_FILE}"
if [ -e $STREAM_FILE ]; then
    echo 'File already exists, good job!' >&2
else
    echo 'Downloading source file...' >&2
    curl -O $STREAM_DOWNLOAD
fi

# https://docs.aws.amazon.com/ivs/latest/userguide/ivs-developer-streaming.html
# Channel Types              | "BASIC"   | "STANDARD" | "STANDARD"  |
BITRATE="1500" #             | "1500"    | "4500"     | "8500"      |
RESOLUTION="852x480" #       | "852x480" | "1280x720" | "1920x1080" |
FRAMERATE="30" #             | "30"      | "30" "60"  | "30" "60"   |

# https://docs.aws.amazon.com/ivs/latest/userguide/GSIVS-live-streaming.html
ffmpeg -stream_loop -1 -re -i $STREAM_FILE \
-vf drawtext="fontfile=monofonto.ttf: fontsize=96: box=1: boxcolor=black@0.75: boxborderw=5: fontcolor=white: x=(w-text_w)/2: y=((h-text_h)/2)+((h-text_h)/4): text='%{gmtime\:%H\\\\\:%M\\\\\:%S}'" \
-r $FRAMERATE \
-c:v libx264 -pix_fmt yuv420p -profile:v main -preset veryfast \
-x264opts "nal-hrd=cbr:no-scenecut" -g 60 \
-s $RESOLUTION -minrate $BITRATE -maxrate $BITRATE \
-c:a aac -b:a 160k -ac 2 -ar 44100 \
-f flv "$PROJECT_INGESTSERVER$PROJECT_STREAMKEY"