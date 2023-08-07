import os
os.chdir(os.path.dirname(__file__))

import get_images
import tweepy

def twitter_post(message, impath):
    auth = tweepy.OAuth1UserHandler(
        get_images.CONFIG["twitterapi"]["consumer_key"], 
        get_images.CONFIG["twitterapi"]["consumer_secret"],
        get_images.CONFIG["twitterapi"]["access_token"],
        get_images.CONFIG["twitterapi"]["access_token_secret"],
    )

    api = tweepy.API(auth)

    media_upload = api.simple_upload(impath)
    media_id = media_upload.media_id

    client = tweepy.Client(
        **get_images.CONFIG["twitterapi"]
    )

    response = client.create_tweet(text = message, media_ids = [media_id])
    get_images.logging.info(str(response))
    return response

def post():
    images = get_images.main()
    while images is None:
        images = get_images.main()

    impath, source, text = images
    twitter_post("%s (%s)" % (text, source), impath)
    get_images.logging.info("Posted to twitter.")

if __name__ == "__main__":
    post()
