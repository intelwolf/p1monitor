<?php

function config_page_menu_header_powerproduction( $id ) {

$m0=$m1=$m2=$m3=$m4=$m5='';

switch ( $id ) {
    case 0: /* kWh S0 */
        $m0 = "menu-active";
           break;
    case 1: /* grafiek */
        $m1 = "menu-active";
        break;
    default:
    /* default value so always a menu is available */
    $m0="menu-active";
}
echo <<< EOT
<div>
    <div class="content-wrapper pad-40">
        <div class="pos-44 content-wrapper $m0"><a href="config-powerproduction.php"           class="$m0">kWh S0 puls</a></div>
        <div class="pos-44 content-wrapper $m1"><a href="config-powerproduction-solaredge.php" class="$m1">SolarEdge</a></div>
    </div>
</div>
EOT;
}
?>

