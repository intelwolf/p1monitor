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
#print_r($_POST);

loginInit();
passwordSessionLogoutCheck();

$noInetCheck = isInternetIPAllowed();
$localip     = validLocalIpAdress(getClientIP());
if( $localip == False ){ 
        if( $noInetCheck == False ) {
            die();
        }
}

?>
<!doctype html>
<html lang="nl">
<head>
<meta name="robots" content="noindex">
<title>Log viewer</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css" />
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>

<link type="text/css" rel="stylesheet" href="./css/p1mon-tabulator-alt-1.css" >
<link type="text/css" rel="stylesheet" href="./css/p1mon-tabulator.css" >

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/p1mon-util.js"></script>
<script src="./js/moment-link/moment-with-locales.min.js"></script>
<script src="./js/tabulator-dist/js/tabulator.min.js"></script>
<script src="./js/sheetjs-dist/xlsx.full.min.js"></script>

</head>
<body>

<script>
var initloadtimer;
var logfiles_list_inital_data_loaded = false;
var logfiles_list_table;
var logfile_content_table;
var selected_logfile = "";
var logfile_list_auto_refresh_is_on    = true; 
var logfile_content_auto_refresh_is_on = true;


function LoadData() {

    //console.log( "update " );
    timeout_settings = 5000 // every 5 secs
    clearTimeout( initloadtimer );

    if ( logfiles_list_inital_data_loaded == true ) {

        if ( logfile_list_auto_refresh_is_on == true ) {
            //console.log( "update list" );
            logfiles_list_table.replaceData();
            
        }

        if ( selected_logfile !== "" ) { // only reload when the filename is set

            if ( logfile_content_auto_refresh_is_on == true ) {
                //console.log( "update content" );
                logfile_content_table.replaceData();
            }

        }
        
    }

    initloadtimer = setInterval( function(){ LoadData(); }, timeout_settings );
}


function loadLogFileContent( filename ) {
    //console.log ( filename );
    selected_logfile = filename;
    document.getElementById("logviewer").innerHTML = filename;
    logfile_content_table.setData( "./json/logfiles.php", { file: filename });
    toLocalStorage( 'config-logfile-selected-file', filename ); 
    showStuff( "logcontentframeheader" );
    showStuff( "logcontentframe" );
}


function setClassAutoRefresh( flag, id  ) {

    //console.log ( "setClassAutoRefresh = "  + id );

    if (flag == true ) {
        document.getElementById( id ).classList.remove( "color-menu-not-active" );
        document.getElementById( id ).classList.add("color-menu");
        //console.log ( "set " +  id );
    } else {
        document.getElementById( id ).classList.add( "color-menu-not-active" );
        document.getElementById( id ).classList.remove( "color-menu" );
        //console.log ( "unset " + id );
    }

}


$(function () {

    hideStuff( "logcontentframe" );
    hideStuff( "logcontentframeheader" );
   
    // ###################################
    // Build Tabulator list of log files #
    // ###################################
    logfiles_list_table = new Tabulator("#logfile-list-table", {
        ajaxURL:"./json/logfiles.php", 
        ajaxParams:{ list:"" },
        ajaxLoaderLoading: "<div><img src='./img/ajax-loader.gif' alt='Even geduld aub.' height='15' width='128' /></div>",
        height:"400px",
        layout:"fitColumns",
        tooltips:true,
        tooltipGenerationMode:"hover",
        placeholder:"geen log bestanden beschikbaar.",
        clipboard:true,
        columns:[
            {title:"log bestandsnaam",  field:"filename",  sorter:"string" },
            {title:"laatste wijziging", field:"timestamp", sorter:"string", width:170 },
            {title:"bytes",             field:"filesize",  sorter:"number", width:100  },
        ],
        dataLoaded:function(data){
            logfiles_list_inital_data_loaded = true; // used to prevent pesky error message when intial load is not finshed
        },
        rowClick:function( e, row ){
            //console.log ( row.getData().filename );
            selected_logfile = row.getData().filename 
            loadLogFileContent( selected_logfile );
        },
        rowTap:function(e, row){  
            selected_logfile = row.getData().filename 
            loadLogFileContent( selected_logfile );
        },
    });

    logfiles_list_table.setSort([
        { column:"timestamp", dir:"desc" }, //sort by this first
    ]);
    
    // #####################################
    // Build Tabulator list of log content #
    // #####################################
    logfile_content_table = new Tabulator("#logfile-content-table", {
        //virtualDomHoz:true,
        height:"400px",
        layout:"fitDataFill",
        ajaxLoaderLoading: "<div><img src='./img/ajax-loader.gif' alt='Even geduld aub.' height='15' width='128' /></div>",
        layoutColumnsOnNewData:true,
        tooltips:true,
        tooltipGenerationMode:"hover",
        placeholder:"geen log bestand geselecteerd of het bestand bevat geen data.",
        clipboard:true,
        columns:[
            {title:"tijdstip", field:"timestamp", sorter:"string", }, //width:200  },
            {title:"nivo",     field:"level",     sorter:"string", }, //width:90   },
            {title:"regel",    field:"line",      sorter:"string", }  //width:1710 },
        ],
        rowFormatter:function( row ){

            var data = row.getData();
            // set color according to level.
            switch(data.level) {
            case "INFO":
                row.getElement().style.color = "green";
                break;
            case "WARNING":
                row.getElement().style.color = "#F2BA0F";
                break;
            case "ERROR":
                row.getElement().style.color = "orange";
                break;
            case "CRITICAL":
                row.getElement().style.color = "red";
                break;
            }
        }
    });

    logfile_content_table.setSort([
        { column:"timestamp", dir:"desc" }, //sort by this first
    ]);

    // trigger auto refresh list
    document.getElementById( "buttonLogFileListAutoRefresh" ).addEventListener("click", function(event) {
        logfile_list_auto_refresh_is_on = !logfile_list_auto_refresh_is_on;
        toLocalStorage( 'config-logfile-list-auto-refresh-is-on', logfile_list_auto_refresh_is_on ); 
        setClassAutoRefresh( logfile_list_auto_refresh_is_on, 'textLogFileListAutoRefresh' );
        event.preventDefault();
    }, false );

    // trigger auto refresh content.
    document.getElementById( "buttonLogFileContentAutoRefresh" ).addEventListener("click", function(event) {
        logfile_content_auto_refresh_is_on = !logfile_content_auto_refresh_is_on;
        toLocalStorage( 'config-logfile-content-auto-refresh-is-on', logfile_content_auto_refresh_is_on ); 
        setClassAutoRefresh( logfile_content_auto_refresh_is_on, 'textLogFileListContentRefresh' );
        event.preventDefault();
    }, false );

    //trigger download of data.csv file
    document.getElementById("download-csv").addEventListener("click", function(){
        logfile_content_table.download( "csv", selected_logfile + ".csv" );
        event.preventDefault();
    });

    //trigger download of data.json file
    document.getElementById("download-json").addEventListener("click", function(){
        logfile_content_table.download( "json", selected_logfile + ".json");
        event.preventDefault();
    });

    //trigger download of data.xlsx file
    document.getElementById("download-xlsx").addEventListener("click", function(){
        logfile_content_table.download( "xlsx", selected_logfile + ".xlsx", {sheetName: selected_logfile });
        event.preventDefault();
    });


    // load user browser specific settings.
    logfile_list_auto_refresh_is_on    = JSON.parse( getLocalStorage('config-logfile-list-auto-refresh-is-on')    );
    logfile_content_auto_refresh_is_on = JSON.parse( getLocalStorage('config-logfile-content-auto-refresh-is-on') );

    setClassAutoRefresh( logfile_list_auto_refresh_is_on,    'textLogFileListAutoRefresh' );
    setClassAutoRefresh( logfile_content_auto_refresh_is_on, 'textLogFileListContentRefresh' );

    LoadData();

    if ( getLocalStorage( 'config-logfile-selected-file' ) !== null ) {
        loadLogFileContent( getLocalStorage( 'config-logfile-selected-file' ) );
    }

});


</script>

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
                <?php menu_control( 17 );?>
            </div>

            <div id="right-wrapper-config"> <!-- right block -->
            <!-- inner block right part of screen -->
                <div id="right-wrapper-config-left">
                    <!-- start of content -->
                    <form name="formvalues" id="formvalues" method="POST">

                        <div class="frame-4-top">
                            <span class="text-15">beschikbare log bestanden</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-right">
                                <button id="buttonLogFileListAutoRefresh" name="buttonLogFileListAutoRefresh" class="input-15 cursor-pointer float-right">
                                <span id="textLogFileListAutoRefresh" class="color-menu">automatische vernieuwen</span>
                                </button>
                            </div>
                            <br>
                            <br>
                            <div class='pad-12'>
                                <div id="logfile-list-table">
                                </div>
                            </div>
                        </div>

                        <p></p>

                        <div id="logcontentframeheader" class="frame-4-top">
                            <span class="text-15">log viewer&nbsp;&nbsp;</span>
                            <span id="logviewer" class="text-27"></span>
                        </div>
                        <div id="logcontentframe" class="frame-4-bot">

                            <div class="float-right">
                                <button id="buttonLogFileContentAutoRefresh" name="buttonLogFileContentAutoRefresh" class="input-15 cursor-pointer float-right">
                                    <span id="textLogFileListContentRefresh" class="color-menu">automatische vernieuwen</span>
                                </button>
                            </div>
                            <br>
                            <br>
                            <div class='pad-12'>
                                <div id="logfile-content-table">
                                </div>
                            </div>
                            <p></p>
                            <div class="float-right" >
                                <button id="download-csv"  class="color-menu input-15 cursor-pointer">download CSV</button>
                                <button id="download-json" class="color-menu input-15 cursor-pointer">download JSON</button>
                                <button id="download-xlsx" class="color-menu input-15 cursor-pointer">download XLSX</button>
                            </div>

                        </div>

                        <!-- placeholder variables for session termination -->
                    <input type="hidden" name="logout" id="logout" value="">
                    </form>
                </div>
                                
                <div id="right-wrapper-config-right">
                        <div class="frame-4-top">
                            <span class="text-15">hulp</span>
                        </div>
                        <div class="frame-4-bot text-10">
                            <?php echo strIdx(100);?>
                            
                        </div>
                        </div>
                </div>        
                <!-- end inner block right part of screen -->
        </div>
</body>
</html>