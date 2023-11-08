<?php
session_start();
include_once '/p1mon/www/util/config_read.php';
include_once '/p1mon/www/util/p1mon-util.php';

$ERROR      = 'error';
$OK         = 'ok';
$AUTH_ERROR = 'auth_error';
$STARTED    = 'gestart';
$UNKNOWN    = 'onbekend';
$WAITING    = 'wacht op status rapport';

$arr_execoutput;
$exec_ret_value;
$export_id;

$arr = array('status_code' => $OK, 
             'status_text' => '', 
             'progress_pct' => 0,
             'commando_recieved' => ''
            );

if (!isset($_SESSION)){ 
	$arr['status_code']=$AUTH_ERROR;
    $arr['status_text']='session key ontbreekt.';
    echo json_encode($arr);
    return; 
}

if (!isset($_GET['exportid']) ) { // valid message syntax wise
    $arr['status_code']=$ERROR;
    $arr['status_text']='status="fatale fout: export id ontbreekt, gestopt"';
} else {
    $export_id =  clean($_GET['exportid']);
}

#print_r($_GET);

if ( isset($_GET['command']) ) {
    if ($_GET['command'] === 'STARTEXPORT') {

        $command = "/p1mon/scripts/P1SqlExport -e $export_id > /dev/null &";

        exec($command ,$arr_execoutput, $exec_ret_value );
        #print_r($arr_execoutput);
        $arr['status_text']  = $STARTED;
        $arr['status_code']  = $OK;
        $arr['progress_pct'] = 1;
        $arr['commando_recieved']='STARTEXPORT';
        echo json_encode($arr);
        return;
    }
    
    if ($_GET['command'] === 'GETSTATUS') {
        $filename = '/p1mon/mnt/ramdisk/p1mon-sql-export'.$export_id.'.status';
        if ( file_exists( $filename) ) {
            echo file_get_contents($filename, true);
            return;
        } else {
            $arr['status_code']  = $OK;
            $arr['progress_pct'] = '?';
            $arr['status_text']  = $WAITING;
        }
    }
    
    $arr['status_text']       = 'fatale fout: type commando onbekend, gestopt.';
    $arr['status_code']       = $ERROR;
    $arr['progress_pct']      = 0;
    $arr['commando_recieved'] =$UNKNOWN ; 
    echo json_encode($arr);   
}
?>