<?php 

// update de sqllite DB config met de sql
// fout is een waarde groter dan 1
function updateStatusDb($sql){
    $dbstr = '/p1mon/mnt/ramdisk/status.db'; 
    $r = 0;	
    try {
        $db = new SQLite3( $dbstr, SQLITE3_OPEN_READWRITE );
        $db -> busyTimeout( 300000 );  // fix for database locks, wait 300 sec = 5 min
        $db->exec( $sql );
        if ( $db->lastErrorCode() > 0 ) $r = 1;	
        $db->close();
    } catch ( Exception $e ) {
        $r=1;
    }
    return $r;
}
?>