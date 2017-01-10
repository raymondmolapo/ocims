#
# Dockerfile for CKAN
#

FROM ubuntu:14.04
MAINTAINER dhohls@csir.co.za

RUN sudo apt-get -y update && sudo apt-get -y upgrade
RUN sudo apt-get install -y wget nano subversion
RUN wget http://packaging.ckan.org/python-ckan_2.5-trusty_amd64.deb
RUN sudo apt-get install -y libpq5 supervisor python-dev libxml2-dev libxslt1-dev libgeos-c1 python-pip redis-server git expect apache2 libapache2-mod-wsgi nginx 
RUN sudo apt-get install -y curl zlib1g-dev
RUN sudo apt-get build-dep -y python-lxml
RUN sudo dpkg -i python-ckan_2.5-trusty_amd64.deb
RUN sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
RUN sudo apt-get -y update
RUN sudo apt-get install -y postgresql-client-9.4
COPY ./startup.sh /
RUN chmod +x /startup.sh
ENTRYPOINT ["/startup.sh"]

