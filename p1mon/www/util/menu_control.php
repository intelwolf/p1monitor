<?php

include_once '/p1mon/www/util/textlib.php';

function menu_control($id) {
    $m1=$m1=$m2=$m3=$m4=$m5=$m6=$m7=$m8=$m9=$m10=$m11=$m12=$m13=$m14=$m15=$m16=$m17='';
    
    switch ($id) {
        case 1: /* tarieven */
            $m1="menu-active-control";
               break;
        case 2: /* systeem */
            $m2="menu-active-control";
            break;
        case 17: /* logs */
            $m17="menu-active-control";
            break;
        case 3: /* bestanden */
            $m3="menu-active-control";
            break;
        case 4: /* in-export */
            $m4="menu-active-control";
            break;
        case 5: /*  API */
            $m5="menu-active-control";
            break;
        case 6: /* P1 poort */
            $m6= "menu-active-control";
            break;
        case 7: /* network  */
            $m7= "menu-active-control";
            break;
        case 8: /* weer  */
            $m8= "menu-active-control";
            break;
        case 9: /* weer  */
            $m9= "menu-active-control";
            break;
        case 10: /* backup  */
            $m10= "menu-active-control";
            break;
        case 11: /* security  */
            $m11= "menu-active-control";
            break;
        case 11: /* security  */
            $m11= "menu-active-control";
            break;
        case 12: /* notification  */
            $m12= "menu-active-control";
            break;
        case 13: /* IO config  */
            $m13= "menu-active-control";
            break;
        case 14: /* MQTT config  */
            $m14= "menu-active-control";
            break;
        case 15: /* power production config  */
            $m15= "menu-active-control";
            break;
        case 16: /* watermeter config  */
            $m16= "menu-active-control";
            break;
    }
    
    echo "<div><a href=\"config-tarief.php\"    class=\"text-14 $m1\"><i class=\"fas fa-euro-sign     fa-fw\"></i><span class=\"pad-6\">" . strIdx( 208 ). "</span></a></div>"."\n";
    echo "<div><a href=\"config-systeem.php\"   class=\"text-14 $m2\"><i class=\"fas fa-server        fa-fw\"></i><span class=\"pad-6\">" . strIdx( 209 ). "</span></a></div>"."\n";
    echo "<div><a href=\"config-log.php\"       class=\"text-14 $m17\"><i class=\"far fa-list-alt     fa-fw\"></i><span class=\"pad-6\">" . strIdx( 222 ). "</span></a></div>"."\n";
    echo "<div><a href=\"config-bestanden.php\" class=\"text-14 $m3\"><i class=\"fas fa-database      fa-fw\"></i><span class=\"pad-6\">" . strIdx( 210 ). "</span></a></div>"."\n";
    echo "<div><a href=\"config-in-export.php\" class=\"text-14 $m4\"><i class=\"far fa-file-archive  fa-fw\"></i><span class=\"pad-6\">" . strIdx( 211 ). "</span></a></div>"."\n";
    echo "<div><a href=\"config-API.php\"       class=\"text-14 $m5\"><i class=\"fas fa-rss           fa-fw\"></i><span class=\"pad-6\">API</span></a></div>"."\n";
    echo "<div><a href=\"config-P1poort.php\"   class=\"text-14 $m6\"><i class=\"fas fa-bolt          fa-fw\"></i><span class=\"pad-6\">" . strIdx( 212 ). "</span></a></div>"."\n";
    echo "<div><a href=\"config-netwerk.php\"   class=\"text-14 $m7\"><i class=\"fas fa-code-branch   fa-fw\"></i><span class=\"pad-6\">" . strIdx( 213 ). "</span></a></div>"."\n";
    echo "<div><a href=\"config-weer.php\"      class=\"text-14 $m8\"><i class=\"far fa-sun           fa-fw\"></i><span class=\"pad-6\">" . strIdx( 217 ). "</span></a></div>"."\n";
    echo "<div><a href=\"config-ui.php\"          class=\"text-14 $m9\"><i class=\"fas fa-tv          fa-fw\"></i><span class=\"pad-6\">" . strIdx( 214 ). "</span></a></div>"."\n";
    echo "<div><a href=\"config-backup.php\"    class=\"text-14 $m10\"><i class=\"far fa-hdd          fa-fw\"></i><span class=\"pad-6\">" . strIdx( 215 ). "</span></a></div>"."\n";
    echo "<div><a href=\"config-security.php\"  class=\"text-14 $m11\"><i class=\"fas fa-shield-alt   fa-fw\"></i><span class=\"pad-6\">" . strIdx( 216 ). "</span></a></div>"."\n";
    echo "<div><a href=\"config-notificatie.php\"  class=\"text-14 $m12\"><i class=\"far fa-bell      fa-fw\"></i><span class=\"pad-6\">" . strIdx( 218 ). "</span></a></div>"."\n";
    echo "<div><a href=\"config-io.php\"        class=\"text-14 $m13\"><i class=\"fas fa-exchange-alt fa-fw\"></i><span class=\"pad-6\">" . strIdx( 219 ). "</span></a></div>"."\n";
    echo "<div><a href=\"config-mqtt.php\"      class=\"text-14 $m14\">

        <span class=\"fa-layers fa-gw\">
                <i class=\"fas fa-wifi fa-rotate-90\"  data-fa-transform=\"shrink-6  right-5 \"></i>
                <i class=\"fas fa-wifi fa-rotate-270\" data-fa-transform=\"shrink-6 left-5 \"></i>
        </span>
        <span class=\"pad-6\">MQTT</span>
        </a></div>"."\n";

    echo "<div><a id=\"menu_kwh\" href=\"config-powerproduction.php\" class=\"text-14 $m15\">
        <span class=\"fa-layers fa-gw\">
            <i class=\"fas fa-solar-panel\" data-fa-transform=\"shrink-0 left-0 up-0\"></i>
            <i class=\"fas fa-bolt\" data-fa-transform=\"shrink-7 right-2 up-2\"></i>
        </span>
        <span class=\"pad-6\">kWh</span>
        </a></div>"."\n";

    echo "<div><a href=\"config-water.php\" class=\"text-14 $m16\">
        <span class=\"fa-layers fa-gw\">
            <i class=\"fas fa-hand-holding-water\" data-fa-transform=\"shrink-0 left-0 up-0\"></i>
        </span>
        <span class=\"pad-6\">" . strIdx( 220 ). "</span>
        </a></div>"."\n";

    echo "<div><a href=\"home.php\"             class=\"text-14\">     <i class=\"fas fa-sign-out-alt fa-fw\"></i><span class=\"pad-6\">" . strIdx( 221 ). "</span></a></div>"."\n";
    
    echo "<script>"."\n";
    echo "if ( getLocalStorage('config-powerproduction-menu') !== null ) { $('#menu_kwh' ).attr('href', getLocalStorage('config-powerproduction-menu')); }"."\n";
    echo "</script>"."\n";

}
?>

