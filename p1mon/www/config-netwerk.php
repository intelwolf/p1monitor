<?php
session_start(); #must be here for every page using login
include '/p1mon/www/util/auto_logout.php';
include '/p1mon/www/util/page_header.php';
include '/p1mon/www/util/p1mon-util.php';
include '/p1mon/www/util/menu_control.php';
include '/p1mon/www/util/p1mon-password.php';
include '/p1mon/www/util/config_buttons.php';
include '/p1mon/www/util/config_read.php';
include '/p1mon/www/util/textlib.php';
include '/p1mon/www/util/div_err_succes.php';
include '/p1mon/www/util/pageclock.php';

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

$WIFI_ESSID_FILE  = '/p1mon/mnt/ramdisk/wifi_essid.txt';

$err_cnt = -1;
if( isset($_POST["wifi_essid"]) && isset($_POST["wifi_pw"]) )
{
    #echo "setting wifi essid and password<br>";
    $err_cnt = 0;
    
    $crypto_wifi_pw = encodeString (trim($_POST["wifi_pw"]), 'wifipw');
    #debugLog('$crypto_wifi_pw='.$crypto_wifi_pw);
    
    #echo "crypto password = "+$crypto_wifi_pw+"<br>";
    
    if ( updateConfigDb("update config set parameter = '".$_POST["wifi_essid"]."' where ID = 11"))         $err_cnt += 1;
    if ( updateConfigDb("update config set parameter = '".$crypto_wifi_pw."' where ID = 12"))     $err_cnt += 1;
    
    #echo "error count = "+$err_cnt+"<br>";
    writeSemaphoreFile('wifi_aanpassen');
}

function makeSelector($id) {
    
    global $WIFI_ESSID_FILE;
    
    // WiFi SSID list
     if ( $id == 11 ) {
        $configValueWifiEssid = config_read(11);
        $array = explode("\n", file_get_contents($WIFI_ESSID_FILE));
         foreach ($array as $val) {
             if (strlen($val) != 0) {
                if (strcmp($configValueWifiEssid,$val) == 0) {
                    $selected = 'selected="selected"';
                } else {
                    $selected = '';
                }
                echo '<option ' . $selected . ' value="'.$val.'">'.$val.'</option>';
             }
        }
     }
     
}
?>
<!doctype html>
<html lang="nl">
<head>
<title>Netwerk configuratie</title>
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
var initloadtimer;

function wifiSelectClick() {
    //console.log('wifi click');
    if( $("#wifi_selector").css('display') == 'block' ) {
        hideStuff('wifi_selector');
        return;
    }
    var p = $( "#wifi_search" );
    var position = p.position();
    $('#wifi_selector').css({
            position:'absolute',
            left: p.position().left+10,
            top: p.position().top+30
         });
    showStuff('wifi_selector');
}

function wifiSelect() {
    //console.log('wifi select');
    var v = $("#wifi_selector option:selected" ).val()
    $("#wifi_essid").val(v);
    hideStuff('wifi_selector');
}

function readJsonApiStatus(){ 
    $.getScript( "./api/v1/status", function( data, textStatus, jqxhr ) {
      try {
        var jsonarr = JSON.parse(data); 
        for (var j=0;  j<jsonarr.length; j++){   
             switch(jsonarr[j][0]) {
            case 20:
                if (jsonarr[j][1].length === 0) {
                    hideStuff('ne5b');
                    hideStuff('ne5v');
                    hideStuff('ne5t');
                } else {
                    $('#ne5v').text(jsonarr[j][1]);
                    $('#ne5t').text(jsonarr[j][2]);
                }
                break;
            case 23:
                if (jsonarr[j][1].length === 0) {
                    hideStuff('ne4b');
                    hideStuff('ne4v');
                    hideStuff('ne4t');
                } else {
                    $('#ne4v').text(jsonarr[j][1]);
                    $('#ne4t').text(jsonarr[j][2]);
                }
                break;
            case 24:
                if (jsonarr[j][1].length === 0) {
                    hideStuff('ne1b');
                    hideStuff('ne1v');
                    hideStuff('ne1t');
                } else {
                    $('#ne1v').text(jsonarr[j][1]);
                    $('#ne1t').text(jsonarr[j][2]);
                }
                break;
            case 26:
                $('#ne2v').text(jsonarr[j][1]);
                $('#ne2t').text(jsonarr[j][2]);
                break;
            case 27:
                $('#ne3v').text(jsonarr[j][1]);
                $('#ne3t').text(jsonarr[j][2]);
                break;
            case 28:
                if (jsonarr[j][1].length === 0) {
                    hideStuff('ne6b');
                    hideStuff('ne6v');
                    hideStuff('ne6t');
                } else {
                    $('#ne6v').text(jsonarr[j][1]);
                    $('#ne6t').text(jsonarr[j][2]);
                }
                break;
            case 42:
                $('#ne8v').text(jsonarr[j][1]);
                $('#ne8t').text(jsonarr[j][2]);
                break;
            default:
                break;            
            }    
         }
      } catch(err) {
          console.log( err );
      }
   });
}

function readJsonApiConfiguration(){ 
    $.getScript( "./api/v1/configuration", function( data, textStatus, jqxhr ) {
      try {
        var jsonarr = JSON.parse(data); 
        for (var j=0;  j<jsonarr.length; j++){   
                switch(jsonarr[j][0]) {
                    case 11:
                        $('#ne7v').text( jsonarr[j][1] );
                        $('#ne7t').text( jsonarr[j][2] );
                    default:
                        break;            
            }
        }
      } catch(err) {
          console.log( err );
      }
   });
}

function LoadData() {
    clearTimeout(initloadtimer);
    readJsonApiStatus();
    readJsonApiConfiguration();
    initloadtimer = setInterval(function(){LoadData();}, 2000);
}

$(function () {
    centerPosition('#wifi_selector');
    LoadData(); 
    
});

</script>

        <?php page_header();?>

        <div class="top-wrapper-2">
            <div class="content-wrapper pad-13">
                <!-- header 2 -->
                 <?php pageclock(); ?>
            </div>
             <?php config_buttons(0);?>
        </div> <!-- end top wrapper-2 -->
        
        <div class="mid-section">
            <div class="left-wrapper-config"> <!-- left block -->
                <?php menu_control(7);?>
            </div>
            
            <div id="right-wrapper-config"> <!-- right block -->
            <!-- inner block right part of screen -->
                <div id="right-wrapper-config-left-2">
                    <!-- start of content -->
                    <form name="formvalues" id="formvalues" method="POST">
                        
                        <div class="frame-4-top">
                            <span class="text-15">wifi</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left">                
                                <i class="text-10 pad-7 fa-fw fas fa-wifi"></i>
                                <label class="text-10">Naam</label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-8 fa-fw fas fa-lock"></i>
                                <label class="text-10">Wachtwoord</label> 
                            </div>
                            <div class="float-left pad-1">    
                                <input class="input-7 color-settings color-input-back" id="wifi_essid" name="wifi_essid"  type="text" value="<?php echo config_read(11);?>">
                                <p class="p-1"></p>
                                <input class="input-7 color-settings color-input-back" id="wifi_pw" name="wifi_pw"  type="password" value="<?php echo decodeString(12, 'wifipw');?>">
                                <p class="p-1"></p>
                            </div>
                            <div id="wifi_search" onclick=wifiSelectClick() class="float-left pad-1 cursor-pointer">    
                                <span><i class="color-menu pad-7 fas fa-search"></i></span>
                            </div>
                            <p class="p-1"></p>
                            <div id="wifi_password" onclick="toggelPasswordVisibility('wifi_pw')" class="float-left pad-21 cursor-pointer">    
                                <span><i class="color-menu pad-7 fas fa-eye"></i></span>
                            </div>
                            <p class="p-1"></p>
                            
                        </div>
                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15">network status</span>
                        </div>
                        <div class="frame-4-bot">
                            <div id="ne1t" class="text-16"></div><div id="ne1v" class="text-16"></div><div><br id="ne1b"></div>
                            <div id="ne2t" class="text-16"></div><div id="ne2v" class="text-16"></div><br>
                            <div id="ne3t" class="text-16"></div><div id="ne3v" class="text-16"></div><br>
                            <div id="ne4t" class="text-16"></div><div id="ne4v" class="text-16"></div><div><br id="ne4b"></div>
                            <div id="ne5t" class="text-16"></div><div id="ne5v" class="text-16"></div><div><br id="ne5b"></div>
                            <div id="ne6t" class="text-16"></div><div id="ne6v" class="text-16"></div><div><br id="ne6b"></div>
                            <div id="ne7t" class="text-16"></div><div id="ne7v" class="text-16"></div><div><br id="ne7b"></div>
                            <div id="ne8t" class="text-16"></div><div id="ne8v" class="text-16"></div><div><br id="ne8b"></div>
                        </div>
                        <!-- placeholder variables for session termination -->
                        <input type="hidden" name="logout" id="logout" value="">
                    </form>
                </div>
                
                <div id="right-wrapper-config-right-2">
                    <div class="frame-4-top">
                        <span class="text-15">hulp</span>
                    </div>
                    <div class="frame-4-bot text-10">    
                        <?php echo strIdx(3);?>
                    </div>
                </div>
            </div>    
            <!-- end inner block right part of screen -->
            </div>
      
    <?php echo div_err_succes();?>

    <div class="pos-39" id="wifi_selector">
        <select onchange=wifiSelect() class="select-2 color-select color-input-back" name="wifi_select" id="wifi_select">
            <?php makeSelector(11);?>
        </select>
    </div>
    <?php echo autoLogout(); ?>
</body>
</html>