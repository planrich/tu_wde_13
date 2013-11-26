#!/usr/bin/env python3

import logging, importio, threading, json

# We define a latch class as python doesn't have a counting latch built in
class _Latch(object):
    def __init__(self, count=1):
        self.count = count
        self.lock = threading.Condition()

    def countDown(self):
        with self.lock:
            self.count -= 1

        print("count down %d" % self.count)

        if self.count <= 0:
            self.lock.notifyAll()

    def await(self):
        with self.lock:
            while self.count > 0:
                print("waiting %d" % self.count)
                self.lock.wait()

logging.basicConfig(level=logging.INFO)

# Initialise the library
client = importio.ImportIO(host="https://query.import.io", userId="7f7512f6-461c-4b7d-acc6-f217616e6ca1", apiKey="q2oOB5FKs3mkDfJMpleEU4jPOibqCRBFW/xtCNd7fUE8IUDX+cXq/rTNb6oYj+wIeSkc4TtO0u0cZKcyApXtjg==")
client.connect()

# Use a latch to stop the program from exiting
latch = _Latch(2)

def callback(query, message):

    if message["type"] == "MESSAGE": 
        print "Got data!"
        #print json.dumps(message["data"],indent = 4)

    if query.finished(): latch.countDown()

# Query for widget wde_visual_wrapper
client.query({
    "connectorGuids": [
        "c376d835-369b-4ce8-8bfe-54284a6465b6"
        ],
    "input": {
        "search_input": "Vienna"
        }
    }, callback)

# Query for widget wde_visual_wrapper
client.query({
    "connectorGuids": [
        "c376d835-369b-4ce8-8bfe-54284a6465b6"
        ],
    "input": {
        "search_input": "Salzburg"
        }
    }, callback)

# Wait until queries complete
latch.await()

client.disconnect()
