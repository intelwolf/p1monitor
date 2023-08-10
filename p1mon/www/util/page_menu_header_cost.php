<?php
function page_menu_header_cost($id) {
    
    $m0=$m1=$m2=$m3=$m4=$m5='';

    $text_days   = strIdx( 122 );
    $text_months = strIdx( 123 );
    $text_years  = strIdx( 124 );

    switch ($id) {
        case 0: 
            $m0= "menu-active";
            break;
        case 1:
            $m1 = "menu-active";
            break;
        case 2:
            $m2= "menu-active";
            break;
        case 3:
            $m3= "menu-active";
            break;
        default:
        /* default value so always a menu is available */
        $m0="menu-active";    
    }

    echo "<div class='pad-13 content-wrapper'>\n";
    echo "<div class='pos-7 content-wrapper $m0'><a href='kosten-d.php' class='$m0'>$text_days</a></div>\n";
    echo "<div class='pos-7 content-wrapper $m1'><a href='kosten-m.php' class='$m1'>$text_months</a></div>\n";
    echo "<div class='pos-7 content-wrapper $m2'><a href='kosten-j.php' class='$m2'>$text_years</a></div>\n";
    if ( config_read(204) != 0 ) {
        echo "<div class='pos-7 content-wrapper $m3'><a href='kosten-dynamic-h.php' class='$m3'>dynamisch tarieven</a></div>\n";
    }
    echo "</div>\n";
}
?>
