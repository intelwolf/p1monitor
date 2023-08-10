<?php
function page_menu_header_fase( $id ) {
    $m0=$m1=$m2=$m3=$m4='';

    $current = strIdx(343);
    $history = strIdx(344);

    switch ($id) {
        case 0: /* actueel*/
            $m0= "menu-active";
            break;
        case 1: /* historie */
            $m1 = "menu-active";
            break;
        case 2: /* uiterste Watt */
            $m2 = "menu-active";
            break;
        case 3: /* uiterste Amperage */
            $m3 = "menu-active";
            break;
        case 4: /* uiterste Volt */
            $m4 = "menu-active";
            break;

        default:
        /* default value so always a menu is available */
        $m0="menu-active";
    }

    echo "<div class=\"pad-13 content-wrapper\">";
    echo "    <div class=\"pos-7 content-wrapper $m0\"><a href=\"fase-a.php\" class=\"$m0\">$current</a></div>";
    echo "    <div class=\"pos-7 content-wrapper $m1\"><a href=\"fase-historie.php\" class=\"$m1\">$history</a></div>";
    echo "    <div class=\"pos-7 content-wrapper $m2\"><a href=\"fase-uiterste-d-w.php\" class=\"$m2\"><i class='fas fa-xs fa-rotate-90 fa-arrows-left-right-to-line'></i> W</a></div>";
    echo "    <div class=\"pos-7 content-wrapper $m3\"><a href=\"fase-uiterste-d-a.php\" class=\"$m3\"><i class='fas fa-xs fa-rotate-90 fa-arrows-left-right-to-line'></i> A</a></div>";
    echo "    <div class=\"pos-7 content-wrapper $m4\"><a href=\"fase-uiterste-d-v.php\" class=\"$m4\"><i class='fas fa-xs fa-rotate-90 fa-arrows-left-right-to-line'></i> V</a></div>";
    echo "</div>";

}
?>
