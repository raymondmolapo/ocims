PATH_TO_ETC=/etc/ckan/default
PATH_TO_VAR=/var/lib/ckan
PATH_TO_DEFAULT=/usr/lib/ckan/default
PATH_TO_SOURCE=$PATH_TO_DEFAULT/src
PATH_TO_CKAN=$PATH_TO_SOURCE/ckan
PATH_TO_SETUP=$PATH_TO_SOURCE/ckanext-raymond_theme
PATH_TO_ANALYTICS=$PATH_TO_SOURCE/ckanext-googleanalytics
PATH_TO_TEMPLATE=$PATH_TO_SETUP/ckanext/raymond_theme
PATH_TO_HOME=$PATH_TO_TEMPLATE/templates/home
PATH_TO_DATAPUSHER=/usr/lib/ckan/datapusher/src/datapusher
PATH_TO_RECLINE=$PATH_TO_CKAN/ckanext/reclineview/theme/public/vendor/recline

#define variables
REDIS='/etc/redis/redis.conf'
APACHE_CONF='/etc/apache2/apache2.conf'
DUMP_FILE='/scripts/canned_dump.sql'
CONFIG='/etc/ckan/default/production.ini'
PYCSWGIT='https://github.com/geopython/pycsw.git'
CKAN_CONF='/etc/apache2/sites-available/ckan_default.conf'
CSW_FILE='/usr/lib/ckan/default/src/pycsw/csw.wsgi'
APACHE_WSGI='/etc/ckan/default/apache.wsgi'
PATH_TO_VENV='/usr/lib/ckan/default/bin/activate'
ALL_PATH='/scripts/all.sql'

USERNAME="ckan_default"
PASSWORD="ckan"
PORT=5431
HOST_ADD=146.64.19.119

#
#add auto install plugins
GITPLUGIN='dcat harvest googleanalytics spatial'
EASYPLUGIN='showcase geoview mapviews pdfview'
