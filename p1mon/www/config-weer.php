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

$sw_off   = strIdx( 193 );
$sw_on    = strIdx( 192 );
$lang_idx = config_read( 203 );
$lang     = 'nl';

$err_cnt = -1;
$err_str = '';
$weather_api = array( "city_id"=>"" );

# set language string
switch ( $lang_idx ) {
    case 0:
        $lang = 'nl';
        break;
    case 1:
        $lang = 'en';
        break;
    case 2:
        $lang = 'fr';
        break;
}


if ( isset($_POST["API_key"]) ) { 
    #echo "<br>processing</br>\n";

        if ( $err_cnt == -1 ) $err_cnt=0;
        
        if ( strlen(trim($_POST["API_key"])) !== 32 ) {
                $err_str = 'API key is te lang of te kort!<br>';
                $err_cnt+=1;
        }
        
        if (!ctype_xdigit(trim($_POST["API_key"]))) {
                //echo "hex is false".'<br>';
                $err_str = $err_str.'API invoer niet correct (alleen hex karakters)<br>';
                $err_cnt+=1;
        }
    
        if ( strlen(trim($_POST["stad_id"])) == 0 ) {
            if ( strlen( trim($_POST["stad"]) ) < 3) {
                $err_str = $err_str.'Stad lijkt niet correct.<br>';
                    $err_cnt+=1;
                }
        }

        $input = preg_replace('/[\x00-\x1F\x7F]/u', '',$_POST["API_key"]);
        $crypto_api_key = encodeString ($input, 'weatherapikey');

        #debugLog( '$crypto_api_key api key plain ='.$input );
        #debugLog( '$crypto_api_key api key encoded ='.$crypto_api_key );
        #debugLog( '$crypto_api_key api key decoded ='. decodeString(13, 'weatherapikey') );

        #debugLog( '$_POST["stad"](1) ='. $_POST["stad"] );
        
        # pre process city name
        $city_name = preg_replace( '/[\x00-\x1F\x7F]/u', '',$_POST["stad"] );
        $city_name = str_replace("'", "''", $city_name ); # done to handle city names with ' like Braine-l'Alleud

        if ( updateConfigDb("update config set parameter = '".$crypto_api_key."' where ID = 13")) $err_cnt += 1;
        //if ( updateConfigDb("update config set parameter = '".preg_replace('/[\x00-\x1F\x7F]/u', '',$_POST["stad"])."' where ID = 14")) $err_cnt += 1;
        if ( updateConfigDb("update config set parameter = '".$city_name ."' where ID = 14")) $err_cnt += 1;

        ##$sql = "update config set parameter = '".$city_name."' where ID = 14";
        ##debugLog( 'sql update ='. $sql );

        if ( updateConfigDb($sql)) $err_cnt += 1;

        $busy_indicator = '';
        if ( strlen(trim($_POST["API_key"])) == 0 ) { # to prevent error on a empty input
            header('Location: '.$_SERVER['PHP_SELF']);
            die;
        }

        getJsonGetWeatherData(); // setting the weather id from the city name.
}

# set id by city id by name is skipped.
if ( isset($_POST["stad_id"]) ) {
    if ( strlen(trim($_POST["stad_id"])) > 0 ) {
        $stad_id_clean = preg_replace('/\D/', '', $_POST["stad_id"]);
        #echo $stad_id_clean."<br>";
        if ( updateConfigDb("update config set parameter = '" . $stad_id_clean . "' where ID = 25") ){
            updateConfigDb("update config set parameter = '0' where ID = 25");
            return false; # could not update ID
        }
        setCityNameByID( $stad_id_clean );
    }
}

if ( isset($_POST["graaddagen_recover"]) ) { 
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ($_POST["graaddagen_recover"] == '1' ) {
        if ( updateConfigDb("update config set parameter = '1' where ID = 203")) $err_cnt += 1;
    } else {
        if ( updateConfigDb("update config set parameter = '0' where ID = 203")) $err_cnt += 1;
    }
}

if( isset($_POST["roomtemperature"]) ) {
    if ( $err_cnt == -1 ) $err_cnt=0;
    if ( updateConfigDb("update config set parameter = '" . inputCleanDigitsOnly($_POST["roomtemperature"]) . "' where ID = 202"))  $err_cnt += 1;
}

function setCityNameByID( $city_id ) {
    #echo "setCityNameByID id ". $city_id ."<br>";
    
    $api_key = decodeString(13, 'weatherapikey');
    $url = 'https://api.openweathermap.org/data/2.5/weather?id=' . strval($city_id) .'&units=metric&lang='. $lang. '&appid=' . $api_key;
    $json = @file_get_contents( $url );
   
    #debugLog( '$json   ='.$json   ); 

    # something fishy with the json
    if ( strlen($json) < 10 ) {
        $weather_api['w_city']='';
        return false;
    }

    $main_array = json_decode( $json,true );
    #print_r($main_array);
    $weather_api['w_city'] = $main_array['name'];
    $weather_api['w_city'] = str_replace("'", "''", $weather_api['w_city'] ); # done to handle city names with ' like Braine-l'Alleud

    $sql = "update config set parameter = '" . $weather_api['w_city'] . "' where ID = 14";
    #debugLog( '$sql(2)  ='.$sql  ); 

    #if ( updateConfigDb("update config set parameter = '" . $weather_api['w_city'] . "' where ID = 14") ){
    if ( updateConfigDb( $sql ) ){
        #debugLog( "error 1"  ); 
        updateConfigDb("update config set parameter = '' where ID = 14");
        return false; # could not update city name
    }
    
    # update database 
    $command = '/p1mon/scripts/P1Weather --getweather &';
    exec( $command ,$arr_execoutput, $exec_ret_value );
    return true;
}


function getJsonGetWeatherData() {
    global $weather_api;
    //$api_key = decodePassword(13);

    #echo "<br> stad="+config_read(14)."<br>";

    # only set the ID by name when city ID is not set.
    if ( isset($_POST["stad_id"]) ) {
        if ( strlen(trim($_POST["stad_id"])) > 0 ) {
            #echo "stad id gezet 1 niet door stads naam<br>";
            return;
        }
    }

    $api_key = decodeString( 13, 'weatherapikey');

    $url = 'https://api.openweathermap.org/data/2.5/weather?q='.config_read(14).'&units=metric&lang='.$lang.'&appid='.$api_key; 

    #debugLog( '$url ='.$url );

    #echo '<br>'.$url.'<br>';
    $json = @file_get_contents($url);
    //echo "json length = ". strlen($json). '<br>';
    #echo $json;
    
    # something fishy with the json
    if ( strlen($json) < 10 ) {
            $weather_api['w_city']='';
            return false;
    }

    $main_array = json_decode($json,true);
    #print_r($main_array);
    $weather_api['city_id']=$main_array['id'];

    if ( updateConfigDb("update config set parameter = '".preg_replace('/\D/', '',$weather_api['city_id'])."' where ID = 25") ){
        updateConfigDb("update config set parameter = '0' where ID = 25");
        return false; # could not update ID
    }

    # update database 
    $command = '/p1mon/scripts/P1Weather --getweather &';
    exec($command ,$arr_execoutput, $exec_ret_value );
    return true;
}

# to get updated status info.

#$command = '/p1mon/scripts/P1Weather.py &'; 
#exec( $command ,$arr_execoutput, $exec_ret_value );


?>
<!doctype html>
<html lang="nl">
<head>
<meta name="robots" content="noindex">
<title>Weer configuratie</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css">
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css">

<script defer src="./font/awsome/js/all.js"></script>
<script       src="./js/jquery.min.js"></script>
<script       src="./js/p1mon-util.js"></script>
<script       src="./js/jquery-validate-link/jquery.validate.min.js"></script>
<script       src="./js/jquery-validate-link/additional-methods.min.js"></script>

</head>
<body>
<script>
var initloadtimer;

function readJsonApiWeatherWithID( id ){ 
    $.getScript( "/api/v1/configuration/" + id, function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        //console.log( jsondata[0][1] )
        readJsonApiWeather ( jsondata[0][1] )
      } catch(err) {}
   });
}

function readJsonApiWeather( weatherCityID ){ 
    $.getScript( "./api/v1/weather?limit=50", function( data, textStatus, jqxhr ) {
      try {
              var jsonarr = JSON.parse(data); 
        for (var j=0; j < jsonarr.length; j++ ){    
            item = jsonarr[ j ];
            //console.log ( item[0], item[2], weatherCityID  )
            if ( weatherCityID == item[2] ) {
                $('#w_city').text( item[3] );
                $('#w_timestamp').text( item[0] );
                $('#w_temperature').text( item[4].toFixed(1) + "°C");
                $('#w_description').text( item[5] );
                $('#w_city_id').text( item[2] );
                break;
            }
        }  
      } catch(err) {
          console.log( err );
      }
   });
}

function readJsonApiStatus(){ 
    $.getScript( "./api/v1/status", function( data, textStatus, jqxhr ) {
        try {
                var jsondata = JSON.parse(data); 
        
                for (var j=79;  j < jsondata.length; j++){  
                        // console.log( jsondata[j][0] + ' - ' + jsondata[j][1] )
                        if ( jsondata[j][0] == 80 ) {
                                $('#api_status').text( jsondata[j][1] );
                                continue;
                        }
                        if ( jsondata[j][0] == 81 ) {
                                $('#api_status_timestamp').text( jsondata[j][1] );
                                continue;
                }
            }
        } catch(err) {
            console.log( err )
        }
});
}

readJsonApiWeatherWithID( 25 );

function LoadData() {
    clearTimeout(initloadtimer);
    //readJsonApiWeather();
    readJsonApiWeatherWithID( 25 );
    readJsonApiStatus();
    initloadtimer = setInterval(function(){LoadData();}, 10000);
}

$(function () {
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
                                <?php menu_control(8);?>
                        </div>
                        
                        <div id="right-wrapper-config"> <!-- right block -->
                        <!-- inner block right part of screen -->
                            <div id="right-wrapper-config-left-2">
                                <!-- start of content -->
                                <form name="formvalues" id="formvalues" method="POST">
                                            
                                    <div class="frame-4-top">
                                        <span class="text-15">weer API configuratie</span><span id="busy_indicator" class="display-none" >&nbsp;&nbsp;&nbsp;<i class="fas fa-spinner fa-pulse fa-1x fa-fw"></i></span>
                                    </div>
                                    <div class="frame-4-bot">
                                        <div class="float-left">
                                            <i class="text-10 pad-7 fas fa-key"></i>
                                            <label class="text-10">api key</label>
                                            <p class="p-1"></p>
                                            <i class="text-10 pad-39 fas fa-globe "></i>
                                            <label class="text-10">stad</label> 
                                            <p class="p-1"></p>
                                            <i class="text-10 pad-39 fas fa-globe "></i>
                                            <label class="text-10">stad ID</label> 
                                        </div>
                                        <div class="float-left pad-1">
                                            <input class="input-6 color-settings color-input-back" id="api_key" name="API_key" type="password" value="<?php echo decodeString(13, 'weatherapikey');?>">
                                            <p class="p-1"></p>
                                            <input class="input-6 color-settings color-input-back" name="stad" type="text" value="<?php echo config_read(14); ?>">
                                            <p class="p-1"></p>
                                            <input class="input-6 color-settings color-input-back" name="stad_id" type="text" value="" placeholder="gebruik de stad id als alternatief">
                                            <p class="p-1"></p>
                                        </div>
                                        <div id="api_passwd" onclick="toggelPasswordVisibility('api_key')" class="float-left pad-1 cursor-pointer">        
                                            <span><i class="color-menu pad-7 fas fa-eye"></i></span>
                                        </div>

                                    </div>
                                    <p></p>
                                    <div class="frame-4-top">
                                        <span class="text-15">weer status</span>
                                    </div>
                                    <div class="frame-4-bot">
                                        <div class="text-16">stad:&nbsp;            <span id="w_city"></span></div><br>
                                        <div class="text-16">tijdstip meting:&nbsp; <span id="w_timestamp"></span></div><br>
                                        <div class="text-16">temperatuur:&nbsp;     <span id="w_temperature"></span></div><br>
                                        <div class="text-16">conditie:&nbsp;        <span id="w_description"></span></div><br>        
                                        <div class="text-16">stad id:&nbsp;         <span id="w_city_id"></span></div><br>
                                        <div class="text-16">API status:&nbsp;      <span id="api_status"></span></div><br>
                                    <div class="text-16">API status timestamp:&nbsp; <span id="api_status_timestamp"></span>
                                    </div>
                                    <br>

                                </div>
                                <p></p>
                        <!-- graaddagen -->
                        <p></p>
                        <div class="frame-4-top" title="<?php echo strIdx( 325 );?>">
                            <span class="text-15">graaddagen</span>
                        </div>
                        <div class="frame-4-bot" title="<?php echo strIdx( 325 );?>">
                            <div class="rTable">

                                <div class="rTableRow" title="<?php echo strIdx( 328 );?>">
                                    <div class="rTableCell">
                                        <i class="text-10 fa-solid fa-toggle-off"></i>
                                    </div>
                                    <div class="rTableCell width-280">
                                        <label class="text-10"><?php echo strIdx( 326 );?></label> 
                                    </div>
                                    <div class="rTableCell">
                                        <input class="cursor-pointer" name="graaddagen_recover" type="radio" value="1" <?php if ( config_read( 203 ) == 1 ) { echo 'checked'; }?>><?php echo $sw_on ?>
                                        <input class="cursor-pointer" name="graaddagen_recover" type="radio" value="0" <?php if ( config_read( 203 ) == 0 ) { echo 'checked'; }?>><?php echo $sw_off ?>
                                    </div>
                                </div>

                                <div class="rTableRow" title="<?php echo strIdx( 329 );?>">
                                    <div class="rTableCell">
                                        <i class="text-10 fa-solid fa-temperature-half"></i>
                                    </div>
                                    <div class="rTableCell width-280">
                                        <label class="text-10"><?php echo strIdx( 327 );?></label>
                                    </div>
                                    <div class="rTableCell witdh-24">
                                        <input class="input-12 color-settings color-input-back" id="roomtemperature" name="roomtemperature" type="text" 
                                        value="<?php echo config_read( 202 );?>">
                                    </div>
                                </div>
                                
                            </div>
                        </div>

                        <!-- placeholder variables for session termination -->
                        <input type="hidden" name="logout" id="logout" value="">
                        </form>
                            </div>
                            <div id="right-wrapper-config-right-2">
                                    <div class="frame-4-top">
                                            <span class="text-15">hulp</span>
                                    </div>
                                    <div class="frame-4-bot text-10">
                                            <?php echo strIdx( 10 );?>
                                            <br>
                                            <br>
                                            <?php echo strIdx( 325 );?>
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
?>
<script>
     $(function() {
         $("#formvalues").validate({
             rules: {
                 'roomtemperature': {
                     required: true,
                     number: true,
                     max: 99,
                     min: 0
                 }
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