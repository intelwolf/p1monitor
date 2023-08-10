<?php
function page_menu_header_heating($id) {

    $m0=$m1=$m2=$m3=$m4='';

    $current = strIdx(343);
    $minutes = strIdx(120);
    $hours   = strIdx(121);
    $days    = strIdx(122);
    $months  = strIdx(123);

    switch ($id) {
            case 0: /* actueel */
            $m0 = "menu-active";
            break;
        case 1: /* min */
            $m1 = "menu-active";
            break;
        case 2: /* uren */
            $m2 = "menu-active";		
            break;
        case 3: /* dagen */
            $m3 = "menu-active";		
            break;
        case 4: /* dagen */
            $m4 = "menu-active";		
            break;
        default:
        /* default value so always a menu is available */
        $m0="menu-active";
    }
    echo <<< EOT
    <div class="pad-13 content-wrapper">
    <div class="pos-7 content-wrapper $m0"><a href="verwarming-a.php"   class="$m0">$current</a></div>
    <div class="pos-7 content-wrapper $m1"><a href="verwarming-min.php" class="$m1">$minutes</a></div>
    <div class="pos-7 content-wrapper $m2"><a href="verwarming-h.php"   class="$m2">$hours</a></div>
    <div class="pos-7 content-wrapper $m3"><a href="verwarming-d.php"   class="$m3">$days</a></div>
    <div class="pos-7 content-wrapper $m4"><a href="verwarming-m.php"   class="$m4">$months</a></div>
    </div>
    EOT;
}
?>
