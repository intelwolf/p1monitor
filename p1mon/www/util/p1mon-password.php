<?php 

$P1MON_PWFILE           = '/p1mon/mnt/ramdisk/session.txt';
$P1MON_PWFILE_BACKUP    = '/p1mon/data/session.txt';
$P1MON_SESSION          = 'session';
$P1MON_HTTP_REFERER     = 'http_ref_password';
$P1MON_SESSION_MAX_TIME = 1500; // changed in version > 1.2.0 was 900 is 5 minutes. 1500 is 25 minutes.

function passwordSessionLogoutCheck() {
    global $_POST;
    if ( isset($_POST["logout"]) ) { 
        if ( $_POST["logout"] === 'true') {
            session_unset();
            session_destroy();
            header('Location: ' . $_SERVER['HTTP_REFERER']);
        }
    }    
}

function loginInit() {
    if (strlen(getPasswordSession()) <= 0) {
        setPasswordHttpReferer();
        header('Location: ' . 'login.php');
    }
    #echo "time sessiion = ".getPasswordSession() . '<br>';
    #echo "time  = ".time() . '<br>';
    passwordSessionExpiredCheck();
}

function setPasswordHttpReferer() {
    global $_SESSION, $P1MON_HTTP_REFERER;
    if (isset($_SESSION)){
        $_SESSION[$P1MON_HTTP_REFERER] = $_SERVER['PHP_SELF'];
    }
}

function getPasswordHttpReferer() {
    global $_SESSION, $P1MON_HTTP_REFERER;
    if ( isset($_SESSION[$P1MON_HTTP_REFERER]) ){
        return $_SESSION[$P1MON_HTTP_REFERER];
    }
}

function passwordSessionExpiredCheck() {
    global $_SESSION, $P1MON_SESSION , $P1MON_SESSION_MAX_TIME;
    #echo "1<br>";
    if (isset($_SESSION)){
        if(isset($_SESSION[$P1MON_SESSION])){
            #echo "2<br>";
            $delta = time() - getPasswordSession();
            #echo "delta=".$delta.'<br>';
            #echo $P1MON_SESSION_MAX_TIME;
            if( $delta >= $P1MON_SESSION_MAX_TIME ){ // in seconds is 15min use of login session. //900 default
                #echo "3<br>";
                session_unset();
                session_destroy();
            }
        }
    }
}

function setPasswordSession() {
    global $_SESSION, $P1MON_SESSION;
    $_SESSION[$P1MON_SESSION] = time();
}

function getPasswordSession() {
    global $_SESSION, $P1MON_SESSION;
    if (isset($_SESSION)){
        if (isset($_SESSION[$P1MON_SESSION])){
            return $_SESSION[$P1MON_SESSION];
        }
    }
}

function passwdHashValue($passwd) {
    // from PHP 5.5> version change to password_hash()
    $salt = 'fPv7zGH@!qDrUow5678X2qwSyN3cscgasds%3dqaztatzrules!';
    return md5($salt.$passwd);
}

function writePwFile($pw){
    global $P1MON_PWFILE, $P1MON_PWFILE_BACKUP;
    file_put_contents($P1MON_PWFILE, $pw, LOCK_EX);
    file_put_contents($P1MON_PWFILE_BACKUP, $pw, LOCK_EX);
}

function readPasswordFile(){
    global $P1MON_PWFILE;
    return @file_get_contents($P1MON_PWFILE);
}

function deletePasswordFiles(){
    global $P1MON_PWFILE, $P1MON_PWFILE_BACKUP;
    @unlink($P1MON_PWFILE);
    @unlink($P1MON_PWFILE_BACKUP); 
    session_unset();
    session_destroy();
}

function passwordFileIsSet() {
    if( strlen(readPasswordFile())  < 32 ) {
        return false;
    }
    return true;
}
?>