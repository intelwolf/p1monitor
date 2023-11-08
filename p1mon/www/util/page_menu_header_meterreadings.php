<?php

function page_menu_header_meterreadings( $id ) {
    $m0=$m1='';

    $text_gas_water = strIdx( 516 );

    switch ($id) {
        case 0: 
            $m0 = "menu-active";
            break;
        case 1:
            $m1 = "menu-active";
            break;
        default:
        /* default value so always a menu is available */
        $m0="menu-active";
    }
    echo <<< EOT
    <div class="pad-13 content-wrapper">
        <div class="pos-7 content-wrapper $m0"><a href="meterreadings-d-kwh.php" class="$m0">kWh</a></div>
        <div class="pos-7 content-wrapper $m1"><a href="meterreadings-d-m3.php"  class="$m1">$text_gas_water</a></div>
    </div>
    EOT;
}
?>
