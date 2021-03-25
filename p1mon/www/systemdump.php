<?php
// Set the JSON header
header("Content-type: text/json");

#include '/p1mon/www/util/config_read.php';
include '/p1mon/www/util/p1mon-util.php';

# gebruik ./systemdump.php?dumpid=999
$OK             = "gereed";
$BUSY           = "bezig";
$ERROR          = "fout";
$DUMPNOTACTIVE  = "dump niet gestart";
        
$data[] = array(
            "status_code"     => $ERROR,
            "file_id"         => 0,
            "file_size"       => 0
               
);

if (!isset($_GET['dumpid']) ) { // invalid message syntax wise
    echo json_encode($data); 
    return;
} else {
    $data[0]['file_id'] = $_GET['dumpid'];
    $file = '/p1mon/www/download/full-p1monitor-dump'.$data[0]['file_id'].'.done';
    if (file_exists($file) == 1 ) {
        $data[0]['status_code']=$OK;
    } else {
        $dumpfile = '/tmp/full-p1monitor-dump'.$data[0]['file_id'].'.gz';
        if (file_exists($dumpfile ) == 1 ) {
            $data[0]['status_code']=$BUSY;
            $data[0]['file_size']=filesize($dumpfile);
        } else {
            $data[0]['status_code']=$DUMPNOTACTIVE;
        }
    }
}
echo json_encode($data); 
?>