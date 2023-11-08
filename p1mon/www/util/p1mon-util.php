<?php 

// lees de config database uit om de fileshare status te lezen
// op basis van uit,data of dev word niets of checked terug gegeven.
function readStatusDb($id){
    $sqlstr = "select id, status, label, security from status where id=$id";
    $dbstr = '/p1mon/mnt/ramdisk/status.db'; 
    try {
        $data = array();
        $db = new SQLite3($dbstr,SQLITE3_OPEN_READONLY);
        $db -> busyTimeout(300000);  // fix for database locks, wait 300 sec = 5 min
        $result = $db->query($sqlstr);
        //var_dump($result->fetchArray());
        $row = $result->fetchArray();
        $db->close();
        return $row["STATUS"];
    } catch (Exception $e) {
        echo 'Exception: ',  $e->getMessage(), "\n";
    }
}

function debugLog($string) {
    error_log($string."\n", 3, "/var/tmp/php-debug.log");
}

function encodeString ( $input, $seed ) { # nog niet getest met zonder p1monExec
        $encoded_string = '';
        $command = "/p1mon/scripts/P1CryptoV2 --enc ".base64_encode( $input )." --seed ".$seed;
       
        #debugLog('$input='.$input); 
        #debugLog('$seed='.$seed);

        $arr_execoutput_enc = []; // make sure old stuff is cleared.
        exec( $command ,$arr_execoutput_enc, $exec_ret_value );

        #debugLog('$encodeString output='.$arr_execoutput_enc);
        #debugLog('$encodeString return value='.$exec_ret_value);

        if (empty($arr_execoutput_enc)) { return ''; } // nothing to decode.
        return $arr_execoutput_enc[0];
}

function decodeString( $config_id, $seed ) {
    $decoded_string = '';
    $command = "/p1mon/scripts/P1CryptoV2 --dec ".config_read($config_id)." --seed ".$seed;


    $arr_execoutput_dec = []; // make sure old stuff is cleared.
    exec($command ,$arr_execoutput_dec, $exec_ret_value );
    #debugLog('$decodeString output='.$arr_execoutput_dec);
    #debugLog('$decodeString return value='.$exec_ret_value);
    if (empty($arr_execoutput_dec)) { return ''; } // nothing to decode.
    return base64_decode($arr_execoutput_dec[0], true);
}

function decodeStringNoBase64( $config_id, $seed ) { # used in API
    $decoded_string = '';
    $command = "/p1mon/scripts/P1CryptoV2 --dec ".config_read($config_id)." --seed ".$seed;

    $arr_execoutput_dec = []; // make sure old stuff is cleared.
    exec($command ,$arr_execoutput_dec, $exec_ret_value );
    if (empty($arr_execoutput_dec)) { return ''; } // nothing to decode.
    return $arr_execoutput_dec[0];
}


//maak een string schoon van speciale chars
function clean( $string ) {
   $string = str_replace(' ', '-', $string); // Replaces all spaces with hyphens.
   return preg_replace('/[^A-Za-z0-9\-.]/', '', $string); // Removes special chars.
}

function inputClean($string) {
   return preg_replace('/[^A-Za-z0-9\-._!:\^\{\}\[\]\$\(\)\+\?\>\&\s\/@]/', '', $string); // Removes unwanted charters
}

function timestampClean($string) {
    return preg_replace('/[^0-9\-:\^\{\}\[\]\$\(\)\+\?\>\&\s\/@]/', '', $string); // Removes unwanted charters
}


function inputCleanDigitsOnly($string) {
   return preg_replace('/[^0-9]/', '', $string); // Removes special chars.
}

function inputCleanDigitsOnlyMinus($string) {
    return preg_replace('/[^0-9\-]/', '', $string); // Removes special chars.
 }

// true = ok, false = not ok
function cronSafeCharacters($str_in) {
    $regex = "/[^0-9,\/\-\*]+/";
    if (preg_match($regex, $str_in)) { 
        //echo $str_in;
        return False;
    }
    return True;
}

// update de sqllite DB config met de sql
// fout is een waarde groter dan 1
function updateConfigDb($sql){
      $dbstr = '/p1mon/mnt/ramdisk/config.db'; 
      $r = 0;
      try {
        $db = new SQLite3($dbstr,SQLITE3_OPEN_READWRITE);
        $db -> busyTimeout(300000);  // fix for database locks, wait 300 sec = 5 min
          $db->exec($sql);
          if ($db->lastErrorCode() > 0) $r = 1;
          $db->close();
      } catch (Exception $e) {
        $r=1;
    }
    return $r;
}

// lees de config database uit om de fileshare status te lezen
// op basis van uit,data of dev wordt niets of checked terug gegeven.
function readFileShareStatus($cmpstr){
    $sqlstr = "select id,parameter from config where id=6";
    $dbstr = '/p1mon/mnt/ramdisk/config.db'; 
    try {
        $data = array();
        $db = new SQLite3($dbstr,SQLITE3_OPEN_READONLY);
        $db -> busyTimeout(300000);  // fix for database locks, wait 300 sec = 5 min
        $result = $db->query($sqlstr);
        //var_dump($result->fetchArray());
        $row = $result->fetchArray();    
        $db->close();
    } catch (Exception $e) {
        echo 'Exception: ',  $e->getMessage(), "\n";
    }
    if ($row[1] == $cmpstr ) { echo " checked"; } 
}

// haal het adres van de PHP server op
// de webserver waar php draait
// geeft een IP adress x.x.x.x terug
function getHostIP()
{
    foreach (array('SERVER_ADDR',
                   'LOCAL_ADDR') as $key){
        if (array_key_exists($key, $_SERVER) === true){
            foreach (explode(',', $_SERVER[$key]) as $IPaddress){
                $IPaddress = trim($IPaddress); // Just to be safe
                return $IPaddress;              
            }
        }
    }
} 
  
// haal het IP adres van de web-client op
// geeft een IP adress x.x.x.x terug
function getClientIP()
{
    foreach (array('HTTP_CLIENT_IP',
                   'HTTP_X_FORWARDED_FOR',
                   'HTTP_X_FORWARDED',
                   'HTTP_X_CLUSTER_CLIENT_IP',
                   'HTTP_FORWARDED_FOR',
                   'HTTP_FORWARDED',
                   'REMOTE_ADDR') as $key){
        if (array_key_exists($key, $_SERVER) === true){
            foreach (explode(',', $_SERVER[$key]) as $IPaddress){
                $IPaddress = trim($IPaddress); // Just to be safe
                return $IPaddress;              
            }
        }
    }
}
  
// controleert of een IP adress correct is
// en een private range adres is RFC1918
// True = een valide private range
function validLocalIpAdress($ip) {
    if( filter_var( $ip, FILTER_VALIDATE_IP,FILTER_FLAG_IPV4) ){     
        if( filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4 | FILTER_FLAG_NO_PRIV_RANGE) ){ 
            return False;             
        } else { return True; }
        
    } else { return False; }
}

// check of in de config of internet gebruik is toegestaan.
// place holder zodat het eenvoudig te onderhouden is
// true inet allowed, false not allowed.
function isInternetIPAllowed(){
    if ( config_read(60) == 1 ) { 
        return True; 
    } else { 
        return False;
    }
}

// maak van een string een float format nummer
// $in = waarde, $decimals plaats achter de . $maxwaarde die wordt toegestaan
// $abs (alleen positieve waarde worden terugegeven
// bij een fout wordt 0 terug gegeven.
function checkFloat($in, $decimals, $maxval, $abs) {
      $in = str_replace(",",".",$in);
      if (!is_numeric ($in)){ return 0;} 
      $in = floatval(number_format ( $in ,$decimals ));    
           
     if ( $in > $maxval) { return 0;}
     if ($abs == 1 && $in < 0 ) { $in = $in * -1; }
      return $in;
  }


// indien zomertijd voeg dan een uur in sec toe.
function TimeDSTAdjustTicks()
{
    date_default_timezone_set('Europe/Amsterdam');
    if(date('I')) {return 3600;}
    else return 0; // we are in winter time
}

// indien zomertijd voeg dan een uur toe aan
// uren en strip de datum
function TimeDSTAdjust($t)
{
    date_default_timezone_set('Europe/Amsterdam');
    $s=split(' ',$t);
    // get rid off date
    if (count($s) > 1) { $v = $s[1];}
    else $v = $s[0];
    
    if(date('I')) {
        $arr=split(':', $v);
        
        $h=$arr[0]+1;
        if ($h==24) { $h=0;}
        $arr[0]=sprintf('%02d', $h);    
        return $arr[0].":".$arr[1].":".$arr[2];
    }
    return $v;
}

function DateStrip($t){
    $s=split(' ',$t);
    // get rid off date
    if (count($s) > 1) { $v = $s[1];}
    else $v = $s[0];
    return $v;
}
?>