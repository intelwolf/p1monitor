<script src="./js/p1mon-util.js"></script>
<script>
<?php 
/**************************************************************************/
/* redirector die het mogelijk maakt om andere home pagina's te gebruiken */
/**************************************************************************/
include_once '/p1mon/www/util/config_read.php';

if ( config_read(43) == 1 ) {
   $location = '/custom/p1mon.php';
    echo "var main_location = '" . $location ."';";
} else {
echo "var main_location = '/main-1.php'; // default value when not set"."\n";
echo "if ( getLocalStorage('main-menu') !== null ) {"."\n"; 
echo "   var main_location = getLocalStorage('main-menu');"."\n";
echo "}"."\n";
}
?>
window.location.assign ( main_location );
</script>
