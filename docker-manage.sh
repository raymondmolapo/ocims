#!/bin/bash


source variables.sh

#set up pgpass for postgres docker

cat << EOF > ~/.pgpass
$HOST_ADD:$PORT:$USERNAME:$PASSWORD
EOF

#make dbinit script executable
chmod +x ~/dev/ocims/dbinit.sh

#make ckan_default supersuer
#docker exec -it $(docker ps | grep cheewai | awk -F' ' '{print $NF}') \
#bash -c "su postgres sh -c 'psql -c \"ALTER USER $USERNAME WITH SUPERUSER;\" '"

#copy dbinit to container
docker cp ~/dev/ocims/dbinit.sh \
$(docker ps -a | grep raymondmolapo | awk -F' ' '{print $NF}'):/dbinit.sh

#make ckan_default supersuer
docker exec -it $(docker ps | grep raymondmolapo | awk -F' ' '{print $NF}') \
bash -c "./dbinit.sh"


#make insteract script executable
chmod +x ~/dev/ocims/ckan/scripts/interact.sh

#create template - call interact.sh
docker exec $(docker ps | grep ocims_ckan | awk -F' ' '{print $1}') \
bash -c "cd $PATH_TO_SOURCE; ./interact.sh"

#register template - run setup script
docker exec $(docker ps | grep ocims_ckan | awk -F' ' '{print $1}') \
bash -c "cd $PATH_TO_SETUP; source $PATH_TO_VENV; python setup.py develop"

# \
#git clone https://github.com/GSA/ckanext-geodatagov.git; \
#cd ckanext-geodatagov; python setup.py install; sed -i '1,7d' pip-requirements.txt; \
#pip install -r pip-requirements.txt"


#install plugins
for plugin in $GITPLUGIN; do

docker exec $(docker ps | grep ocims_ckan | awk -F' ' '{print $1}') \
bash -c "cd $PATH_TO_DEFAULT; source $PATH_TO_VENV; pip install -e  git+https://github.com/ckan/ckanext-$plugin.git#egg=ckanext-$plugin";

docker exec $(docker ps | grep ocims_ckan | awk -F' ' '{print $1}') \
bash -c "cd $PATH_TO_DEFAULT; source $PATH_TO_VENV; pip install -r src/ckanext-$plugin/requirements.txt";

docker exec $(docker ps | grep ocims_ckan | awk -F' ' '{print $1}') \
bash -c "cd $PATH_TO_DEFAULT; source $PATH_TO_VENV; pip install -r src/ckanext-$plugin/pip-requirements.txt";


done


for plugs in $EASYPLUGIN; do
docker exec $(docker ps | grep ocims_ckan | awk -F' ' '{print $1}') \
bash -c "cd $PATH_TO_DEFAULT; source $PATH_TO_VENV; pip install ckanext-$plugs";
done

#git clone https://github.com/bopen/ckanext-mapsearch.git; \
#cd ckanext-mapsearch/ckanext-mapsearch; python setup.py install; cd ..; \

docker exec $(docker ps | grep ocims_ckan | awk -F' ' '{print $1}') \
bash -c "cd $PATH_TO_SOURCE; source $PATH_TO_VENV; \
git clone https://github.com/conwetlab/ckanext-datarequests.git; \
cd ckanext-datarequests; python setup.py install; cd .. ; \
git clone https://github.com/ontodia/ckanext-discourse; \
cd ckanext-discourse; python setup.py develop; cd .. ; \
git clone https://github.com/ckan/ckanext-viewhelpers.git; \
cd ckanext-viewhelpers; python setup.py install; cd .. ; \
git clone https://github.com/HHS/ckanext-datajson.git; \
cd ckanext-datajson; pip install -r pip-requirements.txt; python setup.py develop; \
sed -i '4s/.*/\nimport ckanext/' $APACHE_WSGI;cd ..; \
git clone https://github.com/ckan/datapusher.git; \
cd datapusher; pip install -r requirements.txt; pip install -e . ;cd ..; \
sed -i 's/8800/8808/g' $PATH_TO_DATAPUSHER/deployment/datapusher_settings.py; \
git clone https://github.com/geosolutions-it/ckanext-geonetwork.git; \
cd ckanext-geonetwork; python setup.py develop; cd .. ; \
git clone https://github.com/ckan/ckanext-dashboard.git; \
cd ckanext-dashboard; python setup.py install; cd .. ; \
git clone https://github.com/ckan/ckanext-mapviews.git; \
cd ckanext-mapviews; python setup.py install;cd ..; \
git clone https://github.com/Ontodia/ckanext-cartodbmap.git; \
cd ckanext-cartodbmap; python setup.py develop; pip install -r dev-requirements.txt; cd ..; \
pip install -e git+http://github.com/okfn/ckanext-qa.git#egg=ckanext-qa; \
pip install -e git+http://github.com/datagovuk/ckanext-report.git#egg=ckanext-report; \
pip install -r src/ckanext-qa/requirements.txt; "

#sed -i '1,7d' pip-requirements.txt; \

#nohup python datapusher/main.py deployment/datapusher_settings.py > log.txt 2>&1 </dev/null &; cd .. ; \

#docker exec $(docker ps | grep ocims_ckan | awk -F' ' '{print $1}') \
#bash -c "cd $PATH_TO_SOURCE; source $PATH_TO_VENV; \
#git clone https://github.com/geosolutions-it/ckanext-geonetwork.git; \
#cd ckanext-geonetwork; python setup.py develop"

docker exec $(docker ps | grep ocims_ckan | awk -F' ' '{print $1}') \
bash -c "cd $PATH_TO_DEFAULT; source $PATH_TO_VENV; pip install -r src/ckanext-dcat/requirements.txt";

docker exec $(docker ps | grep ocims_ckan | awk -F' ' '{print $1}') \
bash -c "cd $PATH_TO_SOURCE; source $PATH_TO_VENV; git clone $PYCSWGIT; cd pycsw; \
git checkout 1.10.3; pip install -e .; python setup.py build; python setup.py install; \
cp default-sample.cfg default.cfg; \
sudo ln -s $PATH_TO_SOURCE/pycsw/default.cfg $PATH_TO_ETC/pycsw.cfg; \
sed -i '0,/var/ s/var/usr/g; 0,/www/ s/www/lib\/ckan\/default/g' default.cfg; \
sed -i 's/^database/#database/g; s/localhost/$HOST_ADD:$PORT/g; s/password/$PASSWORD/g; \
s/username/$USERNAME/g; s/#database=p/database=p/g' default.cfg; \
cd $PATH_TO_SOURCE/ckanext-spatial; source $PATH_TO_VENV; paster ckan-pycsw setup -p $PATH_TO_ETC/pycsw.cfg; \
sed -i '7s/.*/    WSGIScriptAlias \/csw \/usr\/lib\/ckan\/default\/src\/pycsw\/csw.wsgi\n/' $CKAN_CONF; \
sed -i '58s/.*/\nactivate_this = os.path.join(\"\/usr\/lib\/ckan\/default\/bin\/activate_this.py\")/' $CSW_FILE; \
sed -i '60s/.*/execfile(activate_this, {\"__file__\":activate_this})\n/' $CSW_FILE; \
sed -i '62s/.*/app_path = os.path.dirname(__file__)\n/' $CSW_FILE; \
sed -i 's/8000/8085/g' $CSW_FILE; \
sed -i \"21s/.*/  {{ h.build_nav_icon('issues_dataset\', _('Issues'), dataset_id=pkg.name) }}/\" $EXTEND_MAP; \
sed -i '23s/.*/{% endblock %}\n/' $EXTEND_MAP; \
sed -i 's/4096/32768/g; s/1024\**2/1024\**4/g' $CONTROL; \
sed -i 's/<types>/<types>\
    <!-- ... --> \
    <fieldType name=\"location_rpt\" class=\"solr.SpatialRecursivePrefixTreeFieldType\" \
    spatialContextFactory=\"com.spatial4j.core.context.jts.JtsSpatialContextFactory\" \
    autoIndex=\"true\" \
    distErrPct=\"0.025\" \
    maxDistErr=\"0.000009\" \
    distanceUnits=\"degrees\"\/>/g' $SCHEMA; \
sed -i 's/<fields>/<fields>\
    <!-- ... -->\
    <field name=\"spatial_geom\"  type=\"location_rpt\" indexed=\"true\" stored=\"true\" multiValued=\"true\" \/>/g' $SCHEMA;\
sed -i ':a;\$!N;1,10ba;P;\$d;D' $SEARCH_WIDGET; \
sed -i '72s/.*/{% block secondary_content %}\n\n   $text\n\n{% endblock %}\n/g' $SEARCH_WIDGET;"

#sed -i '72s/.*/$text/g' $SEARCH_WIDGET;
#sed -i ':a;$!N;1,10ba;P;$d;D' $SEARCH_WIDGET; \
#sed -i '8s/.*/    Redirect permanent \/ https:\/\/$HOST_ADD\n/' $CKAN_CONF; \

#cd $PATH_TO_SOURCE/pycsw; source $PATH_TO_VENV; nohup python csw.wsgi > harvester.log 2>&1 </dev/null &"

#cd $PATH_TO_SOURCE/pycsw; source $PATH_TO_VENV; nohup python csw.wsgi > harvester.log 2>&1 </dev/null &"

#paster ckan-pycsw setup -p $PATH_TO_ETC/pycsw.cfg; \

docker exec $(docker ps | grep ocims_ckan | awk -F' ' '{print $1}') \
bash -c "cd /scripts/; python configure.py; sudo service apache2 restart "

docker cp ~/dev/ocims/docker-data/templates \
$(docker ps -a | grep "ocims_ckan" | awk -F' ' '{print $NF}'):\
$PATH_TO_TEMPLATE

docker cp ~/dev/ocims/docker-data/recline.js \
$(docker ps -a | grep "ocims_ckan" | awk -F' ' '{print $NF}'):\
$PATH_TO_RECLINE

docker cp ~/dev/ocims/docker-data/layout1.html \
$(docker ps -a | grep "ocims_ckan" | awk -F' ' '{print $NF}'):\
$PATH_TO_HOME

docker cp ~/dev/ocims/docker-data/default \
$(docker ps -a | grep "ocims_ckan" | awk -F' ' '{print $NF}'):\
$PATH_TO_VAR

docker exec $(docker ps | grep ocims_ckan | awk -F' ' '{print $1}') \
bash -c "chown -R www-data $PATH_TO_VAR; service redis-server restart"

docker cp ~/dev/ocims/docker-data/public \
$(docker ps -a | grep "ocims_ckan" | awk -F' ' '{print $NF}'):\
$PATH_TO_TEMPLATE

docker cp ~/dev/ocims/docker-data/plugin.py \
$(docker ps -a | grep "ocims_ckan" | awk -F' ' '{print $NF}'):\
$PATH_TO_TEMPLATE/plugin.py

#docker exec $(docker ps | grep ocims_ckan | awk -F' ' '{print $1}') \
#bash -c "ckan db init ;ckan db clean -c $CONFIG; ckan db load -c $CONFIG $ALL_PATH"

docker exec $(docker ps | grep ocims_ckan | awk -F' ' '{print $1}') bash -c "source $PATH_TO_VENV;\
nohup python $PATH_TO_DATAPUSHER/datapusher/main.py $PATH_TO_DATAPUSHER/deployment/datapusher_settings.py \
> harvester.log 2>&1 </dev/null &"

docker exec $(docker ps | grep ocims_ckan | awk -F' ' '{print $1}') bash -c "cd $PATH_TO_SOURCE/pycsw; \
source $PATH_TO_VENV; nohup python csw.wsgi > harvester.log 2>&1 </dev/null &"


docker exec $(docker ps | grep ocims_ckan | awk -F' ' '{print $1}') \
bash -c "cd $PATH_TO_DEFAULT; source $PATH_TO_VENV; \
paster --plugin=ckanext-archiver archiver init -c $CONFIG; \
paster --plugin=ckanext-report report initdb -c $CONFIG; \
paster --plugin=ckanext-harvest harvester initdb -c $CONFIG; \
paster --plugin=ckanext-spatial spatial initdb -c $CONFIG; \
paster --plugin=ckanext-issues issues init_db -c $CONFIG; \
paster --plugin=ckanext-qa qa init -c $CONFIG; \
pip install factory-boy mock;sed -i 's/^bind/#bind/g' $REDIS;
sed -i 's/#<Directory \/srv\/>/<IfModule mod_headers.c>\n\
\tHeader always append X-Frame-Options SAMEORIGIN\n\
\tHeader set X-Content-Type-Options \"nosniff\"\n\
\tHeader set Content-Security-Policy \"frame-ancestors \"self\";\"\n\
\tHeader set Strict-Transport-Security \"max-age=31536000\"\n\
\tTraceEnable off\n<\/IfModule>\n/g' $APACHE_CONF; \
sed -i 's/HIGH:MEDIUM:!aNULL:!MD5/SSLCipherSuite HIGH:!MD5:!RC4:!CBC:!DES:!3DES/g' $SSL_CONF; \
nohup paster --plugin=ckanext-archiver celeryd2 run -c $CONFIG > celery.log 2>&1 </dev/null &";



#pip install -e git+http://github.com/ckan/ckanext-issues

#> log.txt 2>&1 </dev/null
# > harvester.log 2>&1 </dev/null 
#cd $PATH_TO_SOURCE/pycsw; nohup python csw.wsgi &



