#############################################
# solar edge site id dict                   #
#############################################
solaredge_site_config = {
    'ID'          :int(0),  # SITE ID
    'DB_INDEX'    :int(0),  # Site id base number used in the SQL database every site has a base number starting from 20 to 90 supporting 8 sites.
    'DB_DELETE'   :False,   # Flag to remove data from the database (true means purge database)
    'SITE_ACTIVE' :False,   # If the site is active an will be processed into the database
    'START_DATE'  :'',      # The energy production start date of the site.
    'END_DATE'    :'',      # The energy production end date of the site.
}
