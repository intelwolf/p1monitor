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
include_once '/p1mon/www/util/pageclock.php';

#print_r($_POST);
loginInit();
passwordSessionLogoutCheck();
$err_cnt = -1;

$noInetCheck = isInternetIPAllowed();
$localip     = validLocalIpAdress(getClientIP());
//$localip        = False;
//$noInetCheck    = False;
if( $localip == False ){ 
        if( $noInetCheck == False ) {
            die();
        }
}

$update_MQTT_setting_flag = False;  #set this flag to true to update the database, so the Pyhton P1MQTY.py is triggert to update
$err_cnt = -1;

if ( isset($_POST["client_id"]) ) { 
    $input = inputClean( trim($_POST["client_id"]) );
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '". $input . "' where ID = 105") ) $err_cnt += 1;
    $update_MQTT_setting_flag = True;
}

if ( isset($_POST["topic_prefix"]) ) { 
    $input = inputClean( trim($_POST["topic_prefix"]) );
    $input = str_replace('/', '', $input ); # topic must not contain /
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '". $input . "' where ID = 106") ) $err_cnt += 1;
    $update_MQTT_setting_flag = True;
}

if ( isset($_POST["broker_host"]) ) { 
    $input = inputClean( trim($_POST["broker_host"]) );
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '". $input . "' where ID = 109") ) $err_cnt += 1;
    $update_MQTT_setting_flag = True;
}

if ( isset($_POST["broker_port"]) ) { 
    $input = inputCleanDigitsOnly( trim($_POST["broker_port"]) );
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '". $input . "' where ID = 110") ) $err_cnt += 1;
    $update_MQTT_setting_flag = True;
}

if ( isset($_POST["keep_alive"]) ) { 
    $input = inputCleanDigitsOnly( trim($_POST["keep_alive"]) );
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '". $input . "' where ID = 111") ) $err_cnt += 1;
    $update_MQTT_setting_flag = True;
}

if ( isset($_POST["broker_user_name"]) ) { 
    $input = inputClean( trim($_POST["broker_user_name"]) );
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '". $input . "' where ID = 107") ) $err_cnt += 1;
    $update_MQTT_setting_flag = True;
}

if ( isset($_POST["broker_user_pw"]) ) { 
    $input = trim($_POST["broker_user_pw"]);
    $password = encodeString ($input, 'mqttclpw');
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".$password."' where ID = 108")) $err_cnt += 1;
    $update_MQTT_setting_flag = True;
}

if ( isset($_POST["qos_list"]) ) { 
    $input = inputCleanDigitsOnly( trim($_POST["qos_list"]) );
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '". $input . "' where ID = 113") ) $err_cnt += 1;
    $update_MQTT_setting_flag = True;
}

if ( isset($_POST["mqtt_version_list"]) ) { 
    $input = inputCleanDigitsOnly( trim($_POST["mqtt_version_list"]) );
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '". $input . "' where ID = 112") ) $err_cnt += 1;
    $update_MQTT_setting_flag = True;
}

if ( isset($_POST["publish_smartmeter_data"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["publish_smartmeter_data"] == '1' ) {
        if ( updateConfigDb( "update config set parameter = '1' where ID = 114") )$err_cnt += 1;
    } else {
        if ( updateConfigDb( "update config set parameter = '0' where ID = 114") )$err_cnt += 1;
    }
    $update_MQTT_setting_flag = True;
}

if ( isset($_POST["publish_watermeter_data"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["publish_watermeter_data"] == '1' ) {
        if ( updateConfigDb( "update config set parameter = '1' where ID = 115") )$err_cnt += 1;
    } else {
        if ( updateConfigDb( "update config set parameter = '0' where ID = 115") )$err_cnt += 1;
    }
    $update_MQTT_setting_flag = True;
}

if ( isset($_POST["publish_weather_data"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["publish_weather_data"] == '1' ) {
        if ( updateConfigDb( "update config set parameter = '1' where ID = 116") )$err_cnt += 1;
    } else {
        if ( updateConfigDb( "update config set parameter = '0' where ID = 116") )$err_cnt += 1;
    }
    $update_MQTT_setting_flag = True;
}

if ( isset($_POST["publish_indoortemperaturer_data"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["publish_indoortemperaturer_data"] == '1' ) {
        if ( updateConfigDb( "update config set parameter = '1' where ID = 117") )$err_cnt += 1;
    } else {
        if ( updateConfigDb( "update config set parameter = '0' where ID = 117") )$err_cnt += 1;
    }
    $update_MQTT_setting_flag = True;
}

if ( isset($_POST["publish_phase_data"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["publish_phase_data"] == '1' ) {
        if ( updateConfigDb( "update config set parameter = '1' where ID = 120") )$err_cnt += 1;
    } else {
        if ( updateConfigDb( "update config set parameter = '0' where ID = 120") )$err_cnt += 1;
    }
    $update_MQTT_setting_flag = True;
}

if ( isset($_POST["publish_ownpowerproduction_data"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["publish_ownpowerproduction_data"] == '1' ) {
        if ( updateConfigDb( "update config set parameter = '1' where ID = 136") )$err_cnt += 1;
    } else {
        if ( updateConfigDb( "update config set parameter = '0' where ID = 136") )$err_cnt += 1;
    }
    $update_MQTT_setting_flag = True;
}

if ( isset($_POST["publish_kwhgas_data"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["publish_kwhgas_data"] == '1' ) {
        if ( updateConfigDb( "update config set parameter = '1' where ID = 176") )$err_cnt += 1;
    } else {
        if ( updateConfigDb( "update config set parameter = '0' where ID = 176") )$err_cnt += 1;
    }
    $update_MQTT_setting_flag = True;
}

if ( isset($_POST["publish_finance_data"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["publish_finance_data"] == '1' ) {
        if ( updateConfigDb( "update config set parameter = '1' where ID = 177") )$err_cnt += 1;
    } else {
        if ( updateConfigDb( "update config set parameter = '0' where ID = 177") )$err_cnt += 1;
    }
    $update_MQTT_setting_flag = True;
}



if ( isset( $_POST["fs_rb_mqtt"] ) ) { //ok
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ "fs_rb_mqtt" ] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 135") ) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 135") ) $err_cnt += 1;
    }
}

if ($update_MQTT_setting_flag == True) {
    updateConfigDb( "update config set parameter = '1' where ID = 118" );
}

function makeSelectorQoSSelector($id) {
    $configValue = config_read($id);
    $val_0=$val_1=$val_2='';

    if ($configValue == '0' ) { $val_0  = 'selected="selected"'; }
    if ($configValue == '1' ) { $val_1  = 'selected="selected"'; }
    if ($configValue == '2' ) { $val_2  = 'selected="selected"'; }
    
    echo '<option ' . $val_0  . ' value="0"  >0</option>';
    echo '<option ' . $val_1  . ' value="1"  >1</option>';
    echo '<option ' . $val_2  . ' value="2"  >2</option>';
}

function makeSelectorMQTTProctocolVersionSelector($id) {
    $configValue = config_read($id);
    $val_3=$val_4=$val_5='';

    if ($configValue == '3' ) { $val_3 = 'selected="selected"'; }
    if ($configValue == '4' ) { $val_4 = 'selected="selected"'; }
    if ($configValue == '5' ) { $val_5 = 'selected="selected"'; }
    
    echo '<option ' . $val_3 . ' value="3" >MQTT V3.1.0</option>';
    echo '<option ' . $val_4 . ' value="4" >MQTT V3.1.1</option>';
    echo '<option ' . $val_5 . ' value="5" >MQTT V5.0</option>';
}

?>
<!doctype html>
<html lang="nl">
<head>
<meta name="robots" content="noindex">
<title>MQTT configuratie</title>
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
                    case 96:
                        $('#publish_timestamp').text( jsonarr[j][1]);
                        break;
                    case 97:
                        $('#publish_status').text( jsonarr[j][1]);
                        break;
            }
        }
      } catch(err) {
          console.log( err );
      }
   });
}

function readJsonTopicList(){ 
        $.getScript( "./json/mqtt_topics.json", function( data, textStatus, jqxhr ) {
        try {
            htmlString = "<ol type='1'>";
            var jsondata = JSON.parse(data); 
            for (var j =0;  j<jsondata.length; j++){    
                htmlString = htmlString + "<li>" + jsondata[j] + "</li>";
            }
            htmlString = htmlString + "</ol>";
            $('#topic_list').html( htmlString );
          } catch(err) {}
       });
    }


function LoadData() {
    clearTimeout(initloadtimer);
    readJsonApiStatus();
    readJsonTopicList();
    initloadtimer = setInterval(function(){LoadData();}, 5000);
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
                <?php menu_control( 14 );?>
            </div>
            
            <div id="right-wrapper-config"> <!-- right block -->
            <!-- inner block right part of screen -->
                <div id="right-wrapper-config-left-4">
                    <!-- start of content -->
                    <form name="formvalues" id="formvalues" method="POST">
                        <div class="frame-4-top">
                            <span class="text-15">MQTT client parameters</span>
                        </div>
                        
                        <div class="frame-4-bot">
                            <div class="float-left">
                                <i class="pad-7 text-10 fas fa-toggle-off"></i>
                                <label class="text-10">MQTT programma is actief</label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-7 fas fa-wrench"></i>
                                <label class="text-10">client ID</label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-27 fas fa-wrench"></i>
                                <label class="text-10">topic voorvoegsel</label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-27 fas fa-server"></i>
                                <label class="text-10">broker servernaam / IP</label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-27 fas fa-server"></i>
                                <label class="text-10">broker IP poort</label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-27 far fa-clock"></i>
                                <label class="text-10">broker keep alive tijd</label>
                                <p class="p-1"></p>

                                <i class="text-10 pad-27 fas fa-user"></i>
                                <label class="text-10">broker gebruikers naam</label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-27 fas fa-lock"></i>
                                <label class="text-10">broker gebruikers wachtwoord</label>
                                <p class="p-1"></p>

                                <i class="text-10 pad-9 fas fa-medal"></i>
                                <label class="text-10">QoS (Quality of Service)</label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-9 fas fa-server"></i>
                                <label class="text-10">protocol versie</label>
                                <p class="p-1"></p>
                                <br>
                                <label class="text-10">laatst verstuurde bericht:</label>
                                <p class="p-1"></p>
                                <label class="text-10">status</label>
                                <p class="p-1"></p>
                            </div>

                            <div class="float-left pad-1">
                                <div class='pad-14'>
                                    <input class="cursor-pointer" id="fs_rb_mqtt_on"  name="fs_rb_mqtt" type="radio" value="1" <?php if ( config_read( 135 ) == 1 ) { echo 'checked'; }?>>Aan
                                    <input class="cursor-pointer" id="fs_rb_mqtt_off" name="fs_rb_mqtt" type="radio" value="0" <?php if ( config_read( 135 ) == 0 ) { echo 'checked'; }?>>Uit
                                </div>
                                <p class="p-1"></p>
                                <input class="input-14 color-settings color-input-back" id="client_id" name="client_id" type="text" value="<?php echo config_read( 105 );?>">
                                <p class="p-1"></p>
                                <input class="input-14 color-settings color-input-back" id="topic_prefix" name="topic_prefix" type="text" value="<?php echo config_read( 106 );?>">
                                <p class="p-1"></p>
                                <input class="input-14 color-settings color-input-back" id="broker_host" name="broker_host" type="text" value="<?php echo config_read( 109 );?>">
                                <p class="p-1"></p>
                                <input class="input-14 color-settings color-input-back" id="broker_port" name="broker_port" type="text" value="<?php echo config_read( 110 );?>">
                                <p class="p-1"></p>
                                <input class="input-14 color-settings color-input-back" id="keep_alive" name="keep_alive" type="text" value="<?php echo config_read( 111 );?>">
                                <p class="p-1"></p>
                                <input class="input-14 color-settings color-input-back" id="broker_user_name" name="broker_user_name" type="text" value="<?php echo config_read( 107 );?>">
                                <p class="p-1"></p>

                                <div class="content-wrapper">
                                    <input class="input-14 color-settings color-input-back" id="broker_user_pw" name="broker_user_pw" type="password" value="<?php echo decodeString( 108, 'mqttclpw');?>">
                                    <div id="broker_passwd" onclick="toggelPasswordVisibility('broker_user_pw')" class="float-right pad-33 cursor-pointer">    
                                        <span><i class="color-menu pad-7 fas fa-eye"></i></span>
                                    </div>
                                </div>
                                <p class="p-1"></p>

                                <select class="select-6 color-select color-input-back cursor-pointer" id="qos_list" name="qos_list">
                                    <?php makeSelectorQoSSelector( 113 );?>
                                </select>
                                <p class="p-1"></p>

                                <select class="select-6 color-select color-input-back cursor-pointer" id="mqtt_version_list" name="mqtt_version_list">
                                    <?php makeSelectorMQTTProctocolVersionSelector( 112 );?>
                                </select>
                                <p class="p-1"></p>
                                <br>
                                <label class="text-10"><span id="publish_timestamp"></span></label>
                                <p class="p-1"></p>
                                <div class="text-10 pos-51"><span id="publish_status"></span></div>
                                <p class="p-1"></p>

                            </div>

                            <div class="rTable text-10">

                                <div class="rTableRow" title="Gegevens wel of niet verwerken.">
                                    <div class="rTableCell width-290">
                                        <i class="fas fa-toggle-off"></i>
                                        <label>verzenden smartmeter</label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="cursor-pointer" id="publish_smartmeter_data_on"  name="publish_smartmeter_data" type="radio" value="1" <?php if ( config_read( 114 ) == 1 ) { echo 'checked'; }?>>Aan
                                        <input class="cursor-pointer" id="publish_smartmeter_data_off" name="publish_smartmeter_data" type="radio" value="0" <?php if ( config_read( 114 ) == 0 ) { echo 'checked'; }?>>Uit
                                    </div>
                                </div> <!-- row end -->

                                <div class="rTableRow" title="Gegevens wel of niet verwerken.">
                                    <div class="rTableCell width-290">
                                        <i class="fas fa-toggle-off"></i>
                                        <label>verzenden watermeter</label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="cursor-pointer" id="publish_watermeter_data_on"  name="publish_watermeter_data" type="radio" value="1" <?php if ( config_read( 115 ) == 1 ) { echo 'checked'; }?>>Aan
                                        <input class="cursor-pointer" id="publish_watermeter_data_off" name="publish_watermeter_data" type="radio" value="0" <?php if ( config_read( 115 ) == 0 ) { echo 'checked'; }?>>Uit
                                    </div>
                                </div> <!-- row end -->

                                <div class="rTableRow" title="Gegevens wel of niet verwerken.">
                                    <div class="rTableCell width-290">
                                        <i class="fas fa-toggle-off"></i>
                                        <label>verzenden weer</label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="cursor-pointer" id="publish_weather_data_on"  name="publish_weather_data" type="radio" value="1" <?php if ( config_read( 116 ) == 1 ) { echo 'checked'; }?>>Aan
                                        <input class="cursor-pointer" id="publish_weather_data_off" name="publish_weather_data" type="radio" value="0" <?php if ( config_read( 116 ) == 0 ) { echo 'checked'; }?>>Uit
                                    </div>
                                </div> <!-- row end -->

                                <div class="rTableRow" title="Gegevens wel of niet verwerken.">
                                    <div class="rTableCell width-290">
                                        <i class="fas fa-toggle-off"></i>
                                        <label>verzenden binnentemperatuur</label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="cursor-pointer" id="publish_indoortemperature_data_on"  name="publish_indoortemperaturer_data" type="radio" value="1" <?php if ( config_read( 117 ) == 1 ) { echo 'checked'; }?>>Aan
                                        <input class="cursor-pointer" id="publish_indoortemperature_data_off" name="publish_indoortemperaturer_data" type="radio" value="0" <?php if ( config_read( 117 ) == 0 ) { echo 'checked'; }?>>Uit
                                    </div>
                                </div> <!-- row end -->

                                <div class="rTableRow" title="Gegevens wel of niet verwerken.">
                                    <div class="rTableCell width-290">
                                        <i class="fas fa-toggle-off"></i>
                                        <label>verzenden fase</label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="cursor-pointer" id="publish_phase_data_on"  name="publish_phase_data" type="radio" value="1" <?php if ( config_read( 120 ) == 1 ) { echo 'checked'; }?>>Aan
                                        <input class="cursor-pointer" id="publish_phase_data_off" name="publish_phase_data" type="radio" value="0" <?php if ( config_read( 120 ) == 0 ) { echo 'checked'; }?>>Uit
                                    </div>
                                </div> <!-- row end -->

                                <div class="rTableRow" title="Gegevens wel of niet verwerken.">
                                    <div class="rTableCell width-290">
                                        <i class="fas fa-toggle-off"></i>
                                        <label>verzenden opgewekte vermogen</label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="cursor-pointer" id="publish_ownpowerproduction_data_on"  name="publish_ownpowerproduction_data" type="radio" value="1" <?php if ( config_read( 136 ) == 1 ) { echo 'checked'; }?>>Aan
                                        <input class="cursor-pointer" id="publish_ownpowerproduction_data_off" name="publish_ownpowerproduction_data" type="radio" value="0" <?php if ( config_read( 136 ) == 0 ) { echo 'checked'; }?>>Uit
                                    </div>
                                </div> <!-- row end -->

                                <div class="rTableRow" title="Gegevens wel of niet verwerken.">
                                    <div class="rTableCell width-290">
                                        <i class="fas fa-toggle-off"></i>
                                        <label>verzenden kWh en gas</label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="cursor-pointer" id="publish_kwhgas_data_on"  name="publish_kwhgas_data" type="radio" value="1" <?php if ( config_read( 176 ) == 1 ) { echo 'checked'; }?>>Aan
                                        <input class="cursor-pointer" id="publish_kwhgas_data_off" name="publish_kwhgas_data" type="radio" value="0" <?php if ( config_read( 176 ) == 0 ) { echo 'checked'; }?>>Uit
                                    </div>
                                </div> <!-- row end -->

                                <div class="rTableRow" title="Gegevens wel of niet verwerken.">
                                    <div class="rTableCell width-290">
                                        <i class="fas fa-toggle-off"></i>
                                        <label>verzenden financieel</label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="cursor-pointer" id="publish_finance_data_on"  name="publish_finance_data" type="radio" value="1" <?php if ( config_read( 177 ) == 1 ) { echo 'checked'; }?>>Aan
                                        <input class="cursor-pointer" id="publish_finance_data_off" name="publish_finance_data" type="radio" value="0" <?php if ( config_read( 177 ) == 0 ) { echo 'checked'; }?>>Uit
                                    </div>
                                </div> <!-- row end -->

                            </div> <!-- table end -->
                            
                        </div>
                        <br>
                        <div class="frame-4-top">
                            <span class="text-15">MQTT published topics</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="text-10" id="topic_list"> </div>
                        </div>
                        <p class="p-1"></p>
                        <!-- placeholder variables for session termination -->
                        <input type="hidden" name="logout" id="logout" value="">
                    </form>
                </div>

                <div id="right-wrapper-config-right-4">
                    <div class="frame-4-top">
                        <span class="text-15">hulp</span>
                    </div>
                    <div class="frame-4-bot text-10">    
                        <?php echo strIdx( 76 );?>
                    </div>
                </div>
            </div>    
            <!-- end inner block right part of screen -->
    </div>
    <script>

$(function() {
    $("#formvalues").validate({
        rules: {
            'broker_port':{
                required: true,
                number: true,
                max: 65535,
                min: 1
            },
            'keep_alive':{
                required: true,
                number: true,
                max: 3600,
                min: 10
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
<?php echo autoLogout();?>
</body>
</html>