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

if ( isset($_POST["i_email_account"]) ) { 
        $input = inputClean(trim($_POST["i_email_account"]));
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ( updateConfigDb("update config set parameter = '".$input."' where ID = 63")) $err_cnt += 1;
}

if ( isset($_POST["i_email_pword"]) ) { 
        $input = trim($_POST["i_email_pword"]);
        $password = encodeString ($input, 'mailpw');
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ( updateConfigDb("update config set parameter = '".$password."' where ID = 64")) $err_cnt += 1;
}

if ( isset($_POST["i_mail_server"]) ) { 
        $input = inputClean(trim($_POST["i_mail_server"]));
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ( updateConfigDb("update config set parameter = '".$input."' where ID = 65")) $err_cnt += 1;
}

if ( isset($_POST["i_email_ssl_port"]) ) { 
        $input = inputCleanDigitsOnly(trim($_POST["i_email_ssl_port"]));
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ( updateConfigDb("update config set parameter = '".$input."' where ID = 66")) $err_cnt += 1;
}

if ( isset($_POST["i_email_starttls_port"]) ) { 
        $input = inputCleanDigitsOnly(trim($_POST["i_email_starttls_port"]));
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ( updateConfigDb("update config set parameter = '".$input."' where ID = 67")) $err_cnt += 1;
}

if ( isset($_POST["i_email_normal_port"]) ) { 
        $input = inputCleanDigitsOnly(trim($_POST["i_email_normal_port"]));
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ( updateConfigDb("update config set parameter = '".$input."' where ID = 68")) $err_cnt += 1;
}

if ( isset($_POST["i_email_subject"]) ) { 
        $input = inputClean(trim($_POST["i_email_subject"]));
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ( updateConfigDb("update config set parameter = '".$input."' where ID = 69")) $err_cnt += 1;
}

if ( isset($_POST["i_email_to"]) ) { 
        $input = inputClean(trim($_POST["i_email_to"]));
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ( updateConfigDb("update config set parameter = '".$input."' where ID = 70")) $err_cnt += 1;
}

if ( isset($_POST["i_email_cc"]) ) { 
        $input = inputClean(trim($_POST["i_email_cc"]));
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ( updateConfigDb("update config set parameter = '".$input."' where ID = 74")) $err_cnt += 1;
}

if ( isset($_POST["i_email_bcc"]) ) { 
        $input = inputClean(trim($_POST["i_email_bcc"]));
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ( updateConfigDb("update config set parameter = '".$input."' where ID = 75")) $err_cnt += 1;
}

if ( isset($_POST["i_email_from"]) ) { 
        $input = inputClean(trim($_POST["i_email_from"]));
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ( updateConfigDb("update config set parameter = '".$input."' where ID = 71")) $err_cnt += 1;
}

if ( isset($_POST["i_email_timeout"]) ) { 
        $input = inputCleanDigitsOnly(trim($_POST["i_email_timeout"]));
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ( updateConfigDb("update config set parameter = '".$input."' where ID = 72")) $err_cnt += 1;
}

if ( isset($_POST["fs_rb_aan_p1_data"]) ) { 
        if ( $err_cnt == -1 ) $err_cnt=0;
        if ($_POST["fs_rb_aan_p1_data"] == '1' ) {
                if ( updateConfigDb("update config set parameter = '1' where ID = 73"))$err_cnt += 1;
        } else {
                if ( updateConfigDb("update config set parameter = '0' where ID = 73"))$err_cnt += 1;
        }
}

if ( isset( $_POST["email_test_button"] ) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    writeSemaphoreFile( 'email_test' );
}


?>
<!doctype html>
<html lang='NL'>
<head>
<meta name="robots" content="noindex">
<title>Notificatie configuratie</title>
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

function selectorUpdate(selected, toupdate) {
        //console.log(selected)
        var v = $(selected+" option:selected" ).val()
        $(toupdate).val(v);
        $("#formvalues").validate().element(toupdate);
}

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
                                <?php menu_control(12);?>
                        </div>
                        
                        <div id="right-wrapper-config"> <!-- right block -->
                        <!-- inner block right part of screen -->
                                <div id="right-wrapper-config-left">
                                        <!-- start of content -->
                                        <form name="formvalues" id="formvalues" method="POST">
                                                
                                                <div class="frame-4-top">
                                                        <span class="text-15">email gegevens</span>
                                                </div>
                                                <div class="frame-4-bot">
                                                        <div class="float-left pad-17">
                                                        
                                                        <div class="content-wrapper pos-36" title="<?php echo strIdx(50);?>"> 
                                                                <div class="pad-24 content-wrapper">
                                                                        <label class="text-14">account</label> 
                                                                </div>
                                                                <div class="content-wrapper">
                                                                        <input class="input-11 color-settings color-input-back" id="i_email_account" name="i_email_account" type="text" value="<?php echo config_read(63);?>">
                                                                </div>
                                                        </div> 
                                                
                                                        <div class="content-wrapper pos-36" title="<?php echo strIdx(51);?>"> 
                                                                <div class="pad-24 content-wrapper">
                                                                        <label class="text-14">wachtwoord</label> 
                                                                </div>
                                                                <div class="content-wrapper">
                                                                        <input class="input-11 color-settings color-input-back" id="i_email_pword" name="i_email_pword" type="password" value="<?php echo decodeString(64, 'mailpw');?>">
                                                                </div>
                                                                <div class="content-wrapper pad-1 cursor-pointer" id="api_passwd" onclick="toggelPasswordVisibility('i_email_pword')" >        
                                                                        <span><i class="color-menu pad-7 fas fa-eye"></i></span>
                                                                </div>
                                                        </div> 
                                                
                                                        <div class="content-wrapper pos-36" title="<?php echo strIdx(52);?>"> 
                                                                <div class="pad-24 content-wrapper">
                                                                        <label class="text-14">mailserver adres</label> 
                                                                </div>
                                                                <div class="content-wrapper">
                                                                        <input class="input-11 color-settings color-input-back" id="i_mail_server" name="i_mail_server" type="text" value="<?php echo config_read(65);?>">
                                                                </div>
                                                        </div> 
                                                        
                                                        <div class="content-wrapper pos-36" title="<?php echo strIdx(53);?>"> 
                                                                <div class="pad-24 content-wrapper">
                                                                        <label class="text-14">TCP poort SSL/TLS</label> 
                                                                </div>
                                                                <div class="content-wrapper">
                                                                        <input class="input-11 color-settings color-input-back" id="i_email_ssl_port" name="i_email_ssl_port" type="text" value="<?php echo config_read(66);?>">
                                                                </div>
                                                        </div> 
                                                        
                                                        <div class="content-wrapper pos-36" title="<?php echo strIdx(54);?>"> 
                                                                <div class="pad-24 content-wrapper">
                                                                        <label class="text-14">TCP poort STARTTLS</label> 
                                                                </div>
                                                                <div class="content-wrapper">
                                                                        <input class="input-11 color-settings color-input-back" id="i_email_starttls_port" name="i_email_starttls_port" type="text" value="<?php echo config_read(67);?>">
                                                                </div>
                                                        </div> 
                                                        
                                                        <div class="content-wrapper pos-36" title="<?php echo strIdx(55);?>"> 
                                                                <div class="pad-24 content-wrapper">
                                                                        <label class="text-14">TCP poort standaard</label> 
                                                                </div>
                                                                <div class="content-wrapper">
                                                                        <input class="input-11 color-settings color-input-back" id="i_email_normal_port" name="i_email_normal_port" type="text" value="<?php echo config_read(68);?>">
                                                                </div>
                                                        </div> 
                            
                            <div class="content-wrapper pos-36" title="<?php echo strIdx(56);?>"> 
                                                                <div class="pad-24 content-wrapper">
                                                                        <label class="text-14">onderwerp</label> 
                                                                </div>
                                                                <div class="content-wrapper">
                                                                        <input class="input-11 color-settings color-input-back" id="i_email_subject" name="i_email_subject" type="text" value="<?php echo config_read(69);?>">
                                                                </div>
                                                        </div> 
                            
                            <div class="content-wrapper pos-36" title="<?php echo strIdx(57);?>"> 
                                                                <div class="pad-24 content-wrapper">
                                                                        <label class="text-14">ontvangers (to)</label> 
                                                                </div>
                                                                <div class="content-wrapper">
                                                                        <input class="input-11 color-settings color-input-back" id="i_email_to" name="i_email_to" type="text" value="<?php echo config_read(70);?>">
                                                                </div>
                                                        </div> 

                            <div class="content-wrapper pos-36" title="<?php echo strIdx(58);?>"> 
                                                                <div class="pad-24 content-wrapper">
                                                                        <label class="text-14">ontvangers (cc)</label> 
                                                                </div>
                                                                <div class="content-wrapper">
                                                                        <input class="input-11 color-settings color-input-back" id="i_email_cc" name="i_email_cc" type="text" value="<?php echo config_read(74);?>">
                                                                </div>
                                                        </div> 

                            <div class="content-wrapper pos-36" title="<?php echo strIdx(59);?>"> 
                                                                <div class="pad-24 content-wrapper">
                                                                        <label class="text-14">ontvangers (bcc)</label> 
                                                                </div>
                                                                <div class="content-wrapper">
                                                                        <input class="input-11 color-settings color-input-back" id="i_email_bcc" name="i_email_bcc" type="text" value="<?php echo config_read(75);?>">
                                                                </div>
                                                        </div> 

                            <div class="content-wrapper pos-36" title="<?php echo strIdx(60);?>"> 
                                                                <div class="pad-24 content-wrapper">
                                                                        <label class="text-14">FROM alias</label> 
                                                                </div>
                                                                <div class="content-wrapper">
                                                                        <input class="input-11 color-settings color-input-back" id="i_email_from" name="i_email_from" type="text" value="<?php echo config_read(71);?>">
                                                                </div>
                                                        </div> 

                            <div class="content-wrapper pos-36" title="<?php echo strIdx(61);?>"> 
                                                                <div class="pad-24 content-wrapper">
                                                                        <label class="text-14">timeout in seconden</label> 
                                                                </div>
                                                                <div class="content-wrapper">
                                                                        <input class="input-11 color-settings color-input-back" id="i_email_timeout" name="i_email_timeout" type="text" value="<?php echo config_read(72);?>">
                                                                </div>
                            </div> 
                            <br>
                            <br>
                            <div class="pad-1 content-wrapper float-left" title="<?php echo strIdx( 74 );?>">
                                                                <button class="input-2 but-1 cursor-pointer" id="email_test_button" name="email_test_button" type="submit">
                                                                        <i class="color-menu fa-3x far fa-play-circle"></i><br>
                                                                        <span class="color-menu text-7">test</span>
                                                                </button>
                                                        </div>


                                                        </div>
                                                        </div>
                            
                            <p></p>
                        
                        <div class="frame-4-top">
                                                        <span class="text-15">P1 poort</span>
                                                </div>
                                                <div class="frame-4-bot">
                                                        <div class='pad-12'>
                            <div> 
                                                                <!-- left side -->
                                                                <div class="float-left" title="<?php echo strIdx(63);?>">
                                                                        <div class="text-10">Notificatie bij het wegvallen van de P1 data.&nbsp;
                                </div>
                                                                </div>
                                <!-- right side -->
                                                                <div class="float-right">
                                                                        <div>
                                                                            <input class="cursor-pointer" id="fs_rb_aan_p1_data_on" name="fs_rb_aan_p1_data" type="radio" value="1" <?php if ( config_read(73) == 1 ) { echo 'checked'; }?>>Aan
                                                                            <input class="cursor-pointer" id="fs_rb_aan_p1_data_off" name="fs_rb_aan_p1_data" type="radio" value="0" <?php if ( config_read(73) == 0 ) { echo 'checked'; }?>>Uit
                                                                        </div>
                                                                        <p></p>
                                                                </div>
                                                        </div>

                                                        </div>
                                                </div>
                        <p></p>



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
                                                <?php echo strIdx(62);?>
                                        </div>
                                </div>
                                
                        </div>
                                        
                <!-- </div> -->
                                
                        
                        <!-- end inner block right part of screen -->
        </div>        
        <?php echo div_err_succes();?>
        
<script>

$(function() {
        $("#formvalues").validate({
                rules: {
                        'i_email_timeout': {
                required: true,
                number: true,
                max: 300,
                min: 1
            },
                        'i_email_ssl_port': {
                required: true,
                number: true,
                max: 65535,
                min: 1
            },
                        'i_email_starttls_port': {
                required: true,
                number: true,
                max: 65535,
                min: 1
            } ,        
            'i_email_normal_port': {
                required: true,
                number: true,
                max: 65535,
                min: 1
            }         
        },
        errorPlacement: function(error, element) {
            return false;  // will suppress error messages    
        }
    }); 
});
</script>
<?php echo autoLogout(); ?>        
</body>
</html>