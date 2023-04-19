#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import re
import base64

found_hrefs = set()
tree = ET.parse("handshake.drawio.svg")
for element in tree.iter():
    if element.tag == "{http://www.w3.org/2000/svg}image":
        # print(element.attrib["{http://www.w3.org/1999/xlink}href"])
        found_hrefs.add(element.attrib["{http://www.w3.org/1999/xlink}href"])

HREF_RE = re.compile(r"data:image/([^;]+);base64,([A-Za-z0-9+/=]+)")
FILETYPES = {
    "svg+xml": "svg",
    "png": "png",
}
for i, href in enumerate(found_hrefs):
    res = HREF_RE.match(href)
    # print(res.group(1), res.group(2))
    ftype = FILETYPES[res.group(1)]
    data = base64.b64decode(res.group(2))
    with open(f"ke-assets/{i}.{ftype}", "wb") as f:
        f.write(data)
