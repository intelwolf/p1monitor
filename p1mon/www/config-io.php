<?php
session_start(); #must be here for every page using login
include_once '/p1mon/www/util/auto_logout.php';
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php';
include_once '/p1mon/www/util/menu_control.php';
include_once '/p1mon/www/util/p1mon-password.php';
include_once '/p1mon/www/util/config_buttons.php';
include_once '/p1mon/www/util/config_read.php';
include_once '/p1mon/www/util/updateStatusDb.php';
include_once '/p1mon/www/util/textlib.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/highchart.php';

#print_r($_POST);
loginInit();
passwordSessionLogoutCheck();
$err_cnt = -1;

$sw_off = strIdx( 193 );
$sw_on = strIdx( 192 );

//print ( updateStatusDb( "update status set status = 'demo van de php pagina' where ID = 107" ) );

$noInetCheck = isInternetIPAllowed();
$localip     = validLocalIpAdress(getClientIP());
//$localip        = False;
//$noInetCheck    = False;
if( $localip == False ){ 
    if( $noInetCheck == False ) {
        die();
    }
}

$time_slot_1 = array( '', '', '', '', '' ,'' , '', '', '', '', '' );
$time_slot_2 = array( '', '', '', '', '' ,'' , '', '', '', '', '' );

function makeSelectortGPIO( $id ) {
    $configValue = config_read($id);
    for ( $i=2; $i<28; $i++ ) {
        if ( $configValue == $i ) {
            $selected = 'selected="selected"';
        } else {
            $selected = '';
        }
        echo '<option ' . $selected. ' value="'. $i . '" >GPIO' . $i .'</option>';
    }

}

function readTarifTimers() {
    global $time_slot_1, $time_slot_2; 
    $data = config_read( 93 );
    $time_slot_1 = explode( '.', $data );
    $data = config_read( 94 );
    $time_slot_2 = explode( '.', $data );
}

readTarifTimers();

// timesslot 1
if ( isset( $_POST["hh_11"] ) ) { 
    $int = (int)inputClean($_POST["hh_11"]);
    if ( $int > 23 or $int < 1 ) { $int=0; }
    $time_slot_1[0]=$int;
}

if ( isset( $_POST["hh_12"] ) ) { 
    $int = (int)inputClean($_POST["hh_12"]);
    if ( $int > 59 or $int < 1 ) { $int=0; }
    $time_slot_1[1]=$int;
}

if ( isset( $_POST["hh_13"] ) ) { 
    $int = (int)inputClean($_POST["hh_13"]);
    if ( $int > 23 or $int < 1 ) { $int=0; }
    $time_slot_1[2]=$int;
}

if ( isset( $_POST["hh_14"] ) ) { 
    $int = (int)inputClean($_POST["hh_14"]);
    if ( $int > 59 or $int < 1 ) { $int=0; }
    $time_slot_1[3]=$int;
}

// timesslot 2
if ( isset( $_POST["hh_21"] ) ) { 
    $int = (int)inputClean($_POST["hh_21"]);
    if ( $int > 23 or $int < 1 ) { $int=0; }
    $time_slot_2[0]=$int;
}

if ( isset( $_POST["hh_22"] ) ) { 
    $int = (int)inputClean($_POST["hh_22"]);
    if ( $int > 59 or $int < 1 ) { $int=0; }
    $time_slot_2[1]=$int;
}

if ( isset( $_POST["hh_23"] ) ) { 
    $int = (int)inputClean($_POST["hh_23"]);
    if ( $int > 23 or $int < 1 ) { $int=0; }
    $time_slot_2[2]=$int;
}

if ( isset( $_POST["hh_24"] ) ) { 
    $int = (int)inputClean($_POST["hh_24"]);
    if ( $int > 59 or $int < 1 ) { $int=0; }
    $time_slot_2[3]=$int;
}

// weekdays slot 1
if ( isset( $_POST['fs_rb_weekday_ma_1'] )) { 
    if ( $_POST['fs_rb_weekday_ma_1'] === 'on') {  $time_slot_1[4] = 1; } else { $time_slot_1[4] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_di_1'] ) ) { 
    if ( $_POST['fs_rb_weekday_di_1'] === 'on') {  $time_slot_1[5] = 1; } else { $time_slot_1[5] = 0; }
}

if ( isset( $_POST['fs_rb_weekday_wo_1'] ) ) { 
    if ( $_POST['fs_rb_weekday_wo_1'] === 'on') {  $time_slot_1[6] = 1; } else { $time_slot_1[6] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_do_1'] ) ) { 
    if ( $_POST['fs_rb_weekday_do_1'] === 'on') {  $time_slot_1[7] = 1; } else {  $time_slot_1[7] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_vr_1'] ) ) { 
    if ( $_POST['fs_rb_weekday_vr_1'] === 'on') { $time_slot_1[8] = 1; } else {  $time_slot_1[8] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_za_1'] ) ) { 
    if ( $_POST['fs_rb_weekday_za_1'] === 'on') { $time_slot_1[9] = 1; } else {  $time_slot_1[9] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_zo_1'] ) ) { 
    if ( $_POST['fs_rb_weekday_zo_1'] === 'on') {  $time_slot_1[10] = 1; } else { $time_slot_1[10] = 0; }
} 

// weekdays slot 2
if ( isset( $_POST['fs_rb_weekday_ma_2'] ) ) { 
    if ( $_POST['fs_rb_weekday_ma_2'] === 'on') {  $time_slot_2[4] = 1; } else { $time_slot_2[4] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_di_2'] ) ) { 
    if ( $_POST['fs_rb_weekday_di_2'] === 'on') {  $time_slot_2[5] = 1; } else { $time_slot_2[5] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_wo_2'] ) ) { 
    if ( $_POST['fs_rb_weekday_wo_2'] === 'on') {  $time_slot_2[6] = 1; } else { $time_slot_2[6] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_do_2'] ) ) { 
    if ( $_POST['fs_rb_weekday_do_2'] === 'on') {  $time_slot_2[7] = 1; } else { $time_slot_2[7] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_vr_2'] ) ) { 
    if ( $_POST['fs_rb_weekday_vr_2'] === 'on') { $time_slot_2[8] = 1; } else { $time_slot_2[8] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_za_2'] ) ) { 
    if ( $_POST['fs_rb_weekday_za_2'] === 'on') { $time_slot_2[9] = 1; } else {  $time_slot_2[9] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_zo_2'] ) ) { 
    if ( $_POST['fs_rb_weekday_zo_2'] === 'on') {  $time_slot_2[10] = 1; } else { $time_slot_2[10] = 0; }
} 

if ( isset( $_POST["fs_rb_powerswitcher"] ) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ "fs_rb_powerswitcher" ] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 86") ) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 86") ) $err_cnt += 1;
    }
}

if ( isset( $_POST["fs_rb_tarifpowerswitcher"] ) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ "fs_rb_tarifpowerswitcher" ] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 90") ) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 90") ) $err_cnt += 1;
    }
}

if ( isset( $_POST["fs_rb_powerswitcher_forced"] ) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ "fs_rb_powerswitcher_forced" ] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 87") ) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 87") ) $err_cnt += 1;
    }
}

if ( isset( $_POST["fs_rb_tarifpowerswitcher_forced"] ) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ "fs_rb_tarifpowerswitcher_forced" ] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 92") ) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 92") ) $err_cnt += 1;
    }
}

if ( isset( $_POST["fs_rb_powerswitcher_inverted"] ) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ "fs_rb_powerswitcher_inverted" ] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 155") ) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 155") ) $err_cnt += 1;
    }
}

if ( isset( $_POST["fs_rb_tarifpowerswitcher_inverted"] ) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ "fs_rb_tarifpowerswitcher_inverted" ] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 156") ) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 156") ) $err_cnt += 1;
    }
}


if( isset($_POST["gpio_list"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '" . $_POST["gpio_list"] . "' where ID = 85"))  $err_cnt += 1;
}

if( isset($_POST["gpio_list_tarif"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '" . $_POST["gpio_list_tarif"] . "' where ID = 95"))  $err_cnt += 1;
}

if ( isset( $_POST[ 'fs_rb_tarif_mode' ] ) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ 'fs_rb_tarif_mode' ] == '0' ) {
        if ( updateConfigDb("update config set parameter = 'D' where ID = 91"))  $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = 'P' where ID = 91"))  $err_cnt += 1;
    }
}


if( isset($_POST["watt_on"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    $int = (int)inputClean($_POST["watt_on"]);
    if ( $int > 1000000 or $int < 1 ) { $int=0; }
    if ( updateConfigDb("update config set parameter = '" . (string)$int . "' where ID = 81"))  $err_cnt += 1;
}

if( isset($_POST["watt_off"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    $int = (int)inputClean($_POST["watt_off"]);
    if ( $int > 1000000 or $int < 1 ) { $int=0; }
    if ( updateConfigDb("update config set parameter = '" . (string)$int . "' where ID = 82"))  $err_cnt += 1;
}

if( isset($_POST["min_on"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    $int = (int)inputClean($_POST["min_on"]);
    if ( $int > 1440 or $int < 1) { $int=1; }
    if ( updateConfigDb("update config set parameter = '" . (string)$int . "' where ID = 83"))  $err_cnt += 1;
}

if( isset($_POST["min_off"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    $int = (int)inputClean($_POST["min_off"]);
    if ( $int > 1440 or $int < 1 ) { $int=1; }
    if ( updateConfigDb("update config set parameter = '" . (string)$int . "' where ID = 84"))  $err_cnt += 1;
}

if( isset($_POST["min_on_minimal"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    $int = (int)inputClean($_POST["min_on_minimal"]);
    if ( $int > 1440 or $int < 0 ) { $int=1; }
    if ( updateConfigDb("update config set parameter = '" . (string)$int . "' where ID = 88"))  $err_cnt += 1;
}

if( isset($_POST["min_off_minimal"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    $int = (int)inputClean($_POST["min_off_minimal"]);
    if ( $int > 1440 or $int < 0 ) { $int=1; }
    if ( updateConfigDb("update config set parameter = '" . (string)$int . "' where ID = 89"))  $err_cnt += 1;
}


// to limit database writes, only write once on changes, write always because of checkboxes.
if ( updateConfigDb("update config set parameter = '" . implode(".",$time_slot_1). "' where ID = 93")) $err_cnt += 1;
if ( updateConfigDb("update config set parameter = '" . implode(".",$time_slot_2). "' where ID = 94")) $err_cnt += 1;

?>
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title><?php echo ucfirst(strIdx( 657 ))?></title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css" />
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>
<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/p1mon-util.js"></script>
<script src="./js/jquery-validate-link/jquery.validate.min.js"></script>
<script src="./js/moment-link/moment-with-locales.min.js"></script>

</head>
<body>
<script>
var initloadtimer;
var day = <?php hc_language_json(); ?> 

function readJsonApiStatus(){ 
    $.getScript( "./api/v1/status", function( data, textStatus, jqxhr ) {
      try {
        var jsonarr = JSON.parse(data); 
        for (var j=0;  j<jsonarr.length; j++){   
                switch(jsonarr[j][0]) {
                    case 83:
                        $('#powerswitcher_power').text( jsonarr[j][1]);
                        break;
                    case 84:
                        $('#powerswitcher_timestamp').text( jsonarr[j][1] );
                        break;
                    case 88:
                        $('#tarifswitcher_timestamp').text( jsonarr[j][1] );
                        break;    
                    case 89:
                        if ( jsonarr[j][1] == 1 ) { 
                            $('#tarifswitcher_status').text( "<?php echo $sw_on ?>" );
                        } else {
                            $('#tarifswitcher_status').text( "<?php echo $sw_off ?>" );
                        }
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
    initloadtimer = setInterval( function(){ LoadData(); }, 1000 );
}

$(function () {
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
                <?php menu_control( 13 );?>
            </div>
            
            <div id="right-wrapper-config"> <!-- right block -->
            <!-- inner block right part of screen -->
                <div id="right-wrapper-config-left-4">
                    <!-- start of content -->
                    <form name="formvalues" id="formvalues" method="POST">

                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 661 )?></span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="rTable">

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-385">
                                        <i class="pad-7 fas fa-bolt"></i>
                                        <label><?php echo strIdx( 660 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="input-1 color-settings color-input-back" id="watt_on" name="watt_on" type="text" value="<?php echo config_read(81);?>">
                                    </div>
                                </div>
                            
                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-385">
                                        <i class="pad-7 fas fa-bolt"></i>
                                        <label><?php echo strIdx( 667 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="input-1 color-settings  color-input-back" id="watt_off" name="watt_off" type="text" value="<?php echo config_read(82);?>">
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-385">
                                        <i class="pad-7 far fa-clock"></i>
                                        <label><?php echo strIdx( 666 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="input-1 color-settings color-input-back" id="min_on" name="min_on" type="text" value="<?php echo config_read(83);?>">
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-385">
                                        <i class="pad-7 far fa-clock"></i>
                                        <label><?php echo strIdx( 668 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="input-1 color-settings  color-input-back" id="min_off" name="min_off" type="text" value="<?php echo config_read(84);?>">
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-385">
                                        <i class="pad-7 far fa-clock"></i>
                                        <label><?php echo strIdx( 669 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="input-1 color-settings color-input-back" id="min_on_minimal" name="min_on_minimal" type="text" value="<?php echo config_read(88);?>">
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-385">
                                        <i class="pad-7 far fa-clock"></i>
                                        <label><?php echo strIdx( 670 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="input-1 color-settings color-input-back" id="min_off_minimal" name="min_off_minimal" type="text" value="<?php echo config_read(89);?>">
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-385">
                                        <i class="pad-7 fas fa-map-pin"></i>
                                        <label><?php echo strIdx( 665 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <select class="select-1 color-select color-input-back cursor-pointer" name="gpio_list" id="gpio_list">
                                            <?php makeSelectortGPIO( 85 ) ;?>
                                        </select>
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-385">
                                        <i class="pad-7 fas fa-toggle-off"></i>
                                        <label><?php echo strIdx( 172 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <div class='pad-22'>
                                            <input class="cursor-pointer" id="fs_rb_powerswitcher_on"  name="fs_rb_powerswitcher" type="radio" value="1" <?php if ( config_read(86) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                            <input class="cursor-pointer" id="fs_rb_powerswitcher_off" name="fs_rb_powerswitcher" type="radio" value="0" <?php if ( config_read(86) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                        </div>
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-385">
                                        <i class="pad-7 fas fa-toggle-off"></i>
                                        <label><?php echo strIdx( 662 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <div class='pad-22'>
                                            <input class="cursor-pointer" id="fs_rb_powerswitcher_forced_on"  name="fs_rb_powerswitcher_forced" type="radio" value="1" <?php if ( config_read(87) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                            <input class="cursor-pointer" id="fs_rb_powerswitcher_forced_off" name="fs_rb_powerswitcher_forced" type="radio" value="0" <?php if ( config_read(87) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                        </div>
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-385">
                                        <i class="pad-7 fas fa-toggle-off"></i>
                                        <label><?php echo strIdx( 663 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <div class='pad-22'>
                                            <input class="cursor-pointer" id="fs_rb_powerswitcher_inverted_on"  name="fs_rb_powerswitcher_inverted" type="radio" value="1" <?php if ( config_read( 155 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                            <input class="cursor-pointer" id="fs_rb_powerswitcher_inverted_off" name="fs_rb_powerswitcher_inverted" type="radio" value="0" <?php if ( config_read( 155 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                        </div>
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell ">
                                        <i class="pad-7 fas fa-bolt"></i>
                                        <label><?php echo strIdx( 671 )?>:</label>
                                        <span id="powerswitcher_power"></span>
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-430">
                                        <i class="pad-7 far fa-clock"></i>
                                        <label><?php echo strIdx( 664 )?>:</label>
                                        <span id="powerswitcher_timestamp"></span>
                                    </div>
                                </div>


                            </div>
                             <p></p>
                        </div>
                        <p></p>

                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 672 )?></span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="rTable">

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-430">
                                        <i class="pad-7 fas fa-toggle-off"></i>
                                        <label><?php echo strIdx( 673 )?></label>
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell">
                                        
                                        <!-- timeslot 1-->
                                        <input class="input-12 color-settings color-input-back" id="hh_11" name="hh_11" type="text" value="<?php echo sprintf('%02d', $time_slot_1[0] );?>">
                                        <span>:</span>
                                        <input class="input-12 color-settings color-input-back" id="hh_12" name="hh_12" type="text" value="<?php echo sprintf('%02d', $time_slot_1[1] ); ?>">
                                        <span>&nbsp;&nbsp;</span>
                                        <input class="input-12 color-settings color-input-back" id="hh_13" name="hh_13" type="text" value="<?php echo sprintf('%02d', $time_slot_1[2] );?>">
                                        <span>:</span>
                                        <input class="input-12 color-settings color-input-back" id="hh_14" name="hh_14" type="text" value="<?php echo sprintf('%02d', $time_slot_1[3] );?>">
                                        <span>&nbsp;</span>
                                        <input type="hidden"                                  name="fs_rb_weekday_ma_1" value="off">
                                        <input class="cursor-pointer margin-6" id="fs_rb_weekday_ma_1" name="fs_rb_weekday_ma_1" type="checkbox" value="on" <?php if ( $time_slot_1[4] == 1 ) { echo 'checked'; }?>>
                                        <label for="fs_rb_weekday_ma_1" class="text-27 margin-5" id="ma_1">ma</label>
                                        <input type="hidden"                                  name="fs_rb_weekday_di_1" value="off">
                                        <input class="cursor-pointer margin-6" id="fs_rb_weekday_di_1" name="fs_rb_weekday_di_1" type="checkbox" value="on" <?php if ( $time_slot_1[5] == 1 ) { echo 'checked'; }?>>
                                        <label for="fs_rb_weekday_di_1" class="text-27 margin-5" id="di_1">di</label>
                                        <input type="hidden"                                  name="fs_rb_weekday_wo_1" value="off">
                                        <input class="cursor-pointer margin-6" id="fs_rb_weekday_wo_1" name="fs_rb_weekday_wo_1" type="checkbox" value="on" <?php if ( $time_slot_1[6] == 1  ) { echo 'checked'; }?>>
                                        <label for="fs_rb_weekday_wo_1" class="text-27 margin-5" id="wo_1">wo</label>
                                        <input type="hidden"                                  name="fs_rb_weekday_do_1" value="off">
                                        <input class="cursor-pointer margin-6" id="fs_rb_weekday_do_1" name="fs_rb_weekday_do_1" type="checkbox" value="on" <?php if ( $time_slot_1[7] == 1 ) { echo 'checked'; }?>>
                                        <label for="fs_rb_weekday_do_1" class="text-27 margin-5" id="do_1">do</label>
                                        <input type="hidden"                                  name="fs_rb_weekday_vr_1" value="off">
                                        <input class="cursor-pointer margin-6" id="fs_rb_weekday_vr_1" name="fs_rb_weekday_vr_1" type="checkbox" value="on" <?php if ( $time_slot_1[8] == 1 ) { echo 'checked'; }?>>
                                        <label for="fs_rb_weekday_vr_1" class="text-27 margin-5" id="vr_1">vr</label>
                                        <input type="hidden"                                  name="fs_rb_weekday_za_1" value="off">
                                        <input class="cursor-pointer margin-6" id="fs_rb_weekday_za_1" name="fs_rb_weekday_za_1" type="checkbox" value="on" <?php if ( $time_slot_1[9] == 1 ) { echo 'checked'; }?>>
                                        <label for="fs_rb_weekday_za_1" class="text-27 margin-5" id="za_1">za</label>
                                        <input type="hidden"                                  name="fs_rb_weekday_zo_1" value="off">
                                        <input class="cursor-pointer margin-6" id="fs_rb_weekday_zo_1" name="fs_rb_weekday_zo_1" type="checkbox" value="on" <?php if ( $time_slot_1[10] == 1) { echo 'checked'; }?>>
                                        <label for="fs_rb_weekday_zo_1" class="text-27 margin-5" id="zo_1">zo</label>
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell">
                                        <!-- timeslot 2-->
                                        <input class="input-12 color-settings color-input-back" id="hh_21" name="hh_21" type="text" value="<?php echo sprintf('%02d', $time_slot_2[0] );?>">
                                        <span>:</span>
                                        <input class="input-12 color-settings color-input-back" id="hh_22" name="hh_22" type="text" value="<?php echo sprintf('%02d', $time_slot_2[1] );?>">
                                        <span>&nbsp;&nbsp;</span>
                                        <input class="input-12 color-settings color-input-back" id="hh_23" name="hh_23" type="text" value="<?php echo sprintf('%02d', $time_slot_2[2] );?>">
                                        <span>:</span>
                                        <input class="input-12 color-settings color-input-back" id="hh_24" name="hh_24" type="text" value="<?php echo sprintf('%02d', $time_slot_2[3] );?>">
                                        <span>&nbsp;</span>
                                        <input type="hidden"                                  name="fs_rb_weekday_ma_2" value="off">
                                        <input class="cursor-pointer margin-6" id="fs_rb_weekday_ma_2" name="fs_rb_weekday_ma_2" type="checkbox" value="on" <?php if ( $time_slot_2[4] == 1 ) { echo 'checked'; }?>>
                                        <label for="fs_rb_weekday_ma_2" class="text-27 margin-5" id="ma_2">ma</label>
                                        <input type="hidden"                                  name="fs_rb_weekday_di_2" value="off">
                                        <input class="cursor-pointer margin-6" id="fs_rb_weekday_di_2" name="fs_rb_weekday_di_2" type="checkbox" value="on" <?php if ( $time_slot_2[5] == 1 ) { echo 'checked'; }?>>
                                        <label for="fs_rb_weekday_di_2" class="text-27 margin-5" id="di_2">di</label>
                                        <input type="hidden"                                  name="fs_rb_weekday_wo_2" value="off">
                                        <input class="cursor-pointer margin-6" id="fs_rb_weekday_wo_2" name="fs_rb_weekday_wo_2" type="checkbox" value="on" <?php if ( $time_slot_2[6] == 1 ) { echo 'checked'; }?>>
                                        <label for="fs_rb_weekday_wo_2" class="text-27 margin-5" id="wo_2">wo</label>
                                        <input type="hidden"                                  name="fs_rb_weekday_do_2" value="off">
                                        <input class="cursor-pointer margin-6" id="fs_rb_weekday_do_2" name="fs_rb_weekday_do_2" type="checkbox" value="on" <?php if ( $time_slot_2[7] == 1 ) { echo 'checked'; }?>>
                                        <label for="fs_rb_weekday_do_2" class="text-27 margin-5" id="do_2">do</label>
                                        <input type="hidden"                                  name="fs_rb_weekday_vr_2" value="off">
                                        <input class="cursor-pointer margin-6" id="fs_rb_weekday_vr_2" name="fs_rb_weekday_vr_2" type="checkbox" value="on" <?php if ( $time_slot_2[8] == 1 ) { echo 'checked'; }?>>
                                        <label for="fs_rb_weekday_vr_2" class="text-27 margin-5" id="vr_2">vr</label>
                                        <input type="hidden"                                  name="fs_rb_weekday_za_2" value="off">
                                        <input class="cursor-pointer margin-6" id="fs_rb_weekday_za_2" name="fs_rb_weekday_za_2" type="checkbox" value="on" <?php if ( $time_slot_2[9] == 1 ) { echo 'checked'; }?>>
                                        <label for="fs_rb_weekday_za_2" class="text-27 margin-5" id="za_2">za</label>
                                        <input type="hidden"                                  name="fs_rb_weekday_zo_2" value="off">
                                        <input class="cursor-pointer margin-6" id="fs_rb_weekday_zo_2" name="fs_rb_weekday_zo_2" type="checkbox" value="on" <?php if ( $time_slot_2[10] == 1 ) { echo 'checked'; }?>>
                                        <label for="fs_rb_weekday_zo_2" class="text-27 margin-5" id="zo_2">zo</label>
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-385">
                                        <i class="pad-7 far fa-clock"></i>
                                        <label><?php echo strIdx( 674 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <div class='pad-22'>
                                            <input class="cursor-pointer" id="fs_rb_tarif_mode_piek" name="fs_rb_tarif_mode" type="radio" value="1" <?php if ( config_read(91) == 'P' ) { echo 'checked'; }?>><?php echo strIdx( 658 )?>
                                            <input class="cursor-pointer" id="fs_rb_tarif_mode_dal"  name="fs_rb_tarif_mode" type="radio" value="0" <?php if ( config_read(91) == 'D' ) { echo 'checked'; }?>><?php echo strIdx( 659 )?>
                                        </div>
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-385">
                                        <i class="pad-7 fas fa-map-pin"></i>
                                        <label><?php echo strIdx( 665 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <div class='pad-22'>
                                            <select class="select-1 color-select color-input-back cursor-pointer" name="gpio_list_tarif" id="gpio_list_tarif">
                                                <?php makeSelectortGPIO( 95 );?>
                                            </select>
                                        </div>
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-385">
                                        <i class="text-10 pad-7 fas fa-toggle-off"></i>
                                        <label><?php echo strIdx( 172 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <div class='pad-22'>
                                            <input class="cursor-pointer" id="fs_rb_tarifpowerswitcher_on"  name="fs_rb_tarifpowerswitcher" type="radio" value="1" <?php if ( config_read(90) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                            <input class="cursor-pointer" id="fs_rb_tarifpowerswitcher_off" name="fs_rb_tarifpowerswitcher" type="radio" value="0" <?php if ( config_read(90) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                        </div>
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-385">
                                        <i class="pad-7 fas fa-toggle-off"></i>
                                        <label><?php echo strIdx( 662 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <div class='pad-22'>
                                            <input class="cursor-pointer" id="fs_rb_tarifpowerswitcher_forced_on"  name="fs_rb_tarifpowerswitcher_forced" type="radio" value="1" <?php if ( config_read(92) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                            <input class="cursor-pointer" id="fs_rb_tarifpowerswitcher_forced_off" name="fs_rb_tarifpowerswitcher_forced" type="radio" value="0" <?php if ( config_read(92) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                        </div>
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-385">
                                        <i class="pad-7 fas fa-toggle-off"></i>
                                        <label><?php echo strIdx( 663 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <div class='pad-22'>
                                            <input class="cursor-pointer" id="fs_rb_tarifpowerswitcher_inverted_on"  name="fs_rb_tarifpowerswitcher_inverted" type="radio" value="1" <?php if ( config_read( 156 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                            <input class="cursor-pointer" id="fs_rb_tarifpowerswitcher_inverted_off" name="fs_rb_tarifpowerswitcher_inverted" type="radio" value="0" <?php if ( config_read( 156 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                        </div>
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-430">
                                        <i class="pad-7 fas fa-bolt"></i>
                                        <label><?php echo strIdx( 246 )?>:</label>
                                        <span id="tarifswitcher_status"></span>
                                    </div>
                                </div>

                                <div class="rTableRow text-16">
                                    <div class="rTableCell width-430">
                                        <i class="pad-7 far fa-clock"></i>
                                        <label><?php echo strIdx( 664 )?>:</label>
                                        <span id="tarifswitcher_timestamp"></span>
                                    </div>
                                </div>

                            </div>
                            <p></p>
                        </div>


                        <!-- placeholder variables for session termination -->
                        <input type="hidden" name="logout" id="logout" value="">
                    </form>
                </div>
                
                <div id="right-wrapper-config-right-4">
                    <div class="frame-4-top">
                        <span class="text-15">hulp</span>
                    </div>
                    <div class="frame-4-bot text-10">    
                        <?php echo strIdx(70);?>
                        <br><br>
                        <?php echo strIdx(72);?>
                        <img class="pos-1" alt="PI GPIO pin layout" src="./img/pin_layout.svg">
                    </div>
                </div>
            </div>    
            <!-- end inner block right part of screen -->
    </div>
    <script>

jQuery.validator.addMethod("ztatz_time_format", function(value, element) {
    if ( value.length == 0 ) {
        //console.log( "ztatz_time_format value is empty" );
        return true;
    }
    // console.log( "ztatz_time_format" );
    if ( /^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]) (2[0-3]|[01][0-9]):[0-5][0-9]:[0-5][0-9]$/.test(value) ) {
        //console.log ( moment(value).isValid() );
        return moment(value).isValid();
    } else {
        return false;
    };
}, '');

jQuery.validator.addMethod( "ztatz_gpio", function(value, element) {

        if ( document.getElementById ("gpio_list_tarif" ).value == document.getElementById("gpio_list").value ) {
            document.getElementById( "gpio_list_tarif" ).style.borderColor = "red";
            document.getElementById( "gpio_list" ).style.borderColor       = "red";
            return false;
        }   
        document.getElementById("gpio_list").style.borderColor       = "#a6a6a6";
        document.getElementById("gpio_list_tarif").style.borderColor = "#a6a6a6";
        return true;
}, '');


$(function() {

    $("#formvalues").validate({
        rules: {
            'gpio_list':{
                required: false,
                ztatz_gpio:true
            },
            'gpio_list_tarif':{
                required: false,
                ztatz_gpio:true
            },
            'watt_on': {
                required: true,
                number: true,
                max: 1000000,
                min: 0
            },
            'watt_off': {
                required: true,
                number: true,
                max: 1000000,
                min: 0
            },
            'min_on': {
                required: true,
                number: true,
                max: 1440,
                min: 1
            },
            'min_off': {
                required: true,
                number: true,
                max: 1440,
                min: 1
            },
            'min_on_minimal': {
                required: true,
                number: true,
                max: 1440,
                min: 0
            },
            'min_off_minimal': {
                required: true,
                number: true,
                max: 1440,
                min: 0
            },
            'hh_11': {
                required: true,
                number: true,
                max: 23,
                min: 0
            },
            'hh_12': {
                required: true,
                number: true,
                max: 59,
                min: 0
            },
            'hh_13': {
                required: true,
                number: true,
                max: 23,
                min: 0
            },
            'hh_14': {
                required: true,
                number: true,
                max: 59,
                min: 0
            },
            'hh_21': {
                required: true,
                number: true,
                max: 23,
                min: 0
            },
            'hh_22': {
                required: true,
                number: true,
                max: 59,
                min: 0
            },
            'hh_23': {
                required: true,
                number: true,
                max: 23,
                min: 0
            },
            'hh_24': {
                required: true,
                number: true,
                max: 59,
                min: 0
            }
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

    document.getElementById('ma_1').innerHTML = day.shortWeekdays[1];
    document.getElementById('ma_2').innerHTML = day.shortWeekdays[1];
    document.getElementById('di_1').innerHTML = day.shortWeekdays[2];
    document.getElementById('di_2').innerHTML = day.shortWeekdays[2];
    document.getElementById('wo_1').innerHTML = day.shortWeekdays[3];
    document.getElementById('wo_2').innerHTML = day.shortWeekdays[3];
    document.getElementById('do_1').innerHTML = day.shortWeekdays[4];
    document.getElementById('do_2').innerHTML = day.shortWeekdays[4];
    document.getElementById('vr_1').innerHTML = day.shortWeekdays[5];
    document.getElementById('vr_2').innerHTML = day.shortWeekdays[5];
    document.getElementById('za_1').innerHTML = day.shortWeekdays[6];
    document.getElementById('za_2').innerHTML = day.shortWeekdays[6];
    document.getElementById('zo_1').innerHTML = day.shortWeekdays[0];
    document.getElementById('zo_2').innerHTML = day.shortWeekdays[0];

});
</script>
<?php echo autoLogout();?>
</body>
</html>