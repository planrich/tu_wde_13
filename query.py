#!/bin/env/python3
# encoding: utf-8

import sys
import urllib.request
import xml.etree.ElementTree as ET
import re
import os
import subprocess
import webbrowser

DAPPER_URL = "http://open.dapper.net/RunDapp?dappName=justeatuk&v=1&applyToUrl=http%3A%2F%2Fwww.just-eat.co.uk%2Farea%2FZIPCODE%2FFILTER"
RESTAURANT_NAMES = set()

def build_just_eat_url(zipcode, food_type):
    URL = "http://open.dapper.net/RunDapp"
    { 'dappName': 'justeatuk',
      'v' : 1,
      'applyToUrl': None
    } #http%3A%2F%2Fwww.just-eat.co.uk%2Farea%2FZIPCODE%2FFILTER

    apply_to_url = "http://www.just-eat.co.uk/area/<zipcode>/<filter>"

def zipcode_type(zipcode):
    if re.match("^[a-zA-Z]+\d+$", zipcode):
        return "uk"

    return "at"

def extract_mjam(zipcode, food_type):
    restaurants = []

    proc = subprocess.Popen(['java', '-cp', 'Webl.zip', 'WebL', 'mjam.webl', zipcode, 'wien', food_type], stdout=subprocess.PIPE)

    content = proc.stdout.read()

    root = ET.fromstring(content)

    restaurants = []

    for orig_restaurant in root.findall("./restaurant"):
        restaurant_ele = ET.Element('restaurant')
        duplicate = False
        for name in orig_restaurant.iter('name'):
            name_ele = ET.SubElement(restaurant_ele, 'name')
            name_ele.text = name.text.strip()
            if name in RESTAURANT_NAMES:
                duplicate = True
            else:
                RESTAURANT_NAMES.add(name)
        for image in orig_restaurant.iter('image'):
            ele = ET.SubElement(restaurant_ele, 'image')
            ele.text = image.text.strip()
        for address in orig_restaurant.iter('address'):
            ele = ET.SubElement(restaurant_ele, 'address')
            ele.text = address.text.strip()

        for food_type in orig_restaurant.iter('food_type'):
            ele = ET.SubElement(restaurant_ele, 'food_type')
            ele.text = food_type.text.strip()

        for food_type in orig_restaurant.iter('openhours'):
            ele = ET.SubElement(restaurant_ele, 'openhours')
            ele.text = food_type.text.strip()

        for ratings in orig_restaurant.iter('ratings'):
            content = ratings.text.replace("QualityRank:","").strip()
            if re.match("^\d+$", content):
                ele = ET.SubElement(restaurant_ele, 'quality_rank')
                ele.text = content

        # not a duplicate -> append it to the xml document
        if not duplicate:
            restaurants.append(restaurant_ele)

    return restaurants

def extract_just_eat(zipcode, food_type):
    """
<restaurants>
    <restaurant groupName="restaurant" type="group">
        <image fieldName="image" href="http://www.just-eat.co.uk/restaurants-vindaloo-m35/menu" originalElement="img" src="http://d30v2pzvrfyzpo.cloudfront.net/uk/images/restaurants/19120.gif" type="field"/>
        <name fieldName="name" href="http://www.just-eat.co.uk/restaurants-vindaloo-m35/menu" originalElement="a" type="field">Vindaloo</name>
        <address fieldName="address" originalElement="address" type="field">608 Oldham Road, Failsworth M35 9DQ</address>
        <food_type fieldName="food_type" originalElement="span" type="field">Indian</food_type>
        <opens_at fieldName="opens_at" originalElement="span" type="field">16:30</opens_at>
        <ratings fieldName="ratings" href="http://www.just-eat.co.uk/restaurants-vindaloo-m35" originalElement="a" type="field">110 ratings</ratings>
    </restaurant>
</restaurants>

    """
    url = DAPPER_URL.replace("ZIPCODE",zipcode)
    url = url.replace("FILTER",food_type)
    req = urllib.request.urlopen(url)
    content = req.read()

    root = ET.fromstring(content)


    restaurants = []

    for orig_restaurant in root.findall("./restaurant"):
        restaurant_ele = ET.Element('restaurant')
        duplicate = False
        for name in orig_restaurant.iter('name'):
            name_ele = ET.SubElement(restaurant_ele, 'name')
            name_ele.text = name.text
            if name in RESTAURANT_NAMES:
                duplicate = True
            else:
                RESTAURANT_NAMES.add(name)
        for image in orig_restaurant.iter('image'):
            src = image.get('src')
            if src is not None:
                ele = ET.SubElement(restaurant_ele, 'image')
                ele.text = src
        for address in orig_restaurant.iter('address'):
            ele = ET.SubElement(restaurant_ele, 'address')
            ele.text = address.text

        for food_type in orig_restaurant.iter('food_type'):
            ele = ET.SubElement(restaurant_ele, 'food_type')
            ele.text = food_type.text

        for food_type in orig_restaurant.iter('opens_at'):
            ele = ET.SubElement(restaurant_ele, 'openhours')
            ele.text = food_type.text + "-23:59"

        for ratings in orig_restaurant.iter('ratings'):
            ele = ET.SubElement(restaurant_ele, 'rating_count')
            ele.text = ratings.text.replace("ratings","").strip()

        # not a duplicate -> append it to the xml document
        if not duplicate:
            restaurants.append(restaurant_ele)

    return restaurants

def main():
    if len(sys.argv) <= 1:
        print("usage: query.py <zipcode,zipcode,...> <filter>")
        print("  example: query.py M40,M50,1090 Pizza")
        print("  -> results are then found in tmp.xml")
        return
    zipcodes = sys.argv[1].split(",")
    food_type = ""
    if len(sys.argv) >= 3:
        food_type = sys.argv[2]

    restaurants = []
    print("fetching from %d sources. may take some time" % len(zipcodes))
    for zipcode in zipcodes:
        print("fetching from %s..." % zipcode, end="")

        # this is the drawback of having two
        # data sources containing data that are
        # geologically separate. one cannot query the same zipcode...
        if zipcode_type(zipcode) == "at":
            try:
                rs = extract_mjam(zipcode, food_type)
                restaurants.extend(rs)
            except Exception:
                print("warning: could not extract %s from mjam" % zipcode)
        else:
            try:
                rs = extract_just_eat(zipcode, food_type)
                restaurants.extend(rs)
            except Exception:
                print("warning: could not extract %s from just eat" % zipcode)
        print("done")

    print("loaded data from web sources")
    def key(doc):
        r = doc.find('rating_count')
        if r is not None and re.match("^\d+$", r.text):
            return int(r.text)

        r = doc.find('quality_rank')
        if r is not None and re.match("^\d+$", r.text):
            return int(r.text)
        return 0

    #restaurants.sort(key=lambda doc: key(doc), reverse=True)

    document = ET.Element('restaurants')
    for restaurant in restaurants:
        document.append(restaurant)
    with open("tmp.xml", "wb") as f:
        f.write(ET.tostring(document))
    print("written integrated data to 'tmp.xml'")
    webbrowser.open_new_tab("file://%s/anzeige.htm" % (os.getcwd()))

if __name__ == "__main__":
    main()
