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
    ls *.py | entr -rc python bot.py dev
end

function fetch
    echo "Fetching db from server..."
    scp -r $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/yemin_bot.db remote.db
    echo "Download complete!"
end

function replace_db
    echo "Uploading remote.db"
    scp -r remote.db $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/yemin_bot.db
    echo "Upload complete!"
end

set available_commands upload start stop restart watch fetch replace_db

if contains $argv[1] $available_commands
    # If the command is in the array of available commands, run the corresponding function
    $argv[1]
else
    set usage_message (string join "|" $available_commands)
    echo "Usage: manager.sh [$usage_message]"
end
