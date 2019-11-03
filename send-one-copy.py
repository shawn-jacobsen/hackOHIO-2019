#!/usr/bin/env python

import os
import sys
import json
import time
import argparse
from datetime import datetime

import geojson
import socketio

# Honda----------
import mobikit
workspace_id = 173
feed_name = "Honda_Hackathon_Data.points"
query = json.loads('{"select":[{"field":"id"},{"field":"tm"},{"field":"point","format":"text"},{"field":"trip_id"}],"sort":[{"field":"point","dir":"descending"},{"field":"id","dir":"ascending"}]}')

mobikit.set_api_key("373afebc8a2b2ee5d5e7743cc73565c82d9ecdd8", environment="ohio")
df = mobikit.workspaces.load(workspace_id, feed_name, query=query)
print("Recent positions query", query)
# Honda---------
# Shawn's API : 502c26634d0243db92233e183d5cf02c6e08536e 
# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--feed-id", "-f", type=int, help="unique feed id", required=True)
parser.add_argument("--latitude", "-y", type=float, help="latitude", required=True)
parser.add_argument("--longitude", "-x", type=float, help="longitude", required=True)
parser.add_argument(
    "--timestamp",
    "-t",
    type=str,
    default=datetime.now().isoformat(),
    help="timestamp in ISO8601 format",
)

parser.add_argument("--tags", "-d", type=str, default="{}", help="JSON object")
parser.add_argument("--debug", action="store_true", help="debug logging")

args = parser.parse_args()

# parse the timestamp as ISO8601 (Python compatible)
try:
    timestamp = datetime.strptime(args.timestamp, "%Y-%m-%dT%H:%M:%S.%f")

except ValueError as e:
    print("Failed to parse timestamp: {}".format(e))
    sys.exit(1)

# connect to the server
sio = socketio.Client(logger=args.debug)
sio.connect(
    os.getenv("https://stream.ohio.mobikit.io/"),
    headers={"Authorization": "Token {}".format(os.getenv("502c26634d0243db92233e183d5cf02c6e08536e"))},
)

print("SID: {}".format(sio.sid))

# assemble the GeoJSON feature
feature = geojson.Feature(
    geometry=geojson.Point((args.longitude, args.latitude)),
    properties=json.loads(args.tags),
)

# assemble the SocketIO event
event = {
    "headers": {"feed_id": args.feed_id, "timestamp": timestamp.isoformat()},
    "feature": feature,
}

# emit the event on the "data" channel and call print() with the response
sio.emit("data", event, callback=print)

# wait for SocketIO to have a chance to send the event and process the response
# alternatively you can use the callback to update some shared state if you
# want to be sure you've waited long enough
time.sleep(1.0)

# disconnect from the server
sio.disconnect()

# XXX: SocketIO will eventually shut down background threads and quit but it
# takes a really long time. at this point we're fairly certain we don't need
# to wait for a response from the Stream API so just force quit the program
os._exit(0)
