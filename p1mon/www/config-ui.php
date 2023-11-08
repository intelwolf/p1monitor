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

$sw_off  = strIdx( 193 );
$sw_on   = strIdx( 192 );
$seconds = strIdx( 194 );
$minutes = strIdx( 120 );
$hour    = strIdx( 129 );

$err_cnt = -1;
if ( isset($_POST["actueel_e"]) ) { 
    $err_cnt = 0;
    if ($_POST["actueel_e"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 18"))$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 18"))$err_cnt += 1;
    }
}

if ( isset($_POST["historie_e"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["historie_e"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 19"))$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 19"))$err_cnt += 1;
    }
}

if ( isset($_POST["historie_g"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["historie_g"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 20"))$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 20"))$err_cnt += 1;
    }
}

if ( isset($_POST["finaciel"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["finaciel"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 21"))$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 21"))$err_cnt += 1;
    }
}

if ( isset($_POST["informatie"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["informatie"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 22"))$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 22"))$err_cnt += 1;
    }
}

if ( isset($_POST["meterstanden"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["meterstanden"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 62"))$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 62"))$err_cnt += 1;
    }
}

if ( isset($_POST["verwarming"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["verwarming"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 46"))$err_cnt += 1;
        if ( updateConfigDb("update config set parameter = '1' where ID = 44"))$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 46"))$err_cnt += 1;
        if ( updateConfigDb("update config set parameter = '0' where ID = 44"))$err_cnt += 1;
    }
}


if ( isset($_POST["watermeter"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["watermeter"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 102"))$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 102"))$err_cnt += 1;
    }
}

if ( isset($_POST["kWhlevering"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["kWhlevering"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 129"))$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 129"))$err_cnt += 1;
    }
}

if ( isset($_POST["kWhleveringSolarEdge"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["kWhleveringSolarEdge"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 147"))$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 147"))$err_cnt += 1;
    }
}

if ( isset($_POST["ui_water_hide"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["ui_water_hide"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 157"))$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 157"))$err_cnt += 1;
    }
}

if ( isset($_POST["ui_gas_hide"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["ui_gas_hide"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 158"))$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 158"))$err_cnt += 1;
    }
}

if ( isset($_POST["ui_w2kw"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["ui_w2kw"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 180") )$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 180") )$err_cnt += 1;
    }
}


if ( isset($_POST["ui_peak_kw_hide"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["ui_peak_kw_hide"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 206") )$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 206") )$err_cnt += 1;
    }
}


if ( isset($_POST["verbruik_list_main"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".preg_replace('/\D/', '', $_POST["verbruik_list_main"])."' where ID = 52"))$err_cnt += 1;
}


if ( isset($_POST["levering_list_main"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".preg_replace('/\D/', '', $_POST["levering_list_main"])."' where ID = 53"))$err_cnt += 1;
}


if ( isset($_POST["verbruik_g_list_main"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".preg_replace('/\D/', '', $_POST["verbruik_g_list_main"])."' where ID = 54"))$err_cnt += 1;
}

if ( isset($_POST["verbruik_list"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".preg_replace('/\D/', '', $_POST["verbruik_list"])."' where ID = 24"))$err_cnt += 1;
}

if ( isset($_POST["levering_list"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".preg_replace('/\D/', '', $_POST["levering_list"])."' where ID = 23"))$err_cnt += 1;
}

if ( isset($_POST["verbruik_g_list"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".preg_replace('/\D/', '', $_POST["verbruik_g_list"])."' where ID = 41"))$err_cnt += 1;
}

if ( isset($_POST["custom_ui_list"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".preg_replace('/\D/', '', $_POST["custom_ui_list"])."' where ID = 43"))$err_cnt += 1;
}

if ( isset($_POST["ui_language"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".preg_replace('/\D/', '', $_POST["ui_language"])."' where ID = 148"))$err_cnt += 1;
}

if ( isset($_POST["levering_list_kwh"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".preg_replace('/\D/', '', $_POST["levering_list_kwh"])."' where ID = 56"))$err_cnt += 1;
}

if ( isset($_POST["verbruik_list_kwh"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".preg_replace('/\D/', '', $_POST["verbruik_list_kwh"])."' where ID = 57"))$err_cnt += 1;
}

if ( isset($_POST["watt_fase_gauge"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".preg_replace('/\D/', '', $_POST["watt_fase_gauge"])."' where ID = 124"))$err_cnt += 1;
}

if ( isset($_POST["amperage_fase_gauge"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".preg_replace('/\D/', '', $_POST["amperage_fase_gauge"])."' where ID = 123"))$err_cnt += 1;
}

if ( isset($_POST["voorspelling"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["voorspelling"] == '1' ) {
        
        if ( updateConfigDb("update config set parameter = '1' where ID = 59"))$err_cnt += 1;
    } else {
        
        if ( updateConfigDb("update config set parameter = '0' where ID = 59"))$err_cnt += 1;
    }
}

if ( isset($_POST["drie_fasen"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["drie_fasen"] == '1' ) {
        
        if ( updateConfigDb("update config set parameter = '1' where ID = 61"))$err_cnt += 1;
    } else {
        
        if ( updateConfigDb("update config set parameter = '0' where ID = 61"))$err_cnt += 1;
    }
}

if ( isset($_POST["ui_header"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["ui_header"] == '1' ) {
        
        if ( updateConfigDb("update config set parameter = '1' where ID = 134"))$err_cnt += 1;
    } else {
        
        if ( updateConfigDb("update config set parameter = '0' where ID = 134"))$err_cnt += 1;
    }
}


if ( isset($_POST["scrsav_wait"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".preg_replace('/\D/', '', $_POST["scrsav_wait"])."' where ID = 79"))$err_cnt += 1;
}

if ( isset($_POST["scrsav_auto_off"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".preg_replace('/\D/', '', $_POST["scrsav_auto_off"])."' where ID = 80"))$err_cnt += 1;
}

if ( isset($_POST["verwarming_in_label"]) ) { 
    $input = inputClean( trim($_POST["verwarming_in_label"]) );
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '". $input . "' where ID = 121") ) $err_cnt += 1;
}

if ( isset($_POST["verwarming_uit_label"]) ) { 
    $input = inputClean( trim($_POST["verwarming_uit_label"]) );
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '". $input . "' where ID = 122") ) $err_cnt += 1;
}

if ( isset($_POST["phase_v_max"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["phase_v_max"],1,499.9,1)."' where ID = 173")) $err_cnt += 1;
}

if ( isset($_POST["phase_v_min"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["phase_v_min"],1,499.9,1)."' where ID = 174")) $err_cnt += 1;
}

function makeSelectorSec( $id ) {

    global $sw_off;
    global $sw_on;
    global $seconds;
    global $minutes;
    global $hour;

    $configValue = config_read($id);
    $val_0=$val_10=$val_30=$val_60=$val_300=$val_600=$val_900=$val_1800=$val_3600='';

    if ($configValue == '0'    ) { $val_0    = 'selected="selected"'; } 
    if ($configValue == '10'   ) { $val_10   = 'selected="selected"'; } 
    if ($configValue == '30'   ) { $val_30   = 'selected="selected"'; } 
    if ($configValue == '60'   ) { $val_60   = 'selected="selected"'; }
    if ($configValue == '300'  ) { $val_300  = 'selected="selected"'; } 
    if ($configValue == '600'  ) { $val_600  = 'selected="selected"'; } 
    if ($configValue == '900'  ) { $val_900  = 'selected="selected"'; } 
    if ($configValue == '1800' ) { $val_1800 = 'selected="selected"'; } 
    if ($configValue == '3600' ) { $val_3600 = 'selected="selected"'; } 

    echo '<option ' . $val_0    . ' value="0"    >'  .  $sw_off  . '</option>';
    echo '<option ' . $val_10   . ' value="10"   >10 '. $seconds . '</option>';
    echo '<option ' . $val_30   . ' value="30"   >30 '. $seconds . '</option>';
    echo '<option ' . $val_60   . ' value="60"   >60 '. $seconds . '</option>';
    echo '<option ' . $val_300  . ' value="300"  >5 ' . $minutes . '</option>';
    echo '<option ' . $val_600  . ' value="600"  >10 '. $minutes . '</option>';
    echo '<option ' . $val_900  . ' value="900"  >15 '. $minutes . '</option>';
    echo '<option ' . $val_1800 . ' value="1800" >30 '. $minutes . '</option>';
    echo '<option ' . $val_3600 . ' value="3600" >1 ' . $hour    . '</option>';

}

function makeSelectorUISelector($id) {
    $configValue = config_read($id);
    $val_0=$val_1='';

    if ($configValue == '0'  ) { $val_0  = 'selected="selected"'; } 
    if ($configValue == '1'  ) { $val_1  = 'selected="selected"'; } 

    echo '<option ' . $val_0  . ' value="0"  >' . strIdx( 203 ) . '</option>';
    echo '<option ' . $val_1  . ' value="1"  >' . strIdx( 204 ) . '</option>';

}

function makeUILanguageSelector($id) {
    $configValue = config_read($id);
    $val_0=$val_1=$val_2='';

    if ($configValue == '0'  ) { $val_0  = 'selected="selected"'; } 
    if ($configValue == '1'  ) { $val_1  = 'selected="selected"'; }
    if ($configValue == '2'  ) { $val_2  = 'selected="selected"'; }  

    echo '<option ' . $val_0  . ' value="0"  >Nederlands (standaard).</option>';
    echo '<option ' . $val_1  . ' value="1"  >English</option>';
    echo '<option ' . $val_2  . ' value="2"  >Français</option>';
}

function makeSelectorHomeSelector($id) {
    $configValue = config_read($id);
    $val_0=$val_1='';

    if ($configValue == '0'  ) { $val_0  = 'selected="selected"'; } 
    if ($configValue == '1'  ) { $val_1  = 'selected="selected"'; } 

    echo '<option ' . $val_0  . ' value="0"  >levering en verbruik</option>';
    echo '<option ' . $val_1  . ' value="1"  >alleen verbruik</option>';
}

function makeSelectorKWhSelector($id) {
    $configValue = config_read($id);
    $val_10=$val_20=$val_40=$val_60=$val_80=$val_100=$val_1000=$val_2000=$val_4000=$val_8000='';
    
    if ($configValue == '10' )  { $val_10   = 'selected="selected"'; }
    if ($configValue == '20' )  { $val_20   = 'selected="selected"'; }
    if ($configValue == '40' )  { $val_40   = 'selected="selected"'; }
    if ($configValue == '60' )  { $val_60   = 'selected="selected"'; }
    if ($configValue == '80' )  { $val_80   = 'selected="selected"'; }
    if ($configValue == '100')  { $val_100  = 'selected="selected"'; }
    if ($configValue == '1000') { $val_1000 = 'selected="selected"'; }
    if ($configValue == '2000') { $val_2000 = 'selected="selected"'; }
    if ($configValue == '4000') { $val_4000 = 'selected="selected"'; }
    if ($configValue == '8000') { $val_8000 = 'selected="selected"'; }

    echo '<option ' . $val_10   . ' value="10"   >10 kWh</option>';
    echo '<option ' . $val_20   . ' value="20"   >20 kWh</option>';
    echo '<option ' . $val_40   . ' value="40"   >40 kWh</option>';
    echo '<option ' . $val_60   . ' value="60"   >60 kWh</option>';
    echo '<option ' . $val_80   . ' value="80"   >80 kWh</option>';
    echo '<option ' . $val_100  . ' value="100"  >100 kWh</option>';
    echo '<option ' . $val_1000 . ' value="1000" >1000 kWh</option>';
    echo '<option ' . $val_2000 . ' value="2000" >2000 kWh</option>';
    echo '<option ' . $val_4000 . ' value="4000" >4000 kWh</option>';
    echo '<option ' . $val_8000 . ' value="8000" >8000 kWh</option>';
}

function makeSelectorKwSelector($id) {
        $configValue = config_read($id);
        $val_1000=$val_2000=$val_2500=$val_5000=$val_10000=$val_20000=$val_25000=$val_50000=$val_100000=$val_250000=$val_500000=$val_1000000='';
        
        if ($configValue == '1000'   ) { $val_1000    = 'selected="selected"'; }
        if ($configValue == '2000'   ) { $val_2000    = 'selected="selected"'; }
        if ($configValue == '2500'   ) { $val_2500    = 'selected="selected"'; }
        if ($configValue == '5000'   ) { $val_5000    = 'selected="selected"'; }
        if ($configValue == '10000'  ) { $val_10000   = 'selected="selected"'; }
        if ($configValue == '20000'  ) { $val_20000   = 'selected="selected"'; }
        if ($configValue == '25000'  ) { $val_25000   = 'selected="selected"'; }
        if ($configValue == '50000'  ) { $val_50000   = 'selected="selected"'; }
        if ($configValue == '100000' ) { $val_100000  = 'selected="selected"'; }
        if ($configValue == '250000' ) { $val_250000  = 'selected="selected"'; }
        if ($configValue == '500000' ) { $val_500000  = 'selected="selected"'; }
        if ($configValue == '1000000') { $val_1000000 = 'selected="selected"'; }
        
        echo '<option ' . $val_1000    . ' value="1000"  >1 kW</option>';
        echo '<option ' . $val_2000    . ' value="2000"  >2 kW</option>';
        echo '<option ' . $val_2500    . ' value="2500"  >2.5 kW</option>';
        echo '<option ' . $val_5000    . ' value="5000"  >5 kW</option>';
        echo '<option ' . $val_10000   . ' value="10000" >10 kW</option>';
        echo '<option ' . $val_20000   . ' value="20000" >20 kW</option>';
        echo '<option ' . $val_25000   . ' value="25000" >25 kW</option>';
        echo '<option ' . $val_50000   . ' value="50000" >50 kW</option>';
        echo '<option ' . $val_100000  . ' value="100000" >100 kW</option>';
        echo '<option ' . $val_250000  . ' value="250000" >250 kW</option>';
        echo '<option ' . $val_500000  . ' value="500000" >500 kW</option>';
        echo '<option ' . $val_1000000 . ' value="1000000" >1000 kW</option>';
}

function makeSelectorGasSelector($id) {
    $configValue = config_read($id);

    $val_1=$val_2=$val_5=$val_10=$val_20='';
    
    if ($configValue == '1'  ) { $val_1  = 'selected="selected"'; } 
    if ($configValue == '2'  ) { $val_2  = 'selected="selected"'; } 
    if ($configValue == '5'  ) { $val_5  = 'selected="selected"'; } 
    if ($configValue == '10' ) { $val_10 = 'selected="selected"'; } 
    if ($configValue == '20' ) { $val_20 = 'selected="selected"'; }
    
    echo '<option ' . $val_1  . ' value="1"  >1 m&#179;/u</option>';
    echo '<option ' . $val_2  . ' value="2"  >2 m&#179;/u</option>';
    echo '<option ' . $val_5  . ' value="5"  >5 m&#179;/u</option>';
    echo '<option ' . $val_10 . ' value="10" >10 m&#179;/u</option>';
    echo '<option ' . $val_20 . ' value="20" >20 m&#179;/u</option>';
}

function makeSelectorGasSelector2($id) {
    $configValue = config_read($id);

    $val_1=$val_20=$val_50='';
    
    if ($configValue == '1'  ) { $val_1  = 'selected="selected"'; } 
    if ($configValue == '2'  ) { $val_20  = 'selected="selected"'; } 
    if ($configValue == '5'  ) { $val_50 = 'selected="selected"'; } 
    
    echo '<option ' . $val_1  . ' value="1" >1 m&#179;</option>';
    echo '<option ' . $val_20 . ' value="2" >2 m&#179;</option>';
    echo '<option ' . $val_50 . ' value="5" >5 m&#179;</option>';
}

function makeSelectorKwSelector2($id) {
    $configValue = config_read($id);
    $val_10=$val_20=$val_50=$val_100=$val_120=$val_150=$val_200=$val_300=$val_1000=$val_3000=$val_5000=$val_7500=$val_10000='';
    
    if ($configValue == '1'    ) { $val_10   = 'selected="selected"'; }
    if ($configValue == '2'    ) { $val_20   = 'selected="selected"'; }
    if ($configValue == '5'    ) { $val_50   = 'selected="selected"'; }
    if ($configValue == '10'   ) { $val_100  = 'selected="selected"'; }
    if ($configValue == '12'   ) { $val_120  = 'selected="selected"'; }
    if ($configValue == '15'   ) { $val_150  = 'selected="selected"'; }
    if ($configValue == '20'   ) { $val_200  = 'selected="selected"'; }
    if ($configValue == '30'   ) { $val_300  = 'selected="selected"'; }
    if ($configValue == '100'  ) { $val_1000 = 'selected="selected"'; }
    if ($configValue == '300'  ) { $val_3000 = 'selected="selected"'; }
    if ($configValue == '500'  ) { $val_5000 = 'selected="selected"'; }
    if ($configValue == '750'  ) { $val_7500 = 'selected="selected"'; }
    if ($configValue == '1000' ) { $val_10000 = 'selected="selected"'; }
    
    echo '<option ' . $val_10    . ' value="1"  >1 kW</option>';
    echo '<option ' . $val_20    . ' value="2"  >2 kW</option>';
    echo '<option ' . $val_50    . ' value="5"  >5 kW</option>';
    echo '<option ' . $val_100   . ' value="10" >10 kW</option>';
    echo '<option ' . $val_120   . ' value="12" >12 kW</option>';
    echo '<option ' . $val_150   . ' value="15" >15 kW</option>';
    echo '<option ' . $val_200   . ' value="20" >20 kW</option>';
    echo '<option ' . $val_300   . ' value="30" >30 kW</option>';
    echo '<option ' . $val_1000  . ' value="100" >100 kW</option>';
    echo '<option ' . $val_3000  . ' value="300" >300 kW</option>';
    echo '<option ' . $val_5000  . ' value="500" >500 kW</option>';
    echo '<option ' . $val_7500  . ' value="750" >750 kW</option>';
    echo '<option ' . $val_10000 . ' value="1000" >1000 kW</option>';
}

function makeSelectorWatt( $id ) {
    $configValue = config_read( $id );
    $val_4000=$val_6000=$val_8000=$val_10000=$val_60000=$val_100000=$val_320000='';

    if ( $configValue == '4000'   ) { $val_4000   = 'selected="selected"'; } 
    if ( $configValue == '6000'   ) { $val_6000   = 'selected="selected"'; } 
    if ( $configValue == '8000'   ) { $val_8000   = 'selected="selected"'; } 
    if ( $configValue == '10000'  ) { $val_10000  = 'selected="selected"'; }
    if ( $configValue == '60000'  ) { $val_60000  = 'selected="selected"'; }
    if ( $configValue == '100000' ) { $val_100000 = 'selected="selected"'; }
    if ( $configValue == '320000' ) { $val_320000 = 'selected="selected"'; }
   
    echo '<option ' . $val_4000   . ' value="4000"   >4 kW</option>';
    echo '<option ' . $val_6000   . ' value="6000"   >6 kW</option>';
    echo '<option ' . $val_8000   . ' value="8000"   >8 kW</option>';
    echo '<option ' . $val_10000  . ' value="10000"  >10 kW</option>';
    echo '<option ' . $val_60000  . ' value="60000"  >60 kW</option>';
    echo '<option ' . $val_100000 . ' value="100000" >100 kW</option>';
    echo '<option ' . $val_320000 . ' value="320000" >320 kW</option>';

}

function makeSelectorAmpere( $id ) {
    $configValue = config_read( $id );
    $val_10=$val_16=$val_25=$val_35=$val_40=$val_50=$val_63=$val_80=$val_160=$val_250=$val_400=$val_1000='';

    if ($configValue == '10'   ) { $val_10  = 'selected="selected"'; }
    if ($configValue == '16'   ) { $val_16  = 'selected="selected"'; }
    if ($configValue == '25'   ) { $val_25  = 'selected="selected"'; }
    if ($configValue == '35'   ) { $val_35  = 'selected="selected"'; }
    if ($configValue == '40'   ) { $val_40  = 'selected="selected"'; }
    if ($configValue == '50'   ) { $val_50  = 'selected="selected"'; }
    if ($configValue == '63'   ) { $val_63  = 'selected="selected"'; }
    if ($configValue == '80'   ) { $val_80  = 'selected="selected"'; }
    if ($configValue == '160'  ) { $val_160 = 'selected="selected"'; }
    if ($configValue == '250'  ) { $val_250 = 'selected="selected"'; }
    if ($configValue == '400'  ) { $val_400 = 'selected="selected"'; }
    if ($configValue == '1000' ) { $val_1000 = 'selected="selected"'; }

    echo '<option ' . $val_10   . ' value="10"   >10 A</option>';
    echo '<option ' . $val_16   . ' value="16"   >16 A</option>';
    echo '<option ' . $val_25   . ' value="25"   >25 A</option>';
    echo '<option ' . $val_35   . ' value="35"   >35 A</option>';
    echo '<option ' . $val_40   . ' value="40"   >40 A</option>';
    echo '<option ' . $val_50   . ' value="50"   >50 A</option>';
    echo '<option ' . $val_63   . ' value="63"   >63 A</option>';
    echo '<option ' . $val_80   . ' value="80"   >80 A</option>';
    echo '<option ' . $val_160  . ' value="160"  >160 A</option>';
    echo '<option ' . $val_250  . ' value="250"  >250 A</option>';
    echo '<option ' . $val_400  . ' value="400"  >400 A</option>';
    echo '<option ' . $val_1000 . ' value="1000" >1000 A</option>';

}


?>
<!doctype html>
<html lang="nl">
<head>
<meta name="robots" content="noindex">
<title>UI configuratie</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css" />
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/p1mon-util.js"></script>
<script src="./js/jquery-validate-link/jquery.validate.min.js"></script>
</head>
<body>

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
                <?php menu_control(9);?>
            </div>
            
            <div id="right-wrapper-config"> <!-- right block -->
            <!-- inner block right part of screen -->
                <div id="right-wrapper-config-left-2">
                    <!-- start of content -->
                    <form name="formvalues" id="formvalues" method="POST">
                        
                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 174 );?></span>
                        </div>
                        <div class="frame-4-bot">
                            <div> 
                                <!-- left side -->
                                <div class="float-left">
                                    <div class="text-10"><?php echo strIdx( 182 );?></div>
                                    <div class="text-10"><?php echo strIdx( 183 );?></div>
                                    <div class="text-10"><?php echo strIdx( 184 );?></div>
                                    <div class="text-10"><?php echo strIdx( 185 );?></div>
                                    <div class="text-10"><?php echo strIdx( 186 );?></div>
                                    <div class="text-10"><?php echo strIdx( 187 );?></div>
                                    <div class="text-10"><?php echo strIdx( 188 );?></div>
                                    <div class="text-10"><?php echo strIdx( 189 );?></div>
                                    <div class="text-10"><?php echo strIdx( 190 );?></div>
                                    <div class="text-10"><?php echo strIdx( 191 );?></div>
                                </div>
                                <!-- right side -->
                                <div class="float-right">
                                    <div>
                                        <input class="cursor-pointer" name="actueel_e" type="radio" value="1" <?php if ( config_read(18) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="actueel_e" type="radio" value="0" <?php if ( config_read(18) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                    <div>
                                        <input class="cursor-pointer" name="historie_e" type="radio" value="1" <?php if ( config_read(19) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="historie_e" type="radio" value="0" <?php if ( config_read(19) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                    <div>
                                        <input class="cursor-pointer" name="historie_g" type="radio" value="1" <?php if ( config_read(20) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="historie_g" type="radio" value="0" <?php if ( config_read(20) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                    <div>
                                        <input class="cursor-pointer" name="finaciel" type="radio" value="1" <?php if ( config_read(21) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="finaciel" type="radio" value="0" <?php if ( config_read(21) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                    <div>
                                        <input class="cursor-pointer" name="informatie" type="radio" value="1" <?php if ( config_read(22) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="informatie" type="radio" value="0" <?php if ( config_read(22) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                    <div>
                                        <input class="cursor-pointer" name="verwarming" type="radio" value="1" <?php if ( config_read(46) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="verwarming" type="radio" value="0" <?php if ( config_read(46) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                    <div>
                                        <input class="cursor-pointer" name="meterstanden" type="radio" value="1" <?php if ( config_read(62) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="meterstanden" type="radio" value="0" <?php if ( config_read(62) == 0 ) { echo 'checked'; }?>><?php echo $sw_off?>
                                    </div>
                                    <div>
                                        <input class="cursor-pointer" name="watermeter" type="radio" value="1" <?php if ( config_read( 102 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="watermeter" type="radio" value="0" <?php if ( config_read( 102 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                    <div>
                                        <input class="cursor-pointer" name="kWhlevering" type="radio" value="1" <?php if ( config_read( 129 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="kWhlevering" type="radio" value="0" <?php if ( config_read( 129 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                    <div>
                                        <input class="cursor-pointer" name="kWhleveringSolarEdge" type="radio" value="1" <?php if ( config_read( 147 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="kWhleveringSolarEdge" type="radio" value="0" <?php if ( config_read( 147 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                </div>
                            </div>
                        </div>    
                            
                        <p></p>
                        
                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 175 );?></span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left">
                                <i class="text-10 pad-7 fas fa-bolt"></i>
                                <label class="text-10"><?php echo strIdx( 195 );?></label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-7 fas fa-bolt"></i>
                                <label class="text-10"><?php echo strIdx( 196 );?></label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-8 fas fa-bolt"></i>
                                <label class="text-10"><?php echo strIdx( 197 );?></label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-8 fas fa-bolt"></i>
                                <label class="text-10"><?php echo strIdx( 198 );?></label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-8 fab fa-gripfire"></i>
                                <label class="text-10"><?php echo strIdx( 199 );?></label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-7 fas fa-bolt"></i>
                                <label class="text-10"><?php echo strIdx( 195 );?> (home scherm)</label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-8 fas fa-bolt"></i>
                                <label class="text-10"><?php echo strIdx( 197 );?> (home scherm)</label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-8 fab fa-gripfire"></i>
                                <label class="text-10"><?php echo strIdx( 199 );?> (home scherm)</label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-7 fas fa-bolt"></i>
                                <label class="text-10"><?php echo strIdx( 200 );?></label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-7 fas fa-bolt"></i>
                                <label class="text-10"><?php echo strIdx( 200 );?></label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-7 fas fa-bolt"></i>
                                <label class="text-10" title="<?php echo strIdx(307);?>"><?php echo strIdx( 305 );?></label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-7 fas fa-bolt"></i>
                                <label class="text-10" title="<?php echo strIdx(307);?>"><?php echo strIdx( 306 );?></label>
                            </div>
                            <div class="float-left pad-1">
                                <select class="select-5 color-select color-input-back cursor-pointer" name="levering_list">
                                    <?php makeSelectorKwSelector(23);?>
                                </select>
                                <p class="p-1"></p>
                                <select class="select-5 color-select color-input-back cursor-pointer" name="levering_list_kwh">
                                    <?php makeSelectorKWhSelector(56);?>
                                </select>
                                <p class="p-1"></p>
                                <select class="select-5 color-select color-input-back cursor-pointer" name="verbruik_list">
                                    <?php makeSelectorKwSelector(24);?>
                                </select>
                                <p class="p-1"></p>
                                <select class="select-5 color-select color-input-back cursor-pointer" name="verbruik_list_kwh">
                                    <?php makeSelectorKWhSelector(57);?>
                                </select>
                                <p class="p-1"></p>
                                <select class="select-5 color-select color-input-back cursor-pointer" name="verbruik_g_list">
                                    <?php makeSelectorGasSelector(41);?>
                                </select>
                                <p class="p-1"></p>
                                <select class="select-5 color-select color-input-back cursor-pointer" name="levering_list_main">
                                    <?php makeSelectorKwSelector2(53);?>
                                </select>
                                <p class="p-1"></p>
                                <select class="select-5 color-select color-input-back cursor-pointer" name="verbruik_list_main">
                                    <?php makeSelectorKwSelector2(52);?>
                                </select>
                                <p class="p-1"></p>
                                <select class="select-5 color-select color-input-back cursor-pointer" name="verbruik_g_list_main">
                                    <?php makeSelectorGasSelector2(54);?>
                                </select>
                                <p class="p-1"></p>
                                <select class="select-5 color-select color-input-back cursor-pointer" name="watt_fase_gauge">
                                    <?php makeSelectorWatt( 124 );?>
                                </select>
                                <p class="p-1"></p>
                                <select class="select-5 color-select color-input-back cursor-pointer" name="amperage_fase_gauge">
                                    <?php makeSelectorAmpere( 123 );?>
                                </select>
                                <p class="p-1"></p>
                                <input title="<?php echo strIdx(307);?>" class="input-17 color-select color-input-back" id="phase_v_max" name="phase_v_max" type="text" value="<?php echo config_read( 173 );?>">
                                <p class="p-1"></p>
                                <input title="<?php echo strIdx(307);?>" class="input-17 color-select color-input-back" id="phase_v_min" name="phase_v_min" type="text" value="<?php echo config_read( 174 );?>">
                            </div>
                        </div>

                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 176 );?></span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left">
                                <span class="fa-layers text-10">
                                    <i class="fas fa-desktop pad-7"></i>
                                    <i class="fas fa-pen-square pad-7" data-fa-transform="shrink-8 up-1 right-1"></i>
                                </span>
                            </div>
                            <div class="float-left pad-1">
                                <select class="select-4 color-select color-input-back cursor-pointer" name="custom_ui_list">
                                    <?php makeSelectorUISelector(43);?>
                                </select>
                            </div>
                        </div>
                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15">taal / language / langue</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left">                
                                <!-- <i class="text-10 fas fa-home pad-7"></i> -->

                                <span class="fa-layers text-10">
                                    <i class="fas fa-desktop pad-7"></i>
                                    <i class="fas fa-pen-square pad-7" data-fa-transform="shrink-8 up-1 right-1"></i>
                                </span>

                            </div>
                            <div class="float-left pad-1">
                                <select class="select-4 color-select color-input-back cursor-pointer" name="ui_language">
                                    <?php makeUILanguageSelector(148);?>
                                </select>
                            </div>
                        </div>

                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 177 );?></span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="rTable"> 
                                <div class="rTableRow">
                                    <div class="rTableCell text-10 width-320">
                                        <?php echo strIdx( 205 );?>
                                    </div>
                                    <div class="rTableCell float-right">
                                        <input class="cursor-pointer" name="voorspelling" type="radio" value="1" <?php if ( config_read(59) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="voorspelling" type="radio" value="0" <?php if ( config_read(59) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                </div>
                                <div class="rTableRow">
                                    <div class="rTableCell text-10 width-320">
                                        <?php echo strIdx( 206 );?>
                                    </div>
                                    <div class="rTableCell float-right">
                                        <input class="cursor-pointer" name="drie_fasen" type="radio" value="1" <?php if ( config_read(61) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="drie_fasen" type="radio" value="0" <?php if ( config_read(61) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                </div>
                                <div class="rTableRow">
                                    <div class="rTableCell text-10 width-320">
                                        <?php echo strIdx( 207 );?>
                                    </div>
                                    <div class="rTableCell float-right">
                                        <input class="cursor-pointer" name="ui_header" type="radio" value="1" <?php if ( config_read(134) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="ui_header" type="radio" value="0" <?php if ( config_read(134) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                </div>
                                <div class="rTableRow">
                                    <div class="rTableCell text-10 width-320">
                                        <?php echo strIdx( 256 );?>
                                    </div>
                                    <div class="rTableCell float-right">
                                        <input class="cursor-pointer" name="ui_water_hide" type="radio" value="1" <?php if ( config_read( 157 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="ui_water_hide" type="radio" value="0" <?php if ( config_read( 157 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                </div>
                                <div class="rTableRow">
                                    <div class="rTableCell text-10 width-320">
                                        <?php echo strIdx( 257 );?>
                                    </div>
                                    <div class="rTableCell float-right">
                                        <input class="cursor-pointer" name="ui_gas_hide" type="radio" value="1" <?php if ( config_read( 158 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="ui_gas_hide" type="radio" value="0" <?php if ( config_read( 158 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                </div>
                                <div class="rTableRow" title="<?php echo strIdx( 314 );?>">
                                    <div class="rTableCell text-10 width-320">
                                        <?php echo strIdx( 313 );?>
                                    </div>
                                    <div class="rTableCell float-right">
                                        <input class="cursor-pointer" name="ui_w2kw" type="radio" value="1" <?php if ( config_read( 180 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="ui_w2kw" type="radio" value="0" <?php if ( config_read( 180 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                </div>
                                <div class="rTableRow" title="<?php echo strIdx( 334 );?>">
                                    <div class="rTableCell text-10 width-320">
                                        <?php echo strIdx( 333 );?>
                                    </div>
                                    <div class="rTableCell float-right">
                                        <input class="cursor-pointer" name="ui_peak_kw_hide" type="radio" value="1" <?php if ( config_read( 206 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="ui_peak_kw_hide" type="radio" value="0" <?php if ( config_read( 206 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!--
                        <div class="frame-4-bot">
                        <div> 
                          
                            <div class="float-left">
                                <div class="text-10"><?php echo strIdx( 205 );?></div>
                                <div class="text-10"><?php echo strIdx( 206 );?></div>
                                <div class="text-10"><?php echo strIdx( 207 );?></div>
                                <div class="text-10"><?php echo strIdx( 256 );?></div>
                                <div class="text-10"><?php echo strIdx( 257 );?></div>
                                <div class="text-10" title="<?php echo strIdx( 314 );?>"><?php echo strIdx( 313 );?></div>
                                <div class="text-10" title="<?php echo strIdx( 334 );?>"><?php echo strIdx( 333 );?></div>
                            </div>
                            
                            <div class="float-right">
                                <div>
                                    <input class="cursor-pointer" name="voorspelling" type="radio" value="1" <?php if ( config_read(59) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                    <input class="cursor-pointer" name="voorspelling" type="radio" value="0" <?php if ( config_read(59) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                </div>
                                <div>
                                    <input class="cursor-pointer" name="drie_fasen" type="radio" value="1" <?php if ( config_read(61) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                    <input class="cursor-pointer" name="drie_fasen" type="radio" value="0" <?php if ( config_read(61) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                </div>
                                <div>
                                    <input class="cursor-pointer" name="ui_header" type="radio" value="1" <?php if ( config_read(134) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                    <input class="cursor-pointer" name="ui_header" type="radio" value="0" <?php if ( config_read(134) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                </div>
                                <div>
                                    <input class="cursor-pointer" name="ui_water_hide" type="radio" value="1" <?php if ( config_read( 157 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                    <input class="cursor-pointer" name="ui_water_hide" type="radio" value="0" <?php if ( config_read( 157 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                </div>
                                <div>
                                    <input class="cursor-pointer" name="ui_gas_hide" type="radio" value="1" <?php if ( config_read( 158 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                    <input class="cursor-pointer" name="ui_gas_hide" type="radio" value="0" <?php if ( config_read( 158 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                </div>
                                <div title="<?php echo strIdx(314);?>">
                                    <input class="cursor-pointer" name="ui_w2kw" type="radio" value="1" <?php if ( config_read( 180 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                    <input class="cursor-pointer" name="ui_w2kw" type="radio" value="0" <?php if ( config_read( 180 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                </div>
                                <div title="<?php echo strIdx(314);?>">
                                    <input class="cursor-pointer" name="ui_peak_kw_hide" type="radio" value="1" <?php if ( config_read( 206 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                    <input class="cursor-pointer" name="ui_peak_kw_hide" type="radio" value="0" <?php if ( config_read( 206 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                </div>
                            </div>
                            </div>
                           
                        </div>
                        -->

                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 178 );?></span>
                        </div>
                        <div class="frame-4-bot">
                        <div> 
                                <!-- left side -->
                                <div class="float-left">
                                    <div class="text-10 pad-25"><?php echo strIdx( 180 );?></div>
                                    <div class="text-10 pad-26"><?php echo strIdx (181 );?></div>
                                </div>
                                <!-- right side -->
                                <div class="float-right">
                                    <div>
                                        <select class="select-2 color-select color-input-back cursor-pointer" name="scrsav_wait" id="scrsav_wait">
                                            <?php makeSelectorSec( 79 );?>
                                        </select>
                                    </div>
                                    <div>
                                        <select class="select-2 color-select color-input-back cursor-pointer" name="scrsav_auto_off" id="scrsav_auto_off">
                                            <?php makeSelectorSec( 80 );?>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 179 );?></span>
                        </div>
                        <div class="frame-4-bot">
                        <div> 
                            <!-- left side -->
                            <div class="float-left">
                                    <div class="text-10 pad-25"><?php echo strIdx( 201 );?></div>
                                    <div class="text-10 pad-26"><?php echo strIdx( 202 );?></div>
                            </div>
                            <!-- right side -->
                            <div class="float-right">
                            <div>
                                <input class="input-14 color-settings color-input-back" id="verwarming_in_label" name="verwarming_in_label" type="text" value="<?php echo config_read( 121 );?>">
                            </div>
                            <div>
                                <input class="input-14 color-settings color-input-back" id="verwarming_uit_label" name="verwarming_uit_label" type="text" value="<?php echo config_read( 122 );?>">
                            </div>
                        </div>
                    </div>
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
                        <?php echo strIdx(9);?>
                        <br><br>
                        <?php echo strIdx(36);?>
                        
                        <?php echo strIdx(69);?>
                        <br><br>
                        <?php echo strIdx(116);?>
                        <br><br>
                        <?php echo strIdx( 83 );?>
                    </div>
                    
                </div>
            </div>    
            <!-- end inner block right part of screen -->
        </div>
    
    <?php echo div_err_succes();?>
<script>

// make sure the max value is larger then the min value
jQuery.validator.addMethod( "max_check", function(value, element) {
    //console.log( document.getElementById("phase_v_max").value )
    //console.log( document.getElementById("phase_v_min").value )
    if ( parseInt(document.getElementById("phase_v_max").value) <= parseInt( document.getElementById("phase_v_min").value)  ) {
        return false;
    } 
    return true;
}, '');

$(function() {
    $("#formvalues").validate({
        rules: {
            'verwarming_in_label':{
                required: false,
                maxlength: 10
            },
            'verwarming_uit_label':{
                required: false,
                maxlength: 10,
            },
            'phase_v_max': {
                required: true,
                number: true,
                max: 499.9,
                min: 1,
                max_check: true
            },
            'phase_v_min': {
                required: true,
                number: true,
                max: 499.9,
                min: 1,
                max_check: true
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