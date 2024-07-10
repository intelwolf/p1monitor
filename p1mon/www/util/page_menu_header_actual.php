<?php

function page_menu_header_actual($id) {
    $m0=$m1=$m2=$m3=$m4=$m5='';

    $consumptionkWh = strIdx( 400 );
    $productionKwh  = strIdx( 401 );
    $gasconsumption = strIdx( 364 );

    /* adjust font and such to fix the longer text */
    $class_pos  = "pos-7"; /* default */
    $language_index = config_read( 148 );
    if(isset($language_index) ) {
        switch ($language_index) {
            case 1:
                $class_pos = "pos-52";
                break;
            case 2:
                $class_pos = "pos-53";
                break;
        }
    } 

    switch ($id) {
        case 0: /* home */
            $m0 = "menu-active";
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
        <div class="$class_pos content-wrapper $m0"><a href="e-verbruik.php" class="$m0">$consumptionkWh</a></div>
        <div class="$class_pos content-wrapper $m1"><a href="e-levering.php" class="$m1">$productionKwh</a></div>
        <div class="$class_pos content-wrapper $m2"><a href="g-verbruik.php" class="$m2">$gasconsumption</a></div>
    </div>
    EOT;
}
?>
