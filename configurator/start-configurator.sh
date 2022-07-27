#!/bin/sh

#
# Create inital config if necessary
#
mkdir -p $HOME/.local/share/actions-for-nautilus

[ -f $HOME/.local/share/actions-for-nautilus/config.json ] || cp ./sample-config.json $HOME/.local/share/actions-for-nautilus/config.json

#
# Start the configuration server, the xdg-open the home page
#

#
# Kill existing instance
#
#pgrep -U $USER -f "python ./actions-for-nautilus-configurator.py" >> /tmp/a4n-start.log 2>&1
pkill -U $USER -f "python3 ./actions-for-nautilus-configurator.py"
RC=$?
#echo "after the kill - $RC" # >> /tmp/a4n-start.log

#
# Find a port
#
PORT=$(python3 ./find-a-port.py)
#echo "the port $PORT" # >> /tmp/a4n-start.log 

#
# Start the server and detatch
#
python3 ./actions-for-nautilus-configurator.py $PORT & # >> /tmp/a4n-start.log 2>&1 &
RC=$?
#echo "server started $RC" # >> /tmp/a4n-start.log

#
# Start web page
#
xdg-open http://localhost:$PORT # >> /tmp/a4n-start.log 2>&1
RC=$?
#echo "XDG done $RC" # >> /tmp/a4n-start.log
