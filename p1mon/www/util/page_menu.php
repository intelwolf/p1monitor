<?php
include_once '/p1mon/www/util/p1mon-password.php';
include_once '/p1mon/www/util/config_read.php';
include_once '/p1mon/www/util/textlib.php';

function page_menu($id) {
    $noInetCheck = isInternetIPAllowed();
    $localip     = validLocalIpAdress(getClientIP());
    $m0=$m1=$m2=$m3=$m4=$m5=$m6=$m7=$m8=$m9=$m10=$m11=$m12='';

    passwordSessionExpiredCheck();

    switch ($id) {
        case 0: /* home */
            $m0= "menu-active";
               break;
        case 1: /* E verbruik */
            $m1 = "menu-active";
            break;
        case 2: /* opties /setup */
            $m2= "menu-active";
            break;   
        case 3: /* info/status  */
            $m3= "menu-active";
            break;  
        case 4: /* grafiek kosten  */
            $m4= "menu-active";
            break; 
        case 5: /* gas verbruik  */
           $m5= "menu-active";
            break;   
        case 6: /* actuele verbruik  */
            $m6= "menu-active";
            break;
        case 7: /* verwarming  */
            $m7= "menu-active";
            break;
        case 8: /* meterstanden */
            $m8= "menu-active";
            break;
        case 9: /* watermeter */
            $m9= "menu-active";
            break;
        case 10: /* fase */
            $m10= "menu-active";
            break;
        case 11: /* E levering kWh (s0)*/
            $m11 = "menu-active";
            break;
        case 12: /* E levering Solar Edge */
            $m12 = "menu-active";
            break;
    }

    echo "<div class=\"menu-left\">"."\n";
    
   
    $t=strIdx(103);
    echo "<a title=\"$t\" id=\"menu0\" href=\"home.php\">
        <span class=\"fa-layers frame-1-top $m0\">
              <i class=\"fas fa-home\" data-fa-transform=\"grow-18\"></i>
        </span>
    </a>"."\n";

    $t=strIdx(104);
    if ( config_read(18) == 1 ) {
        echo "<a title=\"$t\" id=\"menu6\" href=\"e-verbruik.php\">
            <span class=\"fa-layers fa-gw frame-1-mid $m6\">
                <i class=\"fas fa-signal\" data-fa-transform=\"grow-18\"></i>
                <i class=\"far fa-clock\" data-fa-transform=\"grow-2 left-9 up-7\"></i>
            </span>
        </a>"."\n";
    }

    $t=strIdx(105);
    if ( config_read(19) == 1 ) {
        echo "<a title=\"$t\" id=\"menu1\" href=\"stats.php\">
                <span class=\"fa-layers fa-gw frame-1-mid $m1\">
                    <i class=\"fas fa-signal\" data-fa-transform=\"grow-18\"></i>
                    <i class=\"fas fa-bolt\" data-fa-transform=\"grow-6 left-8 up-7\"></i>
                </span>
        </a>"."\n";
    }

    // levering van energie kWh S0
    $t=strIdx(106);
    if ( config_read( 129 ) == 1 ) {
        echo "<a title=\"$t\" id=\"menu11\" href=\"powerproduction-min.php\">
            <span class=\"fa-layers fa-gw frame-1-mid $m11\">
                <i class=\"fas fa-signal\" data-fa-transform=\"grow-18\"></i>
                <i class=\"fas fa-solar-panel\" data-fa-transform=\"grow-4 left-0 up-7\"></i>
                <i class=\"fas fa-bolt\" data-fa-transform=\"shrink-6 left-18 up-9\"></i>
            </span>
        </a>"."\n";
    }

    // levering van energie Solar Edge API
    $t=strIdx(107);
    if ( config_read( 147 ) == 1 ) {
        echo "<a title=\"$t\" id=\"menu12\" href=\"powerproduction-api-min.php\">
            <span class=\"fa-layers fa-gw frame-1-mid $m12\">
                <i class=\"fas fa-signal\" data-fa-transform=\"grow-18\"></i>
                <i class=\"fas fa-solar-panel\" data-fa-transform=\"grow-4 left-0 up-7\"></i>
                <i class=\"fas fa-sun\" data-fa-transform=\"shrink-6 left-18 up-9\"></i>
            </span>
        </a>"."\n";
    }

    $t=strIdx(108);
    if ( config_read(20) == 1 ) {
        echo "<a title=\"$t\" id=\"menu5\" href=\"stats-h-gas.php\">
        <span class=\"fa-layers fa-gw frame-1-mid $m5\">
            <i class=\"fas fa-signal\" data-fa-transform=\"grow-18\"></i>
            <i class=\"fab fa-gripfire\" data-fa-transform=\"grow-10 left-8 up-7\"></i>
        </span>
        </a>"."\n";
    }

    // watermeter
    $t=strIdx(109);
    if ( config_read( 102 ) == 1 ) {
        echo "<a title=\"$t\" id=\"menu9\" href=\"watermeter-h.php\">
        <span class=\"fa-layers fa-gw frame-1-mid $m9\">
            <i class=\"fas fa-signal\" data-fa-transform=\"grow-18\"></i>
            <i class=\"fas fa-tint\" data-fa-transform=\"grow-5 left-8 up-7\"></i>
        </span>
        </a>"."\n";
    }

    // verwarming
    $t=strIdx(110);
    if ( config_read(46) == 1 ) { 
        echo "<a title=\"$t\" id=\"menu7\" href=\"verwarming-a.php\">
        <span class=\"fa-layers fa-gw frame-1-mid $m7\">
            <i class=\"fas fa-home\" data-fa-transform=\"grow-13 right-7\"></i>
            <i class=\"fas fa-thermometer-half \" data-fa-transform=\"grow-8 left-15 down-2\"></i>
        </span> 
        </a>"."\n";
    }

    // kosten overzicht
    $t=strIdx(111);
    if ( config_read(21) == 1 ) {
        echo "<a title=\"$t\" id=\"menu4\" href=\"kosten-d.php\">
                    <span class=\"fa-layers fa-gw frame-1-mid $m4\">
                        <i class=\"fas fa-euro-sign\" data-fa-transform=\"grow-18 left-2\"></i>
                      </span>
        </a>"."\n";
    }
    
    // meterstanden
    $t=strIdx(112);
    if ( config_read(62) == 1 ) {
        echo "<a title=\"$t\" id=\"menu8\" href=\"meterreadings-d-kwh.php\">
                <span class=\"fa-layers fa-gw frame-1-mid $m8\">
                    <i class=\"fas fa-pager\" data-fa-transform=\"grow-18\"></i>
                </span>
        </a>"."\n";
    }

    // fase informatie.
    $t=strIdx(113);
    if ( config_read(61) == 1 ) {
        echo "<a title=\"$t\" id=\"menu10\" href=\"fase-a-home.php\">
            <span class=\"fa-layers fa-gw frame-1-mid $m10\">
                <i class=\"far fa-circle\" data-fa-transform=\"grow-18\"></i>
                <i class=\"fas fa-bolt\" data-fa-transform=\"shrink-6 left-0 up-5\"></i>
                <i class=\"fas fa-bolt\" data-fa-transform=\"shrink-6 left-5 down-4 rotate-220\"></i>
                <i class=\"fas fa-bolt\" data-fa-transform=\"shrink-6 right-4 down-4 rotate-120\"></i>
            </span>
        </a>"."\n";
    }

    // informatie pagina
    $t=ucfirst(strIdx(114));
    if ( config_read(22) == 1 ) {
        echo "<a title=\"$t\" id=\"menu3\" href=\"info.php\">
                    <span class=\"fa-layers frame-1-mid $m3\">
                        <i class=\"fas fa-info-circle\" data-fa-transform=\"grow-18\"></i>
                      </span>
        </a>"."\n";
    }
    
    // tariff page
    $t=strIdx(115);
    if($localip == True or $noInetCheck == True){
        echo "<a  title=\"$t\" id=\"menu2\" href=\"config-tarief.php\">
                    <span class=\"fa-layers frame-1-bot $m2\">
                        <i class=\"fas fa-wrench\" data-fa-transform=\"grow-18\"></i>
                      </span>
        </a>"."\n";
    }

    echo "</div>"."\n";

    echo "<script>"."\n";
    echo " if ( getLocalStorage('main-menu')                !== null ) { $('#menu0' ).attr('href', getLocalStorage('main-menu'));                }"."\n";
    echo " if ( getLocalStorage('stats-menu')               !== null ) { $('#menu1' ).attr('href', getLocalStorage('stats-menu'));               }"."\n";
    echo " if ( getLocalStorage('cost-menu')                !== null ) { $('#menu4' ).attr('href', getLocalStorage('cost-menu'));                }"."\n";
    echo " if ( getLocalStorage('stats-menu-gas')           !== null ) { $('#menu5' ).attr('href', getLocalStorage('stats-menu-gas'));           }"."\n";
    echo " if ( getLocalStorage('actual-menu')              !== null ) { $('#menu6' ).attr('href', getLocalStorage('actual-menu'));              }"."\n";
    echo " if ( getLocalStorage('verwarming-menu')          !== null ) { $('#menu7' ).attr('href', getLocalStorage('verwarming-menu'));          }"."\n";
    echo " if ( getLocalStorage('watermeter-menu')          !== null ) { $('#menu9' ).attr('href', getLocalStorage('watermeter-menu'));          }"."\n";
    echo " if ( getLocalStorage('meterreadings-menu')       !== null ) { $('#menu8' ).attr('href', getLocalStorage('meterreadings-menu'));       }"."\n";
    echo " if ( getLocalStorage('fase-menu')                !== null ) { $('#menu10').attr('href', getLocalStorage('fase-menu'));                }"."\n";
    echo " if ( getLocalStorage('powerproduction-menu')     !== null ) { $('#menu11').attr('href', getLocalStorage('powerproduction-menu'));     }"."\n";
    echo " if ( getLocalStorage('powerproduction-api-menu') !== null ) { $('#menu12').attr('href', getLocalStorage('powerproduction-api-menu')); }"."\n";
    echo "</script>"."\n";
}
?>