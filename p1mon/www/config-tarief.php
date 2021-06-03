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


$err_cnt = -1;
// tarieven E aanpassen
if( isset($_POST["verbr_piek"]) || isset($_POST["verbr_dal"]) || isset($_POST["gelvr_piek"]) || isset($_POST["gelvr_dal"]) || isset($_POST["e_vastrecht"]) )
{
    $err_cnt=0;
    // update database
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["verbr_piek"],5,99.99999,1)."' where ID = 2")) $err_cnt += 1;
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["verbr_dal"], 5,99.99999,1)."' where ID = 1")) $err_cnt += 1;
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["gelvr_piek"],5,99.99999,1)."' where ID = 4")) $err_cnt += 1;
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["gelvr_dal"], 5,99.99999,1)."' where ID = 3")) $err_cnt += 1;
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["e_vastrecht"], 5,99.99999,0)."' where ID = 5")) $err_cnt += 1;
}

// tarieven GAS aanpassen
if( isset($_POST["verbr_gas"]) || isset($_POST["vastrecht_gas"]))
{
    if ( $err_cnt < 0 ) { $err_cnt=0; }
    // update database
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["verbr_gas"],5,99.99999,1)."' where ID = 15")) $err_cnt += 1;
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["vastrecht_gas"], 5,99.99999,0)."' where ID = 16")) $err_cnt += 1;
}

// tarieven kosten aanpassen
if( isset($_POST["max_cost"]) )
{
    if ( $err_cnt < 0 ) { $err_cnt=0; }
    // update database
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["max_cost"],5,9999.99999,1)."' where ID = 39")) $err_cnt += 1;
}

// tarieven water aanpassen
if( isset($_POST["verbr_water"]) || isset($_POST["vastrecht_water"]))
{
    if ( $err_cnt < 0 ) { $err_cnt=0; }
    // update database
    if ( updateConfigDb( "update config set parameter = '" . checkFloat($_POST["verbr_water"],5,99.99999,1) . "' where ID = 104") ) $err_cnt += 1;
    if ( updateConfigDb( "update config set parameter = '" . checkFloat($_POST["vastrecht_water"], 5,99.99999,0) . "' where ID = 103") ) $err_cnt += 1;
}




?>
<!doctype html>
<html lang="nl">
<head>
<title>Tarieven configuratie</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css" />
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/jquery.validate.min.js"></script>
<script src="./js/additional-methods.min.js"></script>
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
                <?php menu_control(1);?>
            </div>
            
            <div id="right-wrapper-config"> <!-- right block -->
            <!-- inner block right part of screen -->
                <div id="right-wrapper-config-left">
                    <!-- start of content -->
                    <form name="formvalues" id="formvalues" method="POST">
                    <!--  tarieven E  start-->
                    <div class="frame-4-top">
                        <span class="text-15">tarieven electricteit</span>
                    </div>
                    <div class="frame-4-bot">
                        <div class="float-left pos-32">
                            <div class="frame-3-top">
                                <span class="text-3">verbruik</span>
                            </div>
                        <div class="frame-2-bot pos-11 margin-2"> 
                            <div class="float-left">                
                                <i class="text-8 far fa-sun"></i>
                                <label class="text-8" for="verbr_piek">hoog/piek</label>
                                <p class="p-1"></p>
                                <i class="text-8 far fa-moon"></i>
                                <label class="text-8" for="verbr_dal">laag/dal</label>                         
                            </div>
                            <div class="float-right">
                                <input class="input-1 color-verbr color-input-back" id="verbr_piek" name="verbr_piek" type="text" value="<?php echo config_read(2);?>">        
                                <p class="p-1"></p>
                                <input class="input-1 color-verbr color-input-back" id="verbr_dal"  name="verbr_dal"  type="text" value="<?php echo config_read(1);?>">
                            </div>
                        </div>
                    </div>
                        
                    <div class="float-left pos-32">
                        <div class="frame-3-top">
                            <span class="text-3">geleverd</span>
                        </div>
                        <div class="frame-2-bot pos-11"> 
                            <div class="float-left">                
                                <i class="text-8 far fa-sun"></i>
                                <label class="text-8" for="gelvr_piek">hoog/piek</label>
                                <p class="p-1"></p>
                                <i class="text-8 far fa-moon"></i>
                                <label class="text-8" for="gelvr_dal">laag/dal</label>                         
                            </div>
                            <div class="float-right">
                                <input class="input-1 color-gelvr color-input-back" id="gelvr_piek" name="gelvr_piek" type="text" value="<?php echo config_read(4);?>">        
                                <p class="p-1"></p>
                                <input class="input-1 color-gelvr color-input-back" id="gelvr_dal"  name="gelvr_dal"  type="text" value="<?php echo config_read(3);?>">
                            </div>
                        </div>
                    </div>
            
                    <div class="float-left pos-32">
                        <div class="frame-3-top">
                            <span class="text-3">vastrecht</span>
                        </div>
                        <div class="frame-2-bot pos-11"> 
                            <div class="float-left">                
                                <i class="text-8 fas fa-bolt"></i>
                                <label class="text-8" for="gelvr_piek">per maand</label>    
                            </div>    
                            <div class="float-right">
                                <input class="input-1 color-settings color-input-back" id="e_vastrecht" name="e_vastrecht" type="text" value="<?php echo config_read(5);?>">            
                            </div>
                        </div>
                    </div>        
                </div>
                <!--  tarieven E end -->
        
                <p></p>
                <!--  tarieven gas start-->
                <div class="frame-4-top">
                    <span class="text-15">tarieven gas</span>
                </div>
                <div class="frame-4-bot">
                    <div class="float-left pos-32">
                        <div class="frame-3-top">
                            <span class="text-3">verbruik</span>
                        </div>
                        <div class="frame-2-bot pos-11 margin-2"> 
                            <div class="float-left">                
                                <i class="text-8 fas fa-euro-sign"></i>
                                <label class="text-8" for="verbr_gas">gas m<sup>3</sup></label>
                                <p class="p-1"></p>            
                            </div>
                            <div class="float-right">
                                <input class="input-1 color-verbr-gas-front color-input-back" id="verbr_gas" name="verbr_gas" type="text" value="<?php echo config_read(15);?>">        
                            </div>
                        </div>
                    </div>
                        
                    <div class="float-left pos-32">
                        <div class="frame-3-top">
                            <span class="text-3">vastrecht</span>
                        </div>
                        <div class="frame-2-bot pos-11"> 
                            <div class="float-left">                
                                <i class="text-8 fab fa-gripfire"></i>
                                <label class="text-8" for="vastrecht_gas">per maand</label>    
                            </div>    
                            <div class="float-right">
                                <input class="input-1 color-settings color-input-back" id="vastrecht_gas" name="vastrecht_gas" type="text" value="<?php echo config_read(16);?>">        
                            </div>
                        </div>
                    </div>        
                </div>
                <!--  tarieven gas end -->

                <p></p>
                <!--  tarieven water start-->
                <div class="frame-4-top">
                    <span class="text-15">tarieven water</span>
                </div>
                <div class="frame-4-bot">
                    <div class="float-left pos-32">
                        <div class="frame-3-top">
                            <span class="text-3">verbruik</span>
                        </div>
                        <div class="frame-2-bot pos-11 margin-2"> 
                            <div class="float-left">                
                                <i class="text-8 fas fa-euro-sign"></i>
                                <label class="text-8" for="verbr_gas">water m<sup>3</sup></label>
                                <p class="p-1"></p>            
                            </div>
                            <div class="float-right">
                                <input class="input-1 color-verbr-gas-front color-input-back" id="verbr_water" name="verbr_water" type="text" value="<?php echo config_read( 104 );?>">        
                            </div>
                        </div>
                    </div>
                        
                    <div class="float-left pos-32">
                        <div class="frame-3-top">
                            <span class="text-3">vastrecht</span>
                        </div>
                        <div class="frame-2-bot pos-11"> 
                            <div class="float-left">
                                <i class="text-8 fas fa-tint"></i>
                                <label class="text-8" for="vastrecht_gas">per maand</label>    
                            </div>    
                            <div class="float-right">
                                <input class="input-1 color-settings color-input-back" id="vastrecht_water" name="vastrecht_water" type="text" value="<?php echo config_read( 103 );?>">        
                            </div>
                        </div>
                    </div>        
                </div>
                <!--  tarieven water end -->



                <p></p>
                <!--  kosten start-->
                <div class="frame-4-top">
                    <span class="text-15">kosten</span>
                </div>
                <div class="frame-4-bot">
                    <div class="float-left pos-40">
                        <div class="frame-3-top">
                            <span class="text-3">grens waarde kosten</span>
                        </div>
                        <div class="frame-2-bot pos-11 margin-2"> 
                            <div class="float-left">                
                                <i class="text-8 far fa-check-square"></i>
                                <label class="text-8" for="verbr_gas">euro per maand</label>
                                <p class="p-1"></p>            
                            </div>
                            <div class="float-right">
                                <input class="input-1 color-verbr-gas-front color-input-back" id="max_cost" name="max_cost" type="text" value="<?php echo config_read(39);?>">        
                            </div>
                        </div>
                    </div>
                </div>
                <!--  kosten end -->

                <!-- placeholder variables for session termination -->
                <input type="hidden" name="logout" id="logout" value="">
                </form>
                </div>
                
                <div id="right-wrapper-config-right">
                    <div class="frame-4-top">
                        <span class="text-15">hulp</span>
                    </div>
                    <div class="frame-4-bot text-10">
                        <?php echo strIdx(4);?>
                        <p></p>
                        <?php echo strIdx(28);?>
                    </div>
                </div>
            </div>    
            <!-- end inner block right part of screen -->
    </div>
    <?php echo div_err_succes();?>
    
<script>
$(function() {
    $("#formvalues").validate({
        rules: {
            'verbr_piek': {
                required: true,
                number: true,
                max: 99.99999,
                min: 0
            },
            'verbr_dal': {
                required: true,
                number: true,
                max: 99.99999,
                min: 0
            },
            'gelvr_piek': {
                required: true,
                number: true,
                max: 99.99999,
                min: 0
            },
            'gelvr_dal': {
                required: true,
                number: true,
                max: 99.99999,
                min: 0
            },
            'e_vastrecht': {
                required: true,
                number: true,
                max: 99.99999,
                min: -99.99999
            } ,
            'verbr_gas': {
                required: true,
                number: true,
                max: 99.99999,
                min: 0
            },
            'vastrecht_gas': {
                required: true,
                number: true,
                max: 99.99999,
                min: -99.99999
            },
            'verbr_water': {
                required: true,
                number: true,
                max: 99.99999,
                min: 0
            },
            'vastrecht_water': {
                required: true,
                number: true,
                max: 99.99999,
                min: -99.99999
            },
            'max_cost': {
                required: true,
                number: true,
                max: 9999.99999,
                min: 0
            }
        },
        invalidHandler: function(e, validator) { 
            var errors = validator.numberOfInvalids(); 
            if (errors) {       
                showStuff('err_msg');
                  setTimeout( function() { hideStuff('err_msg');},5000);
             } 
          },
        errorPlacement: function(error, element) {
            $(this).addClass('error');
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
