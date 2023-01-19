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
# proces post variables.

# read cron values
$configValueChron = config_read(37);
# min=0, hour=1, dayof the month=2, month=3
$cron_pieces = explode(":", config_read(37));
#print_r($cron_pieces);

$must_update_cron = False;

if ( isset($_POST["dbx_backup_active"]) ) { 
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ($_POST["dbx_backup_active"] == '1' ) {
                #echo "on<br>";
                if ( updateConfigDb("update config set parameter = '1' where ID = 49"))$err_cnt += 1;
        } else {
                #echo "off<br>";
                if ( updateConfigDb("update config set parameter = '0' where ID = 49"))$err_cnt += 1;
        }
        $must_update_cron = True;
}

if ( isset($_POST["ftp_backup_active"]) ) { 
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ($_POST["ftp_backup_active"] == '1' ) {
                #echo "on<br>";
                if ( updateConfigDb("update config set parameter = '1' where ID = 36"))$err_cnt += 1;
        } else {
                #echo "off<br>";
                if ( updateConfigDb("update config set parameter = '0' where ID = 36"))$err_cnt += 1;
        }
        $must_update_cron = True;
}

if ( isset($_POST["ftp_mode"]) ) { 
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ($_POST["ftp_mode"] == 'ftp' ) {
        #echo "ftp<br>";
        if ( updateConfigDb("update config set parameter = '0' where ID = 35"))$err_cnt += 1;
        if ( updateConfigDb("update config set parameter = '1' where ID = 76"))$err_cnt += 1;
        if ( updateConfigDb("update config set parameter = '0' where ID = 77"))$err_cnt += 1;
    }
    if ($_POST["ftp_mode"] == 'ftps' ) {
        #echo "ftps<br>";
        if ( updateConfigDb("update config set parameter = '1' where ID = 35"))$err_cnt += 1;
        if ( updateConfigDb("update config set parameter = '0' where ID = 76"))$err_cnt += 1;
        if ( updateConfigDb("update config set parameter = '0' where ID = 77"))$err_cnt += 1;
    }
    if ($_POST["ftp_mode"] == 'sftp' ) {
        #echo "sftp<br>";
        if ( updateConfigDb("update config set parameter = '0' where ID = 35"))$err_cnt += 1;
        if ( updateConfigDb("update config set parameter = '0' where ID = 76"))$err_cnt += 1;
        if ( updateConfigDb("update config set parameter = '1' where ID = 77"))$err_cnt += 1;
        }
}

if ( isset($_POST["i_ftp_name"]) ) { 
        $input = inputClean(trim($_POST["i_ftp_name"]));
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ( updateConfigDb("update config set parameter = '".$input."' where ID = 28")) $err_cnt += 1;
}

if ( isset($_POST["i_ftp_pword"]) ) { 
        $input = trim($_POST["i_ftp_pword"]);
        $password = encodeString ($input, 'ftppw');
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ( updateConfigDb("update config set parameter = '".$password."' where ID = 29")) $err_cnt += 1;
}

if ( isset($_POST["i_ftp_folder"]) ) { 
        $input = inputClean(trim($_POST["i_ftp_folder"]));
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ( updateConfigDb("update config set parameter = '".$input."' where ID = 30")) $err_cnt += 1;
}

if ( isset($_POST["i_ftp_host"]) ) { 
        $input = inputClean(trim($_POST["i_ftp_host"]));
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ( updateConfigDb("update config set parameter = '".$input."' where ID = 31")) $err_cnt += 1;
}

if ( isset($_POST["i_ftp_host_port"]) ) { 
        $input = inputCleanDigitsOnly(trim($_POST["i_ftp_host_port"]));
        if (strlen($input) > 0 ) {
                if ( $err_cnt == -1 ) $err_cnt=0;
                if ( updateConfigDb("update config set parameter = '".$input."' where ID = 32")) $err_cnt += 1;
        }
}

if ( isset($_POST["i_ftp_max_versions"]) ) { 
        $input = inputCleanDigitsOnly(trim($_POST["i_ftp_max_versions"]));
        if (strlen($input) > 0 ) {
                if ( $err_cnt == -1 ) $err_cnt=0;
                if ( updateConfigDb("update config set parameter = '".$input."' where ID = 34")) $err_cnt += 1;
        }
}

if ( isset($_POST["i_dbx_max_versions"]) ) { 
        $input = inputCleanDigitsOnly(trim($_POST["i_dbx_max_versions"]));
        if (strlen($input) > 0 ) {
                if ( $err_cnt == -1 ) $err_cnt=0;
                if ( updateConfigDb("update config set parameter = '".$input."' where ID = 48")) $err_cnt += 1;
        }
}

if ( isset($_POST["i_minutes"]) ) { 
        if ( strlen(trim($_POST["i_minutes"])) > 0 ) {
                $cron_pieces[0] = trim($_POST["i_minutes"]);
                if ( cronSafeCharacters($cron_pieces[0]) == True) {
                        $must_update_cron = True;
                } 
        }
}

if ( isset($_POST["i_hours"]) ) { 
        if ( strlen(trim($_POST["i_hours"])) > 0 ) {
                $cron_pieces[1] = trim($_POST["i_hours"]);
                if ( cronSafeCharacters($cron_pieces[1]) == True) {
                        $must_update_cron = True;
                } 
        }
}

if ( isset($_POST["i_days"]) ) { 
        if ( strlen(trim($_POST["i_days"])) > 0 ) {
                $cron_pieces[2] = trim($_POST["i_days"]);
                if ( cronSafeCharacters($cron_pieces[2]) == True) {
                        $must_update_cron = True;
                }
        }
}

if ( isset($_POST["i_months"]) ) { 
        if ( strlen(trim($_POST["i_months"])) > 0 ) {
                $cron_pieces[3] = trim($_POST["i_months"]);
                if ( cronSafeCharacters($cron_pieces[3]) == True) {
                        $must_update_cron = True;
                }
        }
}

if ( isset($_POST["i_weekdays"]) ) { 
        if ( strlen(trim($_POST["i_weekdays"])) > 0 ) {
                $cron_pieces[4] = trim($_POST["i_weekdays"]);
                if ( cronSafeCharacters($cron_pieces[4]) == True) {
                        $must_update_cron = True;
                }
        }
}

if ( $must_update_cron  == True ) {
        if ( $err_cnt == -1 ) $err_cnt=0;
        $cron_str = $cron_pieces [0].":".$cron_pieces [1].":".$cron_pieces [2].":".$cron_pieces [3].":".$cron_pieces [4];
        if ( updateConfigDb("update config set parameter = '".$cron_str."' where ID = 37")) $err_cnt += 1;
        if ( updateConfigDb("update config set parameter = '1' where ID = 181")) $err_cnt += 1;
        #print $cron_str;
}

if ( isset($_POST['systemaction']) ) { 
        #echo 'systemaction<br>';
        if ($_POST['systemaction'] === 'ftp_test_button'){ 
            if ( updateConfigDb("update config set parameter = '1' where ID = 184") ) $err_cnt += 1;
        }
}

function slectorMinutes() {
        echo "<option value='*'>*</option>";
        for ($x = 0; $x <= 59; $x++) {
                echo "<option value=$x>$x</option>";
        } 
}

function slectorHours() {
        echo "<option value='*'>*</option>";
        for ($x = 0; $x <= 23; $x++) {
                echo "<option value=$x>$x</option>";
        } 
}

function slectorDays() {
        echo "<option value='*'>*</option>";
        for ($x = 1; $x <= 31; $x++) {
                echo "<option value=$x>$x</option>";
        } 
}

function slectorMonths() {
        echo "<option value='*'>* (elke maand)</option>";
        echo "<option value=1>1 (januari)</option>";
        echo "<option value=2>2 (feburari)</option>";
        echo "<option value=3>3 (maart)</option>";
        echo "<option value=4>4 (april)</option>";
        echo "<option value=5>5 (mei)</option>";
        echo "<option value=6>6 (juni)</option>";
        echo "<option value=7>7 (juli)</option>";
        echo "<option value=8>8 (augustus)</option>";
        echo "<option value=9>9 (september)</option>";
        echo "<option value=10>10 (oktober)</option>";
        echo "<option value=11>11 (november)</option>";
        echo "<option value=12>12 (december)</option>";
}

function slectorWeekDays() {
        echo "<option value='*'>* (elke dag)</option>";
        echo "<option value=0>0 (zondag)</option>";
        echo "<option value=1>1 (maandag)</option>";
        echo "<option value=2>2 (dinsdag)</option>";
        echo "<option value=3>3 (woensdag)</option>";
        echo "<option value=4>4 (donderdag)</option>";
        echo "<option value=5>5 (vrijdag)</option>";
        echo "<option value=6>6 (zaterdag)</option>";
}

?>
<!doctype html>
<html lang='NL'>
<head>
<meta name="robots" content="noindex">
<title>Backup configuratie</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css" />
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/jquery-validate-link/jquery.validate.min.js"></script>
<script src="./js/jquery-validate-link/additional-methods.min.js"></script>
<script src="./js/p1mon-util.js"></script>
</head>
<body>
<script>
var initloadtimer;

function selectorUpdate(selected, toupdate) {
        //console.log(selected)
        var v = $(selected+" option:selected" ).val()
        $(toupdate).val(v);
        $("#formvalues").validate().element(toupdate);
}

function readJsonApiConfiguration(){ 
    $.getScript( "./api/v1/status", function( data, textStatus, jqxhr ) {
      try {
        var jsonarr = JSON.parse(data); 
        for (var j=0;  j<jsonarr.length; j++){   
                switch(jsonarr[j][0]) {
                    case 47:
                        $('#ftp_backup_timestamp').text( jsonarr[j][1] );
                                                break;
                    case 49:
                                                $('#ftp_backup_timestamp_succes').text( jsonarr[j][1] );
                        break;
                                        case 48:
                                                $('#ftp_backup_status').text( jsonarr[j][1] );
                        break;
                                        case 60:
                                                $('#dbx_backup_timestamp').text( jsonarr[j][1] );
                        break;
                                        case 61:
                                                $('#dbx_backup_timestamp_succes').text( jsonarr[j][1] );
                        break;
                                        case 62:
                                                $('#dbx_backup_status').text( jsonarr[j][1] );
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

function LoadData() {
        clearTimeout(initloadtimer);
        //readJsonDataConfig();
        readJsonApiConfiguration();
        initloadtimer = setInterval(function(){LoadData();}, 5000);
}

$(function () {
        // prepopulate the select inputs
        $("#minutes").val("<?php echo $cron_pieces[0];?>");
        $("#hours").val("<?php echo $cron_pieces[1];?>");
        $("#days").val("<?php echo $cron_pieces[2];?>");
        $("#months").val("<?php echo $cron_pieces[3];?>");
        $("#weekdays").val("<?php echo $cron_pieces[4];?>");
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
                                <?php menu_control(10);?>
                        </div>
                        
                        <div id="right-wrapper-config"> <!-- right block -->
                        <!-- inner block right part of screen -->
                            <div id="right-wrapper-config-left">
                                    <!-- start of content -->
                                    <form name="formvalues" id="formvalues" method="POST">
                                            
                                            <div class="frame-4-top">
                                                    <span class="text-15">Timer instellingen</span>
                                            </div>
                                            <div class="frame-4-bot">
                                                    
                                                <div class="float-left pad-17">
                                                    <!-- line minutes -->
                                                    <div class="content-wrapper pos-36"> 
                                                        <div class="content-wrapper pad-16">
                                                                <label class="text-14">minuten</label>
                                                        </div>
                                                        <div class="content-wrapper">
                                                                <select onchange="selectorUpdate('#minutes','#i_minutes')" class="select-3 color-menu color-input-back cursor-pointer" id="minutes">
                                                                        <?php slectorMinutes();?>
                                                                </select>
                                                        </div>
                                                        <div class="content-wrapper">
                                                                <input class="input-7 color-settings color-input-back" id="i_minutes" name="i_minutes"  type="text" value="<?php echo $cron_pieces[0];?>">
                                                        </div>
                                                    </div> 

                                                    <!-- line hours -->
                                                    <div class="content-wrapper pos-36"> 
                                                            <div class="pad-16 content-wrapper">
                                                                    <label class="text-14">uren</label> 
                                                            </div>
                                                            <div class="content-wrapper">
                                                                    <select onchange="selectorUpdate('#hours','#i_hours')"  class="select-3 color-menu color-input-back cursor-pointer" id="hours">
                                                                            <?php slectorHours();?>
                                                                    </select>
                                                            </div>
                                                            <div class="content-wrapper">
                                                                    <input class="input-7 color-settings color-input-back" id="i_hours" name="i_hours" type="text" value="<?php echo $cron_pieces[1];?>">
                                                            </div>
                                                    </div> 

                                                    <!-- line day of the month -->
                                                    <div class="content-wrapper pos-36"> 
                                                            <div class="pad-16 content-wrapper">
                                                                    <label class="text-14">dag van de maand</label> 
                                                            </div>
                                                            <div class="content-wrapper">
                                                                    <select onchange="selectorUpdate('#days','#i_days')" class="select-3 color-menu color-input-back cursor-pointer" id="days">
                                                                            <?php slectorDays();?>
                                                                    </select>
                                                            </div>
                                                            <div class="content-wrapper">
                                                                    <input class="input-7 color-settings color-input-back" id="i_days" name="i_days" type="text" value="<?php echo $cron_pieces[2];?>">
                                                            </div>
                                                    </div> 

                                                    <!-- month -->
                                                    <div class="content-wrapper pos-36"> 
                                                            <div class="pad-16 content-wrapper">
                                                                    <label class="text-14">maand</label> 
                                                            </div>
                                                            <div class="content-wrapper">
                                                                    <select onchange="selectorUpdate('#months','#i_months')" class="select-3 color-menu color-input-back cursor-pointer" id="months">
                                                                            <?php slectorMonths();?>
                                                                    </select>
                                                            </div>
                                                            <div class="content-wrapper">
                                                                    <input class="input-7 color-settings color-input-back" id="i_months" name="i_months" type="text" value="<?php echo $cron_pieces[3];?>">
                                                            </div>
                                                    </div> 

                                                    <!-- weekday -->
                                                    <div class="content-wrapper pos-36"> 
                                                        <div class="pad-16 content-wrapper">
                                                                <label class="text-14">dag van de week</label>  
                                                        </div>
                                                        <div class="content-wrapper">
                                                                <select onchange="selectorUpdate('#weekdays','#i_weekdays')" class="select-3 color-menu color-input-back cursor-pointer" id="weekdays">
                                                                        <?php slectorWeekDays();?>
                                                                </select>
                                                        </div>
                                                        <div class="content-wrapper">
                                                                <input class="input-7 color-settings color-input-back" id="i_weekdays" name="i_weekdays" type="text" value="<?php echo $cron_pieces[4];?>">
                                                        </div>
                                                    </div> 
                                                </div>
                                            </div>
                                            <!-- end of timer part -->
                                            <p></p>
                                            <div class="frame-4-top">
                                                    <span class="text-15">FTP gegevens</span>
                                            </div>
                                            <div class="frame-4-bot">
                                                <div class="float-left pad-17">
                                                
                                                <div class="pad-1 content-wrapper float-right" title="<?php echo strIdx(22);?>">
                                                        <button class="input-2 but-1 cursor-pointer" id="ftp_test_button" name="ftp_test_button" type="submit">
                                                                <i class="color-menu fa-3x far fa-play-circle"></i><br>
                                                                <span class="color-menu text-7">test</span>
                                                        </button>
                                                </div>
                                                
                                                <div class="content-wrapper pos-36"> 
                                                        <div class="pad-16 content-wrapper">
                                                                <label class="text-14">back-up</label> 
                                                        </div>
                                                        <div class="content-wrapper">
                                                                <input class="cursor-pointer" id="fs_rb_aan_ftp_backup" name="ftp_backup_active" type="radio" value="1" <?php if ( config_read(36) == 1 ) { echo 'checked'; }?>>Aan
                                                                <input class="cursor-pointer" id="fs_rb_uit_ftp_backup" name="ftp_backup_active" type="radio" value="0" <?php if ( config_read(36) == 0 ) { echo 'checked'; }?>>Uit
                                                        </div>
                                                </div> 
                                                <p class="p-1"></p>
                                                <div class="content-wrapper pos-36" title="<?php echo strIdx(12);?>"> 
                                                        <div class="pad-16 content-wrapper">
                                                                <label class="text-14">ftp mode</label> 
                                                        </div>
                                                        <div class="content-wrapper">
                                                                <input class="cursor-pointer" id="fs_rb_ftp"  name="ftp_mode" type="radio" value="ftp"  <?php if ( config_read(76) == 1 ) { echo 'checked'; }?>>FTP
                            <input class="cursor-pointer" id="fs_rb_ftps" name="ftp_mode" type="radio" value="ftps" <?php if ( config_read(35) == 1 ) { echo 'checked'; }?>>FTPS
                            <input class="cursor-pointer" id="fs_rb_sftp" name="ftp_mode" type="radio" value="sftp" <?php if ( config_read(77) == 1)  { echo 'checked'; }?>>SFTP
                            </div>
                        </div> 

                        <div class="content-wrapper pos-36" title="<?php echo strIdx(13);?>"> 
                                <div class="pad-16 content-wrapper">
                                        <label class="text-14">account naam</label> 
                                </div>
                                <div class="content-wrapper">
                                        <input class="input-6 color-settings color-input-back" id="i_ftp_name" name="i_ftp_name" type="text" value="<?php echo config_read(28);?>">
                                </div>
                        </div> 

                        <div class="content-wrapper pos-36" title="<?php echo strIdx(14);?>"> 
                                <div class="pad-16 content-wrapper">
                                        <label class="text-14">wachtwoord</label> 
                                </div>
                                <div class="content-wrapper">
                                        <input class="input-6 color-settings color-input-back" id="i_ftp_pword" name="i_ftp_pword" type="password" value="<?php echo decodeString( 29, 'ftppw' );?>">
                                </div>
                                <div class="content-wrapper pad-1 cursor-pointer" id="api_passwd" onclick="toggelPasswordVisibility('i_ftp_pword')" >
                                        <span><i class="color-menu pad-7 fas fa-eye"></i></span>
                                </div>
                        </div> 
 
                        <div class="content-wrapper pos-36" title="<?php echo strIdx(15);?>"> 
                                <div class="pad-16 content-wrapper">
                                        <label class="text-14">ftp folder</label> 
                                </div>
                                <div class="content-wrapper">
                                        <input class="input-6 color-settings color-input-back" id="i_ftp_folder" name="i_ftp_folder" type="text" value="<?php echo config_read(30);?>">
                                </div>
                        </div> 

                        <div class="content-wrapper pos-36" title="<?php echo strIdx(16);?>"> 
                                <div class="pad-16 content-wrapper">
                                        <label class="text-14">server adres</label> 
                                </div>
                                <div class="content-wrapper">
                                        <input class="input-6 color-settings color-input-back" id="i_ftp_host" name="i_ftp_host" type="text" value="<?php echo config_read(31);?>">
                                </div>
                        </div> 
                        
                        <div class="content-wrapper pos-36" title="<?php echo strIdx(17);?>"> 
                                <div class="pad-16 content-wrapper">
                                        <label class="text-14">server poort</label> 
                                </div>
                                <div class="content-wrapper">
                                        <input class="input-6 color-settings color-input-back" id="i_ftp_host_port" name="i_ftp_host_port" type="text" value="<?php echo config_read(32);?>">
                                </div>
                        </div> 

                        <div class="content-wrapper pos-36" title="<?php echo strIdx(18);?>"> 
                                <div class="pad-16 content-wrapper">
                                        <label class="text-14">aantal versies</label> 
                                </div>
                                <div class="content-wrapper">
                                        <input class="input-6 color-settings color-input-back" id="i_ftp_max_versions" name="i_ftp_max_versions" type="text" value="<?php echo config_read(34);?>">
                                </div>
                        </div> 
                        <div class="content-wrapper pos-36 margin-4" title="<?php echo strIdx(19);?>"> 
                                <div class="pad-16 content-wrapper">
                                        <label class="text-14">laatste backup</label> 
                                </div>
                                <div class="content-wrapper">
                                        <label id="ftp_backup_timestamp" class="text-14"></label>
                                </div>
                        </div> 
                        <p class="p-1"></p>

                        <div class="content-wrapper pos-36" title="<?php echo strIdx(20);?>"> 
                                <div class="pad-16 content-wrapper">
                                        <label class="text-14">succesvol op</label> 
                                </div>
                                <div class="content-wrapper">
                                        <label id="ftp_backup_timestamp_succes" class="text-14"></label>
                                </div>
                        </div> 
                        <p class="p-1"></p>
                                                    
                        <div class="content-wrapper pos-36" title="<?php echo strIdx(21);?>"> 
                                <div class="pad-16 content-wrapper">
                                        <label class="text-14">backup status</label> 
                                </div>
                                
                        </div> 
                        <div class="content-wrapper pos-37">
                                        <label  id="ftp_backup_status" class="text-14"></label>
                        </div>
                        
                        </div>
                        </div>
                        <!-- end of ftp backup -->
                                            

                        <p></p>
                        <div class="frame-4-top">
                                <span class="text-15">Dropbox gegevens</span>
                        </div>
                        <div class="frame-4-bot">
                                <div class="float-left pad-17">
                                
                                <div class="content-wrapper pos-36"> 
                                        <div class="pad-16 content-wrapper">
                                                <label class="text-14">back-up</label> 
                                        </div>
                                        <div class="content-wrapper">
                                                <input class="cursor-pointer" id="fs_rb_aan_dbx_backup" name="dbx_backup_active" type="radio" value="1" <?php if ( config_read(49) == 1 ) { echo 'checked'; }?>>Aan
                                                <input class="cursor-pointer" id="fs_rb_uit_dbx_backup" name="dbx_backup_active" type="radio" value="0" <?php if ( config_read(49) == 0 ) { echo 'checked'; }?>>Uit
                                        </div>
                                </div> 
                                <p class="p-1"></p>

                                <div class="content-wrapper pos-36" title="<?php echo strIdx(18);?>"> 
                                        <div class="pad-16 content-wrapper">
                                                <label class="text-14">aantal versies</label> 
                                        </div>
                                        <div class="content-wrapper">
                                                <input class="input-6 color-settings color-input-back" id="i_dbx_max_versions" name="i_dbx_max_versions" type="text" value="<?php echo config_read(48);?>">
                                        </div>
                                </div> 
                                <div class="content-wrapper pos-36 margin-4" title="<?php echo strIdx(19);?>"> 
                                        <div class="pad-16 content-wrapper">
                                                <label class="text-14">laatste backup</label> 
                                        </div>
                                        <div class="content-wrapper">
                                                <label id="dbx_backup_timestamp" class="text-14"></label>
                                        </div>
                                </div> 
                                <p class="p-1"></p>
                                
                                <div class="content-wrapper pos-36" title="<?php echo strIdx(20);?>"> 
                                        <div class="pad-16 content-wrapper">
                                                <label class="text-14">succesvol op</label> 
                                        </div>
                                        <div class="content-wrapper">
                                                <label id="dbx_backup_timestamp_succes" class="text-14"></label>
                                        </div>
                                </div> 
                                <p class="p-1"></p>

                                <div class="content-wrapper pos-36" title="<?php echo strIdx(21);?>"> 
                                        <div class="pad-16 content-wrapper">
                                                <label class="text-14">backup status</label> 
                                        </div>
                                        
                                </div> 
                                <div class="content-wrapper pos-33">
                                                <label  id="dbx_backup_status" class="text-14"></label>
                                </div>
                                
                                </div>
                                </div>

                                <!-- placeholder variables for session termination -->
                                <input type="hidden" name="logout" id="logout" value="">
                                <input type="hidden" name="systemaction" id="systemaction" value="">
                        </form>
                </div>

                <div id="right-wrapper-config-right">
                        <div class="frame-4-top">
                            <span class="text-15">hulp</span>
                        </div>
                        <div class="frame-4-bot text-10">
                                <?php echo strIdx(11);?>
                        </div>
                </div>

                </div>

                <!-- </div> -->

        <!-- end inner block right part of screen -->
        </div>
        <?php echo div_err_succes();?>
        
<script>
$('#ftp_test_button').click(function(event) {
        //console.log("ftp_test_button")
        document.formvalues.systemaction.value = 'ftp_test_button';
    $('#formvalues').submit();
        hideStuff('ftp_test_button');
        event.preventDefault();
});

$.validator.addMethod(
    "cron",
    function(value, element) {
                
                v = value.replace(/ /g,'')
                // console.log(v.length) 
                // console.log(value.trim().length)
                if ( value.trim().length != v.length ) { return false } // spaces in input
                // remove all but wanted chars.
                t = v.replace(/[\d/,/*/-]/g,'')
                //console.log(t)
                // check the cleaned string with the input string
                if ( t.length > 0 ) { return false } // unwanted chars detected. 
                v = value.replace(/-/g,',') // easy fix so we can do easy check
                v = value.replace(/[*///]/g,'') // remove wildcard char.
                //console.log(v)
                // split string on ,
                var res = v.split(",")
                var arrayLength = res.length;
                for (var i = 0; i < arrayLength; i++) {
                        //console.log(res[i])
                        if(res[i] > 59) { return false }
                }
                return true; 
    }
);


$(function() {
        $("#formvalues").validate({
                rules: {
                        'i_minutes': {
                                required: true,
                                cron: true
                        },
                        'i_hours': {
                                required: true,
                                cron: true
                        },
                        'i_days': {
                                required: true,
                                cron: true
                        },
                        'i_months': {
                                required: true,
                                cron: true
                        },
                        'i_weekdays': {
                                required: true,
                                cron: true
                        },
                        'i_weekdays': {
                                required: true,
                                cron: true
                        },
                        'i_ftp_host_port': {
                required: true,
                number: true,
                max: 65535,
                min: 1
            },
                        'i_ftp_max_versions': {
                required: true,
                number: true,
                max: 100000,
                min: 1
            }                         
                        
        },
                /*
        invalidHandler: function(e, validator) { 
            var errors = validator.numberOfInvalids(); 
            if (errors) {       
                    showStuff('err_msg');
                          setTimeout( function() { hideStuff('err_msg');},5000);
             } 
          },
                 */
        errorPlacement: function(error, element) {
                //$(this).addClass('error');
                //$("#form_tarieven_button").addClass('error');
                //$("#form_tarieven_button").css("visibility","hidden");
            return false;  // will suppress error messages    
        }
    }); 
});
</script>
<?php echo autoLogout(); ?>        
</body>
</html>