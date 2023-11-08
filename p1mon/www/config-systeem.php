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

?>
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<?php

#print_r( $_POST );
$err_cnt = 0;

$sw_off  = strIdx( 193 );
$sw_on   = strIdx( 192 );

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
        if ( updateConfigDb("update config set parameter = '1' where ID = 189"))$err_cnt += 1;
        header('Location:bye.php');
    }

    if ( $_POST['systemaction'] === 'stop'){ 
        //print "Stop !<br>";
        if ( updateConfigDb("update config set parameter = '1' where ID = 190"))$err_cnt += 1;
        header('Location:bye-halt.php');
    }
    
    if ( $_POST['systemaction'] === 'clear_password'){ 
        deletePasswordFiles();
        header('Location:/home.php');
    }

}

if ( isset($_POST["patchfilepath"]) ) {

    //echo ( "patchfilepath = ".$_POST["patchfilepath"] );

    if ($_POST["patchfilepath"] != '' ) {

        #remove old status file 
        unlink('/p1mon/mnt/ramdisk/patch.status');

        // set the upload path and file of the patchfile
        if( updateConfigDb("update config set parameter = '" . $_POST["patchfilepath"] . "' where ID = 193"))$err_cnt += 1;
        if ( isset($_POST["patch_run_mode"]) ) { 
            if( updateConfigDb("update config set parameter = '" . $_POST["patch_run_mode"] . "' where ID = 194"))$err_cnt += 1;
        }
        # shows the dialog
        setcookie("patch_messages_show", "on", time() + 300); //5 min
    }
}


// check if the watchdog has set an new version available when status idx 66 is not empty there is a new version
if  ( strlen( readStatusDb(66)) > 0 ) {
    $newSoftwareVersionP1monitor = ucfirst(strIdx( 375 )) . ' ' . readStatusDb(66); 
    $download_url = readStatusDb(86);
    $newVersionLink = '<a class="text-10" target="_blank" href="'. $download_url .'"><i class="menu-active-control fas fa-globe"></i>&nbsp;download</a>';
}

?>
<head>
<meta name="robots" content="noindex">
<title><?php echo ucfirst(strIdx( 374 ))?></title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css">
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css">

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/p1mon-util.js"></script>
<script src="./js/download2.js"></script>
<script src="/fine-uploader/fine-uploader.min.js"></script>

<script type="text/template" id="qq-template">
    <div class="qq-uploader-selector qq-uploader">
        <div class="qq-upload-button-selector qq-upload-button">
            <div>
                <button class="input-2 but-3 float-left" id="patchbutton">
                    <i class="color-menu fas fa-3x  fa-bandage"></i><br>
                    <span class="color-menu text-7">patch</span>
                </button>
            </div>
        </div>
        <ul class="qq-upload-list-selector" style="display: none">
            <div></div>
        </ul>
    </div>
</script>
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
                            <span class="text-15"><?php echo ucfirst(strIdx( 376 ))?></span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left text-10">
                                <div><?php echo ucfirst(strIdx( 371 ))?>:&nbsp;<?php echo config_read(0); ?></div>
                                <div><?php echo ucfirst(strIdx( 372 ))?>:&nbsp;<?php echo config_read(128); ?></div>
                                <div><?php echo ucfirst(strIdx( 369 ))?>:&nbsp;<?php echo config_read(133); ?></div>
                                <div><?php echo ucfirst(strIdx( 373 ))?>:&nbsp;<span id="newp1mon"><?php echo strIdx( 377 )?>.</span></div>
                                <div id="p1newdownload" class="display_none"><?php echo $newVersionLink ?></div>
                            </div> 
                        </div> 
                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15"><?php echo ucfirst(strIdx( 378 ))?></span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left">
                                <div class="float-left margin-3">
                                    <button class="input-2 but-3 cursor-pointer" id="fr_button" name="fr_button" type="submit">
                                        <i class="color-warning fa-3x fas fa-sync-alt"></i><br> 
                                        <span class="color-warning text-7"><?php echo strIdx( 379 )?></span>
                                    </button>
                                    <div class="pad-1 content-wrapper">
                                    <button class="input-2 but-3 cursor-pointer" id="fs_button" name="fs_button" type="submit">
                                        <i class="color-error fa-3x fas fa-power-off"></i><br>
                                        <span class="color-error text-7">&nbsp;<?php echo strIdx( 380 )?></span>
                                    </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <p></p>

                        <div class="frame-4-top">
                            <span class="text-15"><?php echo ucfirst(strIdx( 381 ))?></span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left">
                                <div class="float-left margin-3">
                                    <button class="input-2 but-3 cursor-pointer" id="pwreset_button" name="pwreset_button" type="submit">
                                        <i class="color-error fas fa-3x fa-lock"></i><br>
                                        <span class="color-error text-7"><?php echo ucfirst(strIdx( 382 ))?></span>
                                    </button>
                                </div>
                            </div>    
                        </div>
                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15"><?php echo ucfirst(strIdx( 383 ))?></span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="float-left">
                                <div class="float-left margin-3">
                                    <button class="input-2 but-3 cursor-pointer" id="sysdump_button" name="sysdump_button" type="submit">
                                        <i class="color-menu fas fa-3x fa-download"></i><br> 
                                        <span class="color-menu text-7">&nbsp;<?php echo strIdx( 384 )?></span>
                                    </button>
                                </div>
                            </div>
                        </div>

                        <p></p>
                        <div class="frame-4-top" title="<?php echo strIdx( 316 );?>">
                            <span class="text-15"><?php echo strIdx( 385 )?></span>
                        </div>
                        <div class="frame-4-bot" title="<?php echo strIdx( 316 );?>">
                            <div class="float-left margin-3" id="uploader"></div>
                            <div class="pad-1" title="<?php echo strIdx( 315 );?>">
                                <input type="checkbox" id="cb_unsigned_allow" name="cb_unsigned_allow">
                                <label class="text-10" for="cb_unsigned_allow"><?php echo strIdx( 386 )?></label>
                            </div>
                        </div>
                        <p></p>

                        <div class="frame-4-top">
                            <span class="text-15"><?php echo ucfirst(strIdx( 387 ))?></span>
                        </div>
                        <div class="frame-4-bot">
                            <div class='pad-12'>
                                <input class="cursor-pointer" id="fs_rb_aan_version_check" name="version_check_active" type="radio" value="1" <?php if ( config_read(51) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                <input class="cursor-pointer" id="fs_rb_uit_version_check" name="version_check_active" type="radio" value="0" <?php if ( config_read(51) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                            </div>
                        </div>
                        
                        <p></p>
                        <div class="frame-4-top">
                            <span class="text-15"><?php echo ucfirst(strIdx( 388 ))?></span>
                        </div>
                        <div class="frame-4-bot">
                            <div class='pad-12'>
                                <input class="cursor-pointer" id="fs_rb_aan_udp_deamon_check" name="udp_deamon_active" type="radio" value="1" <?php if ( config_read(55) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                <input class="cursor-pointer" id="fs_rb_uit_udp_deamon_check" name="udp_deamon_active" type="radio" value="0" <?php if ( config_read(55) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                            </div>
                        </div>

                    <!-- end pay load area -->    
                    <!-- placeholder variables for session termination -->
                    <input type="hidden" name="logout"         id="logout"         value="">
                    <input type="hidden" name="systemaction"   id="systemaction"   value="">
                    <input type="hidden" name="passwordaction" id="passwordaction" value="">
                    <input type="hidden" name="patchfilepath"  id="patchfilepath"  value="">
                    <input type="hidden" name="patch_run_mode" id="patch_run_mode" value="">
                    </form>
                    </div>
                        <div id="right-wrapper-config-right-2">
                            <div class="frame-4-top">
                                <span class="text-15"><?php echo ucfirst(strIdx( 389 ))?></span>
                            </div>
                            <div class="frame-4-bot text-10">
                                <?php echo strIdx( 5 );?>
                                <p></p>
                                <?php echo strIdx( 33 );?>
                                <p></p>
                                <?php echo strIdx( 34 );?>
                                <p></p>
                                <?php echo strIdx( 317 );?>
                            </div>
                        </div>
            </div>    
            <!-- end inner block right part of screen -->
    </div>
    <?php //echo div_err_succes();?>
<div id="cancel_bar">
    <span id="cancel_bar_text"><?php echo ucfirst(strIdx( 390 ))?>&nbsp;&nbsp;</span><i class="fas fa-times-circle"></i>
    <br>
    <div id="progressbar" class="progressbar-2"></div>
</div>

<div id="system_dump">
    <div class='close_button' id="dump_msg_close">
        <i class="color-select fas fa-times-circle fa-2x" aria-hidden="true"></i>
    </div>
    <br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<?php echo ucfirst(strIdx( 391 ))?><br><?php echo ucfirst(strIdx( 392 ))?>.<br><br>
    <i id="dump_spinner" class="fas fa-spinner fa-pulse fa-2x"></i><br>
    <br>
    <div class="content-wrapper"><?php echo ucfirst(strIdx( 393 ))?>: </div><div class="content-wrapper" id="dump_file_size">0</div>
    <br>
    <div id="dump_dl_link" ><br><a id='dump_dl_href' href=""><?php echo ucfirst(strIdx( 293 ))?></a></div>
</div>

<div id="patch_status_message">
     <div class='close_button' id="patch_status_message_close">
        <i class="color-select fas fa-times-circle fa-2x" aria-hidden="true"></i>
    </div>
    <span class="text-15"><?php echo strIdx( 394 )?></span>
    <div id="scroll_window" class="text-29" >
        <?php echo strIdx( 295 );?>
    </div>
</div> 

<script> 



function readJsonApiConfigurationToStop( id ){

    $.getScript( "./api/v1/configuration/"+id, function( data, textStatus, jqxhr ) {
      try {
        var jsonarr = JSON.parse(data);
        if ( jsonarr[0][1] == 0 ) {
            clearInterval( patchLogTimer );
        } 
      } catch(err) {
          console.log( err );
      }
   });
   

}

function readPatchStatusLogging(){ 
    $.get( "/txt/txt-patch-status.php", function( response, status, xhr ) {
        
        if ( status == "error" ) {
            $("#scroll_window").html("<?php echo strIdx( 395 );?>.");
        }
        
        if ( response.length > 0 ) {
            
            $('#scroll_window').html( response );

            // keep scroll window scrolled down.
             $('#scroll_window').scrollTop($('#scroll_window')[0].scrollHeight);
        } else {
            $('#scroll_window').html( "<b><?php echo strIdx( 396 );?>.</b><br>" );
        }

    });
}

function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}


$('#patch_status_message_close').click(function() {
   hideStuff('patch_status_message');
   PatchMessagesShow = undefined;
   document.cookie = "patch_messages_show=''; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}); 

PatchMessagesShow=getCookie("patch_messages_show"); 


$(function() {
    hideStuff('dump_dl_link')
    centerPosition('#cancel_bar');
    centerPosition('#system_dump');
    centerPosition('#patch_status_message');
    if ( sysdump_id > 0 ) {
        systemDump(sysdump_id);
    }

   //if ( PatchMessagesShow !== undefined ) {
    if ( PatchMessagesShow === "on" ) {
        showStuff('patch_status_message');
        patchLogTimer = setInterval('updatePatchLogging();', 1000);
    }

    var jsNewSoftwareVersion = "<?php echo $newSoftwareVersionP1monitor?>"
    if ( jsNewSoftwareVersion.length > 0 ) {
        newP1SoftwareVersion = jsNewSoftwareVersion;
        showStuff('p1newdownload');
    }
    $('#newp1mon').text( newP1SoftwareVersion )
    
});


function updatePatchLogging(){
    readPatchStatusLogging();
    readJsonApiConfigurationToStop('193');
}

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
    var x=new XMLHttpRequest();
    var dl_filename = filename.split('/').pop();
    x.open("GET", filename, true);
    x.responseType = 'blob';
    x.onload=function(e){download(x.response, dl_filename, "application/zip" ); }
    x.send();
} 

function readJsonDataSystemDump(){ 
    $.getScript( "/systemdump.php?dumpid="+sysdump_id, function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        if ( jsondata[0]['status_code'] === 'gereed' ) {
            clearInterval(systemDumpTimer);
            
            var dl_link = './download/full-p1monitor-dump'+sysdump_id+'.gz';
            $('#dump_dl_href').attr("href", dl_link);
            
            $('#dump_spinner').removeClass("fa-pulse");
            $('#dump_spinner').removeClass("fa-spinner");
            $('#dump_spinner').addClass("fa-square-check");
            showStuff('dump_dl_link');

            autoDownLoad(dl_link);
            return;
        } 
        $('#dump_file_size').html( jsondata[0]['file_size'] );
           
      } catch(err) { }
      
   });
}

function progressIndicator() {
    if (progressPct > 95) {
        
        if ( action === 'clear_password' ) {
             document.formvalues.systemaction.value = 'clear_password';
             $('#formvalues').submit();
        }
        
        if ( action === 'reboot' ) {
             document.formvalues.systemaction.value = 'reboot';
             $('#formvalues').submit();
        }
        if ( action === 'stop' ) {
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
    setUpCancelBar("<?php echo ucfirst(strIdx( 397 ));?>");
    event.preventDefault();
});

$('#fr_button').click(function(event) {
    action = "reboot";
    setUpCancelBar("<?php echo ucfirst(strIdx( 398 ));?>");
    event.preventDefault();
});

$('#fs_button').click(function(event) {
    action = "stop";
    setUpCancelBar("<?php echo ucfirst(strIdx( 399 ));?>");
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
        if ( updateConfigDb("update config set parameter = '1' where ID = 191") ) $err_cnt += 1;
        if ( updateConfigDb("update config set parameter = '".$sysdump_id."' where ID = 192") ) $err_cnt += 1;
        echo "<script>
            var sysdump_id = $sysdump_id;
        </script>";
    }
}
?>

<script>
    var uploader = new qq.FineUploader({
        element: document.getElementById("uploader"),
        debug: false,
        request: {
            endpoint: "/fine-uploader/endpoint.php"
        },
        deleteFile: {
            enabled: false,
            endpoint: "/fine-uploader/endpoint.php"
        },
        chunking: {
            enabled: true,
            concurrent: {
                enabled: true
            },
            success: {
                endpoint: "/fine-uploader/endpoint.php?done"
            }
        },
        resume: {
            enabled: true
        },
        retry: {
            enableAuto: true,
            showButton: true
        },
        callbacks: {
            onComplete: function(id, fileName, responseJSON) {
                if (responseJSON.success) {
                    document.formvalues.patchfilepath.value = '/p1mon/var/tmp/'+this.getUuid (id)+'/'+fileName
                    document.formvalues.patch_run_mode.value = 1; // allow signed only patch file
                    if ( document.formvalues.cb_unsigned_allow.checked == true ) {
                        document.formvalues.patch_run_mode.value = 2; // allow unsigned and signed patch file
                    }
                    document.forms["formvalues"].submit();
                    }
                }
            },
        validation: {
            allowedExtensions: ['signed.zip','unsigned.zip'],
        },
    });
</script>
</body>
</html>