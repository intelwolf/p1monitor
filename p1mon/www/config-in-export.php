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

$err_cnt = -1;

#print_r($_POST);
$showStatusOutput = 0;
if ( isset($_POST["aide_button"]) ) { 
    # remove status file
    unlink('/p1mon/mnt/ramdisk/upgrade-aide.status');
    if ( updateConfigDb("update config set parameter = '1' where ID = 171")) $err_cnt += 1;
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
<meta name="robots" content="noindex">
<title>In en Export</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css" />
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/p1mon-util.js"></script>
<script src="./js/crc32.js"></script>
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
                            <span class="text-15"><?php echo strIdx( 287 );?></span>
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
                            <span class="text-15"><?php echo strIdx( 288 );?></span>
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
                            <span class="text-15">Upgrade Aide</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left pos-32">
                                <div class="float-left margin-3">
                                    <button class="input-2 but-1 cursor-pointer" id="aide_button" name="aide_button" value="start">
                                        <i class="color-menu fas fa-3x fa-upload"></i>
                                        <span class="color-menu text-7">USB</span>
                                    </button>    
                                </div>
                            </div>    
                        </div>
                        <p></p>


                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 289 );?></span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left pos-32">
                                <div class="float-left margin-3">
                                    <button class="input-2 but-1 cursor-pointer" id="excel_button" name="excel_button" onclick="showExcelList()" value="start">
                                        <i class="color-menu fas fa-3x fa-file-excel"></i>
                                        <span class="color-menu text-7">Excel</span>
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



<div id="export_excel_window" class='width-600 display_none' >

    <div class='close_button' id="export_excel_window_close">
        <i class="color-select fas fa-times-circle fa-2x" aria-hidden="true"></i>
    </div>

    <div class="frame-4-top">
        <span class="text-15"><?php echo strIdx( 290 );?></span>
    </div>
    <div class="frame-4-bot">

        <div>
            <div class='left-wrapper-2 text-10'>
                <?php echo strIdx( 291 );?>
                <br><br>
            </div>
            <div class='pad-8'>
                <span id='excel_busy' class='color-busy'>
                    <i class="fas fa-spinner fa-pulse fa-2x"></i>
                </span>
            </div>
        </div>
    

        <div class='pad-12'>
            <div id="db_list">
                <!-- dynamically filled -->
            </div>
        </div>
    </div>
</div>

<div id="export_sql_msg">
    <div class='close_button' id="export_sql_msg_close">
        <i class="color-select fas fa-times-circle fa-2x" aria-hidden="true"></i>
    </div>
    <i class="fas fa-fw fa-1x fa-upload">&nbsp;&nbsp;</i><?php echo strIdx( 292 );?>&nbsp;
    <i id="sql_export_spinner" class="fas fa-spinner fa-1x fa-fw"></i>
    <br><div id="sql_export_pct" >0%</div>
    <div id="sql_export_dl_link" ><br><a id='sql_export_dl_href' href=""><?php echo strIdx( 293 );?></a></div>
</div>

<div id="import_sql_message"> <!-- new  version 1.2.0 -->
     <div class='close_button' id="import_sql_msg_close">
        <i class="color-select fas fa-times-circle fa-2x" aria-hidden="true"></i>
    </div>
    <span class="text-15"><?php echo strIdx( 294 );?></span>
    <div id="scroll_window" class="text-29" >
        <?php echo strIdx( 295 );?>
    </div>
</div> 

<div id="aide_status">
    <div class='close_button-2' id="aide_logging_close">
        <i class="color-select fas fa-times-circle fa-2x" aria-hidden="true"></i>
    </div>
    <span class="text-15">Upgrade Aide logging</span>
        <div id="scroll_window_2" class="text-29">
            <?php echo strIdx( 295 );?>
        </div>
    </div>


<script>
var sqlImportFilename = '';
var sqlExportChecking = false;
var initloadtimer;

var tmp_scroll_crc32_hash = -1;

sqlImportIsActive=getCookie("sqlImportIsActive"); 

$(function() {
    centerPosition('#import_sql_message');
    centerPosition('#export_sql_msg');
    centerPosition('#aide_status');
    centerPosition('#export_excel_window');
    hideStuff('sql_export_dl_link');
    hideStuff('excel_busy');

    // read only once
    readDbNamesJson();

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

$('#aide_logging_close').click(function() {    
   hideStuff('aide_status');
}); 

$('#export_excel_window_close').click(function() {
   hideStuff('export_excel_window');
   toLocalStorage('excel-current_filename', '' ); // stop download if the are running.
   hideStuff('excel_busy');
});

function onFileOnClick( filename ) {
    showStuff('excel_busy');
    setExcelDbFile( filename );
    toLocalStorage('excel-current_filename', filename );
}

function showExcelList() {
    event.preventDefault();
    showStuff('export_excel_window');
}


function LoadData() {

    clearTimeout(initloadtimer);

    readAideLogging();

    if (sqlExportChecking === true)
        startSqlExport(exportID,'GETSTATUS'); 
    
    if (sqlImportIsActive !== undefined ) {
        readSqlImportStatusLogging();
    }

    var datebase_name = getLocalStorage('excel-current_filename');
    if ( datebase_name != null ) {
        if ( datebase_name.length > 2 ) {
            var dl_link = './download/' + datebase_name +'.xlsx';

            if  ( doesFileExistOnWebServer( dl_link) == true ) {
                toLocalStorage('excel-current_filename', '' );  // delete to to only download once
                autoDownLoad( dl_link );
                hideStuff('excel_busy');
                hideStuff('export_excel_window');
            }
        }
    }

    initloadtimer = setInterval(function(){LoadData();}, 2000);

} 

function getCookie(name) {
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length == 2) return parts.pop().split(";").shift();
}

function autoDownLoad( filename ){
    var x=new XMLHttpRequest();
    var dl_filename = filename.split('/').pop();
    x.open("GET", filename, true);
    x.responseType = 'blob';
    x.onload=function(e){download(x.response, dl_filename, "application/zip" ); }
    x.send();
}

function setExcelDbFile( filename ) {

    $.getJSON( "./json/excel-file.php?filename=" + filename, function( d ) {
        //console.log( 'filename=' + filename );
    });
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
            $("#scroll_window").html('Data niet beschikbaar.');
        }

        tmp_local_hash = crc32( response );
        if ( tmp_local_hash != tmp_scroll_crc32_hash ) {
            tmp_scroll_crc32_hash = tmp_local_hash;
            $('#scroll_window').html( response );
            // keep scroll window scrolled down.
            $('#scroll_window').scrollTop($('#scroll_window')[0].scrollHeight);
        } else {
            if ( response.length < 1 ) {
                $('#scroll_window').html( "<b>Even geduld aub, gegevens worden verwerkt.</b><br>" );
            }
        }

    });
}

function readAideLogging(){ 

   $.get( "/txt/txt-aide-status.php", function( response, status, xhr ) {
        if ( status == "error" ) {
            $("#scroll_window_2").html('Upgrade data niet beschikbaar.');
        }

        tmp_local_hash = crc32( response );
        if ( tmp_local_hash != tmp_scroll_crc32_hash ) {
            tmp_scroll_crc32_hash = tmp_local_hash;
            $('#scroll_window_2').html( response );
            
            // keep scroll window scrolled down.
            $('#scroll_window_2').scrollTop($('#scroll_window_2')[0].scrollHeight);
        } else {
            if ( response.length < 1 ) {
                $('#scroll_window_2').html( "<b>Even geduld aub, gegevens worden verwerkt.</b><br>" );
            }
        }
    }); 
}

function readDbNamesJson(){ 
        $.getScript( "./json/sqlite-db-files.php", function( data, textStatus, jqxhr ) {
        try {
            htmlString = "<ol type='1' onclick='onFileOnClick'>";

            var jsondata = JSON.parse( data );
            for (var j=0;  j<jsondata.length; j++ ){
                htmlString = htmlString + "<li class='text-6 menu-hover' onclick='onFileOnClick( \"" + jsondata[j]+ "\" )'>" + jsondata[j] + "</li>";
            }

            htmlString = htmlString + "</ol>";
            $('#db_list').append( htmlString );
          } catch(err) {}
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
 echo "<script>showStuff('aide_status');</script>";
}

echo autoLogout(); 
?>
</body>
</html>
