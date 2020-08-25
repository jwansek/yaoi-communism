from dataclasses import dataclass
from io import StringIO
from lxml import etree
import requests
import urllib
import random
import time
import cv2
import os

# all of these tags are added to all queries. Preceded with '-' to blacklist
base_tags = ["yaoi", "-muscle", "-comic"]
# one of these will be added
search_tags = ["looking_at_another", "kiss", "trap", "2boys", "promare"]

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
    element = random.choice(elements)
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

def main():
    try:
        simg = get_image(get_random_searchtag())
    except ConnectionError:
        main()

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
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        cv2.imshow("Press <q> to exit", img)
        cv2.waitKey(0)

if __name__ == "__main__":
    main()


    


