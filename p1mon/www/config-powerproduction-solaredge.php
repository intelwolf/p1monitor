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
include_once '/p1mon/www/util/config_page_menu_header_powerproduction.php';

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

$sw_off   = strIdx( 193 );
$sw_on    = strIdx( 192 );

$err_cnt  = -1;
$err_str  = '';
$key_seed = 'solaredgeapikey';

// SET API KEY
if ( isset($_POST["SE_API_key"]) ) { 
    #echo "<br>processing</br>\n";

        if ( $err_cnt == -1 ) $err_cnt=0;

        $input = preg_replace( '/[\x00-\x1F\x7F]/u', '', $_POST["SE_API_key"] );
        $crypto_api_key = encodeString ( $input, $key_seed );
       
        if ( updateConfigDb("update config set parameter = '".$crypto_api_key."' where ID = 139")) $err_cnt += 1;
        if ( updateConfigDb("update config set parameter = '1' where ID = 144")) $err_cnt += 1;

        // remove on 2021-06-01 so the API key kan be erased.
        //if ( strlen(trim($_POST["SE_API_key"])) == 0 ) { # to prevent error on a empty input
        //header('Location: '.$_SERVER['PHP_SELF']);
        //die;
        //}
}

// SAVE THE SITE DATA STRUCTURE, LIKE SITE ID's, ACTIVE, DELETE, etc. 
if ( isset($_POST["solar_edge_config"]) ) { 
    if ( strlen( trim( $_POST["solar_edge_config"]) ) > 30) {
        if ( updateConfigDb("update config set parameter = '" .$_POST["solar_edge_config"]. "' where ID = 140") ) $err_cnt += 1;
    }
}

if ( isset($_POST[ "fs_rb_solaredge_active" ]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ "fs_rb_solaredge_active" ] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 141") ) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 141") ) $err_cnt += 1;
    }
}

if ( isset($_POST[ "fs_rb_solaredge_reload" ]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ "fs_rb_solaredge_reload" ] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 142") ) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 142") ) $err_cnt += 1;
    }
}

if ( isset($_POST[ "fs_rb_solaredge_reconfig" ]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ "fs_rb_solaredge_reconfig" ] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 145") ) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 145") ) $err_cnt += 1;
    }
}

if ( isset($_POST[ "fs_rb_smart_api" ]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ "fs_rb_smart_api" ] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 146") ) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 146") ) $err_cnt += 1;
    }
}

if ( isset($_POST[ "tariff" ]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( strlen( trim( $_POST["tariff"]) ) < 2 ) {
        if ( updateConfigDb("update config set parameter = '" .$_POST["tariff"]. "' where ID = 143") ) $err_cnt += 1;
    }
}


if ( isset($_POST[ "fs_rb_solaredge_factory" ]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ "fs_rb_solaredge_factory" ] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 149") ) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 149") ) $err_cnt += 1;
    }
}


function selectorTariffMode( $mode ) {
    $s0=$s1=$s2=0;

    switch ( $mode ) {
        case 0: 
            $s0= 'selected=\"selected\"';
            break;
        case 1: 
            $s1= 'selected=\"selected\"';
            break;
        case 2: 
            $s2= 'selected=\"selected\"';
            break;
    }

    echo '<option '. $s0 . ' value=0>'.strIdx( 165 );
    echo '<option '. $s1 . ' value=1>'.strIdx( 166 );
    echo '<option '. $s2 . ' value=2>'.strIdx( 167 );
}

?>
<!doctype html>
<html lang="nl">
<head>
<meta name="robots" content="noindex">
<title>Solar Edge API configuratie</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css" />
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>
<link type="text/css" rel="stylesheet" href="./css/p1mon-tabulator.css" >
<link type="text/css" rel="stylesheet" href="./css/p1mon-tabulator-alt-2.css" >

<script defer src="./font/awsome/js/all.js"></script>
<script       src="./js/jquery.min.js"></script>
<script       src="./js/p1mon-util.js"></script>
<script       src="./js/tabulator-dist/js/tabulator.min.js"></script>
</head>
<body>
<script>
var initloadtimer;

var site_id    = '<?php echo strIdx( 168 );?>'
var db_index   = '<?php echo strIdx( 169 );?>'
var start_date = '<?php echo strIdx( 170 );?>'
var end_date   = '<?php echo strIdx( 171 );?>'
var active     = '<?php echo strIdx( 172 );?>'
var erease     = '<?php echo strIdx( 173 );?>'

// this var signals if the update of the config is allowed.
// this to prevent that when changing values that the user
// input is lost. After a post the update will be reset
// only used for the solar config of the id's'active, delete status
var readConfigIsActive = true;

function readJsonApiConfig( id ){ 
    $.getScript( "/api/v1/configuration/" + id, function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        //console.log( jsondata[0][1] ) // index 1 is the payload. 
        //return jsondata[0][1];
        site_list_table.replaceData( jsondata[0][1] )
      } catch(err) {}
   });
}

function readJsonApiStatus(){ 
    $.getScript( "./api/v1/status", function( data, textStatus, jqxhr ) {
      try {
        var jsonarr = JSON.parse(data); 
        for (var j=0;  j<jsonarr.length; j++){   
                switch(jsonarr[j][0]) {
                    case 111:
                        $('#api_succes_timestamp').text( jsonarr[j][1] );
                        break;
                    case 112:
                        $('#api_failed_timestamp').text( jsonarr[j][1] );
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

    if ( readConfigIsActive ) {
        readJsonApiConfig( 140 ); 
    }
    readJsonApiStatus();
    initloadtimer = setInterval(function(){ LoadData();}, 1000 );
}

$(function () {

    toLocalStorage('config-powerproduction-menu',window.location.pathname);

    // ###################################
    // Build Tabulator list of log files #
    // ###################################
    site_list_table = new Tabulator("#siteid-list-table", {
        maxHeight:"100%",
        layout:"fitColumns",
        tooltips:true,
        tooltipGenerationMode:"hover",
        placeholder:"geen site id's gevonden.",
        clipboard:true,
        columns:[
            {title:site_id,    field:"ID",         width:104, sorter:"number",},
            {title:db_index,   field:"DB_INDEX",   width:98 },
            {title:start_date, field:"START_DATE", width:107, sorter:"string" },
            {title:end_date,   field:"END_DATE",   width:107, sorter:"string" },
            {title:active,   
                field:"SITE_ACTIVE", 
                width:79,
                tooltip: "<?php echo strIdx(101);?>" ,
                formatter:"tickCross", 
                formatterParams:{
                    allowEmpty:true,
                    allowTruthy:true,
                    crossElement:"<i class='far fa-pause-circle color-warning'></i>",
                    tickElement:"<i class='fas fa-check-square color-menu'></i>",
                },
                hozAlign:"center",
                cellClick:function(e, cell) { setDbAttributeActive( cell.getRow().getData().ID, cell, 'SITE_ACTIVE' ) } 
            },
            {title: erease,
                field:"DB_DELETE", 
                tooltip: "<?php echo strIdx(102);?>" ,
                formatter:"tickCross",
                formatterParams:{
                    allowEmpty:true,
                    allowTruthy:true,
                    crossElement:"<i class='far fas fa-database color-menu'></i>",
                    tickElement:"<i class='fas  fa-trash-alt color-warning'></i>",
                },
                hozAlign: "center", 
                cellClick:function(e, cell) { setDbAttributeActive( cell.getRow().getData().ID, cell, 'DB_DELETE' ) } 
            },
        ],
        /*
        dataLoaded:function( data ){
            logfiles_list_inital_data_loaded = true; // used to prevent pesky error message when intial load is not finshed
        },
        rowClick:function( e, row ){
            //console.log ( row.getData().filename );
            //selected_logfile = row.getData().filename 
            //loadLogFileContent( selected_logfile );
        },
        rowTap:function(e, row){   // Ipad and sutch 
            //selected_logfile = row.getData().filename 
            //loadLogFileContent( selected_logfile );
        },
        */
    });

    LoadData();
    setTimeout( function() { hideStuff('busy_indicator');},9000);

});

function setDbAttributeActive( site_id, cell , attr ) {

    readConfigIsActive = false; // stop auto update when editing, see above.

    //console.log( "active row data for: " + site_id + " status = " + cell.getValue() );
    var data = site_list_table.getData();
    var i;
    for (i = 0; i < data.length; i++) {
        if ( data[i]['ID'] === site_id ) {
            data[i][ attr ] = !cell.getValue();
            site_list_table.replaceData( data );
            document.getElementById( "solar_edge_config").setAttribute( 'value', JSON.stringify( data ) );
            return
        }

    }
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
                                <?php menu_control( 15 );?>
                        </div>
                        
                        <div id="right-wrapper-config"> <!-- right block -->
                            <!-- inner block right part of screen -->
                            <?php config_page_menu_header_powerproduction( 1 ); ?> 
                            <div id="right-wrapper-config-left">
                                <!-- start of content -->
                                <form name="formvalues" id="formvalues" method="POST">
                                            
                                    <div class="frame-4-top"> <!--TODO spinner activeren. -->
                                            <span class="text-15"><?php echo strIdx( 158 );?></span><span id="busy_indicator" class="display-nonex" >&nbsp;&nbsp;&nbsp;<i class="fas fa-spinner fa-pulse fa-1x fa-fw"></i></span>
                                    </div>
                                    <div class="frame-4-bot">
                                            <div title="<?php echo strIdx( 149 );?>" class="float-left">
                                                    <i class="text-10 pad-7 fas fa-key"></i>
                                                    <label class="text-10">api key</label>
                                                    <p class="p-1"></p>
                                            </div>

                                            <div title="<?php echo strIdx( 149 );?>" class="float-left pad-1">    
                                                    <input class="input-10 color-settings color-input-back" id="SE_API_key" name="SE_API_key" type="password" value="<?php echo decodeString(139, $key_seed);?>">
                                                    <p class="p-1"></p>   
                                            </div>
                                            <div id="api_passwd" onclick="toggelPasswordVisibility('SE_API_key')" class="float-left pad-1 cursor-pointer">        
                                                    <span><i class="color-menu pad-7 fas fa-eye"></i></span>
                                            </div>
                                            <p></p>

                                            <div class="rTable">
                                                <div class="rTableRow" title="<?php echo strIdx( 150 );?>">
                                                    <div class="rTableCell width-290">
                                                        <i class="pad-7 text-10 fas fa-toggle-off"></i>
                                                        <label class="text-10"><?php echo strIdx( 160 );?></label>
                                                    </div>
                                                    <div class="rTableCell">
                                                        <input class="cursor-pointer" id="fs_rb_solaredge_active_on"  name="fs_rb_solaredge_active" type="radio" value="1" <?php if ( config_read( 141 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                                        <input class="cursor-pointer" id="fs_rb_solaredge_active_off" name="fs_rb_solaredge_active" type="radio" value="0" <?php if ( config_read( 141 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                                    </div>
                                                </div>
                                                <div class="rTableRow" title="<?php echo strIdx( 151 );?>">
                                                    <div class="rTableCell">
                                                        <i class="pad-7 text-10 fas fa-toggle-off"></i>
                                                        <label class="text-10"><?php echo strIdx( 161 );?></label>
                                                    </div>
                                                    <div class="rTableCell">
                                                        <input class="cursor-pointer" id="fs_rb_solaredge_smart_api_on"  name="fs_rb_smart_api" type="radio" value="1" <?php if ( config_read( 146 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                                        <input class="cursor-pointer" id="fs_rb_solaredge_smart_api_off" name="fs_rb_smart_api" type="radio" value="0" <?php if ( config_read( 146 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                                    </div>
                                                </div>
                                                <div class="rTableRow" title="<?php echo strIdx( 152 );?>">
                                                    <div class="rTableCell">
                                                        <i class="pad-7 text-10 fas fa-toggle-off"></i>
                                                        <label class="text-10"><?php echo strIdx( 162 );?></label>
                                                    </div>
                                                    <div class="rTableCell">
                                                        <input class="cursor-pointer" id="fs_rb_solaredge_reload_on"  name="fs_rb_solaredge_reload" type="radio" value="1" ><?php echo $sw_on ?>
                                                        <input class="cursor-pointer" id="fs_rb_solaredge_reload_off" name="fs_rb_solaredge_reload" type="radio" value="0" checked ><?php echo $sw_off ?>
                                                    </div>
                                                </div>
                                                <div class="rTableRow" title="<?php echo strIdx( 153 );?>">
                                                    <div class="rTableCell">
                                                        <i class="pad-7 text-10 fas fa-toggle-off"></i>
                                                        <label class="text-10"><?php echo strIdx( 163 );?></label>
                                                    </div>
                                                    <div class="rTableCell">
                                                        <input class="cursor-pointer" id="fs_rb_solaredge_reconfig_on"  name="fs_rb_solaredge_reconfig" type="radio" value="1" ><?php echo $sw_on ?>
                                                        <input class="cursor-pointer" id="fs_rb_solaredge_reconfig_off" name="fs_rb_solaredge_reconfig" type="radio" value="0" checked><?php echo $sw_off ?>
                                                    </div>
                                                </div>

                                                <div class="rTableRow" title="<?php echo strIdx( 224 );?>">
                                                    <div class="rTableCell">
                                                        <i class="pad-7 text-10 fas fa-toggle-off"></i>
                                                        <label class="text-10"><?php echo strIdx( 223 );?></label>
                                                    </div>
                                                    <div class="rTableCell">
                                                        <input class="cursor-pointer" id="fs_rb_solaredge_factory_on"  name="fs_rb_solaredge_factory" type="radio" value="1" ><?php echo $sw_on ?>
                                                        <input class="cursor-pointer" id="fs_rb_solaredge_factory_off" name="fs_rb_solaredge_factory" type="radio" value="0" checked><?php echo $sw_off ?>
                                                    </div>
                                                </div>
                                                
                                                <div class="rTableRow" title="<?php echo strIdx( 154 );?>">
                                                    <div class="rTableCell">
                                                    <span class="fa-layers fa-gw">
                                                        <i class="text-10 fas fa-euro-sign" data-fa-transform="shrink-2 left-5"></i>
                                                        <i class="text-10 fas fa-bolt"      data-fa-transform="shrink-2 right-5"></i>
                                                    </span>
                                                        <label class="text-10"><?php echo strIdx( 164 );?></label>
                                                    </div>
                                                    <div class="rTableCell">
                                                        <select name="tariff" id="tariff" class="select-7 color-menu color-input-back cursor-pointer">
                                                            <?php 
                                                            $mode = config_read( 143 );
                                                            selectorTariffMode( $mode );
                                                            ?>
                                                        </select>
                                                    </div>
                                                </div>

                                                <!-- onchange="selectorUpdate('#tariff','#i_tariff')" -->
                                            </div>
                                            <p></p>

                                            <div class='pad-12'>
                                                <div id="siteid-list-table"></div>
                                            </div>
                                            <p></p>

                                    </div>
                                    <p></p>
                                    <div class="frame-4-top">
                                            <span class="text-15"><?php echo strIdx( 159 );?></span>
                                    </div>
                                    <div class="frame-4-bot">
                                    <div class="rTable">
                                        <div class="rTableRow">
                                            <div class="rTableCell width-290">
                                                <i class="pad-7 text-10 far fa-clock"></i>
                                                <label class="text-10"><?php echo strIdx( 157 );?></label>
                                            </div>
                                            <div id="api_succes_timestamp" class="rTableCell text-10">
                                                ??-??-?? ??:??:??
                                            </div>
                                        </div>
                                    </div>
                                       
                                    <div class="rTable">
                                        <div class="rTableRow">
                                            <div class="rTableCell width-290">
                                                <i class="pad-7 text-10 far fa-clock"></i>
                                                <label class="text-10"><?php echo strIdx( 156 );?></label>
                                            </div>
                                            <div id="api_failed_timestamp" class="rTableCell text-10">
                                                ??-??-?? ??:??:??
                                            </div>
                                        </div>
                                    </div>
                                    <p></p>   

                                    </div>
                                    <!-- placeholder variables for session termination -->
                                    <input type="hidden" name="logout" id="logout" value="">
                                    <input type="hidden" name="solar_edge_config" id="solar_edge_config" value="">
                                </form>
                            </div>
                            
                            <div id="right-wrapper-config-right">
                                    <div class="frame-4-top">
                                            <span class="text-15"><?php echo strIdx( 155 );?></span>
                                    </div>
                                    <div class="frame-4-bot text-10">
                                            <img alt="PI GPIO pin layout" src="./img/SolarEdge_logo_header_new_0.svg" align="left" width="170">
                                            <p><br></p>
                                            <?php echo strIdx( 148 );?>

                                    </div>
                                    
                            </div>
                    </div>        
                        <!-- end inner block right part of screen -->
        </div>        
        <?php echo div_err_succes();?>
        
        <?php 
        //echo "check ".$err_str.'<br>';
        if ($err_cnt > 0) {        
echo <<< "END"
<script>
        $(function () {
                $('#err_msg_text').html("$err_str");
        });
</script>
END;
        }
        # nu alleen bij de save van de api key
        #updateConfigDb("update config set parameter = '1' where ID = 144"); // trigger the Watchdog to do an P1SolarEdgeSetup.py --savesites, this reloads the sites for the API key
        ?>
<?php echo autoLogout(); ?>
</body>
</html>