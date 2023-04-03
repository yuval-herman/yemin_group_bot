#!/usr/bin/env fish

set -x REMOTE_USER root
set -x REMOTE_HOST 172.104.236.178
set -x REMOTE_PATH /root/yemin_group_bot
set -x SYSTEMD_SERVICE yemin_bot.service
set -x PROJECT_FILES *.py secrets.json

function upload
    echo "Uploading project files to remote server..."
    scp -r $PROJECT_FILES $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH
    echo "Upload complete!"
end

function start
    echo "Starting remote systemd service..."
    ssh $REMOTE_USER@$REMOTE_HOST "systemctl start $SYSTEMD_SERVICE"
    echo "Service started!"
end

function stop
    echo "Stopping remote systemd service..."
    ssh $REMOTE_USER@$REMOTE_HOST "systemctl stop $SYSTEMD_SERVICE"
    echo "Service stopped!"
end

function restart
    echo "Restarting remote systemd service..."
    ssh $REMOTE_USER@$REMOTE_HOST "systemctl restart $SYSTEMD_SERVICE"
    echo "Service restarted!"
end

function watch
    echo "Watching code..."
    ls *.py | entr -rc python bot.py
end

switch $argv[1]
    case upload
        upload
    case start
        start
    case stop
        stop
    case restart
        restart
    case watch
        watch
    case "*"
        echo "Usage: python_project_remote.sh [upload|start|stop|restart]"
end
