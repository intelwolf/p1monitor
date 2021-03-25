<?php
function page_menu_header_gas($id) {
$m0=$m1=$m2=$m3=$m4=$m5='';

switch ($id) {
	case 0: /* home */
        $m0= "menu-active";
       	break;
    case 1: /* grafiek */
    	$m1 = "menu-active";
        break;
    case 2: /* opties */
        $m2= "menu-active";		
        break;
	case 3: /* opties */
        $m3= "menu-active";		
        break;
	default:
		/* default value so always a menu is available */
		$m0="menu-active";
}
echo <<< EOT
<div class="pad-13 content-wrapper">
<div class="pos-7 content-wrapper $m3"><a href="stats-h-gas.php" class="$m3">uren</a></div>
<div class="pos-7 content-wrapper $m0"><a href="stats-d-gas.php" class="$m0">dagen</a></div>
<div class="pos-7 content-wrapper $m1"><a href="stats-m-gas.php" class="$m1">maanden</a></div>
<div class="pos-7 content-wrapper $m2"><a href="stats-j-gas.php" class="$m2">jaren</a></div>
</div>
EOT;
}
?>
