#!/usr/bin/env python3

import logging, importio, threading, json
import sys
import xml.etree.ElementTree as ET

# We define a latch class as python doesn't have a counting latch built in
class _Latch(object):
    def __init__(self, count=1):
        self.count = count
        self.lock = threading.Condition()

    def countDown(self):
        with self.lock:
            self.count -= 1

            if self.count <= 0:
                self.lock.notifyAll()

    def await(self):
        print("waiting for %d resources to load!" % self.count)
        with self.lock:
            while self.count > 0:
                self.lock.wait()

logging.basicConfig(level=logging.INFO)

class Hotel(object):

    ATTRS = ["city","accommodation_type", "image", "name", "price", "detail_link", "room_type", "rating"]

    def __init__(self, attr):
        for k,v in attr.items():
            if isinstance(v,list):
                setattr(self,k,v[0])
            else:
                setattr(self,k,v)
        # set None as the default for all attributes
        for attribute in Hotel.ATTRS:
            try:
                getattr(self,attribute)
            except Exception as e:
                setattr(self,attribute,None)


hotels = []

def integrate(hotels, filename):
    root = ET.Element("hotels")
    with open(filename, "w") as output:
        for hotel in hotels:
            et_hotel = ET.SubElement(root, "hotel")
            for attr in Hotel.ATTRS:
                attr_val = getattr(hotel, attr)
                if attr_val is not None:
                    element = ET.SubElement(et_hotel, attr)
                    element.text = unicode(attr_val)

        output.write(ET.tostring(root))



def process(results):
    for result in results:
        hotels.append(Hotel(result))

latch = None

def callback(query, message):

    global latch

    if message["type"] == "MESSAGE": 
        data = message.get("data")
        if data is not None and data.get("results") is not None:
            results = data.get("results")
            print "loaded %d entries from import.io" % len(results)
            process(results)
        else:
            print "could not get data from import.io. API broken?"

    if query.finished(): latch.countDown()

def integrate_mozenda_mock(filename):
    print("integrating the static files from monzenda!")
    with open(filename,"r") as inputfile:
        xml_string = inputfile.read()
        root = ET.fromstring(xml_string)
        attributes = { "name": "Name", "image": "image", "rating": "Bewertung", "city": "city", "price": "price" }
        for item in root.iter("Item"):
            attrs = {}
            for k, attr in attributes.items():
                for tag in item.iter(attr):
                    attrs[k] = tag.text
            hotel = Hotel(attrs)
            hotels.append(hotel)

def main(search_inputs, date_from, date_to):
    # Initialise the library
    client = importio.ImportIO(userId="7f7512f6-461c-4b7d-acc6-f217616e6ca1", apiKey="q2oOB5FKs3mkDfJMpleEU4jPOibqCRBFW/xtCNd7fUE8IUDX+cXq/rTNb6oYj+wIeSkc4TtO0u0cZKcyApXtjg==")
    client.connect()

    # Use a latch to stop the program from exiting
    global latch
    latch = _Latch(len(search_inputs)) 

    integrate_mozenda_mock("monzenda.xml")

    for search_input in search_inputs:
    # Query for widget wde_visual_wrapper
        client.query({
          "connectorGuids": [
            "98bd1827-6e56-42c4-af1e-196ac0e51194"
          ],
          "input": {
            "from": date_from,
            "search_input": search_input,
            "to": date_to,
          },
          "startPage": 1

        }, callback)

    # Wait until queries complete
    latch.await()

    client.disconnect()

    print("integrating them into a single xml")

    integrate(hotels, "tmp.xml")

if __name__ == "__main__":
    try:
        search_inputs = sys.argv[1].split(",")
        date_from = sys.argv[2]
        date_to = sys.argv[3]
        main(search_inputs, date_from, date_to)
    except IndexError as e:
        print("usage: %s Salzburg,Vienna,Innsbruck 29.11.2013 07.12.2013" % sys.argv[0])

