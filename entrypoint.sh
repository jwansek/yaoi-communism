# https://stackoverflow.com/questions/27771781/how-can-i-access-docker-set-environment-variables-from-a-cron-job/35088810#35088810
printenv | grep -v "no_proxy" >> /etc/environment

cron -f