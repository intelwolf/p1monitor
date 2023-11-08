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

$sw_off    = strIdx( 193 );
$sw_on     = strIdx( 192 );

$WIFI_ESSID_FILE  = '/p1mon/mnt/ramdisk/wifi_essid.txt';

$ethO_previous_ip   = config_read( 164 );
$wlan0_previous_ip  = config_read( 165 );
$router_previous_ip = config_read( 166 );
$dns_previous_ip    = config_read( 167 );
$wifi_previous_ssd  = config_read( 11  );
$wifi_previous_pw   = config_read( 12  );

#echo $ethO_previous_ip."<br>";
#echo $wlan0_previous_ip."<br>";
#echo $router_previous_ip."<br>";
#echo $dns_previous_ip."<br>";

$err_cnt = -1;
$watchdog_flag = intval( config_read( 168 ) );

if( isset($_POST["ip_eth0"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST["ip_eth0"] != $ethO_previous_ip ) {
        if ( updateConfigDb("update config set parameter = '".$_POST["ip_eth0"]."' where ID = 164")) $err_cnt += 1;
        $watchdog_flag = $watchdog_flag | 1;
        if ( updateConfigDb("update config set parameter = '".$watchdog_flag."' where ID = 168")) $err_cnt += 1;
    }
}

if( isset($_POST["ip_wlan0"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST["ip_wlan0"] != $wlan0_previous_ip ) {
        if ( updateConfigDb("update config set parameter = '".$_POST["ip_wlan0"]."' where ID = 165")) $err_cnt += 1;
        $watchdog_flag = $watchdog_flag | 2;
        if ( updateConfigDb("update config set parameter = '".$watchdog_flag."' where ID = 168")) $err_cnt += 1;
    }
}

if( isset($_POST["ip_router"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST["ip_router"] != $router_previous_ip ) {
        if ( updateConfigDb("update config set parameter = '".$_POST["ip_router"]."' where ID = 166")) $err_cnt += 1;
        $watchdog_flag = $watchdog_flag | 4;
        if ( updateConfigDb("update config set parameter = '".$watchdog_flag."' where ID = 168")) $err_cnt += 1;
    }
}

if( isset($_POST["ip_dns"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST["ip_dns"] != $dns_previous_ip ) {
        if ( updateConfigDb("update config set parameter = '".$_POST["ip_dns"]."' where ID = 167")) $err_cnt += 1;
        $watchdog_flag = $watchdog_flag | 8;
        if ( updateConfigDb("update config set parameter = '".$watchdog_flag."' where ID = 168")) $err_cnt += 1;
    }
}

#echo "watchdog_flag=".$watchdog_flag."<br>";

if( isset($_POST["wifi_essid"]) && isset($_POST["wifi_pw"]) )
{

    if ( $err_cnt == -1 ) $err_cnt=0;

    $crypto_wifi_pw = encodeString (trim($_POST["wifi_pw"]), 'wifipw');

    if ( updateConfigDb("update config set parameter = '".$_POST["wifi_essid"]."' where ID = 11")) $err_cnt += 1;
    if ( updateConfigDb("update config set parameter = '".$crypto_wifi_pw."' where ID = 12"))      $err_cnt += 1;
    
    if ( strcmp( $wifi_previous_ssd, $_POST["wifi_essid"]) != 0 or strcmp( $wifi_previous_pw , $crypto_wifi_pw) ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 183") ) $err_cnt += 1;
    } 

}

if( isset($_POST["FQDN"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".$_POST["FQDN"]."' where ID = 150")) $err_cnt += 1;
}

if( isset($_POST["duckDNStoken"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    $crypto_token = encodeString ( trim($_POST["duckDNStoken"]), 'dckdckdns');
    if ( updateConfigDb("update config set parameter = '".$crypto_token."' where ID = 151")) $err_cnt += 1;
}

if ( isset($_POST[ "fs_rb_duckdns" ]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ "fs_rb_duckdns" ] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 152") ) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 152") ) $err_cnt += 1;
    }
}


if ( isset($_POST[ "fs_rb_duckdns_force" ]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ "fs_rb_duckdns_force" ] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 153") ) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 153") ) $err_cnt += 1;
    }
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
<meta name="robots" content="noindex">
<title><?php echo strIdx( 225 );?></title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css" />
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/p1mon-util.js"></script>
<script src="./js/jquery-validate-link/jquery.validate.min.js"></script>
<script src="./js/jquery-validate-link/additional-methods.min.js"></script>

</head>
<body>
<script>
var initloadtimer;
var suggestie_text = "<?php echo strIdx( 286 );?>";

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
                $('#ne5v').text(jsonarr[j][1]);
                break;
            case 23:
                $('#ne4v').text(jsonarr[j][1]);
                break;
            case 24:
                if ( jsonarr[j][1] == 'ja' ) {
                    $('#ne1v').html( '<i class="color-ok fas fa-check-circle"></i>' )
                } else {
                    $('#ne1v').html( '<i class="color-warning fas fa-exclamation-triangle"></i>' )
                }
                break;
            case 26:
                $('#ne2v').text(jsonarr[j][1]);
                break;
            case 27:
                $('#ne3v').text(jsonarr[j][1]);
                break;
            case 28:
                $('#ne6v').text(jsonarr[j][1]);
                break;
            case 42:
                $('#ne8v').text(jsonarr[j][1]);
                break;
            case 122:
                document.getElementById("ip_router").placeholder = suggestie_text + " " + jsonarr[j][1]
                document.getElementById("ip_dns").placeholder    = suggestie_text + " " + jsonarr[j][1]
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
                                <label class="text-10">SSID</label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-8 fa-fw fas fa-lock"></i>
                                <label class="text-10"><?php echo strIdx(226);?></label> 
                            </div>
                            <div class="float-left pad-1">
                                <input class="input-5 color-settings color-input-back" id="wifi_essid" name="wifi_essid"  type="text" value="<?php echo config_read(11);?>">
                                <p class="p-1"></p>
                                <input class="input-5 color-settings color-input-back" id="wifi_pw" name="wifi_pw"  type="password" value="<?php echo decodeString(12, 'wifipw');?>">
                                <p class="p-1"></p>
                            </div>
                            <div class="float-right">
                                <div id="wifi_search" onclick=wifiSelectClick() class="float-left pad-1 cursor-pointer">
                                    <span><i class="color-menu pad-7 fas fa-search"></i></span>
                                </div>
                                <p class="p-1"></p>
                                <div id="wifi_password" onclick="toggelPasswordVisibility('wifi_pw')" class="float-left pad-21 cursor-pointer">
                                    <span><i class="color-menu pad-7 fas fa-eye"></i></span>
                                </div>
                            </div>
                            <p class="p-1"></p>
                            
                        </div>
                        <p></p>

                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 234 );?></span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="rTable">

                                <div class="rTableRow">
                                    <div class="rTableCell text-16 width-160">
                                        <?php echo strIdx( 227 );?>
                                    </div>
                                    <div class="rTableCell text-16">
                                        <div id="ne1v"></div>
                                    </div>
                                </div>

                                <div class="rTableRow">
                                    <div class="rTableCell text-16 width-160">
                                        <?php echo strIdx( 228 );?>
                                    </div>
                                    <div class="rTableCell text-16">
                                        <div id="ne2v"></div>
                                    </div>
                                </div>

                                <div class="rTableRow">
                                    <div class="rTableCell text-16 width-160">
                                        <?php echo strIdx( 229 );?>
                                    </div>
                                    <div class="rTableCell text-16">
                                        <div id="ne3v"></div>
                                    </div>
                                </div>

                                <div class="rTableRow">
                                    <div class="rTableCell text-16 width-160">
                                        <?php echo strIdx( 230 );?>
                                    </div>
                                    <div class="rTableCell text-16">
                                        <div id="ne4v"></div>
                                    </div>
                                </div>

                                <div class="rTableRow">
                                    <div class="rTableCell text-16 width-160">
                                        <?php echo strIdx( 231 );?>
                                    </div>
                                    <div class="rTableCell text-16">
                                        <div id="ne5v"></div>
                                    </div>
                                </div>

                                <div class="rTableRow">
                                    <div class="rTableCell text-16 width-160">
                                        <?php echo strIdx( 232 );?>
                                    </div>
                                    <div class="rTableCell text-16">
                                        <div id="ne6v"></div>
                                    </div>
                                </div>

                                <div class="rTableRow">
                                    <div class="rTableCell text-16 width-160">
                                        wifi SSID
                                    </div>
                                    <div class="rTableCell text-16">
                                        <div id="ne7v"></div>
                                    </div>
                                </div>

                                <div class="rTableRow">
                                    <div class="rTableCell text-16 width-160">
                                        <?php echo strIdx( 233 );?>
                                    </div>
                                    <div class="rTableCell text-16">
                                        <div id="ne8v"></div>
                                    </div>
                                </div>

                            </div>
                        </div>

                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 235 );?></span>
                        </div>
                        <div class="frame-4-bot" title="<?php echo strIdx( 239 );?>">
                            <div class="rTable">
                                <div class="rTableRow">
                                    <div class="rTableCell">
                                        <i class="pad-7 text-10 fas fa-globe"></i>
                                    </div>  
                                    <div class="rTableCell">
                                        <input class="input-10 color-settings color-input-back" id="FQDN" name="FQDN" type="text" value="<?php echo config_read( 150 );?>">
                                        <p class="p-1"></p> 
                                    </div>
                                </div>
                            </div>
                        </div>

                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15">DuckDNS dynamic DNS</span>
                        </div>
                        <div class="frame-4-bot">

                            <div class="rTable">
                                <div class="rTableRow" title="<?php echo strIdx( 240 );?>">
                                    <div class="rTableCell width-22">
                                        <i class="pad-7 text-10 fas fa-lock"></i>
                                    </div>
                                    <div class="rTableCell">
                                        <label class="text-10">token</label> 
                                    </div>
                                    <div class="rTableCell">
                                        <input class="input-10 color-settings color-input-back" id="duckDNStoken" name="duckDNStoken" type="password" value="<?php echo decodeString(151, 'dckdckdns');?>">
                                        <p class="p-1"></p> 
                                    </div>
                                    <div class="rTableCell">
                                        <div id="duckDNStoken_eye" onclick="toggelPasswordVisibility('duckDNStoken')" class="cursor-pointer">
                                            <span><i class="color-menu pad-7 fas fa-eye"></i></span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="rTable">
                                <div class="rTableRow" title="<?php echo strIdx( 241 );?>">
                                        <div class="rTableCell width-22">
                                            <i class="pad-7 text-10 fas fa-toggle-off"></i>
                                        </div>
                                        <div class="rTableCell width-290">
                                            <label class="text-10"><?php echo strIdx( 172 );?></label> 
                                        </div>
                                        <div class="rTableCell">
                                            <input class="cursor-pointer" id="fs_rb_duckdns_on"  name="fs_rb_duckdns" type="radio" value="1" <?php if ( config_read( 152 ) == 1 ) { echo 'checked'; }?> ><?php echo $sw_on ?>
                                            <input class="cursor-pointer" id="fs_rb_duckdns_off" name="fs_rb_duckdns" type="radio" value="0" <?php if ( config_read( 152 ) == 0 ) { echo 'checked'; }?> ><?php echo $sw_off ?>
                                        </div>
                                    </div>
                                    <div class="rTableRow" title="<?php echo strIdx( 242 );?>">
                                        <div class="rTableCell width-22">
                                            <i class="pad-7 text-10 fas fa-toggle-off"></i>
                                        </div>
                                        <div class="rTableCell width-290">
                                            <label class="text-10"><?php echo strIdx( 236 );?></label> 
                                        </div>
                                        <div class="rTableCell">
                                            <input class="cursor-pointer" id="fs_rb_duckdns_force_on"  name="fs_rb_duckdns_force" type="radio" value="1"><?php echo $sw_on ?>
                                            <input class="cursor-pointer" id="fs_rb_duckdns_force_off" name="fs_rb_duckdns_force" type="radio" value="0" checked ><?php echo $sw_off ?>
                                        </div>
                                    </div>
                            </div>
                        </div>

                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 281 );?></span>
                        </div>
                        <div class="frame-4-bot">

                            <div class="rTable">

                                <div class="rTableRow" title="<?php echo strIdx( 273 );?>">
                                    <div class="rTableCell width-22">
                                        <i class="pad-7 text-10 fas fa-network-wired"></i>
                                    </div>
                                    <div class="rTableCell">
                                        <label class="text-10 pad-1"><?php echo strIdx( 277 );?></label> 
                                    </div>
                                    <div class="rTableCell">
                                        <input class="input-14 color-settings color-input-back" id="ip_eth0" name="ip_eth0" type="text" value="<?php echo config_read( 164 );?>">
                                    </div>
                                </div>

                                <div class="rTableRow" title="<?php echo strIdx( 274 );?>">
                                    <div class="rTableCell width-22">
                                        <i class="pad-7 text-10 fas fa-wifi"></i>
                                    </div>
                                    <div class="rTableCell">
                                        <label class="text-10 pad-1"><?php echo strIdx( 278 );?></label> 
                                    </div>
                                    <div class="rTableCell"> 
                                        <input class="input-14 color-settings color-input-back" id="ip_wlan0" name="ip_wlan0" type="text" value="<?php echo config_read( 165 );?>">
                                    </div>
                                </div>

                                <div class="rTableRow" title="<?php echo strIdx( 275 );?>">
                                    <div class="rTableCell width-22">
                                        <i class="pad-7 text-10 fas fa-project-diagram"></i>
                                    </div>
                                    <div class="rTableCell">
                                        <label class="text-10 pad-1"><?php echo strIdx( 279 );?></label> 
                                    </div>
                                    <div class="rTableCell"> 
                                        <input class="input-14 color-settings color-input-back" id="ip_router" name="ip_router" type="text" value="<?php echo config_read( 166 );?>">
                                    </div>
                                </div>

                                <div class="rTableRow" title="<?php echo strIdx( 276 );?>">
                                    <div class="rTableCell width-22">
                                        <i class="pad-7 text-10 fas fa-globe"></i>
                                    </div>
                                    <div class="rTableCell">
                                        <label class="text-10 pad-1"><?php echo strIdx( 280 );?></label>
                                    </div>
                                    <div class="rTableCell"> 
                                        <input class="input-14 color-settings color-input-back" id="ip_dns" name="ip_dns" type="text" value="<?php echo config_read( 167 );?>">
                                    </div>
                                </div>

                            </div>
                            
                            <p></p>

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
                        <?php echo strIdx( 3);?>
                        <br><br>
                        <?php echo strIdx( 237 );?>
                        <br><br>
                        <?php echo strIdx( 238 );?>
                        <br><br>
                        <?php echo strIdx( 282 );?>
                        <br>
                        <span class="text-10">
                            <a href="https://www.ztatz.nl/p1-monitor-internet-api/#static_ip" target="_blank">
                                <i class="pad-7 color-menu fas fa-globe"></i>
                                <?php echo strIdx( 283 );?>
                            </a>
                        </span>
                        <br><br>
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

<script>

jQuery.validator.addMethod( "ztatz_NotEqualTo", function( value, element) {
    eth0  = document.getElementById ( 'ip_eth0' ).value.trim();
    wlan0 =  document.getElementById( 'ip_wlan0' ).value.trim();
    if ( eth0.length == 0 || wlan0.length == 0 ) { 
        return true;
    }
    if ( eth0 == wlan0 ) {
        return false;
    }
    return true;
}, '');

$(function() {
    $("#formvalues").validate({
        rules: {
            'ip_eth0': {
                ipv4: true,
                ztatz_NotEqualTo: true
            },
            'ip_wlan0': {
                ipv4: true,
                ztatz_NotEqualTo: true
            },
            'ip_router': {
                ipv4: true
            },
            'ip_dns': {
                ipv4: true
            },
        
        },
        invalidHandler: function(e, validator) { 
            var errors = validator.numberOfInvalids();
            //console.log ( errors );
        },
        errorPlacement: function(error, element) {
            $(this).addClass('error');
            //console.log ( 'errorPlacement' );
            return false;  // will suppress error messages 
        }
    }); 
});
</script>


    <?php echo autoLogout(); ?>
</body>
</html>