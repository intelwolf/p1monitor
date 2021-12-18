####################################################################
# shared lib for letsencrypt                                       #
####################################################################


BASE_DIR = '/etc/letsencrypt'

RESTORE_FOLDERS = [ 
    BASE_DIR + '/accounts',
    BASE_DIR + '/archive',
    BASE_DIR + '/live',
    BASE_DIR + '/renewal'
]
