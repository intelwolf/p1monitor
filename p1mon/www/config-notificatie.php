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
$mo      = strIdx( 482 );
$tu      = strIdx( 483 );
$we      = strIdx( 484 );
$th      = strIdx( 485 );
$fr      = strIdx( 486 );
$sa      = strIdx( 487 );
$su      = strIdx( 488 );

function timestampSequenceCheck( &$timeslot ){
    // hour check
    if ( (int)$timeslot[2] < (int)$timeslot[0] ) {
        $tmp_hh      = $timeslot[2];
        $tmp_mm      = $timeslot[3];
        $timeslot[2] = $timeslot[0];
        $timeslot[3] = $timeslot[1];
        $timeslot[0] = $tmp_hh;
        $timeslot[1] = $tmp_mm;
    }
    // minuten check
    if ( (int)$timeslot[2] == (int)$timeslot[0] ) {
        if ( (int)$timeslot[3] < (int)$timeslot[1] ) {
            $tmp_mm      = $timeslot[3];
            $timeslot[3] = $timeslot[1];
            $timeslot[1] = $tmp_mm;
        }
    }
}


$timeslot_p_overshoot  = array( '', '', '', '', '' ,'' , '', '', '', '', '' );
$timeslot_p_undershoot = array( '', '', '', '', '' ,'' , '', '', '', '', '' );
$timeslot_c_overshoot  = array( '', '', '', '', '' ,'' , '', '', '', '', '' );
$timeslot_c_undershoot = array( '', '', '', '', '' ,'' , '', '', '', '', '' );

$err_cnt = -1;

$timeslot_p_overshoot   = explode( '.', config_read( 209 ));
$timeslot_p_undershoot  = explode( '.', config_read( 210 ));
$timeslot_c_overshoot   = explode( '.', config_read( 211 ));
$timeslot_c_undershoot  = explode( '.', config_read( 212 ));


// timeslot production overshoot start

if ( isset($_POST["fs_rb_watt_po"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["fs_rb_watt_po"] == '1' ) {
            if ( updateConfigDb("update config set parameter = '1' where ID = 213"))$err_cnt += 1;
    } else {
            if ( updateConfigDb("update config set parameter = '0' where ID = 213"))$err_cnt += 1;
    }
}

if ( isset($_POST["watt_po"]) ) {
    $input = inputCleanDigitsOnlyMinus(trim($_POST["watt_po"]));
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".$input."' where ID = 217")) $err_cnt += 1;
}

if ( isset( $_POST["hh_1_po"] ) ) { 
    $int = (int)inputClean($_POST["hh_1_po"]);
    if ( $int > 23 or $int < 1 ) { $int=0; }
    $timeslot_p_overshoot[0]=$int;
}

if ( isset( $_POST["mm_1_po"] ) ) { 
    $int = (int)inputClean($_POST["mm_1_po"]);
    if ( $int > 59 or $int < 1 ) { $int=0; }
    $timeslot_p_overshoot[1]=$int;
}

if ( isset( $_POST["hh_2_po"] ) ) { 
    $int = (int)inputClean($_POST["hh_2_po"]);
    if ( $int > 23 or $int < 1 ) { $int=0; }
    $timeslot_p_overshoot[2]=$int;
}

if ( isset( $_POST["mm_2_po"] ) ) { 
    $int = (int)inputClean($_POST["mm_2_po"]);
    if ( $int > 59 or $int < 1 ) { $int=0; }
    $timeslot_p_overshoot[3]=$int;
}

if ( isset( $_POST['fs_rb_weekday_ma_po'] )) { 
    if ( $_POST['fs_rb_weekday_ma_po'] === 'on') {  $timeslot_p_overshoot[4] = 1; } else { $timeslot_p_overshoot[4] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_di_po'] ) ) { 
    if ( $_POST['fs_rb_weekday_di_po'] === 'on') {  $timeslot_p_overshoot[5] = 1; } else { $timeslot_p_overshoot[5] = 0; }
}

if ( isset( $_POST['fs_rb_weekday_wo_po'] ) ) { 
    if ( $_POST['fs_rb_weekday_wo_po'] === 'on') {  $timeslot_p_overshoot[6] = 1; } else { $timeslot_p_overshoot[6] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_do_po'] ) ) { 
    if ( $_POST['fs_rb_weekday_do_po'] === 'on') {  $timeslot_p_overshoot[7] = 1; } else {  $timeslot_p_overshoot[7] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_vr_po'] ) ) { 
    if ( $_POST['fs_rb_weekday_vr_po'] === 'on') { $timeslot_p_overshoot[8] = 1; } else {  $timeslot_p_overshoot[8] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_za_po'] ) ) { 
    if ( $_POST['fs_rb_weekday_za_po'] === 'on') { $timeslot_p_overshoot[9] = 1; } else {  $timeslot_p_overshoot[9] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_zo_po'] ) ) { 
    if ( $_POST['fs_rb_weekday_zo_po'] === 'on') { $timeslot_p_overshoot[10] = 1; } else { $timeslot_p_overshoot[10] = 0; }
} 

// to limit database writes, only write once on changes, write always because of checkboxes.
if ( updateConfigDb("update config set parameter = '" . implode(".",$timeslot_p_overshoot). "' where ID = 209")) $err_cnt += 1;

// timeslot production overshoot end

///////////////////////////////////////
// timeslot production undershoot start

if ( isset($_POST["fs_rb_watt_pu"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["fs_rb_watt_pu"] == '1' ) {
            if ( updateConfigDb("update config set parameter = '1' where ID = 214"))$err_cnt += 1;
    } else {
            if ( updateConfigDb("update config set parameter = '0' where ID = 214"))$err_cnt += 1;
    }
}

if ( isset($_POST["watt_pu"]) ) {
    $input = inputCleanDigitsOnlyMinus(trim($_POST["watt_pu"]));
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".$input."' where ID = 218")) $err_cnt += 1;
}

if ( isset( $_POST["hh_1_pu"] ) ) {
    $int = (int)inputClean($_POST["hh_1_pu"]);
    if ( $int > 23 or $int < 1 ) { $int=0; }
    $timeslot_p_undershoot[0]=$int;
}

if ( isset( $_POST["mm_1_pu"] ) ) {
    $int = (int)inputClean($_POST["mm_1_pu"]);
    if ( $int > 59 or $int < 1 ) { $int=0; }
    $timeslot_p_undershoot[1]=$int;
}

if ( isset( $_POST["hh_2_pu"] ) ) {
    $int = (int)inputClean($_POST["hh_2_pu"]);
    if ( $int > 23 or $int < 1 ) { $int=0; }
    $timeslot_p_undershoot[2]=$int;
}

if ( isset( $_POST["mm_2_pu"] ) ) { 
    $int = (int)inputClean($_POST["mm_2_pu"]);
    if ( $int > 59 or $int < 1 ) { $int=0; }
    $timeslot_p_undershoot[3]=$int;
}

if ( isset( $_POST['fs_rb_weekday_ma_pu'] )) { 
    if ( $_POST['fs_rb_weekday_ma_pu'] === 'on') { $timeslot_p_undershoot[4] = 1; } else { $timeslot_p_undershoot[4] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_di_pu'] ) ) { 
    if ( $_POST['fs_rb_weekday_di_pu'] === 'on') { $timeslot_p_undershoot[5] = 1; } else { $timeslot_p_undershoot[5] = 0; }
}

if ( isset( $_POST['fs_rb_weekday_wo_pu'] ) ) { 
    if ( $_POST['fs_rb_weekday_wo_pu'] === 'on') { $timeslot_p_undershoot[6] = 1; } else { $timeslot_p_undershoot[6] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_do_pu'] ) ) { 
    if ( $_POST['fs_rb_weekday_do_pu'] === 'on') { $timeslot_p_undershoot[7] = 1; } else { $timeslot_p_undershoot[7] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_vr_pu'] ) ) { 
    if ( $_POST['fs_rb_weekday_vr_pu'] === 'on') { $timeslot_p_undershoot[8] = 1; } else { $timeslot_p_undershoot[8] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_za_pu'] ) ) { 
    if ( $_POST['fs_rb_weekday_za_pu'] === 'on') { $timeslot_p_undershoot[9] = 1; } else { $timeslot_p_undershoot[9] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_zo_pu'] ) ) { 
    if ( $_POST['fs_rb_weekday_zo_pu'] === 'on') { $timeslot_p_undershoot[10] = 1; } else { $timeslot_p_undershoot[10] = 0; }
} 

// to limit database writes, only write once on changes, write always because of checkboxes.
if ( updateConfigDb("update config set parameter = '" . implode(".",$timeslot_p_undershoot). "' where ID = 210")) $err_cnt += 1;

// timeslot production unbdershoot end

//////////////////////////////////////
// timeslot consumption overshoot start

if ( isset($_POST["fs_rb_watt_co"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["fs_rb_watt_co"] == '1' ) {
            if ( updateConfigDb("update config set parameter = '1' where ID = 215"))$err_cnt += 1;
    } else {
            if ( updateConfigDb("update config set parameter = '0' where ID = 215"))$err_cnt += 1;
    }
}

if ( isset($_POST["watt_co"]) ) {
    $input = inputCleanDigitsOnlyMinus(trim($_POST["watt_co"]));
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".$input."' where ID = 219")) $err_cnt += 1;
}

if ( isset( $_POST["hh_1_co"] ) ) {
    $int = (int)inputClean($_POST["hh_1_co"]);
    if ( $int > 23 or $int < 1 ) { $int=0; }
    $timeslot_c_overshoot[0]=$int;
}

if ( isset( $_POST["mm_1_co"] ) ) {
    $int = (int)inputClean($_POST["mm_1_co"]);
    if ( $int > 59 or $int < 1 ) { $int=0; }
    $timeslot_c_overshoot[1]=$int;
}

if ( isset( $_POST["hh_2_co"] ) ) {
    $int = (int)inputClean($_POST["hh_2_co"]);
    if ( $int > 23 or $int < 1 ) { $int=0; }
    $timeslot_c_overshoot[2]=$int;
}

if ( isset( $_POST["mm_2_co"] ) ) {
    $int = (int)inputClean($_POST["mm_2_co"]);
    if ( $int > 59 or $int < 1 ) { $int=0; }
    $timeslot_c_overshoot[3]=$int;
}

if ( isset( $_POST['fs_rb_weekday_ma_co'] )) { 
    if ( $_POST['fs_rb_weekday_ma_co'] === 'on') { $timeslot_c_overshoot[4] = 1; } else { $timeslot_c_overshoot[4] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_di_co'] ) ) { 
    if ( $_POST['fs_rb_weekday_di_co'] === 'on') { $timeslot_c_overshoot[5] = 1; } else { $timeslot_c_overshoot[5] = 0; }
}

if ( isset( $_POST['fs_rb_weekday_wo_co'] ) ) { 
    if ( $_POST['fs_rb_weekday_wo_co'] === 'on') { $timeslot_c_overshoot[6] = 1; } else { $timeslot_c_overshoot[6] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_do_co'] ) ) { 
    if ( $_POST['fs_rb_weekday_do_co'] === 'on') { $timeslot_c_overshoot[7] = 1; } else { $timeslot_c_overshoot[7] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_vr_co'] ) ) { 
    if ( $_POST['fs_rb_weekday_vr_co'] === 'on') { $timeslot_c_overshoot[8] = 1; } else { $timeslot_c_overshoot[8] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_za_co'] ) ) { 
    if ( $_POST['fs_rb_weekday_za_co'] === 'on') { $timeslot_c_overshoot[9] = 1; } else { $timeslot_c_overshoot[9] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_zo_co'] ) ) { 
    if ( $_POST['fs_rb_weekday_zo_co'] === 'on') { $timeslot_c_overshoot[10] = 1; } else { $timeslot_c_overshoot[10] = 0; }
} 

// to limit database writes, only write once on changes, write always because of checkboxes.
if ( updateConfigDb("update config set parameter = '" . implode(".", $timeslot_c_overshoot). "' where ID = 211")) $err_cnt += 1;

// timeslot consumption overshoot end

//////////////////////////////////////
// timeslot consumption undershoot start

if ( isset($_POST["fs_rb_watt_cu"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["fs_rb_watt_cu"] == '1' ) {
            if ( updateConfigDb("update config set parameter = '1' where ID = 216"))$err_cnt += 1;
    } else {
            if ( updateConfigDb("update config set parameter = '0' where ID = 216"))$err_cnt += 1;
    }
}

if ( isset($_POST["watt_cu"]) ) {
    $input = inputCleanDigitsOnlyMinus(trim($_POST["watt_cu"]));
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '".$input."' where ID = 220")) $err_cnt += 1;
}

if ( isset( $_POST["hh_1_cu"] ) ) {
    $int = (int)inputClean($_POST["hh_1_cu"]);
    if ( $int > 23 or $int < 1 ) { $int=0; }
    $timeslot_c_undershoot[0]=$int;
}

if ( isset( $_POST["mm_1_cu"] ) ) {
    $int = (int)inputClean($_POST["mm_1_cu"]);
    if ( $int > 59 or $int < 1 ) { $int=0; }
    $timeslot_c_undershoot[1]=$int;
}

if ( isset( $_POST["hh_2_cu"] ) ) {
    $int = (int)inputClean($_POST["hh_2_cu"]);
    if ( $int > 23 or $int < 1 ) { $int=0; }
    $timeslot_c_undershoot[2]=$int;
}

if ( isset( $_POST["mm_2_cu"] ) ) {
    $int = (int)inputClean($_POST["mm_2_cu"]);
    if ( $int > 59 or $int < 1 ) { $int=0; }
    $timeslot_c_undershoot[3]=$int;
}

if ( isset( $_POST['fs_rb_weekday_ma_cu'] )) { 
    if ( $_POST['fs_rb_weekday_ma_cu'] === 'on') { $timeslot_c_undershoot[4] = 1; } else { $timeslot_c_undershoot[4] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_di_cu'] ) ) { 
    if ( $_POST['fs_rb_weekday_di_cu'] === 'on') { $timeslot_c_undershoot[5] = 1; } else { $timeslot_c_undershoot[5] = 0; }
}

if ( isset( $_POST['fs_rb_weekday_wo_cu'] ) ) { 
    if ( $_POST['fs_rb_weekday_wo_cu'] === 'on') { $timeslot_c_undershoot[6] = 1; } else { $timeslot_c_undershoot[6] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_do_cu'] ) ) { 
    if ( $_POST['fs_rb_weekday_do_cu'] === 'on') { $timeslot_c_undershoot[7] = 1; } else { $timeslot_c_undershoot[7] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_vr_cu'] ) ) { 
    if ( $_POST['fs_rb_weekday_vr_cu'] === 'on') { $timeslot_c_undershoot[8] = 1; } else { $timeslot_c_undershoot[8] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_za_cu'] ) ) { 
    if ( $_POST['fs_rb_weekday_za_cu'] === 'on') { $timeslot_c_undershoot[9] = 1; } else { $timeslot_c_undershoot[9] = 0; }
} 

if ( isset( $_POST['fs_rb_weekday_zo_cu'] ) ) { 
    if ( $_POST['fs_rb_weekday_zo_cu'] === 'on') { $timeslot_c_undershoot[10] = 1; } else { $timeslot_c_undershoot[10] = 0; }
} 

// to limit database writes, only write once on changes, write always because of checkboxes.
if ( updateConfigDb("update config set parameter = '" . implode(".", $timeslot_c_undershoot). "' where ID = 212")) $err_cnt += 1;

// timeslot consumption undershoot end

// check that the start time is not later then
// then end time, if so swap.
timestampSequenceCheck( $timeslot_p_overshoot );
timestampSequenceCheck( $timeslot_p_undershoot );
timestampSequenceCheck( $timeslot_c_overshoot );
timestampSequenceCheck( $timeslot_c_undershoot );

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

if ( isset($_POST["fs_rb_v"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["fs_rb_v"] == '1' ) {
            if ( updateConfigDb("update config set parameter = '1' where ID = 175"))$err_cnt += 1;
    } else {
            if ( updateConfigDb("update config set parameter = '0' where ID = 175"))$err_cnt += 1;
    }
}

if ( isset( $_POST["email_test_button"] ) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '1' where ID = 187") )$err_cnt += 1;
}


?>
 <!doctype html>
 <html lang="<?php echo strIdx( 370 )?>">
 <head>
     <meta name="robots" content="noindex">
     <title>P1-monitor <?php echo strIdx( 463 )?></title>
     <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
     <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
     <link type="text/css" rel="stylesheet" href="./css/p1mon.css">
     <link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css">
     <script defer src="./font/awsome/js/all.js"></script>
     <script src="./js/jquery.min.js"></script>
     <script src="./js/jquery-validate-link/jquery.validate.min.js"></script>
     <script src="./js/jquery-validate-link/additional-methods.min.js"></script>
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
         <div class="left-wrapper-config">
             <!-- left block -->
             <?php menu_control(12);?>
         </div>

         <div id="right-wrapper-config">
             <!-- right block -->
             <!-- inner block right part of screen -->
             <div id="right-wrapper-config-left">
                 <!-- start of content -->
                 <form name="formvalues" id="formvalues" method="POST">

                     <div class="frame-4-top">
                         <span class="text-15"><?php echo strIdx( 464 )?></span>
                     </div>
                     <div class="frame-4-bot">
                         <div class="float-left pad-17">

                             <div class="content-wrapper pos-36" title="<?php echo strIdx(50);?>">
                                 <div class="pad-24 content-wrapper">
                                     <label class="text-14"><?php echo strIdx( 465 )?></label>
                                 </div>
                                 <div class="content-wrapper">
                                     <input class="input-11 color-settings color-input-back" id="i_email_account"
                                         name="i_email_account" type="text" value="<?php echo config_read(63);?>">
                                 </div>
                             </div>

                             <div class="content-wrapper pos-36" title="<?php echo strIdx(51);?>">
                                 <div class="pad-24 content-wrapper">
                                     <label class="text-14"><?php echo strIdx( 226 )?></label>
                                 </div>
                                 <div class="content-wrapper">
                                     <input class="input-11 color-settings color-input-back" id="i_email_pword"
                                         name="i_email_pword" type="password"
                                         value="<?php echo decodeString(64, 'mailpw');?>">
                                 </div>
                                 <div class="content-wrapper pad-1 cursor-pointer" id="api_passwd"
                                     onclick="toggelPasswordVisibility('i_email_pword')">
                                     <span><i class="color-menu pad-7 fas fa-eye"></i></span>
                                 </div>
                             </div>

                             <div class="content-wrapper pos-36" title="<?php echo strIdx(52);?>">
                                 <div class="pad-24 content-wrapper">
                                     <label class="text-14"><?php echo strIdx( 466 )?></label>
                                 </div>
                                 <div class="content-wrapper">
                                     <input class="input-11 color-settings color-input-back" id="i_mail_server"
                                         name="i_mail_server" type="text" value="<?php echo config_read(65);?>">
                                 </div>
                             </div>

                             <div class="content-wrapper pos-36" title="<?php echo strIdx(53);?>">
                                 <div class="pad-24 content-wrapper">
                                     <label class="text-14"><?php echo strIdx( 467 )?></label>
                                 </div>
                                 <div class="content-wrapper">
                                     <input class="input-11 color-settings color-input-back" id="i_email_ssl_port"
                                         name="i_email_ssl_port" type="text" value="<?php echo config_read(66);?>">
                                 </div>
                             </div>

                             <div class="content-wrapper pos-36" title="<?php echo strIdx(54);?>">
                                 <div class="pad-24 content-wrapper">
                                     <label class="text-14"><?php echo strIdx( 468 )?></label>
                                 </div>
                                 <div class="content-wrapper">
                                     <input class="input-11 color-settings color-input-back" id="i_email_starttls_port"
                                         name="i_email_starttls_port" type="text" value="<?php echo config_read(67);?>">
                                 </div>
                             </div>

                             <div class="content-wrapper pos-36" title="<?php echo strIdx(55);?>">
                                 <div class="pad-24 content-wrapper">
                                     <label class="text-14"><?php echo strIdx( 469 )?></label>
                                 </div>
                                 <div class="content-wrapper">
                                     <input class="input-11 color-settings color-input-back" id="i_email_normal_port"
                                         name="i_email_normal_port" type="text" value="<?php echo config_read(68);?>">
                                 </div>
                             </div>

                             <div class="content-wrapper pos-36" title="<?php echo strIdx(56);?>">
                                 <div class="pad-24 content-wrapper">
                                     <label class="text-14"><?php echo strIdx( 470 )?></label>
                                 </div>
                                 <div class="content-wrapper">
                                     <input class="input-11 color-settings color-input-back" id="i_email_subject"
                                         name="i_email_subject" type="text" value="<?php echo config_read(69);?>">
                                 </div>
                             </div>

                             <div class="content-wrapper pos-36" title="<?php echo strIdx(57);?>">
                                 <div class="pad-24 content-wrapper">
                                     <label class="text-14"><?php echo strIdx( 471 )?> (to)</label>
                                 </div>
                                 <div class="content-wrapper">
                                     <input class="input-11 color-settings color-input-back" id="i_email_to"
                                         name="i_email_to" type="text" value="<?php echo config_read(70);?>">
                                 </div>
                             </div>

                             <div class="content-wrapper pos-36" title="<?php echo strIdx(58);?>">
                                 <div class="pad-24 content-wrapper">
                                     <label class="text-14"><?php echo strIdx( 471 )?> (cc)</label>
                                 </div>
                                 <div class="content-wrapper">
                                     <input class="input-11 color-settings color-input-back" id="i_email_cc"
                                         name="i_email_cc" type="text" value="<?php echo config_read(74);?>">
                                 </div>
                             </div>

                             <div class="content-wrapper pos-36" title="<?php echo strIdx(59);?>">
                                 <div class="pad-24 content-wrapper">
                                     <label class="text-14"><?php echo strIdx( 471 )?> (bcc)</label>
                                 </div>
                                 <div class="content-wrapper">
                                     <input class="input-11 color-settings color-input-back" id="i_email_bcc"
                                         name="i_email_bcc" type="text" value="<?php echo config_read(75);?>">
                                 </div>
                             </div>

                             <div class="content-wrapper pos-36" title="<?php echo strIdx(60);?>">
                                 <div class="pad-24 content-wrapper">
                                     <label class="text-14">FROM alias</label>
                                 </div>
                                 <div class="content-wrapper">
                                     <input class="input-11 color-settings color-input-back" id="i_email_from"
                                         name="i_email_from" type="text" value="<?php echo config_read(71);?>">
                                 </div>
                             </div>

                             <div class="content-wrapper pos-36" title="<?php echo strIdx(61);?>">
                                 <div class="pad-24 content-wrapper">
                                     <label class="text-14"><?php echo strIdx( 472 )?></label>
                                 </div>
                                 <div class="content-wrapper">
                                     <input class="input-11 color-settings color-input-back" id="i_email_timeout"
                                         name="i_email_timeout" type="text" value="<?php echo config_read(72);?>">
                                 </div>
                             </div>
                             <br>
                             <br>

                             <div class="pad-1 content-wrapper float-left" title="<?php echo strIdx( 74 );?>">
                                 <button class="input-2 but-1 cursor-pointer" id="email_test_button"
                                     name="email_test_button" type="submit">
                                     <i class="color-menu fa-3x far fa-play-circle"></i><br>
                                     <span class="color-menu text-7">test</span>
                                 </button>
                             </div>

                         </div>
                     </div>

                     <p></p>

                     <div class="frame-4-top">
                         <span class="text-15"><?php echo strIdx( 212 )?></span>
                     </div>
                     <div class="frame-4-bot">
                         <div class='pad-12'>
                             <div>
                                 <!-- left side -->
                                 <div class="float-left" title="<?php echo strIdx(63);?>">
                                     <div class="text-10"><?php echo strIdx( 473 )?>&nbsp;</div>
                                 </div>
                                 <!-- right side -->
                                 <div class="float-right">
                                     <div>
                                         <input class="cursor-pointer" id="fs_rb_aan_p1_data_on"
                                             name="fs_rb_aan_p1_data" type="radio" value="1"
                                             <?php if ( config_read(73) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                         <input class="cursor-pointer" id="fs_rb_aan_p1_data_off"
                                             name="fs_rb_aan_p1_data" type="radio" value="0"
                                             <?php if ( config_read(73) == 0 ) { echo 'checked'; }?>><?php echo $sw_off?>
                                     </div>
                                     <p></p>
                                 </div>
                             </div>
                         </div>
                     </div>
                     <p></p>

                     <div class="frame-4-top">
                         <span class="text-15"><?php echo strIdx( 474 )?></span>
                     </div>
                     <div class="frame-4-bot">
                         <div class='pad-12'>
                             <div>
                                 <!-- left side -->
                                 <div class="float-left" title="<?php echo strIdx(63);?>">
                                     <div class="text-10"><?php echo strIdx( 475 )?>&nbsp;</div>
                                 </div>
                                 <!-- right side -->
                                 <div class="float-right">
                                     <div>
                                         <input class="cursor-pointer" id="fs_rb_v_max_on" name="fs_rb_v" type="radio"
                                             value="1" <?php if ( config_read( 175 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                         <input class="cursor-pointer" id="fs_rb_v_max_off" name="fs_rb_v" type="radio"
                                             value="0" <?php if ( config_read( 175 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off?>
                                     </div>
                                     <p></p>
                                 </div>
                             </div>
                         </div>
                     </div>
                     <p></p>

                     <div class="frame-4-top">
                         <span class="text-15"><?php echo strIdx( 476 )?></span>
                     </div>
                     <div class="frame-4-bot">

                        <div class="rTable">

                            <div class="rTableRow text-16">
                                <?php echo strIdx( 477 )?>
                            </div>

                            <div class="rTableRow">

                                <div class="rTableCell pad-1">
                                    <input class="input-14 color-settings color-input-back" id="watt_po" name="watt_po" type="text" value="<?php echo config_read( 217 );?>">
                                </div>
                                <div class="rTableCell">
                                    <input class="cursor-pointer" id="fs_rb_watt_po_on"  name="fs_rb_watt_po" type="radio"
                                    value="1" <?php if ( config_read( 213 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                    <input class="cursor-pointer" id="fs_rb_watt_po_off" name="fs_rb_watt_po" type="radio"
                                    value="0" <?php if ( config_read( 213 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off?>
                                </div>
                            </div>

                            <div class="rTableRow text-16 ">
                                <div class="rTableCell width-430">
                                    <i class="pad-7 fas fa-toggle-off"></i>
                                    <label><?php echo strIdx( 478 )?></label>
                                </div>
                            </div>

                            <div class="rTableRow text-16">
                                <div class="rTableCell">

                                    <!-- timeslot production overshoot -->
                                    <input class="input-12 color-settings color-input-back" id="hh_1_po" name="hh_1_po" type="text" value="<?php echo sprintf('%02d', $timeslot_p_overshoot[0] );?>">
                                    <span>:</span>
                                    <input class="input-12 color-settings color-input-back" id="mm_1_po" name="mm_1_po" type="text" value="<?php echo sprintf('%02d', $timeslot_p_overshoot[1] ); ?>">
                                    <span>&nbsp;&nbsp;</span>
                                    <input class="input-12 color-settings color-input-back" id="hh_2_po" name="hh_2_po" type="text" value="<?php echo sprintf('%02d', $timeslot_p_overshoot[2] );?>">
                                    <span>:</span>
                                    <input class="input-12 color-settings color-input-back" id="mm_2_po" name="mm_2_po" type="text" value="<?php echo sprintf('%02d', $timeslot_p_overshoot[3] );?>">
                                    <span>&nbsp;</span>
                                    <input type="hidden"                                            name="fs_rb_weekday_ma_po" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_ma_po" name="fs_rb_weekday_ma_po" type="checkbox" value="on" <?php if ( $timeslot_p_overshoot[4] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_ma_po" class="text-27 margin-5"><?php echo $mo?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_di_po" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_di_po" name="fs_rb_weekday_di_po" type="checkbox" value="on" <?php if ( $timeslot_p_overshoot[5] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_di_po" class="text-27 margin-5"><?php echo $tu?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_wo_po" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_wo_po" name="fs_rb_weekday_wo_po" type="checkbox" value="on" <?php if ( $timeslot_p_overshoot[6] == 1  ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_wo_po" class="text-27 margin-5"><?php echo $we?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_do_po" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_do_po" name="fs_rb_weekday_do_po" type="checkbox" value="on" <?php if ( $timeslot_p_overshoot[7] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_do_po" class="text-27 margin-5"><?php echo $th?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_vr_po" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_vr_po" name="fs_rb_weekday_vr_po" type="checkbox" value="on" <?php if ( $timeslot_p_overshoot[8] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_vr_po" class="text-27 margin-5"><?php echo $fr?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_za_po" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_za_po" name="fs_rb_weekday_za_po" type="checkbox" value="on" <?php if ( $timeslot_p_overshoot[9] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_za_po" class="text-27 margin-5"><?php echo $sa?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_zo_po" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_zo_po" name="fs_rb_weekday_zo_po" type="checkbox" value="on" <?php if ( $timeslot_p_overshoot[10] == 1) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_zo_po" class="text-27 margin-5"><?php echo $su ?></label>
                                </div>
                            </div>
                        </div>
                        <HR>


                        <div class="rTable">

                            <div class="rTableRow text-16">
                                <?php echo strIdx( 479 )?>
                            </div>

                            <div class="rTableRow">
                                <div class="rTableCell pad-1">
                                <input class="input-14 color-settings color-input-back" id="watt_pu" name="watt_pu" type="text" value="<?php echo config_read( 218 );?>">
                                </div>
                                <div class="rTableCell">
                                    <input class="cursor-pointer" id="fs_rb_watt_pu_on"  name="fs_rb_watt_pu" type="radio"
                                    value="1" <?php if ( config_read( 214 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                    <input class="cursor-pointer" id="fs_rb_watt_pu_off" name="fs_rb_watt_pu" type="radio"
                                    value="0" <?php if ( config_read( 214 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off?>
                                </div>
                            </div>

                            <div class="rTableRow text-16">
                                <div class="rTableCell width-430">
                                    <i class="pad-7 fas fa-toggle-off"></i>
                                    <label><?php echo strIdx( 478 )?></label>
                                </div>
                            </div>

                            <div class="rTableRow text-16">
                                <div class="rTableCell">

                                    <!-- timeslot production overshoot -->
                                    <input class="input-12 color-settings color-input-back" id="hh_1_pu" name="hh_1_pu" type="text" value="<?php echo sprintf('%02d', $timeslot_p_undershoot[0] );?>">
                                    <span>:</span>
                                    <input class="input-12 color-settings color-input-back" id="mm_1_pu" name="mm_1_pu" type="text" value="<?php echo sprintf('%02d', $timeslot_p_undershoot[1] ); ?>">
                                    <span>&nbsp;&nbsp;</span>
                                    <input class="input-12 color-settings color-input-back" id="hh_2_pu" name="hh_2_pu" type="text" value="<?php echo sprintf('%02d', $timeslot_p_undershoot[2] );?>">
                                    <span>:</span>
                                    <input class="input-12 color-settings color-input-back" id="mm_2_pu" name="mm_2_pu" type="text" value="<?php echo sprintf('%02d', $timeslot_p_undershoot[3] );?>">
                                    <span>&nbsp;</span>
                                    <input type="hidden"                                            name="fs_rb_weekday_ma_pu" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_ma_pu" name="fs_rb_weekday_ma_pu" type="checkbox" value="on" <?php if ( $timeslot_p_undershoot[4] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_ma_pu" class="text-27 margin-5"><?php echo $mo?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_di_pu" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_di_pu" name="fs_rb_weekday_di_pu" type="checkbox" value="on" <?php if ( $timeslot_p_undershoot[5] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_di_pu" class="text-27 margin-5"><?php echo $tu?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_wo_pu" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_wo_pu" name="fs_rb_weekday_wo_pu" type="checkbox" value="on" <?php if ( $timeslot_p_undershoot[6] == 1  ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_wo_pu" class="text-27 margin-5"><?php echo $we?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_do_pu" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_do_pu" name="fs_rb_weekday_do_pu" type="checkbox" value="on" <?php if ( $timeslot_p_undershoot[7] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_do_pu" class="text-27 margin-5"><?php echo $th?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_vr_pu" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_vr_pu" name="fs_rb_weekday_vr_pu" type="checkbox" value="on" <?php if ( $timeslot_p_undershoot[8] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_vr_pu" class="text-27 margin-5"><?php echo $fr?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_za_pu" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_za_pu" name="fs_rb_weekday_za_pu" type="checkbox" value="on" <?php if ( $timeslot_p_undershoot[9] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_za_pu" class="text-27 margin-5"><?php echo $sa?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_zo_pu" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_zo_pu" name="fs_rb_weekday_zo_pu" type="checkbox" value="on" <?php if ( $timeslot_p_undershoot[10] == 1) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_zo_pu" class="text-27 margin-5"><?php echo $su ?></label>
                                </div>
                            </div>
                        </div>

                        <HR>
                        <div class="rTable">
                            <div class="rTableRow text-16">
                            <?php echo strIdx( 480 )?>
                            </div>

                            <div class="rTableRow">
                                <div class="rTableCell pad-1">
                                <input class="input-14 color-settings color-input-back" id="watt_co" name="watt_co" type="text" value="<?php echo config_read( 219 );?>">
                                </div>
                                <div class="rTableCell">
                                    <input class="cursor-pointer" id="fs_rb_watt_co_on"  name="fs_rb_watt_co" type="radio"
                                    value="1" <?php if ( config_read( 215 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                    <input class="cursor-pointer" id="fs_rb_watt_co_off" name="fs_rb_watt_co" type="radio"
                                    value="0" <?php if ( config_read( 215 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off?>
                                </div>
                            </div>

                            <div class="rTableRow text-16">
                                <div class="rTableCell width-430">
                                    <i class="pad-7 fas fa-toggle-off"></i>
                                    <label><?php echo strIdx( 478 )?></label>
                                </div>
                            </div>

                            <div class="rTableRow text-16">
                                <div class="rTableCell">

                                    <!-- timeslot consumption overshoot -->
                                    <input class="input-12 color-settings color-input-back" id="hh_1_co" name="hh_1_co" type="text" value="<?php echo sprintf('%02d', $timeslot_c_overshoot[0] );?>">
                                    <span>:</span>
                                    <input class="input-12 color-settings color-input-back" id="mm_1_co" name="mm_1_co" type="text" value="<?php echo sprintf('%02d', $timeslot_c_overshoot[1] ); ?>">
                                    <span>&nbsp;&nbsp;</span>
                                    <input class="input-12 color-settings color-input-back" id="hh_2_co" name="hh_2_co" type="text" value="<?php echo sprintf('%02d', $timeslot_c_overshoot[2] );?>">
                                    <span>:</span>
                                    <input class="input-12 color-settings color-input-back" id="mm_2_co" name="mm_2_co" type="text" value="<?php echo sprintf('%02d', $timeslot_c_overshoot[3] );?>">
                                    <span>&nbsp;</span>
                                    <input type="hidden"                                            name="fs_rb_weekday_ma_co" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_ma_co" name="fs_rb_weekday_ma_co" type="checkbox" value="on" <?php if ( $timeslot_c_overshoot[4] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_ma_co" class="text-27 margin-5"><?php echo $mo?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_di_co" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_di_co" name="fs_rb_weekday_di_co" type="checkbox" value="on" <?php if ( $timeslot_c_overshoot[5] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_di_co" class="text-27 margin-5"><?php echo $tu?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_wo_co" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_wo_co" name="fs_rb_weekday_wo_co" type="checkbox" value="on" <?php if ( $timeslot_c_overshoot[6] == 1  ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_wo_co" class="text-27 margin-5"><?php echo $we?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_do_co" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_do_co" name="fs_rb_weekday_do_co" type="checkbox" value="on" <?php if ( $timeslot_c_overshoot[7] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_do_co" class="text-27 margin-5"><?php echo $th?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_vr_co" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_vr_co" name="fs_rb_weekday_vr_co" type="checkbox" value="on" <?php if ( $timeslot_c_overshoot[8] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_vr_co" class="text-27 margin-5"><?php echo $fr?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_za_co" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_za_co" name="fs_rb_weekday_za_co" type="checkbox" value="on" <?php if ( $timeslot_c_overshoot[9] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_za_co" class="text-27 margin-5"><?php echo $sa?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_zo_co" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_zo_co" name="fs_rb_weekday_zo_co" type="checkbox" value="on" <?php if ( $timeslot_c_overshoot[10] == 1) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_zo_co" class="text-27 margin-5"><?php echo $su ?></label>
                                </div>
                            </div>

                        </div>
                        <HR>

                        <div class="rTable">

                            <div class="rTableRow text-16">
                                <?php echo strIdx( 481 )?>
                            </div>

                            <div class="rTableRow">
                                <div class="rTableCell pad-1">
                                <input class="input-14 color-settings color-input-back" id="watt_cu" name="watt_cu" type="text" value="<?php echo config_read( 220 );?>">
                                </div>
                                <div class="rTableCell">
                                    <input class="cursor-pointer" id="fs_rb_watt_cu_on"  name="fs_rb_watt_cu" type="radio"
                                    value="1" <?php if ( config_read( 216 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                    <input class="cursor-pointer" id="fs_rb_watt_cu_off" name="fs_rb_watt_cu" type="radio"
                                    value="0" <?php if ( config_read( 216 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off?>
                                </div>
                            </div>

                            <div class="rTableRow text-16">

                                <div class="rTableCell width-430">
                                    <i class="pad-7 fas fa-toggle-off"></i>
                                    <label><?php echo strIdx( 478 )?></label>
                                </div>
                            </div>

                            <div class="rTableRow text-16">
                                <div class="rTableCell">

                                    <!-- timeslot consumption overshoot -->
                                    <input class="input-12 color-settings color-input-back" id="hh_1_cu" name="hh_1_cu" type="text" value="<?php echo sprintf('%02d', $timeslot_c_undershoot[0] );?>">
                                    <span>:</span>
                                    <input class="input-12 color-settings color-input-back" id="mm_1_cu" name="mm_1_cu" type="text" value="<?php echo sprintf('%02d', $timeslot_c_undershoot[1] ); ?>">
                                    <span>&nbsp;&nbsp;</span>
                                    <input class="input-12 color-settings color-input-back" id="hh_2_cu" name="hh_2_cu" type="text" value="<?php echo sprintf('%02d', $timeslot_c_undershoot[2] );?>">
                                    <span>:</span>
                                    <input class="input-12 color-settings color-input-back" id="mm_2_cu" name="mm_2_cu" type="text" value="<?php echo sprintf('%02d', $timeslot_c_undershoot[3] );?>">
                                    <span>&nbsp;</span>
                                    <input type="hidden"                                            name="fs_rb_weekday_ma_cu" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_ma_cu" name="fs_rb_weekday_ma_cu" type="checkbox" value="on" <?php if ( $timeslot_c_undershoot[4] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_ma_cu" class="text-27 margin-5"><?php echo $mo?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_di_cu" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_di_cu" name="fs_rb_weekday_di_cu" type="checkbox" value="on" <?php if ( $timeslot_c_undershoot[5] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_di_cu" class="text-27 margin-5"><?php echo $tu?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_wo_cu" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_wo_cu" name="fs_rb_weekday_wo_cu" type="checkbox" value="on" <?php if ( $timeslot_c_undershoot[6] == 1  ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_wo_cu" class="text-27 margin-5"><?php echo $we?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_do_cu" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_do_cu" name="fs_rb_weekday_do_cu" type="checkbox" value="on" <?php if ( $timeslot_c_undershoot[7] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_do_cu" class="text-27 margin-5"><?php echo $th?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_vr_cu" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_vr_cu" name="fs_rb_weekday_vr_cu" type="checkbox" value="on" <?php if ( $timeslot_c_undershoot[8] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_vr_cu" class="text-27 margin-5"><?php echo $fr?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_za_cu" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_za_cu" name="fs_rb_weekday_za_cu" type="checkbox" value="on" <?php if ( $timeslot_c_undershoot[9] == 1 ) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_za_co" class="text-27 margin-5"><?php echo $sa?></label>
                                    <input type="hidden"                                            name="fs_rb_weekday_zo_cu" value="off">
                                    <input class="cursor-pointer margin-6" id="fs_rb_weekday_zo_cu" name="fs_rb_weekday_zo_cu" type="checkbox" value="on" <?php if ( $timeslot_c_undershoot[10] == 1) { echo 'checked'; }?>>
                                    <label for="fs_rb_weekday_zo_cu" class="text-27 margin-5">zo</label>
                                </div>
                            </div>

                        </div>
                        <p></p>

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
                     <?php echo strIdx( 62 );?>
                     <br><br>
                     <?php echo strIdx( 489 );?>
                     <br><br>
                     <?php echo strIdx( 490 );?>
                     <br><br>
                     <?php echo strIdx( 491 );?>
                 </div>
             </div>
         </div>

     </div>
     <?php echo div_err_succes();?>

    <script>
    jQuery.validator.addMethod("check_any_to_cc_bcc", function(value, element) {

         //console.log("Log" +  value, element );

         var to = document.getElementById("i_email_to").value.trim().length;
         var cc = document.getElementById("i_email_cc").value.trim().length;
         var bcc = document.getElementById("i_email_bcc").value.trim().length;

         total_len = to + cc + bcc;

         if (total_len > 0) {
             return true;
         } else {
             return false;
         }

     }, '');

     $(function() {
         $("#formvalues").validate({
             rules: {
                'hh_1_po': {
                    required: true,
                    number: true,
                    max: 23,
                    min: 0
                },
                'hh_2_po': {
                    required: true,
                    number: true,
                    max: 23,
                    min: 0
                },
                'mm_1_po': {
                    required: true,
                    number: true,
                    max: 59,
                    min: 0
                },
                'mm_2_po': {
                    required: true,
                    number: true,
                    max: 59,
                    min: 0
                },

                'hh_1_pu': {
                    required: true,
                    number: true,
                    max: 23,
                    min: 0
                },
                'hh_2_pu': {
                    required: true,
                    number: true,
                    max: 23,
                    min: 0
                },
                'mm_1_pu': {
                    required: true,
                    number: true,
                    max: 59,
                    min: 0
                },
                'mm_2_pu': {
                    required: true,
                    number: true,
                    max: 59,
                    min: 0
                },

                'hh_1_co': {
                    required: true,
                    number: true,
                    max: 23,
                    min: 0
                },
                'hh_2_co': {
                    required: true,
                    number: true,
                    max: 23,
                    min: 0
                },
                'mm_1_co': {
                    required: true,
                    number: true,
                    max: 59,
                    min: 0
                },
                'mm_2_co': {
                    required: true,
                    number: true,
                    max: 59,
                    min: 0
                },

                'hh_1_cu': {
                    required: true,
                    number: true,
                    max: 23,
                    min: 0
                },
                'hh_2_cu': {
                    required: true,
                    number: true,
                    max: 23,
                    min: 0
                },
                'mm_1_cu': {
                    required: true,
                    number: true,
                    max: 59,
                    min: 0
                },
                'mm_2_cu': {
                    required: true,
                    number: true,
                    max: 59,
                    min: 0
                },
                'watt_po': {
                    required: true,
                    number: true,
                    max: 99999999999999999999,
                    min: -1
                },
                'watt_pu': {
                    required: true,
                    number: true,
                    max: 99999999999999999999,
                    min: -1
                },
                'watt_co': {
                    required: true,
                    number: true,
                    max: 99999999999999999999,
                    min: -1
                },
                'watt_cu': {
                    required: true,
                    number: true,
                    max: 99999999999999999999,
                    min: -1
                },
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
                 },
                 'i_email_normal_port': {
                     required: true,
                     number: true,
                     max: 65535,
                     min: 1
                 },
                 'i_email_to': {
                     required: false,
                     email: true,
                     check_any_to_cc_bcc: true
                 },
                 'i_email_cc': {
                     required: false,
                     email: true,
                     check_any_to_cc_bcc: true
                 },
                 'i_email_bcc': {
                     required: false,
                     email: true,
                     check_any_to_cc_bcc: true
                 },
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