####################################################################
# shared lib for nginx data and functions                          #
# !!! TODO migrate other scripts to this lib.                      #
####################################################################
import const

P80FILE         = const.DIR_NGINX_BASE + '/sites-enabled/p1mon_80'
P443FILE        = const.DIR_NGINX_BASE + '/sites-enabled/p1mon_443'
APIKEYFILE      = const.DIR_NGINX_BASE + '/conf.d/api-tokens.conf'
DIVMAPSFILE     = const.DIR_NGINX_BASE + '/conf.d/divmaps.conf'
BASE_DIR        = const.DIR_NGINX_BASE


RESTORE_FOLDERS = [ 
    BASE_DIR + '/sites-enabled',
    BASE_DIR + '/conf.d'
]