FROM ubuntu:latest
MAINTAINER Eden Attenborough "eda@e.email"
ENV TZ=Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update -y
RUN apt-get install -y tzdata python3-pip build-essential pkg-config cron libjpeg-dev zlib1g-dev libfreetype6-dev libgeos-dev libxml2-dev libxslt-dev
RUN mkdir app
COPY . /app
WORKDIR /app
RUN touch .docker
RUN pip3 install -r requirements.txt

RUN echo "0 */3 * * * root python3 /app/bot.py > /proc/1/fd/1 2>/proc/1/fd/2" > /etc/crontab
ENTRYPOINT ["bash"]
CMD ["entrypoint.sh"]
