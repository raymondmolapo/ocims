#!/bin/bash
# initialise and start up the processes in the CKAN/Apache container
cd /

#create resource and upload folder

mkdir -p /var/lib/ckan/default
chown www-data /var/lib/ckan/default
chmod u+rwx /var/lib/ckan/default

# configure will set necessary params and links to services for CKAN
#cd /usr/lib/ckan/default
#pip install ckanext-showcase

cd /

/usr/sbin/apache2ctl -DFOREGROUND

tail -f /dev/null

