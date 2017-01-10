#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by: Derek Hohls
Created on: 2016-05-11
Purpose:
    Setup CKAN configuration & services inside a Docker container
Notes:
    This setup requires a `configure.json` file with all necessary variables
"""
import datetime
import json
import logging
import os
from subprocess import Popen, PIPE
import sys
from shutil import move, copyfile
from tempfile import mkstemp

logger = logging.getLogger()
handler = logging.FileHandler('/logs/configure.log')
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

CONFIG = 'configure.json'
CURRENT = '/etc/ckan/default/production.ini'
CLEAN = '/etc/ckan/default/production.ini.CLEAN'
DIRECT = '/usr/lib/ckan/default'
DB_PASSWORD = os.environ.get('CKAN_POSTGRESQL_PASSWORD')


def exec_external_cmd(cmd_line):
    retcode = None
    try:
        process = Popen(cmd_line, bufsize=2048, executable="/bin/bash",
                        shell=True, stdout=None, stderr=None)
        while retcode == None:
            retcode = process.poll()
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal", retcode
        elif retcode > 0:
            print >>sys.stderr, "Child returned", retcode
    except OSError, e:
        print >>sys.stderr, "Execution failed:", e
    return retcode


def str_replace(file_path, pattern, substitution, whole=False, append=False,
                backup=False):
    """Search file for `pattern` string and add/replace it with `substitution`.
    
    Args:
        whole: boolean
            if True, replace the entire line containing `pattern` with the 
            `substitution` string;
            if False, only replace  `pattern` string with `substitution`
        append: boolean
            if True, append a line containing `pattern` to the end of file
        backup: boolean
            if True, make a copy of the file before changing it
    """
    result = False
    # create temp file
    fh, abs_path = mkstemp()
    with open(abs_path, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                if pattern in line:
		    if not append: 
                        if whole:  # replace whole line
                            new_file.write(substitution)
                            new_file.write('\n')
                        else:  # partial replacement
                            new_file.write(line.replace(pattern, substitution))
		    if append:
			if whole:
			    tr = '%s %s' %(line.replace('\n',''), substitution.split('=')[-1].strip())
			    new_file.write(tr.strip())
		            new_file.write('\n')	
                    result = True
                else:
                    new_file.write(line)

     	#if append and pattern in line:
	#	    if whole:	
	#	        tr = '%s %s' %(line, substitution.split('=')[-1].strip())
        #               new_file.write(tr)
           
    os.close(fh)
    if result:
        # create copy
        if backup:
            bak = '%s.BAK' % file_path
            os.remove(bak)
            copyfile(file_path, bak)
        else:
            # remove original file
            os.remove(file_path)
        # move new file
        move(abs_path, file_path)
    else:
        os.remove(abs_path)
    return result


def validate_config(config):
    # TODO - add in validation
    return config


def main():
    # ini file
    try:
        if os.path.exists(CURRENT):
            if not os.path.exists(CLEAN):
                copyfile(CURRENT, CLEAN)
    except Exception, e:
        logging.error('Unable to create backup of `%s`: %s' % (CURRENT,e))
        sys.exit(1)
    # load config settings
    try:
        with open(CONFIG) as json_file:
            _settings = json.load(json_file)
        settings = validate_config(_settings)
        settings['date'] = {'date': datetime.date.today().strftime("%Y-%m-%d")}
        logging.debug("settings:%s", settings)
    except (IOError, ValueError), e:
        logging.error("Please check config settings and `%s` file: %s" % (CONFIG, e))
        sys.exit(1)
    # implement setting changes
    print settings.keys()
    for key in settings.keys():
        print settings, type(settings)
        try:
            substitution = settings.get(key, {}).get('value')
            if substitution and not key == 'ckan.plugins =':
                whole = settings.get(key).get('line', True)
                append = settings.get(key).get('append', False)
                str_replace(CURRENT, key, substitution, whole=whole, append=append)
	    if  substitution and key == 'ckan.plugins =':
		whole = True
                append = True
                str_replace(CURRENT, key, substitution, whole=whole, append=append)	
		append = False
	    if  substitution and key == 'ckan.views.default_views':
		whole = True
                append = True
                str_replace(CURRENT, key, substitution, whole=whole, append=append)	
		append = False

        except AttributeError:
            pass  # ignore entries that are plain strings or Booleans
    # run setup; this runs as root user (no sudo needed)
    # DATABASE ================================================================
    # TODO - first check to see if tables and/or user is already created ...!
    pg_password = DB_PASSWORD or \
        settings.get('postgresql', {}).get('password', 'password')
    pg_db_ckan = settings.get('postgresql', {}).get('database', 'ckan_default')
    host = settings.get('general', {}).get('host', 'localhost')
    username = settings.get('postgresql', {}).get('user', 'ckan_default')
    logging.debug("DB:%s:%s:%s:%s" % ( pg_password, pg_db_ckan, host, username))
    logging.debug(settings)
    #create_user = "psql -h %s -U %s -d %s" % (host, username, pg_db_ckan)
    #exec_external_cmd(create_user)
    exec_external_cmd('chown -R www-data:www-data %s' % DIRECT)
    exec_external_cmd('ckan db init')
    # UPDATES  ================================================================
    exec_external_cmd('chown www-data:www-data %s' % CURRENT)
    # OTHER ===================================================================
    exec_external_cmd('service apache2 restart')
    exec_external_cmd('service nginx restart')
    logging.debug("TESTING: ALL OK")

if __name__ == "__main__":
    main()
    
"""
Test Inside Container:

docker run -it --entrypoint=/bin/bash -p 81:80 -v ~/dev/ocims/ckan/scripts/:/scripts ocims_ckan -s
mkdir -p /logs && cd /scripts && python configure.py
more /logs/configure.log
"""

