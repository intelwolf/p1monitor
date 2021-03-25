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

if( isset($_POST["day_night_mode"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '" . $_POST["day_night_mode"] . "' where ID = 78"))  $err_cnt += 1;
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
<title>P1-poort configuratie</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css" />
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/p1mon-util.js"></script>
</head>
<body>
<audio id="audio" src="./sound/beep-04.wav"></audio>
<script>
var initloadtimer;
var soundPlayed = false;

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

function readJsonApiConfiguration(){ 
    $.getScript( "./api/v1/configuration", function( data, textStatus, jqxhr ) {
      try {
        var jsonarr = JSON.parse(data); 
        for (var j=0;  j<jsonarr.length; j++){   
                switch(jsonarr[j][0]) {
                    case 45:
                       if ( jsonarr[j][1] == '0') {
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
                    default:
                        break;
            }
        }
      } catch(err) {
          console.log( err );
      }
   });
}

function readJsonApiStatus(){ 
    $.getScript( "./api/v1/status", function( data, textStatus, jqxhr ) {
        try {
            var jsondata = JSON.parse(data); 
    
            for (var j=91;  j < jsondata.length; j++){  
                // console.log( jsondata[j][0] + ' - ' + jsondata[j][1] )
                if ( jsondata[j][0] == 92 ) {
                    $('#ser_device').text( jsondata[j][1] );
                    break; // only one item needed
                }
            }
        } catch(err) {
            console.log( err )
        }
    });
}


function LoadData() {
    clearTimeout(initloadtimer);
    readJsonApiConfiguration();
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
                            <span class="text-15">seriële instellingen</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left">
                                <i class="text-10 pad-7 fas fa-download"></i>
                                <label class="text-10" >baudrate</label>
                                <p class="p-1"></p>
                                <i class="text-10 pad-8 fas fa-download"></i>
                                <label class="text-10">byte size</label> 
                                <p class="p-1"></p>
                                <i class="text-10 pad-9 fas fa-download"></i>
                                <label class="text-10">parity</label> 
                                <p class="p-1"></p>
                                <i class="text-10 pad-8 fas fa-download"></i>
                                <label class="text-10">stopbits</label> 
                            </div>
                            <div class="float-left pad-1">
                                <select class="select-1 color-select color-input-back cursor-pointer" name="baudrate_list" id="baudrate_list">
                                    <?php makeSelector(7);?>
                                </select>
                                <p class="p-1"></p>
                        
                                <select class="select-1 color-select color-input-back cursor-pointer" name="bytesize_list" id="bytesize_list">
                                    <?php makeSelector(8);?>
                                </select>
                                <p class="p-1"></p>
                                <select class="select-1 color-select color-input-back cursor-pointer" name="parity_list" id="parity_list">
                                    <?php makeSelector(9);?>
                                </select>
                                <p class="p-1"></p>
                                <select class="select-1 color-select color-input-back cursor-pointer" name="stopbit_list" id="stopbit_list">
                                    <?php makeSelector(10);?>
                                </select>
                            </div>
                            
                        </div>
                       
                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15">status</span>
                        </div>
                        <div class="frame-4-bot">
                        <div class="text-10">Seriële device in gebruik:&nbsp;<span id="ser_device"></span></div>
                            <br>
                            <div class="float-left">
                                <div class="float-left pad-10">
                                    <i style="display:none" id="serial_ok"  class="color-ok fas fa-3x fa-check-square" title="<?php strIdx(2);?>"></i> 
                                    <i style="display:none" id="serial_nok" class="color-error fas fa-3x fa-exclamation-triangle" title="<?php strIdx(2);?>"></i> 
                                </div> 
                                <div>
                                    <label style="display:none" id="serial_ok_label" class="float-left text-10" >&nbsp;&nbsp;&nbsp;&nbsp;in orde</label>
                                    <label style="display:none" id="serial_nok_label" class="float-left text-10" >&nbsp;geen data</label>
                                </div>
                            </div>
                        
                            <div class="pos-33 float-right text-10">
                                <?php echo strIdx(2);?>
                            </div>

                        </div>
                        
                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15">P1 telegram</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left">
                                <div class="pad-20">
                                    <i class="text-10 fas fa-cogs"></i>
                                    <label class="text-10" >gas code nummer</label>
                                </div>
                                
                                <div class="pad-20">
                                    <i class="text-10 fas fa-check-double"></i> 
                                    <label class="text-10" >crc controle aan</label>
                                </div>
                                
                                <div class="pad-20">
                                    <i class="text-10 fas fa-cogs"></i> 
                                    <label class="text-10 pad-20">dag/nacht mode</label>
                                </div>
                            </div>
                            
                            <div class="float-left pad-19">
                                <select class="select-1 color-select color-input-back cursor-pointer" name="gas_prefix_list" id="gas_prefix_list">
                                    <?php makeSelector(6);?>
                                </select>
                                
                                <div>
                                    <input class="cursor-pointer" name="crc" type="radio" value="1" <?php if ( config_read(45) == 1 ) { echo 'checked'; }?>>Aan
                                    <input class="cursor-pointer" name="crc" type="radio" value="0" <?php if ( config_read(45) == 0 ) { echo 'checked'; }?>>Uit
                                </div>
                                
                                <select class="select-2 color-select color-input-back cursor-pointer" name="day_night_mode" id="day_night_mode">
                                    <?php makeSelector(5);?>
                                </select>
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
                    </div>
                </div>
            </div>    
            <!-- end inner block right part of screen -->
    </div>    
    <?php echo autoLogout(); ?>
</body>
</html>