#!/bin/bash

psql -U postgres << EOF

CREATE USER datastore_default NOSUPERUSER CREATEDB CREATEROLE INHERIT PASSWORD 'ckan';
ALTER VIEW geography_columns OWNER TO ckan_default;
ALTER VIEW spatial_ref_sys OWNER TO ckan_default;
CREATE DATABASE ckan_default OWNER = ckan_default ENCODING 'UTF8';
CREATE DATABASE datastore_default OWNER = ckan_default ENCODING 'UTF8';
CREATE DATABASE pycsw OWNER = ckan_default ENCODING 'UTF8';
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
\c ckan_default;
CREATE EXTENSION postgis;
ALTER DATABASE ckan_default SET search_path= public, postgis, postgis_topology;

EOF
