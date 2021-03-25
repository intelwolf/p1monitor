<?php
// Set the JSON header
header("Content-type: text/json");

if (isset($_GET['fileid']) ) { // valid message syntax wise
     $file_id = urldecode( $_GET['fileid'] );
     #error_log("P1 DEBUG (ID=0001) -> ".$file_id , 0);
     $file = '/p1mon/mnt/ramdisk/'.$file_id;

     if (file_exists($file) == 1 ) {
        echo file_get_contents($file , true); 
        #echo '{"records_total": 92019, "records_processed_nok": 0, "status_text": "klaar", "records_processed_ok": 92019, "export_timestamp": "2018-09-01 13:53:40"}';
     } else {
         echo "";
     }
}
?>