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

//print_r($_POST);
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

$socat_previous_ip     = config_read( 198 );
$socat_previous_port   = config_read( 199 );
$socat_previous_active = config_read( 200 );
$socat_is_changed      = false;


if( isset($_POST["socat_ip"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $socat_previous_ip != $_POST["socat_ip"] ) { $socat_is_changed = true; }
    if ( updateConfigDb("update config set parameter = '" . $_POST["socat_ip"] . "' where ID = 198"))  $err_cnt += 1;
}

if( isset($_POST["socat_port"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $socat_previous_port != $_POST["socat_port"] ) { $socat_is_changed = true; }
    if ( updateConfigDb("update config set parameter = '" . $_POST["socat_port"] . "' where ID = 199"))  $err_cnt += 1;
}


if ( isset($_POST["socat_on_off"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $socat_previous_active != $_POST["socat_on_off"] ) { $socat_is_changed = true; }
    if ($_POST["socat_on_off"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 200")) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 200")) $err_cnt += 1;
    }
}

if( isset($_POST["baudrate_list"]) || isset($_POST["bytesize_list"]) || isset($_POST["parity_list"]) || isset($_POST["stopbit_list "]))
{
    // convert from user format to machine format if needed.
        
    // stopbits
    if ( $_POST["stopbit_list"] == 'STOPBITS_TWO')  { $stopbit = 2; }
    else { $stopbit = 1; }
    //print_r("stopbits=".$stopbit." ");
        
    // parity
    $parity='E'; //default 
    if ( $_POST["parity_list"] == 'PARITY_ODD')   $parity='O';
    if ( $_POST["parity_list"] == 'PARITY_NONE')  $parity='N';
    if ( $_POST["parity_list"] == 'PARITY_MARK')  $parity='M';
    if ( $_POST["parity_list"] == 'PARITY_SPACE') $parity='S';
    //print_r("parity=".$parity." ");
        
    // byte size
    $bytesize = '7'; // default
    if ( $_POST["bytesize_list"] == 'FIVEBITS')  $bytesize = '5' ;
    if ( $_POST["bytesize_list"] == 'SIXBITS')   $bytesize = '6' ;
    if ( $_POST["bytesize_list"] == 'EIGHTBITS') $bytesize = '8' ;
    //print_r("bytesize=".$bytesize." "); 
    //print_r("baudrate=".$_POST["baudrate_list"]." "); 
        
    $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '" . $_POST["baudrate_list"] . "' where ID = 7"))  $err_cnt += 1;
    if ( updateConfigDb("update config set parameter = '" . $bytesize               . "' where ID = 8"))  $err_cnt += 1;
    if ( updateConfigDb("update config set parameter = '" . $parity                 . "' where ID = 9"))  $err_cnt += 1;
    if ( updateConfigDb("update config set parameter = '" . $stopbit                . "' where ID = 10")) $err_cnt += 1;
}

if( isset($_POST["gas_prefix_list"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '" . $_POST["gas_prefix_list"] . "' where ID = 38"))  $err_cnt += 1;
}


if ( isset($_POST["crc"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["crc"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 45")) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 45")) $err_cnt += 1;
    }
}

if ( isset($_POST["p1_telgram_speed"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["p1_telgram_speed"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 154")) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 154")) $err_cnt += 1;
    }
}

if ( isset($_POST["p1_large_consumer"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST["p1_large_consumer"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 178")) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 178")) $err_cnt += 1;
    }
}

if( isset($_POST["day_night_mode"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '" . $_POST["day_night_mode"] . "' where ID = 78"))  $err_cnt += 1;
}


if( isset($_POST["serial_device"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '" . $_POST["serial_device"] . "' where ID = 197"))  $err_cnt += 1;
}

//echo "socat_is_changed = ".$socat_is_changed;

if ( $socat_is_changed == true ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '1' where ID = 201"))  $err_cnt += 1;
}

function makeSelector($id) {

      // day/night mode
      if ( $id == 5 ) { 
        $configValue = config_read(78);
        $g1=$g2=$g3=$g4='';
        if ($configValue == '0' ) { $g1 = 'selected="selected"';} 
        if ($configValue == '1' ) { $g2 = 'selected="selected"';} 
        echo '<option ' . $g1 . ' value="0">Nederland (standaard)</option>';
        echo '<option ' . $g2 . ' value="1">Belgie</option>';
    }

    // values 1 to 4
    if ( $id == 6 ) { 
        $configValue = config_read(38);
        $g1=$g2=$g3=$g4='';
        if ($configValue == '1' ) { $g1 = 'selected="selected"';} 
        if ($configValue == '2' ) { $g2 = 'selected="selected"';} 
        if ($configValue == '3' ) { $g3 = 'selected="selected"';} 
        if ($configValue == '4' ) { $g4 = 'selected="selected"';} 
        echo '<option ' . $g1 . ' value="1">1</option>';
        echo '<option ' . $g2 . ' value="2">2</option>';
        echo '<option ' . $g3 . ' value="3">3</option>';
        echo '<option ' . $g4 . ' value="4">4</option>';
    }
    
    // stop bits
    if ( $id == 10 ) { 
        $configValue = config_read($id);
        if ($configValue == '1' ) {
            $bit1 = 'selected="selected"';
            $bit2 = ''; 
        } else {
            $bit1 = '';
            $bit2 = 'selected="selected"';    
        }
        echo '<option ' . $bit1 . ' value="STOPBITS_ONE">1 stop bit </option>';
        echo '<option ' . $bit2 . ' value="STOPBITS_TWO">2 stop bits</option>';
    }
    
    // partity bits
    // serial.PARITY_EVEN=E
    // serial.PARITY_ODD=O
    // serial.PARITY_NONE=N
    // serial.PARITY_MARK=M
    // serial.PARITY_SPACE=S
    if ( $id == 9 ) { 
        $configValue = config_read($id);
        $bit_even  = '';
        $bit_odd   = ''; 
        $bit_none  = ''; 
        $bit_mark  = ''; 
        $bit_space = ''; 
        
        // MARK & SPACE geeft problemen, is alleen uitgemarkeerd hier, achterliggende code is actief.
        if ($configValue == 'E' ) { $bit_even  = 'selected="selected"'; }  
        if ($configValue == 'O' ) { $bit_odd   = 'selected="selected"'; }  
        if ($configValue == 'N' ) { $bit_none  = 'selected="selected"'; }  
        //if ($configValue == 'M' ) { $bit_mark  = 'selected="selected"'; }  
        //if ($configValue == 'S' ) { $bit_space = 'selected="selected"'; }  
        
        echo '<option ' . $bit_even  . ' value="PARITY_EVEN" >even    </option>';
        echo '<option ' . $bit_odd   . ' value="PARITY_ODD"  >oneven  </option>';
        echo '<option ' . $bit_none  . ' value="PARITY_NONE" >geen    </option>';
        //echo '<option ' . $bit_mark  . ' value="PARITY_MARK" >altijd 1</option>';
        //echo '<option ' . $bit_space . ' value="PARITY_SPACE">altijd 0</option>';
    }
    
    // byte size
    // serial.FIVEBITS=5
    // serial.SIXBITS=6
    // serial.SEVENBITS=7
    // serial.EIGHTBITS=8
    if ( $id == 8 ) { 
        $configValue = config_read($id);
        $ser_fivebits  = '';
        $ser_sixbits   = ''; 
        $ser_zevenbits = ''; 
        $ser_eightbits = ''; 
       
        if ($configValue == '5' ) { $ser_fivebits  = 'selected="selected"'; }  
        if ($configValue == '6' ) { $ser_sixbits   = 'selected="selected"'; }  
        if ($configValue == '7' ) { $ser_zevenbits = 'selected="selected"'; }  
        if ($configValue == '8' ) { $ser_eightbits = 'selected="selected"'; }  
        
        echo '<option ' . $ser_fivebits  . ' value="FIVEBITS"  >5 bits</option>';
        echo '<option ' . $ser_sixbits   . ' value="SIXBITS"   >6 bits</option>';
        echo '<option ' . $ser_zevenbits . ' value="SEVENBITS" >7 bits</option>';
        echo '<option ' . $ser_eightbits . ' value="EIGHTBITS" >8 bits</option>';
    }
    
    // baudrates
    // 9600
    // 14400
    // 19200
    // 28800
    // 38400
    // 57600
    // 115200
    // 230400
    if ( $id == 7 ) { 
        $configValue = config_read($id);
        $baud9k6  = '';
        $baud14k4 = ''; 
        $baud19k2 = ''; 
        $baud28k8 = '';
        $baud34k4 = ''; 
        $baud57k6 = '';
        $baud115k2 = '';
        $baud230k4 = ''; 
        
        if ($configValue == '9600'  )  { $baud9k6   = 'selected="selected"'; }  
        if ($configValue == '14400'  ) { $baud14k4  = 'selected="selected"'; }  
        if ($configValue == '19200'  ) { $baud19k2  = 'selected="selected"'; }  
        if ($configValue == '28800'  ) { $baud28k8  = 'selected="selected"'; } 
        if ($configValue == '38400'  ) { $baud34k4  = 'selected="selected"'; }  
        if ($configValue == '57600'  ) { $baud57k6  = 'selected="selected"'; }  
        if ($configValue == '115200' ) { $baud115k2 = 'selected="selected"'; }
        if ($configValue == '230400' ) { $baud230k4 = 'selected="selected"'; } 
        
        echo '<option ' . $baud9k6   . ' value="9600"   >9600  </option>';
        echo '<option ' . $baud14k4  . ' value="14400"  >14400 </option>';
        echo '<option ' . $baud19k2  . ' value="19200"  >19200 </option>';
        echo '<option ' . $baud28k8  . ' value="28800"  >28800 </option>';
        echo '<option ' . $baud34k4  . ' value="38400"  >38400 </option>';
        echo '<option ' . $baud57k6  . ' value="57600"  >57600 </option>';
        echo '<option ' . $baud115k2 . ' value="115200" >115200</option>';
        echo '<option ' . $baud230k4 . ' value="230400" >230400</option>';
    }  
}
?>
<!doctype html>
<html lang="nl">
<head>
<meta name="robots" content="noindex">
<title><?php echo strIdx( 244 );?></title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css">
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css">

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/p1mon-util.js"></script>
<script src="./js/jquery-validate-link/jquery.validate.min.js"></script>
<script src="./js/jquery-validate-link/additional-methods.min.js"></script>

</head>
<body>
<audio id="audio" src="./sound/beep-04.wav"></audio>
<script>
var initloadtimer;
var soundPlayed = false;
var socat_timestamp_str = '<?php echo strIdx( 324 );?>'

function PlaySound() {
    var sound = document.getElementById("audio");
    sound.play()
} 

function getFormattedDate() {
    var date = new Date();

    var month = date.getMonth() + 1;
    var day = date.getDate();
    var hour = date.getHours();
    var min = date.getMinutes();
    var sec = date.getSeconds();

    month = (month < 10 ? "0" : "") + month;
    day = (day < 10 ? "0" : "") + day;
    hour = (hour < 10 ? "0" : "") + hour;
    min = (min < 10 ? "0" : "") + min;
    sec = (sec < 10 ? "0" : "") + sec;

    var str = date.getFullYear() + "-" + month + "-" + day + " " +  hour + ":" + min + ":" + sec;
    return str;
}

function readJsonApiStatus(){ 
    $.getScript( "./api/v1/status", function( data, textStatus, jqxhr ) {
        try {
            var jsondata = JSON.parse(data); 
    
            for (var j=91;  j < jsondata.length; j++){  
                //console.log(" x="+ jsondata[j][0] + ' - ' + jsondata[j][1] )

                if ( jsondata[j][0] == 123 ) {

                    if ( jsondata[j][1] == '0' ) {
                        hideStuff('serial_ok'); 
                        showStuff('serial_nok');
                        if(!soundPlayed) {
                            soundPlayed = true;
                            PlaySound();
                        }
                    } else {
                        hideStuff('serial_nok'); 
                        showStuff('serial_ok');
                        if(soundPlayed) soundPlayed = false; // reset
                    }
                }

                if ( jsondata[j][0] == 92 ) {
                    $('#ser_device').text( jsondata[j][1] );
                }

                if ( jsondata[j][0] == 128 ) {
                    $('#socat_timestamp').html( socat_timestamp_str + "&nbsp;:&nbsp;" +jsondata[j][1] );
                }

                socat_timestamp
            }
        } catch(err) {
            console.log( err )
        }
    });
}

function LoadData() {
    clearTimeout(initloadtimer);
    readJsonApiStatus();
    initloadtimer = setInterval(function(){LoadData();}, 3000);
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
                <?php menu_control(6);?>
            </div>
            
            <div id="right-wrapper-config"> <!-- right block -->
            <!-- inner block right part of screen -->
                <div id="right-wrapper-config-left-2">
                    <!-- start of content -->
                    <form name="formvalues" id="formvalues" method="POST">

                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 245 );?></span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="rTable">
                                    <div class="rTableRow">
                                        <div class="rTableCell width-24">
                                            <i class="text-10 fas fa-download"></i>
                                        </div>
                                        <div class="rTableCell width-80">
                                            <label class="text-10">baudrate</label> 
                                        </div>
                                        <div class="rTableCell">
                                            <select class="select-3 color-select color-input-back cursor-pointer" name="baudrate_list" id="baudrate_list">
                                                <?php makeSelector(7);?>
                                            </select>
                                        </div>
                                    </div>

                                    <div class="rTableRow"> 
                                        <div class="rTableCell width-24">
                                            <i class="text-10 fas fa-download"></i>
                                        </div>
                                        <div class="rTableCell width-80">
                                            <label class="text-10">byte size</label> 
                                        </div>
                                        <div class="rTableCell">
                                            <select class="select-3 color-select color-input-back cursor-pointer" name="bytesize_list" id="bytesize_list">
                                                <?php makeSelector(8);?>
                                            </select>
                                        </div>
                                    </div>

                                    <div class="rTableRow">
                                        <div class="rTableCell width-24">
                                            <i class="text-10 fas fa-download"></i>
                                        </div>
                                        <div class="rTableCell width-80">
                                            <label class="text-10">parity</label> 
                                        </div>
                                        <div class="rTableCell">
                                            <select class="select-3 color-select color-input-back cursor-pointer" name="parity_list" id="parity_list">
                                                <?php makeSelector(9);?>
                                            </select>
                                        </div>
                                    </div>

                                    <div class="rTableRow">
                                        <div class="rTableCell width-24">
                                            <i class="text-10 fas fa-download"></i>
                                        </div>
                                        <div class="rTableCell width-80">
                                            <label class="text-10">stopbits</label> 
                                        </div>
                                        <div class="rTableCell">
                                            <select class="select-3 color-select color-input-back cursor-pointer" name="stopbit_list" id="stopbit_list">
                                                <?php makeSelector(10);?>
                                            </select>
                                        </div>
                                    </div>

                                    <div class="rTableRow">
                                        <div class="rTableCell width-24">
                                            <i class="text-10 fas fa-network-wired"></i>
                                        </div>
                                        <div class="rTableCell width-80">
                                            <label class="text-10">device</label> 
                                        </div>
                                        <div class="rTableCell">
                                            <input class="input-3 color-settings color-input-back" id="serial_device" name="serial_device" 
                                            type="text" placeholder="/dev/xxxx" value="<?php echo config_read(197);?>">
                                        </div>
                                    </div>

                                </div>
                        </div>

                        <!-- socat -->
                        <p></p>
                        <div class="frame-4-top" title="<?php echo strIdx( 321 );?>">
                            <span class="text-15"><?php echo strIdx( 318 );?></span>
                        </div>
                        <div class="frame-4-bot" title="<?php echo strIdx( 321 );?>">
                            <div class="rTable">

                                    <div class="rTableRow">
                                        <div class="rTableCell width-24">
                                            <i class="text-10 fa-solid fa-toggle-off"></i>
                                        </div>
                                        <div class="rTableCell">
                                            <label class="text-10"><?php echo strIdx( 172 );?></label> 
                                        </div>
                                        <div class="rTableCell">
                                            <input class="cursor-pointer" name="socat_on_off" type="radio" value="1" <?php if ( config_read( 200 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                            <input class="cursor-pointer" name="socat_on_off" type="radio" value="0" <?php if ( config_read( 200 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                        </div>
                                    </div>

                                    <div class="rTableRow" title="<?php echo strIdx( 322 );?>">
                                        <div class="rTableCell width-24">
                                            <i class="text-10 fas fa-network-wired"></i>
                                        </div>
                                        <div class="rTableCell width-80">
                                            <label class="text-10"><?php echo strIdx( 319 );?></label> 
                                        </div>
                                        <div class="rTableCell">
                                            <input class="input-3 color-settings color-input-back" placeholder="n.n.n.n" id="socat_ip" name="socat_ip" type="text" value="<?php echo config_read( 198 );?>">
                                        </div>
                                    </div>

                                    <div class="rTableRow" title="<?php echo strIdx( 323 );?>">
                                        <div class="rTableCell width-24">
                                            <i class="text-10 fas  fa-network-wired"></i>
                                        </div>
                                        <div class="rTableCell width-80">
                                            <label class="text-10">IP poort</label> 
                                        </div>
                                        <div class="rTableCell">
                                            <input class="input-3 color-settings color-input-back" placeholder="1-65535"  id="socat_port" name="socat_port" type="text" value="<?php echo config_read( 199 );?>">
                                        </div>
                                    </div>

                                </div>

                                <div class="rTable">
                                    <div class="rTableRow">
                                        <div class="rTableCell width-210x">
                                            <i class="pad-7 text-10 far fa-clock"></i>
                                            <label id="socat_timestamp" class="text-10"><?php echo strIdx( 324 );?>:"??-??-?? ??:??:??"</label>
                                        </div>
                                    </div>
                                </div>
                               
                        </div>

                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 246 );?></span>
                        </div>
                        <div class="frame-4-bot" title="<?php echo strIdx( 2 );?>">
                            <div class="rTable">
                                <div class="rTableRow">
                                    <div class="rTableCell width-24">
                                        <i style="display:none" id="serial_ok"  class="color-ok fas fa-1x fa-check-square"></i> 
                                        <i style="display:none" id="serial_nok" class="color-error fas fa-1x fa-exclamation-triangle"></i> 
                                    </div>
                                    <div class="rTableCell text-10">
                                        <?php echo strIdx( 248 );?>&nbsp;<span id="ser_device"></span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 247 );?></span>
                        </div>
                        <div class="frame-4-bot">
                           <div class="rTable">

                                <div class="rTableRow" title="<?php echo strIdx( 27 );?>">
                                    <div class="rTableCell width-24">
                                        <i class="text-10 fas fa-cogs"></i>
                                    </div>
                                    <div class="rTableCell">
                                        <label class="text-10"><?php echo strIdx( 249 );?></label> 
                                    </div>
                                    <div class="rTableCell">
                                        <select class="select-1 color-select color-input-back cursor-pointer" name="gas_prefix_list" id="gas_prefix_list">
                                            <?php makeSelector(6);?>
                                        </select>
                                    </div>
                                </div>

                                <div class="rTableRow" title="<?php echo strIdx( 29 );?>">
                                    <div class="rTableCell width-24">
                                        <i class="text-10 fas fa-check-double"></i>
                                    </div>
                                    <div class="rTableCell">
                                        <label class="text-10"><?php echo strIdx( 250 );?></label> 
                                    </div>
                                    <div class="rTableCell">
                                        <input class="cursor-pointer" name="crc" type="radio" value="1" <?php if ( config_read(45) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="crc" type="radio" value="0" <?php if ( config_read(45) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                </div>


                                <div class="rTableRow" title="<?php echo strIdx( 64 );?>">
                                    <div class="rTableCell width-24">
                                        <i class="text-10 fas fa-cogs"></i>
                                    </div>
                                    <div class="rTableCell">
                                        <label class="text-10"><?php echo strIdx( 251 );?></label> 
                                    </div>
                                    <div class="rTableCell">
                                        <select class="select-2 color-select color-input-back cursor-pointer" name="day_night_mode" id="day_night_mode">
                                            <?php makeSelector(5);?>
                                        </select>
                                    </div>
                                </div>

                                <div class="rTableRow" title="<?php echo strIdx( 243 );?>">
                                    <div class="rTableCell width-24">
                                        <i class="text-10 fas fa-tachometer-alt"></i>
                                    </div>
                                    <div class="rTableCell">
                                        <label class="text-10"><?php echo strIdx( 252 );?></label> 
                                    </div>
                                    <div class="rTableCell">
                                        <input class="cursor-pointer" name="p1_telgram_speed" type="radio" value="1" <?php if ( config_read(154) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="p1_telgram_speed" type="radio" value="0" <?php if ( config_read(154) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                </div>

                                <div class="rTableRow" title="<?php echo strIdx( 309 );?>">
                                    <div class="rTableCell width-24">
                                        <i class="text-10 fa-solid fa-industry"></i>
                                    </div>
                                    <div class="rTableCell">
                                        <label class="text-10"><?php echo strIdx( 308 );?></label> 
                                    </div>
                                    <div class="rTableCell">
                                        <input class="cursor-pointer" name="p1_large_consumer" type="radio" value="1" <?php if ( config_read( 178 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="p1_large_consumer" type="radio" value="0" <?php if ( config_read( 178 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
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
                        <?php echo strIdx(1);?>
                        <?php echo strIdx(27);?>
                        <br><br>
                        <?php echo strIdx(29);?>
                        <br><br>
                        <?php echo strIdx(64);?>
                        <br><br>
                        <?php echo strIdx( 321 );?>
                    </div>
                </div>
            </div>    
            <!-- end inner block right part of screen -->
    </div>

    <script>
     $(function() {
         $("#formvalues").validate({
             rules: {
                 'socat_port': {
                     required: false,
                     number: true,
                     max: 65535,
                     min: 1
                 },
                 'socat_ip': {
                    ipv4: true
                }
             },
             errorPlacement: function(error, element) {
                 return false; // will suppress error messages
             }
         });
     });
     </script>

    <?php echo autoLogout(); ?>
</body>
</html>