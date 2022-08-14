# yaoi communism twitter bot 

Forked from the yuri version.

Unlike the yuri version, we don't have an archive of images and sources
to use. Instead, download yaoi images on the fly from safebooru.org.
Designed to be run once an hour using a cron job.

## Steps

- `git clone https://github.com/jwansek/yaoi-communism`

- `sudo pip3 install -r requirements.txt`

- `mv exampleconfig.json config.json`

- Populate `config.json` with API keys

- `python3 bot.py`

## Running in docker

- `sudo docker-compose build`

- `sudo docker-compose up -d`

Should do everything by itself if you set the config file correctly

To manually run (for testing):

`sudo docker run -it --entrypoint python3 --rm jwansek/yaoi-communism /app/bot.py`

![Example image](https://pbs.twimg.com/media/EgSA-hVXoAIXLbB?format=jpg&name=large)
