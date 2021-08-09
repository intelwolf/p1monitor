<?php

function config_read( $id ) {
    $dbstr  = '/p1mon/mnt/ramdisk/config.db';
    $sqlstr = "select id, parameter from config where id = " . $id;
    // read from database 
    try {
        $data = array();
        $db = new SQLite3( $dbstr, SQLITE3_OPEN_READONLY );
        $db -> busyTimeout( 300000 );  // fix for database locks, wait 300 sec = 5 min
        $result = $db->query($sqlstr);
        while ( $row = $result->fetchArray() ) {
            return $row[1];
            break;
        } 
        $db->close();
    } catch (Exception $e) {
        echo 'Exception: ',  $e->getMessage(), "\n";
    }
}
?>
