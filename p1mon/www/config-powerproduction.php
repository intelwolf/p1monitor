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
include_once '/p1mon/www/util/config_page_menu_header_powerproduction.php';

//print_r($_POST);
loginInit();
passwordSessionLogoutCheck();
$err_cnt = -1;
$file_name = '/p1mon/mnt/ramdisk/powerproduction-counter-reset.status';

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
if ( isset($_POST["fs_rb_kwhmeter_reset"]) ) {
    if ( $_POST[ "fs_rb_kwhmeter_reset" ] == '1' ) {
        # remove status file
        unlink( $file_name );
        if ( updateConfigDb("update config set parameter = '1' where ID = 186") ) $err_cnt += 1;
        $showStatusOutput = 1;
        ##echo "<br>action=" . $showStatusOutput . "<br>";
    }
}

function makeSelectortGPIO( $id ) {
    $configValue = config_read( $id );
    for ( $i=2; $i<28; $i++ ) {
        if ( $configValue == $i ) {
            $selected = 'selected="selected"';
        } else {
            $selected = '';
        }
        echo '<option ' . $selected. ' value="'. $i . '" >GPIO' . $i .'</option>';
    }

}

if ( isset( $_POST["fs_rb_kwhmeter"] ) ) { //ok
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ "fs_rb_kwhmeter" ] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 125") ) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 125") ) $err_cnt += 1;
    }
}

if( isset($_POST["puls_kwh_value"]) ) { //ok
    if ( $err_cnt == -1 ) $err_cnt=0;
    $float = (float)inputClean($_POST["puls_kwh_value"]);
    if ( $float > 1000 or $float < 0 ) { $float=1; }
    if ( updateConfigDb("update config set parameter = '" . (string)$float . "' where ID = 127"))  $err_cnt += 1;
}

if( isset($_POST["kwhmeter_high_value"]) ) { //ok
    if ( $err_cnt == -1 ) $err_cnt=0;
    $float = (float)inputClean($_POST["kwhmeter_high_value"]);
    if ( $float > 1000000 or $float < 0 ) { $float=0; }
    if ( updateConfigDb("update config set parameter = '" . (string)$float . "' where ID = 130"))  $err_cnt += 1;
}

if( isset($_POST["kwhmeter_low_value"]) ) { //ok
    if ( $err_cnt == -1 ) $err_cnt=0;
    $float = (float)inputClean($_POST["kwhmeter_low_value"]);
    if ( $float > 1000000 or $float < 0 ) { $float=0; }
    if ( updateConfigDb("update config set parameter = '" . (string)$float . "' where ID = 131"))  $err_cnt += 1;
}

if( isset($_POST["timestamp_kwhmeter"]) ) { //ok
    if ( $err_cnt == -1 ) $err_cnt=0;
    
    $val = timestampClean( $_POST["timestamp_kwhmeter"] );
    if ( strlen( $val ) != 19 ) {
        $val = '';
    } 
    if ( updateConfigDb("update config set parameter = '" .$val . "' where ID = 132") )  $err_cnt += 1;
}

if( isset($_POST["gpio_kwhmeter"]) ) { //ok
    if ( $err_cnt == -1 ) $err_cnt=0;
    $int = (int)inputClean($_POST["gpio_kwhmeter"]);
    $configValue = config_read( 126 );
    #echo "<br>";
    #echo $int . "<br>";
    #echo $configValue  . "<br>";
    if ( updateConfigDb( "update config set parameter = '" . (string)$int . "' where ID = 126") )  $err_cnt += 1;
}

?>
<!doctype html>
<html lang="nl">
<head>
<meta name="robots" content="noindex">
<title>Energie levering configuratie</title>
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

function readJsonApiStatus(){ 
    $.getScript( "./api/v1/status", function( data, textStatus, jqxhr ) {
      try {
        var jsonarr = JSON.parse(data); 
        for (var j=0;  j<jsonarr.length; j++){   
                switch(jsonarr[j][0]) {
                    case 109:
                        $('#kwhmeter_puls_timestamp').text( jsonarr[j][1] );
                        break;
            }
        }
      } catch(err) {
          console.log( err );
      }
   });
}

function readJsonApiHistoryPowerDay( cnt ){ 
    $.getScript( "/api/v1/powerproduction/day?limit=" + cnt, function( data, textStatus, jqxhr ) {
        try {
        var jsondata = JSON.parse(data); 

        if ( jsondata.length == 0 ) {
            $('#verbruikKwhHoog').html(   padXX( 0 ,5, 3 ) + '&nbsp;kWh');
            $('#verbruikKwhlaag').html(   padXX( 0 ,5, 3 ) + '&nbsp;kWh');
            $('#verbruikKwhTotaal').html( padXX( 0 ,5, 3 ) + '&nbsp;kWh');
        } else {
            $('#verbruikKwhHoog').html(   padXX( jsondata[0][8]  ,5, 3 ) + '&nbsp;kWh' );
            $('#verbruikKwhLaag').html(   padXX( jsondata[0][9]  ,5, 3 ) + '&nbsp;kWh' );
            $('#verbruikKwhTotaal').html( padXX( jsondata[0][10] ,5, 3 ) + '&nbsp;kWh' );
            
        }
      } catch(err) {}
   });
}

function readUpgradeLogging(){ 
    $.get( '/txt/txt-powerproduction-reset-status.php', function( response, status, xhr ) {
        if ( status == "error" ) {
            $("#upgrade_asssist_logging").html('Data niet beschikbaar.');
        }
        if ( response.length > 0 ) {
            $('#upgrade_asssist_logging').html( response );
        } else {
            if ( document.getElementById('upgrade_asssist_logging').innerHTML.length < 60 ) { // prevent the flashing of the log window.
                $('#upgrade_asssist_logging').html( "<b>Even geduld aub, gegevens worden verwerkt.</b><br>" );
            }
        }
    }); 
}

function LoadData() {
    timout_setting = 2000
    clearTimeout(initloadtimer);
    readJsonApiStatus();
    readJsonApiHistoryPowerDay( 1 );
    if ( document.getElementById('counter_status').style.display == "block" ) {
        readUpgradeLogging();
        timout_setting = 150;
    }
    initloadtimer = setInterval( function(){ LoadData(); }, timout_setting );
}

$(function () {
    toLocalStorage('config-powerproduction-menu',window.location.pathname);
    centerPosition('#counter_status');
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
                <?php menu_control( 15 );?>
            </div>
            
            <div id="right-wrapper-config"> <!-- right block -->
                <!-- inner block right part of screen -->
                <?php config_page_menu_header_powerproduction( 0 ); ?> 

                <div id="right-wrapper-config-left-4">
                    <!-- start of content -->
                    <form name="formvalues" id="formvalues" method="POST">

                        <div class="frame-4-top">
                            <span class="text-15">opgewekte kWh</span>
                        </div>
                        <div class="frame-4-bot">
                           
                            <div class="float-left">
                                <p class="p-1"></p>
                                <i class="text-10 pad-14 fas fa-map-pin"></i>
                                <label class="text-10">GPIO pin selectie</label> 
                                <p class="p-1"></p>
                                <i class="pad-7 text-10 fas fa-toggle-off"></i>
                                <label class="text-10">kWh S0 puls meting actief</label>
                                <p class="p-1"></p>
                                <i class="pad-7 text-10 fas fa-bolt"></i>
                                <label class="text-10" title='<?php echo strIdx( 92 );?>'>puls waarde in kWh</label>
                                <p class="p-1"></p>
                                <i class="pad-27 text-10 fas fa-bolt"></i>
                                <label class="text-10" title='<?php echo strIdx( 93 );?>'>kWh meterstand hoog tarief in kWh</label>
                                <p class="p-1"></p>
                                <i class="pad-27 text-10 fas fa-bolt"></i>
                                <label class="text-10" title='<?php echo strIdx( 93 );?>'>kWh meterstand laag tarief in kWh</label>
                                <p class="p-1"></p>
                                <i class="pad-27 text-10 far fa-clock"></i>
                                <label class="text-10" title='<?php echo strIdx( 96 );?>'>kWh meterstand timestamp</label>
                                <p class="p-1"></p>
                                <i class="pad-7 text-10 fas fa-toggle-off"></i>
                                <label class="text-10" title='<?php echo strIdx( 94 );?>'>kWh meterstand reset</label>
                                <p class="p-1"></p>
                                <i class="pad-7 text-10 fas fa-bolt"></i>
                                <label class="text-10" title='<?php echo strIdx( 97 );?>'>kWh meterstand hoog tarief</label>
                                <p class="p-1"></p>
                                <i class="pad-7 text-10 fas fa-bolt"></i>
                                <label class="text-10" title='<?php echo strIdx( 97 );?>'>kWh meterstand laag tarief</label>
                                <p class="p-1"></p>
                                <i class="pad-7 text-10 fas fa-bolt"></i>
                                <label class="text-10" title='<?php echo strIdx( 97 );?>'>kWh meterstand totaal</label>
                                <p class="p-1"></p>
                                <i class="pad-7 text-10 far fa-clock"></i>
                                <label class="text-10" title='<?php echo strIdx( 95 );?>'>tijdstip kWh puls</label>
                            </div>
                            <div class="float-right pad-1">
                                <p class="p-1"></p>
                                <select class="select-1 color-select color-input-back cursor-pointer" name="gpio_kwhmeter" id="gpio_kwhmeter">
                                    <?php makeSelectortGPIO( 126 ) ;?>
                                </select>
                                <p class="p-1"></p>
                                <div class=''>
                                    <input class="cursor-pointer" id="fs_rb_kwhmeter_on"  name="fs_rb_kwhmeter" type="radio" value="1" <?php if ( config_read( 125 ) == 1 ) { echo 'checked'; }?>>Aan
                                    <input class="cursor-pointer" id="fs_rb_kwhmeter_off" name="fs_rb_kwhmeter" type="radio" value="0" <?php if ( config_read( 125 ) == 0 ) { echo 'checked'; }?>>Uit
                                </div>
                                <p class="p-1"></p>
                                <input title='<?php echo strIdx( 92 );?>' class="input-13 color-settings color-input-back" id="puls_kwh_value" name="puls_kwh_value" type="text" value="<?php echo config_read( 127 );?>">
                                <p class="p-1"></p>
                                <input title='<?php echo strIdx( 93 );?>' class="input-13 color-settings color-input-back" id="kwhmeter_high_value" name="kwhmeter_high_value" type="text" value="<?php echo config_read( 130 );?>">
                                <p class="p-1"></p>
                                <input title='<?php echo strIdx( 93 );?>' class="input-13 color-settings color-input-back" id="kwhmeter_low_value" name="kwhmeter_low_value" type="text" value="<?php echo config_read( 131 );?>">
                                <p class="p-1"></p>
                                <input title='<?php echo strIdx( 96 );?>' placeholder="YYYY-MM-DD HH:MM:00" class="input-14 color-settings color-input-back" id="timestamp_kwhmeter" name="timestamp_kwhmeter" type="text" value="<?php echo config_read( 132 );?>" >
                                <p class="p-1"></p>
                                <div title='<?php echo strIdx( 94 );?>'>
                                    <input class="cursor-pointer" id="fs_rb_kwhmeter_reset_on"  name="fs_rb_kwhmeter_reset" type="radio" value="1">Aan
                                    <input class="cursor-pointer" id="fs_rb_kwhmeter_reset_off" name="fs_rb_kwhmeter_reset" type="radio" value="0" checked>Uit
                                </div>
                                <p class="p-1"></p>
                                <div title='<?php echo strIdx( 97 );?>' class="text-10 pad-20" ><span id="verbruikKwhHoog">onbekend</span></div>
                                <p class="p-1"></p>
                                <div title='<?php echo strIdx( 97 );?>' class="text-10 pad-20" ><span id="verbruikKwhLaag">onbekend</span></div>
                                <p class="p-1"></p>
                                <div title='<?php echo strIdx( 97 );?>' class="text-10 pad-20" ><span id="verbruikKwhTotaal">onbekend</span></div>
                                <p class="p-1"></p>
                                <div title='<?php echo strIdx( 95 );?>' class="text-10 pad-20" ><span id="kwhmeter_puls_timestamp">onbekend</span></div>
                            </div>
                        </div>
                        <p></p>
                        
                        <!-- placeholder variables for session termination -->
                        <input type="hidden" name="logout" id="logout" value="">
                    </form>
                </div>

                <div id="right-wrapper-config-right-4">
                    <div class="frame-4-top">
                        <span class="text-15">hulp</span>
                    </div>
                    <div class="frame-4-bot text-10">
                        <img class="pos-1" alt="PI GPIO pin layout" src="./img/pin_layout.svg">
                    </div>
                </div>
            </div>
            <!-- end inner block right part of screen -->
    </div>

    <!-- start block -->
    <div id="counter_status" class="pos-45" style="display: none">
        <div class='close_button-2' id="assist_logging_close">
            <i class="color-select fas fa-times-circle" data-fa-transform="grow-6"></i>
        </div>
    <div class="frame-4-top">
        <span class="text-15">Meterstand reset logging</span>
            </div>
                <div class="frame-4-bot">
                    <div id="upgrade_asssist_logging" class="text-9">
                     
                    </div>
                </div>
        </div>
    </div>
    <!-- end block -->

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

jQuery.validator.addMethod("ztatz_gpio", function(value, element) {
        if ( document.getElementById("gpio_kwhmeter").value == document.getElementById("gpio_list").value ) {
            return false;
        }
        if ( document.getElementById("gpio_kwhmeter").value == document.getElementById("gpio_list_tarif").value ) {
            d
            return false;
        }   
        document.getElementById("gpio_list").style.borderColor = "#a6a6a6";
        return true;
}, '');

$(function() {
    $("#formvalues").validate({
        rules: {
            'gpio_kwhmeter':{
                required: false,
                //ztatz_gpio:true
            },
            'timestamp_kwhmeter': {
                required: false,
                //minlength: 19,
                //maxlength: 19,
                ztatz_time_format: true
            },
            'water_m3_value': {
                required: true,
                number: true,
                max: 1000000,
                min: 0
            },
            'puls_kwh_value': {
                required: true,
                number: true,
                max: 1000,
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
});

$('#assist_logging_close').click(function() {    
   hideStuff('counter_status');
});

centerPosition('#counter_status');

</script>
<?php 
if ( $showStatusOutput == 1 ) {
    echo "<script>showStuff('counter_status');</script>";
}
echo autoLogout();?>
</body>
</html>