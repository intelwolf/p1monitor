
<?php

    $command = '/p1mon/scripts/P1DropBoxAuth -u';
    exec( $command ,$arr_execoutput, $exec_ret_value );
    echo $arr_execoutput[0];

    chmod( "/var/log/p1monitor/P1DropBoxAuth.log", 0664 ); # make sure p1mon / www-data group user has access.
    chgrp( "/var/log/p1monitor/P1DropBoxAuth.log", "p1mon" );

    $url = "Location: ".$arr_execoutput[0];

    
    #echo $url;
    header ( $url ); /* Redirect browser */
    #header("Location: https://www.dropbox.com/oauth2/authorize?response_type=code&client_id=sefdetwey2877wd");
    #exit();
?>
