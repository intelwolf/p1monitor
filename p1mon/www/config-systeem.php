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

#print_r($_POST);
$err_cnt = 0;

if ( isset($_POST["udp_deamon_active"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["udp_deamon_active"] == '1' ) {
        #echo "on<br>";
        if ( updateConfigDb("update config set parameter = '1' where ID = 55"))$err_cnt += 1;
    } else {
        #echo "off<br>";
        if ( updateConfigDb("update config set parameter = '0' where ID = 55"))$err_cnt += 1;
    }
}

if ( isset($_POST["version_check_active"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["version_check_active"] == '1' ) {
        #echo "on<br>";
        if ( updateConfigDb("update config set parameter = '1' where ID = 51"))$err_cnt += 1;
    } else {
        #echo "off<br>";
        if ( updateConfigDb("update config set parameter = '0' where ID = 51"))$err_cnt += 1;
    }
}

if ( isset($_POST['systemaction']) ) { 

    if ($_POST['systemaction'] === 'reboot'){ 
        //print "Reboot !<br>";
        writeSemaphoreFile('reboot');
        header('Location:bye.php');
    }

    if ( $_POST['systemaction'] === 'stop'){ 
        //print "Stop !<br>";
        writeSemaphoreFile('halt');
        header('Location:bye.php');
    }
    
    if ( $_POST['systemaction'] === 'clear_password'){ 
        deletePasswordFiles();
        header('Location:/home.php');
    }

}
?>
<!doctype html>
<html lang="nl">
<head>
<title>Systeem configuratie</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css" />
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/p1mon-util.js"></script>
<script src="./js/download2.js"></script>
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
                <?php menu_control(2);?>
            </div>
            
            <div id="right-wrapper-config"> <!-- right block -->
            <!-- inner block right part of screen -->
                <div id="right-wrapper-config-left-2">
                    <!-- start of content -->
                    <form name="formvalues" id="formvalues" method="POST">
                        <div class="frame-4-top">
                            <span class="text-15">herstart of stop systeem</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left pos-32">
                                <div class="float-left margin-3">
                                    <button class="input-2 but-1 cursor-pointer" id="fr_button" name="fr_button" type="submit">
                                        <i class="color-warning fa-3x fas fa-sync-alt"></i><br> 
                                        <span class="color-warning text-7">herstart</span>
                                    </button>
                                    <div class="pad-1 content-wrapper">
                                    <button class="input-2 but-1 cursor-pointer" id="fs_button" name="fs_button" type="submit">
                                        <i class="color-error fa-3x fas fa-power-off"></i><br>
                                        <span class="color-error text-7">&nbsp;stop</span>
                                    </button>
                                    </div>
                                </div>
                            
                            </div>    
                        </div>
                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15">wachtwoord reset</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left pos-32">
                                <div class="float-left margin-3">    
                                    <button class="input-2 but-1 cursor-pointer" id="pwreset_button" name="pwreset_button" type="submit">
                                        <i class="color-error fas fa-3x fa-lock"></i><br>    
                                        <span class="color-error text-7">&nbsp;reset</span>
                                    </button>
                                </div>
                            </div>    
                        </div>
                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15">systeem dump</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left pos-32">
                                <div class="float-left margin-3">    
                                    <button class="input-2 but-1 cursor-pointer" id="sysdump_button" name="sysdump_button" type="submit">
                                        <i class="color-menu fas fa-3x fa-download"></i><br>    
                                        <span class="color-menu text-7">&nbsp;dump</span>
                                    </button>
                                </div>
                            </div>    
                        </div>

                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15">Nieuwe P1 monitor versie controle</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class='pad-12'>
                                <input class="cursor-pointer" id="fs_rb_aan_version_check" name="version_check_active" type="radio" value="1" <?php if ( config_read(51) == 1 ) { echo 'checked'; }?>>Aan
                                <input class="cursor-pointer" id="fs_rb_uit_version_check" name="version_check_active" type="radio" value="0" <?php if ( config_read(51) == 0 ) { echo 'checked'; }?>>Uit
                            </div>
                        </div>
                        
                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15">UDP broadcast deamon</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class='pad-12'>
                                <input class="cursor-pointer" id="fs_rb_aan_udp_deamon_check" name="udp_deamon_active" type="radio" value="1" <?php if ( config_read(55) == 1 ) { echo 'checked'; }?>>Aan
                                <input class="cursor-pointer" id="fs_rb_uit_udp_deamon_check" name="udp_deamon_active" type="radio" value="0" <?php if ( config_read(55) == 0 ) { echo 'checked'; }?>>Uit
                            </div>
                        </div>

                    <!-- end pay load area -->    
                    <!-- placeholder variables for session termination -->
                    <input type="hidden" name="logout" id="logout" value="">
                    <input type="hidden" name="systemaction" id="systemaction" value="">
                    <input type="hidden" name="passwordaction" id="passwordaction" value="">
                    </form>
                    </div>
                        <div id="right-wrapper-config-right-2">
                            <div class="frame-4-top">
                                <span class="text-15">hulp</span>
                            </div>
                            <div class="frame-4-bot text-10">
                                <?php echo strIdx(5);?>
                                <p></p>
                                <?php echo strIdx(33);?>
                                <p></p>
                                <?php echo strIdx(34);?>
                            </div>
                        </div>
            </div>    
            <!-- end inner block right part of screen -->
    </div>
    <?php //echo div_err_succes();?>
<div id="cancel_bar">
    <span id="cancel_bar_text">Onderbreek systeem stop&nbsp;&nbsp;</span><i class="fas fa-times-circle"></i>
    <br>
    <div id="progressbar" class="progressbar-2"></div>
    
</div>

<div id="system_dump">
    <div class='close_button' id="dump_msg_close">
        <i class="color-select fas fa-times-circle fa-2x" aria-hidden="true"></i>
    </div>
    <br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Dump van het systeem<br>Wacht tot de download start.<br><br>
    <i id="dump_spinner" class="fas fa-spinner fa-pulse fa-2x"></i><br>
    <br>
    <div class="content-wrapper">Bytes verwerkt: </div><div class="content-wrapper" id="dump_file_size">0</div>
    <br>
    <div id="dump_dl_link" ><br><a id='dump_dl_href' href="">Als de download niet start klik dan hier</a></div>
</div>

<script>    
  
$(function() {
    hideStuff('dump_dl_link')
    centerPosition('#cancel_bar');
    centerPosition('#system_dump');
    if ( sysdump_id > 0 ) {
        systemDump(sysdump_id);
    }    
});

var sysdump_id = 0;
var progressPct = 0;
var action = '';
var progress = 0;
var systemDumpTimer = 0;

$('#dump_msg_close').click(function() {    
   hideStuff('system_dump');
   sysdump_id = 0;
}); 

function systemDump() {
    showStuff('system_dump');
    systemDumpTimer = setInterval('readJsonDataSystemDump()', 300);
}

function autoDownLoad(filename){
    console.log(filename);
    var x=new XMLHttpRequest();
    var dl_filename = filename.split('/').pop();
    x.open("GET", filename, true);
    x.responseType = 'blob';
    x.onload=function(e){download(x.response, dl_filename, "application/zip" ); }
    x.send();
} 

function readJsonDataSystemDump(){ 
    //console.log('readJsonDataSystemDump id = '+sysdump_id); 
    $.getScript( "/systemdump.php?dumpid="+sysdump_id, function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        if ( jsondata[0]['status_code'] === 'gereed' ) {
            clearInterval(systemDumpTimer);
            
            var dl_link = './download/full-p1monitor-dump'+sysdump_id+'.gz';
            $('#dump_dl_href').attr("href", dl_link);
            
            $('#dump_spinner').removeClass("fa-pulse");
            $('#dump_spinner').removeClass("fa-spinner");
            $('#dump_spinner').addClass("fa-check-square");
            showStuff('dump_dl_link');

            autoDownLoad(dl_link);
            return;
        } 
        $('#dump_file_size').html( jsondata[0]['file_size'] );
           
      } catch(err) { }
      
   });
}

function progressIndicator() {
    if (progressPct >= 100) {
        
        if ( action === 'clear_password' ) {
             console.log("clear_password");
             document.formvalues.systemaction.value = 'clear_password';
             $('#formvalues').submit();
        }
        
        if ( action === 'reboot' ) {
             console.log("reboot");
             document.formvalues.systemaction.value = 'reboot';
             $('#formvalues').submit();
        }
        if ( action === 'stop' ) {
              console.log('stop');
               document.formvalues.systemaction.value = 'stop';
                $('#formvalues').submit();
        }
         action = '';
         return;
    }
    progressPct=progressPct+0.1;
    $('#progressbar').width( progressPct+'%' );    
}

function setUpCancelBar(text) {
    progressPct = 0;
    $('#cancel_bar_text').html( text+"&nbsp;&nbsp;" );
    showStuff('cancel_bar');
    clearInterval(progress);
    progress = setInterval(function(){ progressIndicator();},20);
}

$('#sysdump_button').click(function(event) {
    document.formvalues.systemaction.value = 'system_dump';
    $('#formvalues').submit();
    event.preventDefault();    
});


$('#pwreset_button').click(function(event) {
    action = "clear_password";
    setUpCancelBar("Onderbreek wissen van wachtwoord");
    event.preventDefault();    
});

$('#fr_button').click(function(event) {
    action = "reboot";
    setUpCancelBar("Onderbreek systeem herstart");
    event.preventDefault();    
});

$('#fs_button').click(function(event) {
    action = "stop";
    setUpCancelBar("Onderbreek systeem stop");
    event.preventDefault();    
});

$('#cancel_bar').click(function() {    
    hideStuff('cancel_bar');
    progressPct = 0;
    clearInterval(progress);    
});
    
</script>
<?php echo autoLogout(); ?>
<?php
# moet hier staan wegens de brug naar javascript.
if ( isset($_POST['systemaction']) ) { 
    if ( $_POST['systemaction'] === 'system_dump'){ 
        $sysdump_id = strval(mt_rand (100,999));
        $sysdump_filename = 'debugdump'.$sysdump_id;
        writeSemaphoreFile($sysdump_filename);
        echo "<script>
            var sysdump_id = $sysdump_id;
        </script>";
    }
}
?>
</body>
</html>
