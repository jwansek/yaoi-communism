from dataclasses import dataclass
from PIL import Image, ImageDraw
from io import StringIO
from lxml import etree
import requests
import logging
import urllib
import random
import utils
import time
import json
import cv2
import os

with open("config.json", "r") as f:
    CONFIG = json.load(f)

logging.basicConfig( 
    format = "%(levelname)s\t[%(asctime)s]\t%(message)s", 
    level = logging.INFO,
    handlers=[
        logging.FileHandler(CONFIG["logpath"]),
        logging.StreamHandler()
    ])

# all of these tags are added to all queries. Preceded with '-' to blacklist
base_tags = CONFIG["base_tags"]
# one of these will be added
search_tags = CONFIG["search_tags"]

def get_random_searchtag():
    return [random.choice(search_tags)]

@dataclass
class SafebooruImage:
    id: int
    tags: list
    source: str
    imurl: str

def get_id_from_url(url):
    return int(urllib.parse.parse_qs(url)["id"][0])

def get_image(tags):
    search_url = "https://safebooru.org/index.php?page=post&s=list&tags=%s&pid=%i" % ("+".join(base_tags+tags), (random.randint(1, get_num_pages(tags))-1)*5*8)
    tree = etree.parse(StringIO(requests.get(search_url).text), etree.HTMLParser())
    elements = [e for e in tree.xpath("/html/body/div[6]/div/div[2]/div[1]")[0].iter(tag = "a")]
    try:
        element = random.choice(elements)
    except IndexError:
        raise ConnectionError("Couldn't find any images")
    simg = SafebooruImage(
        id = get_id_from_url(element.get("href")),
        tags = element.find("img").get("alt").split(),
        source = get_source("https://safebooru.org/" + element.get("href")),
        imurl = get_imurl("https://safebooru.org/" + element.get("href"))
    )
    if simg.source is None:
        print("https://safebooru.org/" + element.get("href"))
    return simg

def get_source(url):
    tree = etree.parse(StringIO(requests.get(url).text), etree.HTMLParser())
    for element in tree.xpath('//*[@id="stats"]')[0].iter("li"):
        if element.text.startswith("Source: h"):
            return element.text[8:]
        elif element.text.startswith("Source:"):
            for child in element.iter():
                if child.get("href") is not None:
                    return child.get("href")
    raise ConnectionError("Couldn't find source image for id %i" % get_id_from_url(url))

def get_imurl(url):
    tree = etree.parse(StringIO(requests.get(url).text), etree.HTMLParser())
    return tree.xpath('//*[@id="image"]')[0].get("src")

def get_num_pages(tags):
    search_url = "https://safebooru.org/index.php?page=post&s=list&tags=%s" % "+".join(base_tags+tags)
    html = requests.get(search_url).text
    tree = etree.parse(StringIO(html), etree.HTMLParser())
    try:
        page_element = tree.xpath("/html/body/div[6]/div/div[2]/div[2]/div/a[12]")[0]
    except IndexError:
        return 1
    else:
        return int(int(urllib.parse.parse_qs(page_element.get("href"))["pid"][0]) / (5*8))

def fix_source_url(url):
    if "pixiv.net" in url or "pximg.net" in url: 
        if requests.get(url).status_code == 403:
            return "https://www.pixiv.net/en/artworks/%s" % url.split("/")[-1][:8]                

    return url 

def append_blacklisted(id_):
    with open(CONFIG["blacklist"], "a") as f:
        f.write(str(id_) + "\n")

def id_is_blacklisted(id_):
    if not os.path.exists(CONFIG["blacklist"]):
        return False
    with open(CONFIG["blacklist"], "r") as f:
        return str(id_) in f.read().splitlines()

@dataclass
class DownloadedImage:
    imurl: str
    
    def __enter__(self):
        self.filename = urllib.parse.urlparse(self.imurl).path.split("/")[-1]

        req = urllib.request.Request(self.imurl, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_5_8) AppleWebKit/534.50.2 (KHTML, like Gecko) Version/5.0.6 Safari/533.22.3'})
        mediaContent = urllib.request.urlopen(req).read()
        with open(self.filename, "wb") as f:
            f.write(mediaContent)
        return self.filename

    def __exit__(self, type, value, traceback):
        os.remove(self.filename)

def main(draw_faces = False):
    try:
        simg = get_image(get_random_searchtag())
    except ConnectionError:
        logging.warning("Retried since couldn't get source...")
        return main()

    if id_is_blacklisted(simg.id):
        logging.info("Retried, already posted image...")
        return main()

    append_blacklisted(simg.id)

    with DownloadedImage(simg.imurl) as impath:
        img = cv2.imread(impath)

        cascade = cascade = cv2.CascadeClassifier(os.path.join("lbpcascade_animeface", "lbpcascade_animeface.xml"))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        faces = cascade.detectMultiScale(gray,
                                        # detector options
                                        scaleFactor = 1.1,
                                        minNeighbors = 5,
                                        minSize = (24, 24))
        if draw_faces:
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        logging.info("Found image %i faces, id: %i" % (len(faces), simg.id))

        pilimg = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        text = utils.get_quote(CONFIG["texts"])
        logging.info(text)
        font = utils.set_font(pilimg, text)
        draw = ImageDraw.Draw(pilimg)
        lines = utils.messages_multiline(text, font, pilimg)
        colours = utils.get_colors(impath)

        (x, y, faces) = utils.randomize_location(pilimg, lines, font, faces)
        for line in lines:
            height = font.getsize(line[1])[1]
            utils.draw_with_border(x, y, line, colours[0], colours[1], font, draw)
            y = y + height

        pilimg.save("img.png")
        return "img.png", fix_source_url(simg.source), text


if __name__ == "__main__":
    print(main())


    


