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

#print_r( $_POST );
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

$err_cnt = -1;
if ( isset($_POST["samba"]) ) { 
    $err_cnt = 0;
    if ( updateConfigDb( "update config set parameter = '".$_POST["samba"]."' where ID = 6")) $err_cnt += 1;
    if ( updateConfigDb( "update config set parameter = '1' where ID = 182")                ) $err_cnt += 1;
}

if ( isset($_POST["dboxauth"]) ) {

    if ( $err_cnt == -1 ) $err_cnt=0;
   
    if ( strlen(trim($_POST["dboxauth"])) > 32 ) { /* normale 44 chars long */
        $clean_dbox_auth = trim( $_POST["dboxauth"] );

        // magic to handle tokens that start with a hypen, thank you Dropbox :)
        if ( substr( $clean_dbox_auth , 0, 1 ) === "-" ) {
            $clean_dbox_auth_changed = substr( $clean_dbox_auth , 1, strlen( $clean_dbox_auth ) );
            $command = '/p1mon/scripts/P1DropBoxAuth --token --addhyphen ' . $clean_dbox_auth_changed;
        } else {
            #$command = '/p1mon/scripts/p1monExec -p ' . ' "/p1mon/scripts/P1DropBoxAuth.py --token  ' . $clean_dbox_auth  . '"';
            $command = "/p1mon/scripts/P1DropBoxAuth --token " . $clean_dbox_auth;
        }

        //echo "command = " . $command . "<br>";
        exec( $command ,$arr_execoutput, $exec_ret_value );
     

        if ( 'ERROR' == $arr_execoutput[0] ) {
            $err_cnt += 1;
            #debugLog(' $err_cnt(1) = '. $err_cnt);
        }

        #print_r( "dropbox token return= ". $arr_execoutput[0]. "<br>" );

        /*
        if ( 'ERROR' != $arr_execoutput[0] ) {
            $crypto_key = encodeString ( $arr_execoutput[0], 'dbxkey' );
            #print ($crypto_key.",<br>");
            # if ( updateConfigDb("update config set parameter = '".$crypto_key."' where ID = 47")) $err_cnt += 1;
        } else {
            $err_cnt += 1;
        }
        */
    }  else {

       if ( strlen(trim($_POST["dboxauth"]))  > 0 ) {
        $err_cnt += 1;
       }
    }

}

if ( isset($_POST["dbx_data_active"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["dbx_data_active"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 50"))$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 50"))$err_cnt += 1;
    }
}

if ( isset($_POST["faseDB_active"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["faseDB_active"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 119"))$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 119"))$err_cnt += 1;
    }
}

if ( isset( $_POST["systemaction"] ) ) { 
    if ( $_POST['systemaction'] === 'db_erase' ) {
        #echo "db erease";
        if ( updateConfigDb("update config set parameter = '1' where ID = 188") )$err_cnt += 1;
    }
}

if ( isset($_POST["calc_values"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["calc_values"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 179") )$err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 179") )$err_cnt += 1;
    }
}

?>
<!doctype html>
<html lang="nl">
<head>
<meta name="robots" content="noindex">
<title>Bestanden configuratie</title>
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

var progress    = 0;
var action      = '';

function readJsonApiConfiguration(){ 
    $.getScript( "./api/v1/status", function( data, textStatus, jqxhr ) {
      try {
        var jsonarr = JSON.parse(data); 
        for (var j=0;  j<jsonarr.length; j++){
                switch(jsonarr[j][0]) {
                    case 59:
                        $('#dbx_timestamp').text( jsonarr[j][1] );
                        break;
                    case 63:
                        $('#dbx_data_timestamp_succes').text( jsonarr[j][1] );
                        break;
                    case 64:
                        $('#dbx_data_status').text( jsonarr[j][1] );
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
    readJsonApiConfiguration()
    initloadtimer = setInterval(function(){LoadData();}, 5000);
}

$(function () {

    // block enter key to prevent accidental editing
    $("form").bind("keypress", function (e) {
    if (e.keyCode == 13) {
        $("#db_erase_button").attr('value');
        return false;
    }
    });

    centerPosition('#cancel_bar');
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
                <?php menu_control(3);?>
            </div>
            
            <div id="right-wrapper-config"> <!-- right block -->
            <!-- inner block right part of screen -->
                <div id="right-wrapper-config-left-2">
                    <!-- start of content -->
                    <form name="formvalues" id="formvalues" method="POST">
                        
                        <div class="frame-4-top">
                            <span class="text-15">lokaal bestanden delen</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class='pad-12'>
                                <input class="cursor-pointer" id="fs_rb_hidden" name="samba" type="radio" value="uit" <?php readFileShareStatus('uit'); ?>>Uit
                                <input class="cursor-pointer" id="fs_rb_data"   name="samba" type="radio" value="data"<?php readFileShareStatus('data');?>>Database
                                <input class="cursor-pointer" id="fs_rb_dev"    name="samba" type="radio" value="dev" <?php readFileShareStatus('dev'); ?>>Ontwikkeling
                            </div>
                        </div>
                        <p></p>
                       
                        <div class="frame-4-top">
                            <span class="text-15">Database wissen</span><span><i class="color-warning fas fa-exclamation-triangle fa-1x" data-fa-transform="up-1 right-15"></i></span> 
                        </div>
                        <div class="frame-4-bot">
                            
                        <div class="float-left margin-3">    
                            <button class="input-2 but-1 cursor-pointer" id="db_erase_button" name="db_erase_button" type="submit">
                                <i class="color-menu fas fa-3x fa-trash-alt"></i><br>    
                                <span class="color-menu text-7">&nbsp;wissen</span>
                            </button>
                        </div>

                        </div>
                        <p></p>

                        <div class="frame-4-top">
                            <span class="text-15">DropBox API configuratie</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left">
                                <label class="text-10">1: DropBox authenticatie code opvragen.</label>
                                <a href="./dropbox-redirect.php" target="_blank"><span><i class="color-menu fab fa-dropbox fa-2x" data-fa-transform="down-5 right-5"></i></span></a>
                            </div>
                            
                            <div class="float-left pad-14">
                                <label class="text-10">2: Knip en plak de code van Dropbox hier en sla deze op.</label><input class="input-9 color-settings color-input-back" id="dboxauth"  name="dboxauth" type="text">
                            </div>
                            
                            <div class="float-left pad-22">
                                <label class="text-10">Laatste succesvolle authenticatie: </label><label id='dbx_timestamp' class="text-10">yyyy-mm-dd hh:mm:ss</label>
                            </div>
                        </div>

                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15">Dropbox gegevens delen</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class='pad-12'>
                                <input class="cursor-pointer" id="fs_rb_aan_dbx" name="dbx_data_active" type="radio" value="1" <?php if ( config_read(50) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                <input class="cursor-pointer" id="fs_rb_uit_dbx" name="dbx_data_active" type="radio" value="0" <?php if ( config_read(50) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                            </div>

                            <p class="p-1"></p>
                            <div class="content-wrapper pos-36" title="<?php echo strIdx(31);?>"> 
                                <div class="pad-23 content-wrapper">
                                    <label class="text-10">Succesvol op:</label> 
                                </div>
                                <div class="content-wrapper">
                                    <label id="dbx_data_timestamp_succes" class="text-10"></label>
                                </div>
                            </div> 
                            <p class="p-1"></p>
                            
                            <div class="content-wrapper pos-36" title="<?php echo strIdx(32);?>"> 
                                <div class="pad-23 content-wrapper">
                                    <label class="text-10">Data status:</label> 
                                </div>
                            </div> 

                            <div class="content-wrapper">
                                    <label id="dbx_data_status" class="text-10"></label>
                            </div>

                        </div>
                        

                        <p></p>
                        <div class="frame-4-top" title="<?php echo strIdx( 82 );?>">
                            <span class="text-15">Historische fase informatie opslaan in de database</span>
                        </div>
                        <div class="frame-4-bot" title="<?php echo strIdx( 82 );?>" >
                            <div class='pad-12'>
                                <input class="cursor-pointer" id="fs_rb_aan_faseDB" name="faseDB_active" type="radio" value="1" <?php if ( config_read( 119 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                <input class="cursor-pointer" id="fs_rb_uit_faseDB" name="faseDB_active" type="radio" value="0" <?php if ( config_read( 119 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                            </div>
                        </div>

                        <p></p>
                        <div class="frame-4-top" title="<?php echo strIdx( 311 );?>">
                            <span class="text-15"><?php echo strIdx( 310 );?></span>
                        </div>
                        <div class="frame-4-bot" title="<?php echo strIdx( 311 );?>" >
                            <div class='pad-12'>
                                <div title="<?php echo strIdx(314);?>">
                                    <input class="cursor-pointer" name="calc_values" type="radio" value="1" <?php if ( config_read( 179 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                    <input class="cursor-pointer" name="calc_values" type="radio" value="0" <?php if ( config_read( 179 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                </div>
                            </div>
                        </div>

                        <!-- placeholder variables for session termination -->
                        <input type="hidden" name="logout" id="logout" value="">
                        <input type="hidden" name="systemaction" id="systemaction" value="">
                    </form>
                </div>
                
                <div id="right-wrapper-config-right-2">
                    <div class="frame-4-top">
                        <span class="text-15">hulp</span>
                    </div>
                    <div class="frame-4-bot text-10">
                        <?php echo strIdx(6);?>
                        <p></p>
                        <?php echo strIdx(71);?>
                        <p></p>
                        <?php echo strIdx(30);?>
                        <p></p>
                        <?php echo strIdx( 82 );?>
                        <p></p>
                        <?php echo strIdx( 311 );?>
                    </div>
                </div>
            </div>    
            <!-- end inner block right part of screen -->
    </div>
    <?php echo div_err_succes();?>


<div id="cancel_bar">
        <span id="cancel_bar_text"></span><i class="fas fa-times-circle"></i>
            <br>
            <div id="progressbar" class="progressbar-2"></div>
</div>
<script>

function setUpCancelBar(text) {
    progressPct = 0;
    $('#cancel_bar_text').html( text+"&nbsp;&nbsp;" );
    showStuff('cancel_bar');
    clearInterval( progress );
    progress = setInterval (function(){ progressIndicator();},20 );
}



$('#db_erase_button').click( function(event) {
    //console.log( event.type )
    //console.log ('db_erase')
    action = 'db_erase';
    setUpCancelBar("Onderbreek database wissen&nbsp;&nbsp;");
    event.preventDefault();
});


function progressIndicator() {
    console.log( progressPct )
    if ( progressPct >95 ) {
        if ( action === 'db_erase' ) {
            //console.log("db_erase do");
            document.formvalues.systemaction.value = 'db_erase';
            $('#formvalues').submit();
        }
        action = '';
        return;
    }
    progressPct=progressPct+0.1;
    $('#progressbar').width( progressPct +'%' );
}


$('#cancel_bar').click(function() {    
    hideStuff('cancel_bar');
    progressPct = 0;
    clearInterval(progress);    
});

</script>

</body>
</html>