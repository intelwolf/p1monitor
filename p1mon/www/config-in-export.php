<?php
session_start(); #must be here for every page using login
include_once '/p1mon/www/util/auto_logout.php';
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php';
include_once '/p1mon/www/util/menu_control.php';
include_once '/p1mon/www/util/p1mon-password.php';
include_once '/p1mon/www/util/config_buttons.php';
include_once '/p1mon/www/util/config_read.php';
include_once '/p1mon/www/util/textlib.php';
include_once '/p1mon/www/util/div_err_succes.php';
include_once '/p1mon/www/util/pageclock.php';

loginInit();
passwordSessionLogoutCheck();

$noInetCheck = isInternetIPAllowed();
$localip     = validLocalIpAdress(getClientIP());
//$localip        = False;
//$noInetCheck    = False;
if( $localip == False ){ 
        if( $noInetCheck == False ) {
            die();
        }
}

#print_r($_POST);
$showStatusOutput = 0;
if ( isset($_POST["upgrade_button"]) ) { 
    # remove status file
    unlink('/p1mon/mnt/ramdisk/upgrade-assist.status');
    writeSemaphoreFile('upgrade_assist');
    $showStatusOutput = 1;
}

if ( isset($_POST["import"]) ) { 
    
            if ( strlen($_POST["import"]) > 1 ) { // we have a file, now check it
                
                    #echo ("$showStatusOutput=".$showStatusOutput);

                    #remove old status file 
                    unlink('/p1mon/mnt/ramdisk/sqlimport.status');

                    $file_tmp = '/p1mon/var/tmp/'.$_POST["import"];
                    $info = pathinfo($file_tmp);
                    $file_name = basename($file_tmp,'.'.$info['extension']);

                    #error_log("P1 DEBUG (in en export) ".$file_name , 0);
                    #echo($file_name);

                    $date = date_create();
                    $random_number_str =  date_timestamp_get($date) . strval(mt_rand (100,999));
                    $sqlImportFilename = '/p1mon/var/tmp/import-' . $random_number_str . ".zip";
                    #echo $sqlImportFilename;
                    
                    # shows the dialog
                    setcookie("sqlImportIsActive", basename($sqlImportFilename), time()+1200); //20 min 

                    rename( $file_tmp, $sqlImportFilename );
                    chmod( $sqlImportFilename, 0770 );
                    chgrp( $sqlImportFilename,'p1mon' );
                    rmdir( '/p1mon/var/tmp/'.trim($_POST["importdir"]) );

                    updateConfigDb("update config set parameter = '". $sqlImportFilename . "' where ID = 138");
                    updateConfigDb("update config set parameter = '" . $random_number_str . "' where ID = 137");

            }
}

?>
<!doctype html>
<html lang="nl">
<head>
<title>In en Export</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css" />
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/p1mon-util.js"></script>
<script src="./js/download2.js"></script>
<script src="/fine-uploader/fine-uploader.min.js"></script>
<script type="text/template" id="qq-template">
    <div class="qq-uploader-selector qq-uploader">
        <div class="qq-upload-button-selector qq-upload-button">
            <div>
                <button class="input-2 but-1 float-left" id="sqlimport">
                    <i class="color-menu fas fa-3x fa-download"></i><br>
                    <span class="color-menu text-7">import</span>
                </button>
            </div>
        </div>
        <ul class="qq-upload-list-selector" style="display: none">
            <div></div>
        </ul>
    </div>
    
</script>
</head>
<body>

    <?php page_header();?>
        
    <div class="top-wrapper-2">
        <div class="content-wrapper pad-13">
                <!-- header 2 -->
            <?php pageclock(); ?>
        </div>
            <?php config_buttons(1);?>
        </div> <!-- end top wrapper-2 -->
        
        <div class="mid-section">
            <div class="left-wrapper-config"> <!-- left block -->
                <?php menu_control(4);?>
            </div>
            
            <div id="right-wrapper-config"> <!-- right block -->
            <!-- inner block right part of screen -->
                <div id="right-wrapper-config-left-3">
                    <!-- start of content -->
                    <form name="formvalues" id="formvalues" method="POST">
                        <div class="frame-4-top">
                            <span class="text-15">export database data</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left pos-32">
                                <div class="float-left margin-3">
                                    <button class="input-2 but-1 cursor-pointer" id="sqlexport_button" name="sqlexport_button">
                                        <i class="color-menu fas fa-3x fa-upload"></i>
                                        <span class="color-menu text-7">export</span>
                                    </button>    
                                </div>
                            </div>    
                        </div>
                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15">importeer database data</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left pos-32">
                                <div class="float-left margin-3">    
                                    <div id="uploader"></div>
                                </div>
                            </div>    
                        </div>
                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15">Upgrade assistent</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left pos-32">
                                <div class="float-left margin-3">
                                    <button class="input-2 but-1 cursor-pointer" id="upgrade_button" name="upgrade_button" value="start">
                                        <i class="color-menu fas fa-3x fa-arrow-alt-circle-up"></i>
                                        <span class="color-menu text-7">Upgrade</span>
                                    </button>    
                                </div>
                            </div>    
                        </div>
                        <p></p>

                    <!-- end pay load area -->    
                    <!-- placeholder variables for session termination -->
                    <input type="hidden" name="logout" id="logout" value="">
                    <input type="hidden" name="export" id="export" value="">
                    <input type="hidden" name="import" id="import" value="">
                    <input type="hidden" name="importdir" id="importdir" value="">
                    <!-- <input type="hidden" name="import_file" id="import_value" value=""> -->
                    
                    </form>
                    </div>
                        <div id="right-wrapper-config-right-3">
                            <div class="frame-4-top">
                                <span class="text-15">hulp</span>
                            </div>
                            <div class="frame-4-bot text-10">
                                <?php echo strIdx(7);?>
                                <br><br>
                                <?php echo strIdx( 37 );?>
                            </div>
                        </div>
            </div>    
            <!-- end inner block right part of screen -->
    </div>
    

<div id="export_sql_msg">
    <div class='close_button' id="export_sql_msg_close">
        <i class="color-select fas fa-times-circle fa-2x" aria-hidden="true"></i>
    </div>
    <i class="fas fa-fw fa-1x fa-upload">&nbsp;&nbsp;</i>SQL gegevens exporteren&nbsp;
    <i id="sql_export_spinner" class="fas fa-spinner fa-1x fa-fw"></i>
    <br><div id="sql_export_pct" >0%</div>
    <div id="sql_export_dl_link" ><br><a id='sql_export_dl_href' href="">Als de download niet start klik dan hier</a></div>
</div>    

<div id="import_sql_message"> <!-- new  version 1.2.0 -->
     <div class='close_button' id="import_sql_msg_close">
        <i class="color-select fas fa-times-circle fa-2x" aria-hidden="true"></i>
    </div>
    <span class="text-15">import status</span>
    <div id="scroll_window" class="text-29" >
        Even geduld aub.
    </div>
</div> 


<div id="upgrade_status" class="pos-45" style="display: none" >
    <div class='close_button-2' id="assist_logging_close">
        <i class="color-select fas fa-times-circle" data-fa-transform="grow-6" aria-hidden="true"></i>
    </div>
    <div class="frame-4-top">
        <span class="text-15">Upgrade logging</span>
            </div>
                <div class="frame-4-bot">
                    <div id="upgrade_assist_logging" class="text-9">

                    </div>
                </div>
</div>

<script>    
var sqlImportFilename = '';
var sqlExportChecking = false;
var initloadtimer;

sqlImportIsActive=getCookie("sqlImportIsActive"); 

$(function() {
    centerPosition('#import_sql_message');
    centerPosition('#export_sql_msg');
    centerPosition('#upgrade_status');
    hideStuff('sql_export_dl_link');
    LoadData(); 
    if (sqlImportIsActive !== undefined) {
        showStuff('import_sql_message');
    }
});

$('#sqlexport_button').click(function(event) {
    hideStuff('sql_export_dl_link');
    event.preventDefault();    
    exportID = Date.now()+'.'+randomIntFromInterval(100,999);
    startSqlExport(exportID,'STARTEXPORT')
});

$('#export_sql_msg_close').click(function() {    
   hideStuff('export_sql_msg');
}); 

$('#import_sql_msg_close').click(function() {    
   hideStuff('import_sql_message');
   sqlImportIsActive = undefined;
   document.cookie = "sqlImportIsActive=''; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}); 

$('#assist_logging_close').click(function() {    
   hideStuff('upgrade_status');
}); 

function LoadData() {
    
    clearTimeout(initloadtimer);
    
    readCounterResetLogging();

    if (sqlExportChecking === true)
        startSqlExport(exportID,'GETSTATUS'); 
    
    if (sqlImportIsActive !== undefined ) {
        readSqlImportStatusLogging();
    }

    initloadtimer = setInterval(function(){LoadData();}, 1000);

} 

function getCookie(name) {
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length == 2) return parts.pop().split(";").shift();
}

function autoDownLoad(filename){
    var x=new XMLHttpRequest();
    var dl_filename = filename.split('/').pop();
    x.open("GET", filename, true);
    x.responseType = 'blob';
    x.onload=function(e){download(x.response, dl_filename, "application/zip" ); }
    x.send();
} 

function startSqlExport(exp_id, command){ 
    $.getJSON( "./sqlexport.php?exportid=" + exp_id + '&command=' + command, function( d ) {
        
        try {
        //console.log("sqlexport return ="+data);
        //var d = JSON.parse(data);
       
        if ( d['status_code'] === 'auth_error' ) {
            hideStuff('export_sql_msg');
            return;
        }
        
        if ( d['status_text'] === 'gestart' ) {
            $('#sql_export_spinner').addClass("fa-pulse");
            sqlExportChecking = true; // polling check for updates
            showStuff('export_sql_msg');
            //console.log("gestart");
        }
         
        $('#sql_export_pct').html(d['progress_pct']+'%')
         
        if ( d['status_code'] === 'klaar' ) {
            sqlExportChecking = false;
            $('#sql_export_spinner').removeClass("fa-pulse");
            var dl_link = './download/p1mon-sql-export'+exportID+'.zip';
            autoDownLoad(dl_link);
            $('#sql_export_dl_href').attr("href", dl_link);
            setTimeout(function(){
                hideStuff('sql_export_spinner');
                showStuff('sql_export_dl_link');
                showStuff('export_sql_msg_close');
            },1000);
            //setTimeout(function(){hideStuff('export_sql_msg');},2000);
        }
        
     } catch(err) {    
         console.log("startSqlExport error."+err);
        //return null;
     }       

    });
}


function readSqlImportStatusLogging(){ 
    $.get( "/txt/txt-sql-import-status.php", function( response, status, xhr ) {
        
        if ( status == "error" ) {
            $("#scroll_window").html('SQL import log data niet beschikbaar.');
        }
        
        if ( response.length > 0 ) {
            //console.log("update =" + response.length )
            $('#scroll_window').html( response );
            // keep scroll window scrolled down.
            $('#scroll_window').scrollTop($('#scroll_window')[0].scrollHeight);
        } else {
            $('#scroll_window').html( "<b>Even geduld aub, gegevens worden verwerkt.</b><br>" );
        }

    });
}

function readCounterResetLogging(){ 

   $.get( "/txt/txt-upgrade-status.php", function( response, status, xhr ) {
        if ( status == "error" ) {
            $("#upgrade_assist_logging").html('Upgrade data niet beschikbaar.');
        }
        if ( response.length > 0 ) {
            $('#upgrade_assist_logging').html( response );
        } else {
            $('#upgrade_assist_logging').html( "<b>Even geduld aub, gegevens worden verwerkt.</b><br>" );
        }
    }); 
}
</script>

<script>
    var uploader = new qq.FineUploader({
        element: document.getElementById("uploader"),
        debug: false,
        request: {
            endpoint: "/fine-uploader/endpoint.php"
        },
        deleteFile: {
            enabled: false,
            endpoint: "/fine-uploader/endpoint.php"
        },
        chunking: {
            enabled: true,
            concurrent: {
                enabled: true
            },
            success: {
                endpoint: "/fine-uploader/endpoint.php?done"
            }
        },
        resume: {
            enabled: true
        },
        retry: {
            enableAuto: true,
            showButton: true
        },
        callbacks: {
            onComplete: function(id, fileName, responseJSON) {
                if (responseJSON.success) {
                    document.formvalues.import.value = this.getUuid (id)+'/'+fileName;
                    document.formvalues.importdir.value = this.getUuid (id);
                    document.forms["formvalues"].submit();
                    }
                }
            },
        validation: {
            allowedExtensions: ['zip'],
        },
    });
</script>
<?php 

if ( $showStatusOutput == 1 ) {
 echo "<script>showStuff('upgrade_status');</script>";
}

echo autoLogout(); 
?>
</body>
</html>
