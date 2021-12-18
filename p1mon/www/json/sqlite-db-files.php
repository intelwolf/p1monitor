<?php 
session_start(); #must be here for every page using login

// if the php session is not set, stop the script
if( isset( $_SESSION['session'] ) ){} else {
    die();
}

// this script generates list all sqlite database files in the ram folder
// and returns a JSON file of available databases.

// Set the JSON header
header("Content-type: text/json");

$dir = '/p1mon/mnt/ramdisk/';
$files_arr = array();

foreach ( glob( $dir."*.db" ) as $filename) {
    #echo basename( $filename );
    array_push( $files_arr, basename( $filename ) );
}

#print_r( $files_arr );
echo json_encode( $files_arr );
return;

?>
