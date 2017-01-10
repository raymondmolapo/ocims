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
PATH_TO_READBASE=$PATH_TO_DEFAULT/lib/python2.7/site-packages/ckanext/showcase/templates/package


#define variables
REDIS='/etc/redis/redis.conf'
APACHE_CONF='/etc/apache2/apache2.conf'
SSL_CONF='/etc/apache2/mods-available/ssl.conf'
DUMP_FILE='/scripts/canned_dump.sql'
CONFIG=${PATH_TO_ETC}/production.ini
PYCSWGIT='https://github.com/geopython/pycsw.git'
CKAN_CONF='/etc/apache2/sites-available/ckan_default.conf'
CSW_FILE=${PATH_TO_SOURCE}/pycsw/csw.wsgi
APACHE_WSGI=${PATH_TO_ETC}/apache.wsgi
PATH_TO_VENV=${PATH_TO_DEFAULT}/bin/activate
ALL_PATH='/scripts/all.sql'
READ_BASE=${PATH_TO_READBASE}/read_base.html
SCHEMA=$PATH_TO_CKAN/ckan/config/solr/schema.xml
EXTEND_MAP=$PATH_TO_CKAN/ckan/templates/package/read_base.html
SEARCH_WIDGET=$PATH_TO_CKAN/ckan/templates/package/search.html

#SA bounding box
BBOX="[[[12.22,-35.11],[12.22,-21.87], [34.72,-21.87], [34.72,-35.11], [12.22, -35.11]]]"

text='{% snippet "spatial\/snippets\/spatial_query.html", default_extent="{ \\\"type\\\":\\\"Polygon\\\", \\\"coordinates\\\":'${BBOX}'}" %}'


USERNAME="ckan_default"
PASSWORD="ckan"
PORT=5431
HOST_ADD=146.64.19.62

#
#add auto install plugins
GITPLUGIN='dcat harvest googleanalytics spatial issues archiver'
EASYPLUGIN='showcase geoview mapviews pdfview'
