#!/bin/bash


#get declared variable
#source variables.sh

su postgres sh -c "psql -c \"CREATE USER datastore_default NOSUPERUSER CREATEDB CREATEROLE INHERIT PASSWORD 'ckan';\""

su postgres sh -c "psql -c \"ALTER VIEW geography_columns OWNER TO ckan_default;\""
su postgres sh -c "psql -c \"ALTER VIEW spatial_ref_sys OWNER TO ckan_default;\""

su postgres sh -c "psql -c \"CREATE DATABASE ckan_default OWNER = ckan_default ENCODING 'UTF8';\""
su postgres sh -c "psql -c \"CREATE DATABASE datastore_default OWNER = ckan_default ENCODING 'UTF8';\""
su postgres sh -c "psql -c \"CREATE DATABASE pycsw OWNER = ckan_default ENCODING 'UTF8';\""
su postgres sh -c "psql -c \"CREATE EXTENSION postgis;\""

#CREATE USER ckan_default NOSUPERUSER CREATEDB CREATEROLE INHERIT PASSWORD 'ckan';
#CREATE USER datastore_default NOSUPERUSER CREATEDB CREATEROLE INHERIT PASSWORD 'ckan';

#CREATE DATABASE ckan_default OWNER = ckan_default ENCODING 'UTF8';
#CREATE DATABASE datastore_default OWNER = ckan_default ENCODING 'UTF8';
#CREATE DATABASE pycsw OWNER = ckan_default ENCODING 'UTF8';

#ALTER VIEW geography_columns OWNER TO ckan_default;
#ALTER VIEW spatial_ref_sys OWNER TO ckan_default;

#CREATE EXTENSION postgis;
