#!/bin/bash
export CKAN_POSTGRESQL_PASSWORD="ckan"
docker run -it --entrypoint=/bin/bash  --env CKAN_POSTGRESQL_PASSWORD=$CKAN_POSTGRESQL_PASSWORD -p 81:80 -p 5000:5000 -v ~/dev/ocims/ckan/scripts/:/scripts -v ~/dev/ocims/ckan/schema.xml:/usr/lib/ckan/default/src/ckan/ckan/config/solr/schema.xml ocims_ckan -s

