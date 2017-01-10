#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by: Derek Hohls
Created on: 2016-05-09
Purpose:
    CKAN deployment setup:-
        Create docker-compose.yml file; 
        Run docker-compose e.g. to Setup or Pull Docker images
"""
# lib
import argparse
import datetime
import json
import os
import pprint
import random
import string
from subprocess import Popen, PIPE
import sys
# third-party
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound, UndefinedError
# local
from utils import replace

CKAN_CONF_DIR = 'ckan/conf'


def cmdline(command):
    retcode = None
    try:
        process = Popen(command, bufsize=2048, executable="/bin/bash",
                        shell=True, stdout=None, stderr=None)
        while retcode == None:
            retcode = process.poll()
        if retcode < 0:
            sys.stderr.write("Child was terminated by signal:%s\n" % retcode)
        elif retcode > 0:
            sys.stderr.write("Child returned:%s\n" % retcode)
    except OSError, e:
        sys.stderr.write("Execution failed: %s\n" % e)
    return retcode


def parse_args():
    """Create the parser & parse the command-line args
    """
    parser = argparse.ArgumentParser(
        description="Command line options to control CKAN Dockers' deployment")
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='Show debug output')
    parser.add_argument('-v', '--version',
                        action='store_true',
                        help='Display version information')
    parser.add_argument('-k', '--ckan',
                        help='Name of CKAN .deb package '+\
                             '(default:python-ckan_2.5-trusty_amd64.deb)')
    parser.add_argument('-f', '--file',
                        help='Name of .yml template with compose settings'+\
                             ' (default:compose.yml)')
    parser.add_argument('-g', '--config',
                        help='Name of JSON config file (default: config.json)')
    parser.add_argument('-c', '--cmd',
                        help='Docker Compose command (default: up)')
    parser.add_argument('-x', '--exclude', nargs='*', 
                        help='List of containers to exclude' +
                             ' (ckan|postgresql|tomcat|solr)')
    return parser.parse_args()


def validate_config(config):
    """Check entries in the config dict"""
    # TODO - add in additional validation
    if not config.get("general"):
        config["general"] = {}
    if not config.get("postgresql"):
        config["postgresql"] = {}
    return config


def update_ckan(settings):
    """Update CKAN entries in the settings dict"""
    try:
        port = settings.get('solr', {}).get('port', '8980')
        host = settings.get('general', {}).get('host', 'localhost')
        settings["solr_url"] = \
            {"value": "solr_url = http://%s:%s/" % (host, port), "line": True}
        return settings
    except Exception, e:
        sys.stderr.write('Settings update error: %s\n' % e)
        sys.exit(1)


def update_postgresql(settings):
    """Create password entry in the settings dict, based on an ENV variable."""
    ENV_PASSWORD = 'CKAN_POSTGRESQL_PASSWORD'
    password = os.environ.get(ENV_PASSWORD, 'password')
    try:
        settings['postgresql']['password'] = password
        return settings
    except Exception, e:
        sys.stderr.write('Settings update error: %s\n' % e)
        sys.exit(1)


def extract_solr_files(settings):
    """Extract config files from solr to use for creating a custom CKAN core.
    Download and make other files available to Docker (e.g. via -v)
    
    Do a once-off startup of the solr Docker to make a copy of the needed files
    """
    SOURCE = '/opt/solr/server/solr/configsets/basic_configs/conf'
    JST_FILE = 'jts-1.13.jar'
    JTS_SRC = 'https://repo1.maven.org/maven2/com/vividsolutions/jts/1.13/%s'\
              % JST_FILE
    solr_image = settings.get("solr", {}).get('image', 'solr')
    test_file = os.path.join(CKAN_CONF_DIR, 'solrconfig.xml')
    if not os.path.exists(test_file):
        solr_name = 'solr_%s' % \
            ''.join(random.choice(string.lowercase) for i in range(6))
        try:
            command = 'docker run -d --name %s %s' % (solr_name, solr_image)
            cmdline(command)
            command = 'docker cp %s:%s %s' % (solr_name, SOURCE, CKAN_CONF_DIR)
            cmdline(command)
        except Exception, e:
            sys.stderr.write('Error running temporary solr Docker:%s\n' % e)
        finally:
            command = 'docker stop %s' % solr_name
            cmdline(command)
        if not os.path.exists(test_file):
            sys.stderr.write('Unable to extract config files from %s\n' % 
                             solr_image)
            sys.exit(1)
    # geometry search file
    if not os.path.exists(JST_FILE):
        command = 'wget %s' % JTS_SRC
        cmdline(command)
        if not os.path.exists(JST_FILE):
            sys.stderr.write('Unable to wget "%s" file from %s\n' % 
                             (JST_FILE, JST_SRC))
            sys.exit(1)


def extract_ckan_files(conf):
    """Download the CKAN deb and extract files from it."""
    ckan_deb = conf.ckan or 'python-ckan_2.5-trusty_amd64.deb'
    CKAN_URL = 'http://packaging.ckan.org'
    CKAN_SCHEMA = 'tmp/usr/lib/ckan/default/src/ckan/ckan/config/solr/schema.xml'
    if not os.path.exists(ckan_deb):
        command = 'wget %s/%s' % (CKAN_URL, ckan_deb)
        cmdline(command)
        if not os.path.exists(os.path.join('tmp', ckan_deb)):
            sys.stderr.write('Unable to download:`%s` from `%s`\n' % 
                             (ckan_deb, CKAN_URL))
            sys.exit(1)
    else:
        # extract .deb file
        command = 'dpkg -x %s tmp/' % ckan_deb
        cmdline(command)
        if not os.path.exists(CKAN_SCHEMA):
            sys.stderr.write('Unable to locate:`%s` in extracted `%s`\n' % 
                             (CKAN_SCHEMA, ckan_deb))
            sys.exit(1)
        # extract schema to conf directory
        destination = os.path.join(CKAN_CONF_DIR, 'schema.xml')
        command = 'cp %s %s' % (CKAN_SCHEMA, destination)
        cmdline(command)
        if not os.path.exists(destination):
            sys.stderr.write('Unable to copy `%s` to %s\n' % 
                             (CKAN_SCHEMA, destination))
            sys.exit(1)


def create_ckan_settings(settings):
    """Create a JSON file to store CKAN settings.
    
    This file will be utilised inside the container as part of CKAN startup.
    """
    CONFIG_FILE = 'configure.json'
    data = settings.get('ckan', {}).get('settings', {})
    user = settings.get('postgresql', {}).get('user', 'ckan_default')
    database = settings.get('postgresql', {}).get('database', 'ckan_default')
    datastore = settings.get('postgresql', {}).get('datastore', 'datastore_default')
    # password should already be acquired in create_template()
    password = settings.get('postgresql', {}).get('password', '')
    data['host'] = settings.get('general', {}).get('host', 'localhost')
    data['port'] = settings.get('postgresql', {}).get('port', '5431')
    data['sqlalchemy.url'] = {
        'value': 'sqlalchemy.url = postgresql://%s:%s@%s:%s/%s' % \
            (user, password, data['host'], data['port'], database),
        'line': True
    }

#Removed plugin defaults
##geojson_view
##geo_view

    data['ckan.plugins ='] = {
	'value':'ckan.plugins = showcase datastore datapusher harvest geonetwork_harvester datajson \
ckan_harvester csw_harvester googleanalytics resource_proxy recline_map_view pdf_view webpage_view \
geojson_view geo_view dcat dcat_rdf_harvester dcat_json_harvester recline_grid_view recline_graph_view \
dcat_json_interface raymond_theme viewhelpers dashboard_preview navigablemap datajson_harvest',
	'line' : True
    }

#Removed views defaults
##
    data['ckan.views.default_views ='] = {
	'value':'ckan.views.default_views = geo_view geojson_view',
	'line' : True
    }	
    	
    data['#email_to'] = {
	'value':'googleanalytics.id = UA-82750254-1',
	'line' : True
    }

    data['#error_email_from'] = {
	'value':'googleanalytics.account = %s' %data['host'],
	'line' : True
    }

    data['# ckan.template_footer_end ='] = {
	'value':'ckan.harvest.mq.type = redis\nckan.harvest.log_scope = 0\nckan.harvest.log_level = info',
	'line' : True
    }

#for openstreetMap
    data['#ckan.simple_search ='] = {
	'value':'ckanext.spatial.common_map.type = custom\n\
ckanext.spatial.common_map.custom.url =//{s}.tile.openstreetmap.org/{z}/{x}/{y}.png\n\
ckanext.spatial.common_map.subdomains = abc\n\
ckanext.spatial.harvest.xslt_html_content = ckanext.datagovtheme:templates/xslt/iso-details.xslt\n\
ckanext.spatial.harvest.xslt_html_content_original = ckanext.datagovtheme:templates/xslt/esri-iso-fgdc-details.xslt\n\
ckanext.spatial.common_map.attribution = Map tiles &amp; Data by \
<a href="http://openstreetmap.org">OpenStreetMap</a>, under \
<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC BY SA</a>.',
	'line' : True
    }	

    	
#for thunderforest
#    data['#ckan.simple_search ='] = {
#	'value':'ckanext.spatial.common_map.type = custom\n\
#ckanext.spatial.common_map.custom.url = http://tile.thunderforest.com/neighbourhood/{z}/{x}/{y}.png\n\
#ckanext.spatial.common_map.attribution = Maps <a \
#href="http://www.thunderforest.com">Thunderforest</a>, Data <a \
#href="http://www.openstreetmap.org/copyright">OpenStreetMap \
#contributors</a>',
#	'line' : True
#    }	


#for mapbox
#mapbox.satellite
#mapbox.mapbox-terrain-v2
#mapbox.mapbox-streets-v7
#"mapbox.streets";
#"mapbox.light";
#"mapbox.dark";
# "mapbox.satellite";
#"mapbox.streets-satellite";
#"mapbox.wheatpaste";
#"mapbox.streets-basic";
#"mapbox.comic";
#"mapbox.outdoors";
#"mapbox.run-bike-hike";
#"mapbox.pencil";
#"mapbox.pirates";
#"mapbox.emerald";
#"mapbox.high-contrast";

    data['#ckan.simple_search ='] = {
	'value':'ckanext.spatial.common_map.type = mapbox\n\
ckanext.spatial.common_map.mapbox.map_id = mapbox.streets-satellite\n\
ckanext.spatial.common_map.mapbox.access_token = \
pk.eyJ1IjoiaWN0NGVvZGV2IiwiYSI6ImNpdGs5NTVyaDAwNGQ0MnBkMWcwaXBjOGUifQ.DxdLOprbW9LGcMe1s0JprA',
	'line' : True
    }	

    data['ckan.views.default_views'] = {
	'value':'ckan.views.default_views = geo_view geojson_view wmts_view \
\nckanext.geoview.ol_viewer.formats = wms kml wfs geojson gml arcgis_rest gft',
	'line' : True
    }

#cartoDB setup
#    data['ckan.feeds.author_link'] = {
#	'value':'ckanext.cartodbmap.cartodb.username = ict4eodev\n\
#ckanext.cartodbmap.cartodb.key = c2dc358d573b5353274595e05052968f5e847b15',
#	'line' : True
#    }	


    data['#smtp.server'] = {
	'value':'googleanalytics.username = ict4eodev@gmail.com',
	'line' : True
    }

    data['#smtp.starttls'] = {
	'value':'googleanalytics.password = devict4eo',
	'line' : True
    }

    data['#smtp.user'] = {
	'value':'googleanalytics_resource_prefix = /downloads/',
	'line' : True
    }
   
    data['#smtp.password'] = {
	'value':'googleanalytics.domain = auto',
	'line' : True
    }

    data['#smtp.mail_from'] = {
	'value':'googleanalytics.track_events = true\ngoogleanalytics.show_downloads = true',
	'line' : True
    }

    data['ckan.auth.anon_create_dataset'] = {
	'value':'ckan.auth.anon_create_dataset = true',
	'line' : True
    }

    data['ckan.auth.create_unowned_dataset'] = {
	'value':'ckan.auth.create_unowned_dataset = true',
	'line' : True
    }

    data['ckan.auth.create_dataset_if_not_in_organization'] = {
	'value':'ckan.auth.create_dataset_if_not_in_organization = true',
	'line' : True
    }

    data['ckan.auth.user_create_groups'] = {
	'value':'ckan.auth.user_create_groups = true',
	'line' : True
    }

    data['ckan.auth.user_create_organizations'] = {
	'value':'ckan.auth.user_create_organizations = true',
	'line' : True
    }

    data['ckan.auth.create_user_via_api'] = {
	'value':'ckan.auth.create_user_via_api = true',
	'line' : True
    }

    data['ckan.datapusher.url ='] = {
	'value':'ckan.datapusher.url = http://%s:8808' %data['host'],
	'line' : True
    }

    data['ckan.cors.origin_allow_all'] = {
	'value':'ckan.cors.origin_allow_all = false',
	'line' : True
    }
 
    data['ckan.cors.origin_whitelist ='] = {
	'value':'ckan.cors.origin_whitelist = %s' %data['host'],
	'line' : True
    }		



    data['ckan.auth.create_user_via_web'] = {
	'value':'ckan.auth.create_user_via_web = true',
	'line' : True
    }	
    	

    data['ckan.storage_path ='] = {
	'value':'ckan.storage_path = /var/lib/ckan/default',
	'line' : True
    }

    data['#ckan.datastore.write_url'] = {
	'value':'ckan.datastore.write_url = postgresql://%s:ckan@%s:%s/%s'\
		 %(database,data['host'],data['port'],datastore),
	'line' : True
    }
    
    data['#ckan.datastore.read_url'] = {
	'value':'ckan.datastore.read_url = postgresql://%s:ckan@%s:%s/%s'\
		 %(datastore,data['host'],data['port'],datastore),
	'line' : True
    }
    

    solr_port = settings.get('solr', {}).get('port', '8983')
    # NOTE 1. NO `/` at end of solr_url !
    # NOTE 2. This is the URL for solr version 5.3+
    data['#solr_url'] = {
        'value': 'solr_url = http://%s:%s/solr/ckan' % (data['host'], solr_port),
        'line': True
    }
    try:
        with open("ckan/scripts/%s" % CONFIG_FILE, "w") as json_file:
            json_file.write(json.dumps(data))
    except Exception, e:
        sys.stderr.write('Unable to create `%s`: %s\n' % (CONFIG_FILE, e))
        sys.exit(1)


def create_template(file_template, config, fileout, cmds):
    """Fill in key variables into a template version of docker-compose file.
    
    Args:
        file_template: string
            name of template file with the .yml configuration
        config: string
            name of file containing JSON configuration variables
        fileout: string
            name of the output .yml file; used by Docker Compose
        cmds: dict
            additional configuration settings
    Returns:
        settings:
            JSON file contents; or empty dict, if error
    """
    settings = {}
    directory, template_file = os.path.split(file_template)
    loader = FileSystemLoader(directory)
    env = Environment(loader=loader)
    # load config variables
    try:
        with open(config) as json_file:
            _settings = json.load(json_file)
        settings = validate_config(_settings)
        # settings changes as required
        settings['general']['date'] = datetime.date.today().strftime("%Y-%m-%d")
        if cmds.exclude:
            if 'ckan' in cmds.exclude:
                settings['no_ckan'] = True
            if 'postgresql' in cmds.exclude:
                settings['no_postgresql'] = True
            if 'solr' in cmds.exclude:
                settings['no_solr'] = True
            if 'tomcat' in cmds.exclude:
                settings['no_tomcat'] = True
        settings = update_postgresql(settings)
        print("DEBUG: config/settings:\n%s" % settings)
    except (IOError, ValueError), e:
        sys.stderr.write("Please check config settings in %s: %s\n" % (config, e))
        sys.exit(1)
    try:
        # create output file from template & settings
        template = env.get_template(template_file)
        template.stream(**settings).dump(fileout)
    except TemplateNotFound, e:
        sys.stderr.write('Template file "{}" not found\n'.format(file_template))
        sys.exit(1)
    except UndefinedError, e:
        sys.stderr.write('Template error: %s\n' % e)
        sys.exit(1)
    return settings


def main(conf):
    """Core controller method.
    
    Args
        conf: dict
            configuration settings
    """
    cmd = conf.cmd or 'up'
    # setup the working environment
    if conf.version:
        print("CKAN Docker Setup version 1.0")
        sys.exit(1)
    if conf.debug:
        print("Debug is ON")
    conf_file = conf.file or 'compose.yml'
    fname = 'docker-compose.yml'
    config = conf.config or 'config.json'
    if cmd == 'down':
        # bypass further code for down
        command = 'docker-compose down'
        cmdline(command) 
    else:
        # create compose file AND update settings
        settings = create_template(conf_file, config, fname, cmds=conf)
        # startup solr once to extract key files
        extract_solr_files(settings)
        # access the full CKAN package to extract key files
        extract_ckan_files(conf)
        # create CKAN settings file (plus other data as needed)
        create_ckan_settings(settings)
        # execute compose file from the command line
        if cmd == 'up':
            cmd = 'up -d'
        command = 'docker-compose -f %s %s' % (fname, cmd)
        cmdline(command)


if __name__ == "__main__":
    conf = parse_args()
    main(conf)
    #os.system('docker stop ocims_ckan') 
    
   # exec_external_cmd('docker run -it --entrypoint=/bin/bash -p 81:80 -v '\
#		'~/dev/ocims/ckan/scripts/:/scripts ocims_ckan -s')
    #os.system('mkdir -p /logs && cd /scripts && python configure.py')
    #os.system('exit')

