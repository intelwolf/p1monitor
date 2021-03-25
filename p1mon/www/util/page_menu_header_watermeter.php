<?php
function page_menu_header_watermeter( $id ) {
$m0=$m1=$m2=$m3=$m4='';

switch ( $id ) {
	case 0: /* uren */
        $m0= "menu-active";
       	break;
    case 1: /* dagen */
    	$m1 = "menu-active";
        break;
    case 2: /* maanden */
        $m2= "menu-active";		
        break;
	case 3: /* jaren */
        $m3= "menu-active";		
        break;
    case 4: /* jaren */
        $m4= "menu-active";		
        break;
	default:
		/* default value so always a menu is available */
		$m0="menu-active";
}
echo <<< EOT
<div class="pad-13 content-wrapper">
<div class="pos-7 content-wrapper $m4"><a href="watermeter-min.php" class="$m4">minuten</a></div>
<div class="pos-7 content-wrapper $m0"><a href="watermeter-h.php" class="$m0">uren</a></div>
<div class="pos-7 content-wrapper $m1"><a href="watermeter-d.php" class="$m1">dagen</a></div>
<div class="pos-7 content-wrapper $m2"><a href="watermeter-m.php" class="$m2">maanden</a></div>
<div class="pos-7 content-wrapper $m3"><a href="watermeter-j.php" class="$m3">jaren</a></div>
</div>
EOT;
}
?>
