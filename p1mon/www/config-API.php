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
//$localip        = False;
//$noInetCheck    = False;
if( $localip == False ){ 
        if( $noInetCheck == False ) {
            die();
        }
}

$err_cnt = -1;

?>
<!doctype html>
<html lang='NL'>
<head>
<title>API configuratie</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css" />
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/p1mon-util.js"></script>
</head>
<body>
<script>
var initloadtimer

    function readJsonApiList(){ 
        $.getScript( "./api/v1/catalog", function( data, textStatus, jqxhr ) {
        try {
            htmlString = "<ol type='1'>";
            var jsondata = JSON.parse(data); 
            for (var j =0;  j<jsondata.length; j++){    
                splitBuf = jsondata[j].split('/');            // get rid of IP adres for url
                url = jsondata[j].replace(splitBuf[0],'.');   // get rid of IP adres for url
                htmlString = htmlString + "<li><a href='" + url + "' target='_blank'>" + jsondata[j] + "</a></li>";
            }
            htmlString = htmlString + "</ol>";
            $('#apiList').append( htmlString );
          } catch(err) {}
       });
    }

    function LoadData() {
        clearTimeout(initloadtimer);
        initloadtimer = setInterval(function(){LoadData();}, 5000);
    }

    $(function () {
        readJsonApiList()
        LoadData();
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
                <?php menu_control(5);?>
            </div>

            <div id="right-wrapper-config"> <!-- right block -->
            <!-- inner block right part of screen -->
                <div id="right-wrapper-config-left">
                    <!-- start of content -->
                    <form name="formvalues" id="formvalues" method="POST">

                    <div class="frame-4-top">
                            <span class="text-15">API lijst</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class='pad-12'>
                                <div id="apiList">
                                <!-- dynamicly filled -->
                                </div>
                            </div>
                        </div>
                        <p></p>    

                        <!-- placeholder variables for session termination -->
                        <input type="hidden" name="logout" id="logout" value="">
                    </form>
                </div>
                
                <div id="right-wrapper-config-right">
                    <div class="frame-4-top">
                        <span class="text-15">hulp</span>
                    </div>
                    <div class="frame-4-bot text-10">    
                        <?php echo strIdx(8);?>
                    </div>
                    
                    </div>
                </div>
            
            <!-- end inner block right part of screen -->
    </div>    
    <?php echo div_err_succes();?>
    <?php echo autoLogout(); ?>
</body>
</html>