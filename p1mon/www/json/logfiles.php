<?php 
session_start(); #must be here for every page using login

// if the php session is not set, stop the script
if( isset( $_SESSION['session'] ) ){} else {
    die();
}

// this script generates a file in ram from available log files
// and returns a JSON file of available logfiles with stats.

// Set the JSON header
header("Content-type: text/json");

// create list with information 

$dir = '/var/log/p1monitor/';

// ##################################################
// list the records in the specified log file       #
// http://<ip>/json/logfiles.php?file=<file name    #
// without the path                                 #
// ##################################################
if ( isset(  $_GET['file'] ) ) {
    $file = $dir.$_GET['file'];

    //echo  $file."\n";
    $lines_arr = array();
    $handle    = fopen( $file, "r" );
    $id        = 1;

    if ($file = fopen( $file, "r" ) ) {
        while( !feof($file) ) {
            $line = fgets( $file );
            //echo $line;
            $parts = explode(" - ", $line );
            //var_dump( count($parts ) );
            //print_r ( $parts );

            if  ( count($parts ) ==  4 ) { // skip entry that has less then 4 parts (timestap, prgname, level, log entry ).
                // $parts index 1 is skipped it is the name of program.
                $tmp_arr = array( "id" => $id, "timestamp" => trim ( $parts[0] ), "level" => $parts[2], "line" => trim ( $parts[3] ) );
                $id++;
                array_push( $lines_arr, $tmp_arr );
            }
        }
        fclose($file);
    }
    //echo "done\n";
    echo json_encode( $lines_arr );
    return;
}


// ##################################################
// give parameter list to get available logfiles in #
// format name, size in byts and last date changed  #
// http://<ip>/json/logfiles.php?list               #
// ##################################################
if ( isset(  $_GET['list'] ) ) {
    $files_arr  = array();

    $id = 1;

    foreach ( glob( $dir."*.log" ) as $filename) {
        //echo "$filename size " . filesize( $filename ) . "\n";
        //echo "$filename was last modified: " . date ( "Y-m-d H:i:s", filemtime($filename) );
        //echo basename( $filename );
        
        if ( filesize( $filename ) > 0 ) { // when the file is empty, skip it.
            $tmp_arr = array( "id" => $id, "filename" => basename( $filename ), "filesize" => filesize( $filename ), "timestamp" => date( "Y-m-d H:i:s", filemtime($filename) ) );
            $id++;
            array_push( $files_arr, $tmp_arr);
        }

    }

    //print_r( $files_arr );
    echo json_encode( $files_arr );
    return;
}

?>
