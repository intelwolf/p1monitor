<?php
function page_menu_header_watermeter( $id ) {

    $m0=$m1=$m2=$m3=$m4='';

    $text_minutes   = strIdx( 120 );
    $text_hours     = strIdx( 121 );
    $text_days      = strIdx( 122 );
    $text_months    = strIdx( 123 );
    $text_years     = strIdx( 124 );

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
<div class="pos-7 content-wrapper $m4"><a href="watermeter-min.php" class="$m4">$text_minutes</a></div>
<div class="pos-7 content-wrapper $m0"><a href="watermeter-h.php" class="$m0">$text_hours</a></div>
<div class="pos-7 content-wrapper $m1"><a href="watermeter-d.php" class="$m1">$text_days</a></div>
<div class="pos-7 content-wrapper $m2"><a href="watermeter-m.php" class="$m2">$text_months</a></div>
<div class="pos-7 content-wrapper $m3"><a href="watermeter-j.php" class="$m3">$text_years</a></div>
</div>
EOT;
}
?>
