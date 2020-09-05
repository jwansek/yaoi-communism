import os
os.chdir("/root/yaoi-communism")

from twython import Twython
import get_images

twitter = Twython(*get_images.CONFIG["twitterapi"].values())

def post():
    impath, source, text = get_images.main()
    with open(impath, "rb") as img:
        response = twitter.upload_media(media = img)
        message = f"{text} ({source})"
        out = twitter.update_status(status=message, media_ids=[response["media_id"]])

    get_images.logging.info("Posted to twitter.")

if __name__ == "__main__":
    post()
