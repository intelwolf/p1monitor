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

function makeTariffProvider($id) {
    $configValue = config_read($id);
    $val_0=$val_1='';

    if ($configValue == '0'  ) { $val_0  = 'selected="selected"'; } 
    if ($configValue == '1'  ) { $val_1  = 'selected="selected"'; }

    echo '<option ' . $val_0  . ' value="0"  >vaste tarieven</option>';
    echo '<option ' . $val_1  . ' value="1"  >energyzero</option>';
}

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
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["verbr_piek"],5,999.99999,1)."' where ID = 2")) $err_cnt += 1;
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["verbr_dal"], 5,999.99999,1)."' where ID = 1")) $err_cnt += 1;
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["gelvr_piek"],5,999.99999,1)."' where ID = 4")) $err_cnt += 1;
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["gelvr_dal"], 5,999.99999,1)."' where ID = 3")) $err_cnt += 1;
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["e_vastrecht"], 5,999.99999,0)."' where ID = 5")) $err_cnt += 1;
}

// tarieven GAS aanpassen
if( isset($_POST["verbr_gas"]) || isset($_POST["vastrecht_gas"]))
{
    if ( $err_cnt < 0 ) { $err_cnt=0; }
    // update database
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["verbr_gas"],5,999.99999,1)."' where ID = 15")) $err_cnt += 1;
    if ( updateConfigDb("update config set parameter = '".checkFloat($_POST["vastrecht_gas"], 5,999.99999,0)."' where ID = 16")) $err_cnt += 1;
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
    if ( updateConfigDb( "update config set parameter = '" . checkFloat($_POST["verbr_water"],5,999.99999,1) . "' where ID = 104") ) $err_cnt += 1;
    if ( updateConfigDb( "update config set parameter = '" . checkFloat($_POST["vastrecht_water"], 5,999.99999,0) . "' where ID = 103") ) $err_cnt += 1;
}

if( isset($_POST["inkoop_kwh_kosten"]))
{
    if ( $err_cnt < 0 ) { $err_cnt=0; }
    // update database
    if ( updateConfigDb( "update config set parameter = '" . checkFloat($_POST["inkoop_kwh_kosten"],5,999.99999,0) . "' where ID = 205") ) $err_cnt += 1;
}

if( isset($_POST["inkoop_gas_kosten"]))
{
    if ( $err_cnt < 0 ) { $err_cnt=0; }
    // update database
    if ( updateConfigDb( "update config set parameter = '" . checkFloat($_POST["inkoop_gas_kosten"],5,999.99999,0) . "' where ID = 208") ) $err_cnt += 1;
}

if( isset($_POST["tariff_provider"]))
{
    if ( $err_cnt < 0 ) { $err_cnt=0; }
    // update database
    if ( updateConfigDb( "update config set parameter = '" . preg_replace('/\D/', '', $_POST["tariff_provider"]) . "' where ID = 204") ) $err_cnt += 1;

    $command = "/p1mon/scripts/P1DynamicPrices -g &";
    exec( $command ,$arr_execoutput, $exec_ret_value );
}

?>
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title><?php echo ucfirst(strIdx( 617 ))?></title>
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
                        <span class="text-15"><?php echo strIdx( 618 )?></span>
                    </div>
                    <div class="frame-4-bot">
                        <div class="frame-3-top">
                            <span class="text-3"><?php echo strIdx( 354 )?></span>
                        </div>
                        <div class="frame-2-bot pos-11"> 
                            <div class="rTable">
                                <div class="rTableRow">
                                    <div class="rTableCell width-120">
                                    <i class="text-8 far fa-sun"></i>
                                        <label class="text-8" for="verbr_piek"><?php echo strIdx( 626 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="input-1 color-verbr color-input-back" id="verbr_piek" name="verbr_piek" type="text" value="<?php echo config_read(2);?>">
                                    </div>
                                </div>

                                <div class="rTableRow">
                                    <div class="rTableCell width-120">
                                        <i class="text-8 far fa-moon"></i>
                                        <label class="text-8" for="verbr_dal"><?php echo strIdx( 627 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="input-1 color-verbr color-input-back" id="verbr_dal"  name="verbr_dal"  type="text" value="<?php echo config_read(1);?>">
                                    </div>
                                </div>
                            </div> 
                        </div>
                        <p></p>

                        <div class="frame-3-top">
                            <span class="text-3"><?php echo strIdx( 360 )?></span>
                        </div>
                        <div class="frame-2-bot pos-11"> 
                            <div class="rTable">
                                <div class="rTableRow">
                                    <div class="rTableCell width-120">
                                    <i class="text-8 far fa-sun"></i>
                                        <label class="text-8" for="verbr_piek"><?php echo strIdx( 626 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="input-1 color-gelvr color-input-back" id="gelvr_piek" name="gelvr_piek" type="text" value="<?php echo config_read(4);?>">
                                    </div>
                                </div>

                                <div class="rTableRow">
                                    <div class="rTableCell width-120">
                                        <i class="text-8 far fa-moon"></i>
                                        <label class="text-8" for="verbr_dal"><?php echo strIdx( 627 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="input-1 color-gelvr color-input-back" id="gelvr_dal"  name="gelvr_dal"  type="text" value="<?php echo config_read(3);?>">
                                    </div>
                                </div>
                            </div> 

                        </div>
                        <p></p>


                        <div class="frame-3-top">
                            <span class="text-3"><?php echo strIdx( 623 )?></span>
                        </div>
                        <div class="frame-2-bot pos-11"> 
                            <div class="rTable">
                                <div class="rTableRow">
                                    <div class="rTableCell width-120">
                                        <i class="text-8 fas fa-bolt"></i>
                                        <label class="text-8" for="gelvr_piek"><?php echo strIdx( 628 )?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="input-1 color-settings color-input-back" id="e_vastrecht" name="e_vastrecht" type="text" value="<?php echo config_read(5);?>">
                                    </div>
                                </div>
                            </div> 
                        </div>
                        <p></p>
                </div>
                <!--  tarieven E end -->
        
                <p></p>
                <!--  tarieven gas start-->
                <div class="frame-4-top">
                    <span class="text-15"><?php echo strIdx( 619 )?></span>
                </div>
                <div class="frame-4-bot">
                    <div class="float-left pos-32">
                        <div class="frame-3-top">
                            <span class="text-3"><?php echo strIdx( 354 )?></span>
                        </div>
                        <div class="frame-2-bot pos-11 margin-2"> 
                            <div class="float-left">
                                <i class="text-8 fas fa-euro-sign"></i>
                                <label class="text-8" for="verbr_gas"><?php echo strIdx( 336 )?> m<sup>3</sup></label>
                                <p class="p-1"></p>
                            </div>
                            <div class="float-right">
                                <input class="input-1 color-verbr-gas-front color-input-back" id="verbr_gas" name="verbr_gas" type="text" value="<?php echo config_read(15);?>">
                            </div>
                        </div>
                    </div>
                        
                    <div class="float-left pos-32">
                        <div class="frame-3-top">
                            <span class="text-3"><?php echo strIdx( 623 )?></span>
                        </div>
                        <div class="frame-2-bot pos-11"> 
                            <div class="float-left">
                                <i class="text-8 fab fa-gripfire"></i>
                                <label class="text-8" for="vastrecht_gas"><?php echo strIdx( 628 )?></label>
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
                    <span class="text-15"><?php echo strIdx( 620 )?></span>
                </div>
                <div class="frame-4-bot">
                    <div class="float-left pos-32">
                        <div class="frame-3-top">
                            <span class="text-3"><?php echo strIdx( 354 )?></span>
                        </div>
                        <div class="frame-2-bot pos-11 margin-2"> 
                            <div class="float-left">
                                <i class="text-8 fas fa-euro-sign"></i>
                                <label class="text-8" for="verbr_gas"><?php echo strIdx( 629 )?> m<sup>3</sup></label>
                                <p class="p-1"></p> 
                            </div>
                            <div class="float-right">
                                <input class="input-1 color-verbr-gas-front color-input-back" id="verbr_water" name="verbr_water" type="text" value="<?php echo config_read( 104 );?>">
                            </div>
                        </div>
                    </div>
                        
                    <div class="float-left pos-32">
                        <div class="frame-3-top">
                            <span class="text-3"><?php echo strIdx( 623 )?></span>
                        </div>
                        <div class="frame-2-bot pos-11"> 
                            <div class="float-left">
                                <i class="text-8 fas fa-tint"></i>
                                <label class="text-8" for="vastrecht_gas"><?php echo strIdx( 628 )?></label>
                            </div>    
                            <div class="float-right">
                                <input class="input-1 color-settings color-input-back" id="vastrecht_water" name="vastrecht_water" type="text" value="<?php echo config_read( 103 );?>">
                            </div>
                        </div>
                    </div>        
                </div>
                <p></p>
                <!--  tarieven water end -->

                <!--  flexibele tarieven start -->
                <div class="frame-4-top">
                    <span class="text-15"><?php echo strIdx( 621 )?></span>
                </div>
                <div class="frame-4-bot">
                    <div class="float-left">
                       
                        <div class="frame-3-top">
                            <span class="text-3"><?php echo strIdx( 624 )?></span>
                        </div>
                        <div class="frame-2-bot pos-11"> 
                            <div class="rTable"> 
                                <div class="rTableRow">
                                    <div class="rTableCell width-120">
                                        <i class="text-8 fas fa-euro-sign"></i>
                                        <label class="text-10"><?php echo strIdx( 631 )?></label>
                                    </div>
                                    <div class="rTableCell pad-12">
                                        <input class="input-17 color-settings color-input-back" id="inkoop_kwh_kosten" name="inkoop_kwh_kosten" type="text" value="<?php echo config_read( 205 );?>">
                                    </div>
                                </div>
                            </div> 
                        </div>
                        <p></p>

                        <div class="frame-3-top">
                            <span class="text-3"><?php echo strIdx( 625 )?></span>
                        </div>
                        <div class="frame-2-bot pos-11"> 
                            <div class="rTable"> 
                                <div class="rTableRow">
                                    <div class="rTableCell width-120">
                                        <i class="text-8 fas fa-euro-sign"></i>
                                        <label class="text-10"><?php echo strIdx( 631 )?></label>
                                    </div>
                                    <div class="rTableCell pad-12">
                                        <input class="input-17 color-settings color-input-back" id="inkoop_gas_kosten" name="inkoop_gas_kosten" type="text" value="<?php echo config_read( 208 );?>">
                                    </div>
                                </div>
                            </div> 
                        </div>
                        <p></p>

                        <div class="frame-3-top">
                            <span class="text-3"><?php echo strIdx( 630 )?></span>
                        </div>
                        <div class="frame-2-bot pos-11"> 

                        <div class="rTable"> 
                            <div class="rTableRow" title="">
                                <div class="rTableCell">
                                    <label class="text-10"><?php echo strIdx( 632 )?></label>
                                </div>
                                <div class="rTableCell pad-12">
                                <select class="select-4 color-select color-input-back cursor-pointer" name="tariff_provider">
                                    <?php makeTariffProvider(204);?>
                                </select>
                                </div>
                            </div>
                        </div>
                    </div>
                    <p></p>
                </div>
                

                
                </div>
                <p></p>
            
                <!--  flexibele tarieven end -->

                <p></p>
                <!--  kosten start-->
                <div class="frame-4-top">
                    <span class="text-15"><?php echo strIdx( 622 )?></span>
                </div>
                <div class="frame-4-bot">
                    <div class="float-left pos-40">

                    <div class="frame-3-top">
                        <span class="text-3"><?php echo strIdx( 652 )?></span>
                    </div>
                    <div class="frame-2-bot pos-11"> 
                        <div class="rTable"> 
                            <div class="rTableRow" title="">
                                <div class="rTableCell">
                                    <i class="text-8 far fa-check-square"></i>
                                    <label class="text-8" for="verbr_gas"><?php echo strIdx( 505 )?></label>
                                </div>
                                <div class="rTableCell pad-12">
                                    <input class="input-1 color-verbr-gas-front color-input-back" id="max_cost" name="max_cost" type="text" value="<?php echo config_read(39);?>">
                                </div>
                            </div>
                        </div>
                    </div>
                    <p></p>
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
            'inkoop_kwh_kosten': {
                required: true,
                number: true,
                max: 999.99999,
                min: -999.99999
            },
            'belasting_kwh_kosten': {
                required: true,
                number: true,
                max: 999.99999,
                min: -999.99999
            },
            'ODE_kwh_kosten': {
                required: true,
                number: true,
                max: 999.99999,
                min: -999.99999
            },
            'inkoop_gas_kosten': {
                required: true,
                number: true,
                max: 999.99999,
                min: -999.99999
            },
            'belasting_gas_kosten': {
                required: true,
                number: true,
                max: 999.99999,
                min: -999.99999
            },
            'ODE_gas_kosten': {
                required: true,
                number: true,
                max: 999.99999,
                min: -999.99999
            },
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
                max: 999.99999,
                min: -999.99999
            },
            'verbr_gas': {
                required: true,
                number: true,
                max: 99.99999,
                min: 0
            },
            'vastrecht_gas': {
                required: true,
                number: true,
                max: 999.99999,
                min: -999.99999
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
                max: 999.99999,
                min: -999.99999
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
