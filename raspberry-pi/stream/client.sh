#!/bin/sh

# Trap for cleanup on keyboard interrupt (Ctrl + C)
trap cleanup INT
cleanup() {
    echo "Stream interrupted, cleaning up..."
    if [ -n "$ffmpeg_pid" ]; then
        echo "Attempting to gracefully stop ffmpeg..."
        kill "$ffmpeg_pid"

        sleep 2
        if ps -p "$ffmpeg_pid" >/dev/null; then
            echo "ffmpeg did not terminate, forcing it to stop..."
            kill -9 "$ffmpeg_pid"
        fi
    fi
    exit 0
}

if [ -z "/dev/video0" ] || [ -z "$STREAM_SERVER_URL" ]; then
    echo "Both \$STREAM_DEVICE=/dev/video0 and \$STREAM_SERVER_URL=$STREAM_SERVER_URL options are required"
    exit 1
fi

# Check if RTMP server is reachable
while ! nc -z "$STREAM_SERVER_URL" $STREAM_SERVER_PORT; do
    echo "RTMP server at $STREAM_SERVER_URL not reachable, make sure netcat is installed, retrying in 5 seconds..."
    sleep 5
done
echo "RTMP server at $STREAM_SERVER_URL is reachable."

while true; do
    echo "Starting stream from $STREAM_DEVICE to $STREAM_SERVER_URL"
    ffmpeg -f v4l2 -i "/dev/video0" \
        -pix_fmt yuv420p -s 640x480 -r 30 \
        -preset ultrafast -tune zerolatency \
        -g 10 -keyint_min 10 \
        -vcodec libx264 -b:v 1000k \
        -acodec aac -b:a 128k -f flv \
        "rtmp://$STREAM_SERVER_URL/live/$STREAM_TOKEN" &

    ffmpeg_pid=$!      
    wait "$ffmpeg_pid" 
    echo "ffmpeg encountered an error or was terminated. Restarting in 5 seconds..."
    sleep 5
done