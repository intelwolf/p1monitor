<?php 
session_start(); #must be here for every page using login
include_once '/p1mon/www/util/p1mon-util.php';

//if the php session is not set, stop the script
if( !isset( $_SESSION['session'] ) ){
    die();
    //echo 'die';
}

// use json/excel-file.php?filename=xxxx.db to set the config record
// use json/excel-file.php?filename= to erease the config record.
if (isset($_GET['filename']) ) { // valid message syntax wise
    $filename =  inputClean($_GET['filename']);

    // remove possible old file
    unlink('/p1mon/www/download/' . $filename . '.xlsx');

    updateConfigDb( "update config set parameter = '" . $filename . "' where ID = 172" );
    //echo $filename;

}

?>

