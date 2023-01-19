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

$sw_off          = strIdx( 193 );
$sw_on           = strIdx( 192 );
$err_cnt         = -1;
$api_crypto_seed = '20210731apikey';

if ( isset($_POST[ "cert_email" ]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    $input = inputClean( trim($_POST[ "cert_email" ]) );
    if ( updateConfigDb("update config set parameter = '" . $input . "' where ID = 159") ) $err_cnt += 1;
}

if ( isset($_POST[ "tokenupdate" ]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( $_POST[ "tokenupdate"  ] != '' ) {
        $input = preg_replace('/[\x00-\x1F\x7F]/u', '',$_POST["tokenupdate"]);
        $crypto_api_data = encodeString ($input, $api_crypto_seed);
        if ( updateConfigDb( "update config set parameter = '" . $crypto_api_data . "' where ID = 160") ) $err_cnt += 1;
        if ( $err_cnt == 0 ) { // onnly do updates when there are no errors
            if ( updateConfigDb( "update config set parameter = '1' where ID = 161") ) $err_cnt += 1;
        }
    }
}

if ( isset($_POST[ "fs_inet_api_active" ]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;

    # only write the toggle flag when the radio button is changed.
    if ( intval( config_read( 163 )) !== intval( $_POST[ "fs_inet_api_active" ] ) ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 162") ) $err_cnt += 1; // Watchdog toggle flag
    }

    if ( $_POST[ "fs_inet_api_active" ] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 163") ) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 163") ) $err_cnt += 1;
    }
}

?>
<!doctype html>
<html lang='NL'>
<head>
<meta name="robots" content="noindex">
<title><?php echo strIdx( 259 );?></title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css" />
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>
<link type="text/css" rel="stylesheet" href="./css/p1mon-tabulator.css" >
<link type="text/css" rel="stylesheet" href="./css/p1mon-tabulator-alt-2.css" >

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/p1mon-util.js"></script>
<script src="./js/tabulator-dist/js/tabulator.min.js"></script>
<script src="./js/qrious-link/qrious.min.js"></script>

</head>
<body>
<script>
var initloadtimer
var api_keys_data = '<?php echo decodeString(160, $api_crypto_seed);?>';

var erease     = '<?php echo strIdx( 173 );?>';
var token      = 'API token';
var timestamp  = 'Timestamp';
var sec_id     = '<?php echo decodeStringNoBase64( 58,"sysid" );?>'

    function readJsonStatus(){ 
        $.getScript( "./api/v1/status", function( data, textStatus, jqxhr ) {
        try {
            var jsonarr = JSON.parse(data); 
            for (var j=0;  j<jsonarr.length; j++){   
                    switch(jsonarr[j][0]) {
                        case 117:
                            setIconClasses( "http_status",  jsonarr[j][1] )
                            break;
                        case 118:
                            setIconClasses( "cert_renew",  jsonarr[j][1] )
                            break; 
                        case 119:
                            setIconClasses( "web_config",  jsonarr[j][1] )
                            break;
                        case 120:
                            document.getElementById("renewtime").innerHTML = jsonarr[j][1]
                            break;
                        case 121:
                            document.getElementById("validtime").innerHTML = jsonarr[j][1]
                            break;
                }
            }
        } catch(err) {
            console.log( err );
        }
    });
    }

    function setIconClasses( itemName,  status ) {

        item = document.getElementById( itemName );
        item.classList.remove('fa-question-circle')
        item.classList.remove('fa-circle-check')
        item.classList.remove('fa-exclamation-triangle')
        item.classList.add('fas');

        //console.log(item.classList )
        if ( status == 0 ) {
            item.classList.add('color-ok');
            item.classList.add('fa-circle-check');
        } else if ( status == 1 ) {
                item.classList.add('color-error');
                item.classList.add('fa-exclamation-triangle')
        } else {
            item.classList.add('color-text');
            item.classList.add('fa-question-circle');
        }

    }

    function readJsonApiList(){ 
        $.getScript( "./api/v1/catalog", function( data, textStatus, jqxhr ) {
        try {
            htmlString = "<ol type='1'>";
            var jsondata = JSON.parse(data); 
            for (var j =0;  j<jsondata.length; j++){    
                splitBuf = jsondata[j].split('/');            // get rid of IP adres for url
                url = jsondata[j].replace(splitBuf[0],'.');   // get rid of IP adres for url
                htmlString = htmlString + "<li><a href='" + url + "' target='_blank'>" + jsondata[j] + "</a></li>";
            }
            htmlString = htmlString + "</ol>";
            $('#apiList').append( htmlString );
          } catch(err) {}
       });
    }

    function LoadData() {
        clearTimeout(initloadtimer);
        readJsonStatus();
        
        initloadtimer = setInterval(function(){LoadData();}, 5000);
    }

    $(function () {

        centerPosition('#qrcode');

        // ###################################
        // create random seed                #
        // ###################################
        seed = parseInt( sec_id.replace(/-/g,'').substr( 0,6 ), 16);

        // ####################################################
        // Build Tabulator list for API authentication tokens #
        // ####################################################
        api_token_table = new Tabulator("#api-token-table", {
            maxHeight:"100%",
            layout:"fitColumns",
            tooltips:true,
            tooltipGenerationMode:"hover",
            placeholder:"API tokens, gebruik plus om toe te voegen.",
            clipboard:true,
            columns:[
                {title:token,     field:"TOKEN",     sorter:"string",  width:210},
                {title:timestamp, field:"TIMESTAMP", sorter:"string",  width:178 },
                {title: erease,
                    field:"DELETE",
                    tooltip: "<?php echo strIdx( 258 );?>" ,
                    formatter:"tickCross",
                    formatterParams:{
                        crossElement:"<i class='far fas fa-trash-alt color-menu'></i>",
                    },
                    hozAlign: "center",
                    width:90,
                    cellClick:function(e, cell) { 
                        deleteRow( cell )
                    },
                    headerSort:false 
                },
                {title: "QR",
                    field:"QRCODE",
                    tooltip: "<?php echo strIdx( 284 );?>",
                    formatter:"tickCross",
                    formatterParams:{
                        crossElement:"<i class='far fas fa-qrcode color-menu'></i>",  
                    },
                    hozAlign: "center",
                    width:50,
                    cellClick:function(e, cell) { 
                        showQRcode( cell );
                    },
                    headerSort:false 
                },
            ],
            resizableColumns:false,
            initialSort:[
                { column:"TIMESTAMP", dir:"desc"}, 
            ]
        });


        document.getElementById("add_token_button").addEventListener("click", function(){
            
            event.preventDefault();

            api_token_table.updateOrAddData([ {TOKEN: getRandomHex( 20, seed ), TIMESTAMP:getTimestamp() }] );
            document.formvalues.tokenupdate.value = JSON.stringify( api_token_table.getData() );
            api_token_table.setSort("TIMESTAMP", "desc");

            if ( api_token_table.getDataCount() > 25 ) {
                alert('<?php echo strIdx( 264 );?>');
            }
        });

        readJsonApiList();
        LoadData();
        api_token_table.replaceData( api_keys_data )

        FQDN = '<?php echo config_read( 150 );?>';
        if ( FQDN.length < 3 ) {
            FQDN = '<?php echo strIdx( 269 );?>'
            document.getElementById( "FQDN" ).innerHTML = '<span style = "color: red">' + FQDN + '</span>';
        } else {
            document.getElementById( "FQDN" ).innerHTML = FQDN;
        }

    // end of init
    });


    function deleteRow( cell ) {
        api_token_table.deleteRow( cell.getRow() )
        document.formvalues.tokenupdate.value = JSON.stringify( api_token_table.getData() );
    }

    function showQRcode( cell ) {
    
        var qr_data = ' { "apiurl": "' + FQDN + 
                      '","apitoken": "' + cell.getRow().getData().TOKEN + 
                      '","requesttimestamp": ' + Math.floor(Date.now() / 1000) + 
                      ',"version": 1'  +
                      ' }'
        //console.log( qr_data )
        
        var qr  = new QRious({
            element: document.getElementById('qr'),
            level: 'M',
            background: getStyleRuleValue('.color-back','color'),
            backgroundAlpha: 0.5,
            foreground: getStyleRuleValue('.color-select','color'),
            foregroundAlpha: 1,
            value: qr_data,
            size: 200,
        });

        document.getElementById('qrurl').innerHTML = FQDN;
        document.getElementById('qrtoken').innerHTML = cell.getRow().getData().TOKEN;
        showStuff('qrcode');
        document.getElementById('qrcode').onclick = function(){
            hideStuff('qrcode');
        };

    }


</script>
        <?php page_header();?>

        <div class="top-wrapper-2">
            <div class="content-wrapper pad-13">
                <!-- header 2 -->
                <?php pageclock(); ?>
            </div>
            <?php config_buttons( 0 );?>
        </div> <!-- end top wrapper-2 -->

        <div class="mid-section">
            <div class="left-wrapper-config"> <!-- left block -->
                <?php menu_control(5);?>
            </div>

            <div id="right-wrapper-config"> <!-- right block -->
            <!-- inner block right part of screen -->
                <div id="right-wrapper-config-left">
                    <!-- start of content -->
                    <form name="formvalues" id="formvalues" method="POST">

                        <div class="frame-4-top">
                            <span class="text-15">Internet API</span>
                        </div>
                        <div class="frame-4-bot">
                            <div class="rTable">

                                <div class="rTableRow">
                                    <div class="rTableCell">
                                        <i class="pad-7 text-10 fas fa-envelope-square"></i>
                                        <label class="text-10"><?php echo strIdx( 270 );?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="input-5 color-settings color-input-back" id="cert_email" name="cert_email" type="text" value="<?php echo config_read( 159 );?>">
                                    </div>
                                </div>

                                <div class="rTableRow">
                                    <div class="rTableCell">
                                        <i class="pad-7 text-10 fas fa-rss-square"></i>
                                        <label class="text-10"><?php echo strIdx( 265 );?></label>
                                    </div>
                                    <div class="rTableCell">
                                        <input class="cursor-pointer" id="fs_inet_api_active_on"  name="fs_inet_api_active" type="radio" value="1" <?php if ( config_read( 163 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" id="fs_inet_api_active_off" name="fs_inet_api_active" type="radio" value="0" <?php if ( config_read( 163 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                </div>

                                <div class="rTableRow">
                                    <div class="rTableCell">
                                        <i class="pad-7 text-10 fas fa-file-alt"></i>
                                        <label class="text-10"><?php echo strIdx( 266 );?></label>
                                    </div>
                                    <div class="rTableCell pad-18">
                                        <i id="http_status" class="fas fa-question-circle"></i>
                                    </div>
                                </div>

                                <div class="rTableRow">
                                    <div class="rTableCell">
                                        <i class="pad-7 text-10 fas fa-calendar-check"></i>
                                        <label class="text-10"><?php echo strIdx( 267 );?></label>
                                    </div>
                                    <div class="rTableCell pad-18">
                                        <i id="cert_renew" class="fas fa-question-circle"></i>
                                    </div>
                                </div>

                                <div class="rTableRow">
                                    <div class="rTableCell">
                                        <i class="pad-7 text-10 fas fa-globe"></i>
                                        <label class="text-10"><?php echo strIdx( 268 );?></label>
                                    </div>
                                    <div class="rTableCell pad-18">
                                        <i id="web_config" class="fas fa-question-circle"></i>
                                    </div>
                                </div>

                            </div>

                            <div class="rTable">
                                <div class="rTableRow">
                                    <div class="rTableCell">
                                        <i class="pad-7 text-10 fas fa-globe"></i>
                                        <label class="text-10"><?php echo strIdx( 235 );?>&nbsp;:&nbsp;</label>
                                        <label id="FQDN" class="text-10"></label>
                                    </div>
                                </div>
                                <div class="rTableRow">
                                    <div class="rTableCell">
                                        <i class="pad-7 text-10 fas fa-clock"></i>
                                        <label class="text-10"><?php echo strIdx( 271 );?>&nbsp;:&nbsp;</label>
                                        <label id="renewtime" class="text-10">x</label>
                                    </div>
                                </div>
                                <div class="rTableRow">
                                    <div class="rTableCell">
                                        <i class="pad-7 text-10 fas fa-clock"></i>
                                        <label class="text-10"><?php echo strIdx( 272 );?>&nbsp;:&nbsp;</label>
                                        <label id="validtime" class="text-10"></label>
                                    </div>
                                </div>

                            </div>

                            <p></p>
                        </div>
                        <p></p>

                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 260 );?></span>
                        </div>
                        
                        <div class="frame-4-bot">

                            <div class="float-right" title="<?php echo strIdx( 262 );?>">
                                <button class="input-2 but-1 cursor-pointer" id="add_token_button">
                                    <i class="color-menu fa-3x fas fa-plus"></i><br>
                                </button>
                            </div>

                            <div class="float-left pad-17" >
                                <div id="api-token-table"></div>
                            </div>
                            
                        </div>
                        <p></p>

                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 261 );?></span>
                        </div>
                        <div class="frame-4-bot">
                            <div class='pad-12'>
                                <div id="apiList">
                                  <!-- dynamicly filled -->
                                </div>
                            </div>
                        </div>
                        <p></p>

                        <!-- placeholder variables for session termination -->
                        <input type="hidden" name="logout" id="logout" value="">
                        <input type="hidden" name="tokenupdate" id="tokenupdate" value="">
                    </form>
                </div>
                
                <div id="right-wrapper-config-right">
                    <div class="frame-4-top">
                        <span class="text-15"><?php echo strIdx( 155 );?></span>
                    </div>
                    <div class="frame-4-bot text-10">
                        <?php echo strIdx( 263);?>
                        <p></p>
                        <span class="text-10">
                            <a href="https://www.ztatz.nl/p1-monitor-internet-api/#static_ip" target="_blank">
                                <i class="pad-7 color-menu fas fa-globe"></i>
                                <?php echo strIdx( 283 );?>
                            </a>
                        </span>
                        <br><br>
                        <?php echo strIdx(8);?>
                    </div>
                    
                    </div>
                </div>
            
            <!-- end inner block right part of screen -->
    </div>    
    <?php echo div_err_succes();?>
    <?php echo autoLogout(); ?>
    
    <div id='qrcode' title="<?php echo strIdx( 285 );?>" class="cursor-pointer" >
        <canvas id="qr"></canvas>
        <div><span>api url:&nbsp;</span><span id=qrurl></span></div>
        <div><span>token:&nbsp;</span><span id="qrtoken"></span></div>
    </div>

</body>
</html>