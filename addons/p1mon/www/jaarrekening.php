<?php

/**********************************************
 *                                            *
 *            Opmaken Jaarrekening          *
 *             door Edwin Lakeman             *
 *                                            *
 *         Gebaseerd op data uit P1mon        *
 *                                            *
 *********************************************/
$titel      = 'Jaarrekening.';
$versie     = '1.1';

// Default settings
$p1monIP = '127.0.0.1';
$datumlayout = 1;
$gasweergeven = 1;
$hoog = 'Piek';
$laag = 'Dal';
$checklaatsteversie = 1;
$topicurl = 'https://forum.p1mon.nl/viewtopic.php?t=796';

// Overwrite settings
include 'settings.php';

if ($checklaatsteversie) {
    $laatsteversie = file_get_contents("http://www.etq.nl/p1monver.php?v=$versie");
}


/************************************************************
 *                 startdatum contract doorgeven            *
 *                  of jaaroverzicht weergeven              *
 ***********************************************************/
// voorbeeld : kosten.php?s=2023-10-01
if (isset($_GET["s"])) {
    $startdatum = $_GET["s"];
}
$eindcontract = eenjaarverder($startdatum, '+1 year');

// Jaaroverzicht ?
if (isset($_GET["jaar"])) {
    if ($_GET["jaar"] == '1') {
        $startdatum = eenjaarverder(date('Y-m-d'), '-1 year');
    }
}


/************************************************************
 *                Datum en titels formatteren               *
 ***********************************************************/
switch ($datumlayout) {
    case 1:
        $df = 'Y-m-d';
        break;
    case 2:
        $df = 'd-m-Y';
        break;
    case 3:
        $df = 'j M Y';
        break;
}
$startdatumtitel   = date_format(date_create($startdatum), $df);
$eindcontracttitel = date_format(date_create($eindcontract), $df);

$veld       = [
    "T1: Verbruik $laag",
    "T2: Verbruik $hoog",
    "T3: Produktie $laag",
    "T4: Produktie $hoog",
    "TG: Gasverbruik"
];


/************************************************************
 *                       Functies                           *
 ***********************************************************/
function eenjaarverder($contractdatum, $periode)
{
    $vandaag = date_create(date('Y-m-d'));      // datum van vandaag
    $inputDate = date_create($contractdatum);
    $inputDate->modify($periode);              // tel er jaar bij op
    if ($inputDate > $vandaag) {                // als datum in de toekomst is, dan datum van vandaag gebruiken
        return date_format($vandaag, 'Y-m-d');
    }
    return date_format($inputDate, 'Y-m-d');
}


/************************************************************
 *                       Start HTML                         *
 ***********************************************************/
echo "<!DOCTYPE HTML>";
echo "
<html>
<head>
   <title>" . $titel . " V" . $versie . "</title>
</head>        
<body style='font-family: monospace'>\n";
if ($checklaatsteversie) {
    if ($versie <> $laatsteversie) {
        echo "Huidige versie: V$versie<br>\nUpdate V$laatsteversie beschikbaar.<br>\nKijk <a href='$topicurl'>hier</a> voor meer informatie.<br><br>\n";
    }
}

//URLs voor diverse overzichten
echo "Maak een keuze:<br>\n<ul>\n";
echo "  <li>\n      <a href='jaarrekening.php?s=" . $_GET['s'] . "'>Contractoverzicht</a><br>\n    </li>\n";  //Start contractdatum
echo "  <li>\n      <a href='jaarrekening.php?s=" . $_GET['s'] . "&jaar=1'>Jaaroverzicht</a><br>\n </li>\n";   //Jaaroverzicht
echo "</ul>\n\n";

echo "<table style='background-color:#EEEEEE; padding: 10px'><tr><td>\n";


/*************************************
 *            Huidige stand          *
 ************************************/
$nu         = date('Y-m-d');
$urlnu = "http://$p1monIP/api/v1/powergas/day?limit=1&sort=asc&json=object&round=on&starttime=$nu";
$nudata = file_get_contents($urlnu);
$decdata = json_decode($nudata, false);
//echo 'Huidige PHP versie: ' . phpversion();
echo "
<!--*************************************
*              Huidige stand            *
**************************************-->\n";
echo "<table style='border:1px solid black; padding: 10px' width=100%>\n";
echo "<tr><td><b>Huidige tellerstanden</b></td></tr>\n";
echo "   <tr>\n      <td>$veld[0]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $decdata[0]->CONSUMPTION_KWH_LOW .  " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[1]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $decdata[0]->CONSUMPTION_KWH_HIGH . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[2]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $decdata[0]->PRODUCTION_KWH_LOW .   " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[3]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $decdata[0]->PRODUCTION_KWH_HIGH .  " kWh</td>\n   </tr>\n";
if ($gasweergeven)
    echo "   <tr>\n      <td>$veld[4]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $decdata[0]->CONSUMPTION_GAS_M3 .   " m&#179;&nbsp;</td>\n   </tr>\n";
echo "</table>\n\n";
echo "<br>\n\n";


/*************************************
 *             Startstand       *
 ************************************/
echo "
<!--*************************************
*               Startstand              *
**************************************-->\n";
$urlstart = "http://$p1monIP/api/v1/powergas/day?limit=1&sort=asc&json=object&round=on&starttime=$startdatum";
$startdata = file_get_contents($urlstart);
$decdata = json_decode($startdata, false);
$startstamp = $decdata[0]->TIMESTAMP_lOCAL;
$scl = $decdata[0]->CONSUMPTION_KWH_LOW;
$sch = $decdata[0]->CONSUMPTION_KWH_HIGH;
$spl = $decdata[0]->PRODUCTION_KWH_LOW;
$sph = $decdata[0]->PRODUCTION_KWH_HIGH;
$scg = $decdata[0]->CONSUMPTION_GAS_M3;;

echo "<br><b>Periode : $startdatumtitel tot $eindcontracttitel</b><br>\n";
echo "<b>Tellerstanden</b><br>\n";
echo "<table style='border:1px solid black; padding: 10px' width=100%>\n";
echo "<tr><td><b>Beginstand op $startdatumtitel</b></td></tr>\n";
echo "   <tr>\n      <td>$veld[0]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $scl . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[1]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $sch . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[2]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $spl . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[3]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $sph . " kWh</td>\n   </tr>\n";
if ($gasweergeven)
    echo "   <tr>\n      <td>$veld[4]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $scg . " m&#179;&nbsp;</td>\n   </tr>\n";
echo "</table>\n\n";
echo "<br>";


/*************************************
 *               Eindstand           *
 *************************************/
echo "
<!--*************************************
*                Eindstand              *
**************************************-->\n";

$urleind = "http://$p1monIP/api/v1/powergas/day?limit=1&sort=asc&json=object&round=on&starttime=$eindcontract";
$einddata = file_get_contents($urleind);
$decdata = json_decode($einddata, false);
$eindstamp = $decdata[0]->TIMESTAMP_lOCAL;
$ech = $decdata[0]->CONSUMPTION_KWH_HIGH;
$eph = $decdata[0]->PRODUCTION_KWH_HIGH;
$ecl = $decdata[0]->CONSUMPTION_KWH_LOW;
$epl = $decdata[0]->PRODUCTION_KWH_LOW;
$ecg = $decdata[0]->CONSUMPTION_GAS_M3;

echo "<!-- Eindstand -->\n";
echo "<table style='border:1px solid black; padding: 10px' width=100%>\n";
echo "<tr><td><b>Eindstand op $eindcontracttitel</b></td></tr>\n";
echo "   <tr>\n      <td>$veld[0]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $ecl . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[1]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $ech . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[2]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $epl . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[3]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $eph . " kWh</td>\n   </tr>\n";
if ($gasweergeven)
    echo "   <tr>\n      <td>$veld[4]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $ecg . " m&#179;&nbsp;</td>\n   </tr>\n";
echo "</table>\n\n";
echo "<br>\n";

/*************************************
 *          Netto resultaten         *
 ************************************/
echo "
<!--*************************************
*             Netto resultaten          *
**************************************-->\n";
echo "<br><b>Periode : $startdatumtitel tot $eindcontracttitel</b><br>\n";
echo "<b>Berekeningen</b><br>\n";
echo "<table style='border:1px solid black; padding: 10px' width=100%>\n";
echo "<tr><td><b>Netto resultaten</b></td></tr>\n";
echo "   <tr>\n      <td>$veld[0]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . ($ecl - $scl) . " kWh</td>\n    </tr>\n";
echo "   <tr>\n      <td>$veld[1]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . ($ech - $sch) . " kWh</td>\n    </tr>\n";
echo "   <tr>\n      <td>$veld[2]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . ($epl - $spl) . " kWh</td>\n    </tr>\n";
echo "   <tr>\n      <td>$veld[3]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . ($eph - $sph) . " kWh</td>\n    </tr>\n";
if ($gasweergeven)
    echo "   <tr>\n      <td>$veld[4]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . ($ecg - $scg) . " m&#179;&nbsp;</td>\n    </tr>\n";
echo "   <tr>\n      <td></td>\n      <td>" . "</td>\n    </tr>\n";
echo "   <tr>\n      <td>Netto $hoog Verbr-Prod</td>\n      <td>: </td>\n      <td style='text-align: right'>" . (($ech - $sch) - ($eph - $sph)) . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>Netto $laag Verbr-Prod</td>\n      <td>: </td>\n      <td style='text-align: right'>" . (($ecl - $scl) - ($epl - $spl)) . " kWh</td>\n   </tr>\n";
if ($gasweergeven)
    echo "   <tr>\n      <td>Gas Verbruik</td>\n      <td>: </td>\n      <td style='text-align: right'>" . ($ecg - $scg) . " m&#179;&nbsp;</td>\n   </tr>\n";
echo "<table>\n\n";
echo "<br>\n";

/*************************************
 *                Totalen            *
 ************************************/
echo "
<!--*************************************
*                 Totalen               *
**************************************-->\n";
echo "<table style='border:1px solid black; padding: 10px' width=100%>\n";
echo "<tr><td><b>Totalen elektriciteit</b></td></tr>\n";
echo "   <tr>\n      <td>Verbruik $hoog+$laag</td>\n      <td>: </td>\n      <td style='text-align: right'>"   . (($ech - $sch) + ($ecl - $scl)) . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>Produktie $hoog+$laag</td>\n      <td>: </td>\n      <td style='text-align: right'>"  . (($eph - $sph) + ($epl - $spl)) . " kWh</td>\n   </tr>\n";
echo "</table>\n\n";
echo "<br>\n";

/*************************************
 *            Totaal score           *
 ************************************/
echo "
<!--*************************************
*                Eindstand              *
**************************************-->\n";
echo "<table style='border:1px solid black; padding: 10px' width=100%>\n";
echo "<tr><td><b>Eindstand</b></td></tr>\n";
echo "   <tr>\n      <td>Totaal verbruik</td>\n      <td>: </td>\n      <td style='text-align: right'>" . ((($ech - $sch) + ($ecl - $scl)) - (($eph - $sph) + ($epl - $spl))) . " kWh</td>\n   </tr>\n";
if ($gasweergeven)
    echo "   <tr>\n      <td>Gas</td>\n           <td>: </td>\n      <td style='text-align: right'>"  . ($ecg - $scg) .  " m&#179;&nbsp;</td>\n   </tr>\n";
echo "</table>\n";


/*************************************
 *               The End             *
 ************************************/
echo "<br></td></tr></table></body>\n</html>";


/************************************
 *              Versies             *
 ************************************

 V1.1 29-5-2024
   Voor het overzicht kun je nu kiezen uit contractoverzicht of jaaroverzicht.

 V1.03 8-5-2024
   Aankondiging beschikbaarheid nieuwe versie.

V1.02 8-5-2024
   Default settings gebruiken indien settings.php ontbreekt of geen waarde bevat.
   M^3 gas weergeven als m³.
   Code cleanup.
   Naam gewijzigd naar 'jaarrekening.php'.

V1.02 8-5-2024
   Default settings gebruiken indien settings.php ontbreekt of geen waarde bevat.
   M^3 gas weergeven als m³.
   Code cleanup.
   Naam gewijzigd naar 'jaarrekening.php'.

V1.01 7-5-2024
    Settings naar externe file.
    Gas wel of niet tonen.
    Datumlayout inatelbaar.

V0.97 2024-03-25
    Berekent einddatum contract.
        Indien start langer dan een jaar geleden, dan is einddatum de startdatum + 1 jaar.
        Anders wordt er met 'vandaag' gerekend.
    Startdatum op te geven als parameter in URL:
        afrekening.php?s=2023-10-01
    Benaming Hoog/Laag instelbaar.
    Layout aangepast.

 */
