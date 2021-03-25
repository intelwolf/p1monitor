<?php
function page_menu_header_actual($id) {
$m0=$m1=$m2=$m3=$m4=$m5='';

switch ($id) {
	case 0: /* home */
        $m0= "menu-active";
       	break;
    case 1: /* grafiek */
    	$m1 = "menu-active";
		break;
	case 2: /* grafiek */
    	$m2 = "menu-active";
        break;
	default:
	/* default value so always a menu is available */
	$m0="menu-active";
}
echo <<< EOT
 <div class="pad-13 content-wrapper">
	<div class="pos-7 content-wrapper $m0"><a href="e-verbruik.php" class="$m0">kWh verbruik</a></div>
	<div class="pos-7 content-wrapper $m1"><a href="e-levering.php" class="$m1">kWh levering</a></div>
	<div class="pos-7 content-wrapper $m2"><a href="g-verbruik.php" class="$m2">gas verbruik</a></div>
</div>
EOT;
}
?>
