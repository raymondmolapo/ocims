#!/bin/bash

export CKAN_POSTGRESQL_PASSWORD="ckan"

#remove old folder
./autocopy.sh

chmod +x ~/dev/ocims/docker-manage.sh
chmod +x ~/dev/ocims/dbinit.sh

if ! ["$(docker ps | grep 'ocims_ckan')" == ""]; then 

#stop and remove currrent ckan_ocims docker
docker rm $(docker stop $(docker ps -a | grep "ocims_ckan" | awk -F' ' '{print $1}'));
fi 

#run set up through docker-compose to create images
python setup.py

if ! ["$(docker ps | grep 'ocims_ckan')" == ""]; then 
#stop and remove currrent ckan_ocims docker
docker rm $(docker stop $(docker ps -a | grep "ocims_ckan" | awk -F' ' '{print $1}'));
fi

#run docker
docker run -d -p 80:80 -p 8085:8085 -p 8808:8808 -p 443:443 \
-v ~/dev/ocims/tmp/logs/configure.log:/logs/configure.log \
-v ~/dev/ocims/ckan/scripts/:/scripts/ \
-v ~/dev/ocims/ckan/scripts/interact.sh:/usr/lib/ckan/default/src/interact.sh \
-v ~/dev/ocims/docker-data/canned_dump.sql:/scripts/canned_dump.sql \
ocims_ckan bash ./startup.sh



./docker-manage.sh


