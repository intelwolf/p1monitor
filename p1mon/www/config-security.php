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

$sw_off = strIdx( 193 );
$sw_on = strIdx( 192 );

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
if ( isset($_POST["inet_allowed"]) ) { 
    $err_cnt = 0;
    if ($_POST["inet_allowed"] == '1' ) {
            #echo "on<br>";
            if ( updateConfigDb("update config set parameter = '1' where ID = 60"))$err_cnt += 1;
    } else {
            #echo "off<br>";
            if ( updateConfigDb("update config set parameter = '0' where ID = 60"))$err_cnt += 1;
    }
}

?>
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title><?php echo ucfirst(strIdx( 653 ))?></title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css">
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css">

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/p1mon-util.js"></script>
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
            <?php menu_control(11);?>
        </div>

        <div id="right-wrapper-config"> <!-- right block -->
            <!-- inner block right part of screen -->
            <div id="right-wrapper-config-left-2">
            <!-- start of content -->
                <form name="formvalues" id="formvalues" method="POST">

                    <div class="frame-4-top">
                        <span class="text-15"><?php echo strIdx( 654 )?></span>
                    </div>
                    <div class="frame-4-bot">
                        <div class='pad-12'>
                            <div class='text-14'><?php echo decodeStringNoBase64(58,"sysid")?> </div>
                        </div>
                    </div>
                    <p></p>

                    <div class="frame-4-top">
                        <span class="text-15"><?php echo strIdx( 655 )?></span>
                    </div>
                    <div class="frame-4-bot">
                        <div class='pad-12'>
                            <div> 
                            <!-- left side -->
                            <div class="float-left">
                                <div class="text-10"><?php echo strIdx( 656 )?>&nbsp;
                                    <?php if ( config_read(60) == 1 ) { 
                                        echo '<span><i class="color-warning fas fa-exclamation-triangle fa-1x" data-fa-transform="up-1 right-0"></i></span>';
                                    }
                                ?>
                            </div>
                        </div>
                        <!-- right side -->
                        <div class="float-right">
                            <div>
                                <input class="cursor-pointer" name="inet_allowed" type="radio" value="1" <?php if ( config_read(60) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                <input class="cursor-pointer" name="inet_allowed" type="radio" value="0" <?php if ( config_read(60) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                            </div>
                        </div>
                    </div>

            </div>
        </div>
        <p></p>
        <br>
        <!-- placeholder variables for session termination -->
            <input type="hidden" name="logout" id="logout" value="">
            </form>
        </div>

        <div id="right-wrapper-config-right-2">
            <div class="frame-4-top">
                <span class="text-15"><?php echo strIdx( 155 )?></span>
            </div>
            <div class="frame-4-bot text-10">
                <?php echo strIdx(35);?>
                <p></p>
                <?php echo strIdx(49);?>
            </div>
        </div>
        </div>
        <!-- end inner block right part of screen -->
    </div>
</body>
</html>