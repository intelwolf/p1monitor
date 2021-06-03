 <?php
session_start(); #must be here for every page using login
header("Content-type: text/json");
include_once '/p1mon/www/util/p1mon-password.php';
#print_r($_POST);
passwordSessionExpiredCheck();
$data[0]['SESSION_STATUS'] = (int)session_status();
echo trim(json_encode($data, JSON_PRETTY_PRINT));
?>