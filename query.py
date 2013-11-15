

import sys
import urllib
import xml.etree.ElementTree as ET

DAPPER_URL = "http://open.dapper.net/RunDapp?dappName=justeatuk&v=1&applyToUrl=http%3A%2F%2Fwww.just-eat.co.uk%2Farea%2FZIPCODE%2FFILTER&filter=true"

def main():
    if len(sys.argv) <= 1:
        print("usage: query.py <zipcode,zipcode,...> <filter>\n  example: query.py M40,M50,1090 Pizza")
        return
    zipcodes = sys.argv[1].split(",")
    food_type = ""
    if len(sys.argv) >= 3:
        food_type = sys.argv[2]
    xmls = []
    for zipcode in zipcodes:
        url = DAPPER_URL.replace("ZIPCODE",zipcode)
        url = url.replace("FILTER",food_type)
        req = urllib.urlopen(url)
        xmls.append(ET.fromstring(req.read()))


    count = 0
    out = ET.Element('restaurants')
    for et in xmls:
        for r in et.findall("./restaurant"):
            count += 1
            restaurant = ET.SubElement(out, 'restaurant')
            for name in r.iter('name'):
                name = ET.SubElement(restaurant, 'name')
                name.text = r.find('name').text

    print ET.dump(out)

    print("found %d restaurants" % count)


if __name__ == "__main__":
    main()
