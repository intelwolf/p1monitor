<?php
function page_menu_header_fase( $id ) {
$m0=$m1='';

switch ($id) {
	case 0: /* actueel*/
        $m0= "menu-active";
       	break;
    case 1: /* historie */
    	$m1 = "menu-active";
		break;
	default:
	/* default value so always a menu is available */
	$m0="menu-active";
}
echo <<< EOT
 <div class="pad-13 content-wrapper">
    <div class="pos-7 content-wrapper $m0"><a href="fase-a.php"        class="$m0">actueel</a></div>
    <div class="pos-7 content-wrapper $m1"><a href="fase-historie.php" class="$m1">historie</a></div>
EOT;
}
?>
