<?php

function page_menu_header_powerproduction($id) {

    $m0=$m1=$m2=$m3=$m4=$m5='';

    $minutes = strIdx(120);
    $hours   = strIdx(121);
    $days    = strIdx(122);
    $months  = strIdx(123);
    $years   = strIdx(124);

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
        case 4: /* opties */
            $m4= "menu-active";
            break;
        default:
        /* default value so always a menu is available */
        $m0="menu-active";
    }

echo <<< EOT
<div class="pad-13 content-wrapper">
<div class="pos-7 content-wrapper $m0"><a href="powerproduction-min.php" class="$m0">$minutes</a></div>
<div class="pos-7 content-wrapper $m1"><a href="powerproduction-h.php"  class="$m1">$hours</a></div>
<div class="pos-7 content-wrapper $m2"><a href="powerproduction-d.php"  class="$m2">$days</a></div>
<div class="pos-7 content-wrapper $m3"><a href="powerproduction-m.php" class="$m3">$months</a></div>
<div class="pos-7 content-wrapper $m4"><a href="powerproduction-j.php"  class="$m4">$years</a></div>
</div>
EOT;
}
?>

