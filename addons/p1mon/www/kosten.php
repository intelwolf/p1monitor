<?php

/**********************************************
 *                                            *
 *            Opmaken eindafrekening          *
 *             door Edwin Lakeman             *
 *                                            *
 *         Gebaseerd op data uit P1mon        *
 *                                            *
 *********************************************/
$titel      = ' De jaar afrekening ';
$versie     = ' 1.00';

/**********************************************************
 *            Vul hier het IP adres in van P1mon          *
 *********************************************************/
//$p1monIP    = '192.168.1.22';  <-- voorbeeld
$p1monIP    = '127.0.0.1';


/************************************************************
 *                 startdatum contract doorgeven            *
 ***********************************************************/
// voorbeeld : kosten.php?s=2023-10-01
if (isset($_GET["s"])) {
    $startdatum = $_GET["s"];
$eindcontract = eenjaarverder($startdatum);
$input = $startdatum; 
$startdatum = strtotime($input); 
//echo date('Y-m-d', $startdatum); 
$startdatum =date('Y-m-d', $startdatum);
}

if (isset($_GET["s"])) {
    $startdatum1 = $_GET["s"];;
$nleindcontract = nleenjaarverder($startdatum1);
$input = $startdatum1; 
$nlstartdatum = strtotime($input); 
//echo date('d-m-Y', $nlstartdatum); 
$nlstartdatum =date('d-m-Y', $nlstartdatum);
}

$hoog = 'Hoog';
$laag = 'Laag';
$veld       = [
    "Verbruik &nbsp;$laag",
    "Verbruik &nbsp;$hoog",
    "Produktie $laag",
    "Produktie $hoog",
    "Gas"
];
/************************************************************
 *                       Functies                           *
 ***********************************************************/
function eenjaarverder($contractdatum)
{
    $vandaag = date_create(date('Y-m-d')); // datum van vandaag
    $inputDate = date_create($contractdatum);
    $inputDate->modify('+1 year'); // tel er jaar bij op
    if ($inputDate > $vandaag) { // als datum in de toekomst is, dan datum van vandaag gebruiken
        return date_format($vandaag, 'Y-m-d');
    }
    return date_format($inputDate, 'Y-m-d');
    }
function nleenjaarverder($nlcontractdatum)
{
    $nlvandaag = date_create(date('d-m-Y')); // datum van vandaag
    $nlinputDate = date_create($nlcontractdatum);
    $nlinputDate->modify('+1 year'); // tel er jaar bij op
    if ($nlinputDate > $nlvandaag) { // als datum in de toekomst is, dan datum van vandaag gebruiken
        return date_format($nlvandaag, 'd-m-Y');
    }
    return date_format($nlinputDate, 'd-m-Y');
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
<body style='font-family: monospace'>
<table style='background-color:#EEEEEE; padding: 4px'><tr><td>\n\n";
/*************************************
 *            Huidige stand          *
 ************************************/
$nu         = date('Y-m-d');
$nlnu         = date('d-m-Y');
$urlnu = "http://$p1monIP/api/v1/powergas/day?limit=1&sort=asc&json=object&round=on&starttime=$nu";
$nudata = file_get_contents($urlnu);
$decdata = json_decode($nudata, false);
//echo 'Huidige PHP versie: ' . phpversion() ." <tr><td>\n\n";
//echo $titel ." Versie ". $versie;"
//echo 
//echo "
echo "<table style='border:1px solid with; padding: /2px' width=100%>\n";"
<!--*************************************
*              Huidige stand            *
**************************************-->\n";
echo "<table style='border:1px solid black; padding: -1px' width=100%>\n";
echo "<td style='text-align: center'><b>Datum verwerking $nlnu</b></td></tr>\n";
echo "<td style='text-align: center'><b>Huidige tellerstanden</b></td></tr>\n";
echo "<table style='border:1px solid black; padding: 1px' width=100%>\n";
echo "   <tr>\n      <td>$veld[0]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $decdata[0]->CONSUMPTION_KWH_LOW .  " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[1]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $decdata[0]->CONSUMPTION_KWH_HIGH . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[2]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $decdata[0]->PRODUCTION_KWH_LOW .   " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[3]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $decdata[0]->PRODUCTION_KWH_HIGH .  " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[4]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $decdata[0]->CONSUMPTION_GAS_M3. " m3&nbsp;</td>\n  </tr>\n";
echo "</table>\n";
/*************************************
 *             Startstand       *
 ************************************/
echo "<table style='border:1px solid with; padding: 1px' width=10%>\n";"
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
$sgas = $decdata[0]->CONSUMPTION_GAS_M3;
echo "<table style='border:1px solid with; padding: 1px' width=10%>\n";
echo "<b>Periode: $nlstartdatum tot $nleindcontract</b>";
echo "<table style='border:1px solid black; padding: 0,1px' width=100%>\n";
echo "<td style='text-align: center'><b>Tellerstanden</b></td></tr>\n";
//echo "<table style='border:1px solid black; padding: 0,1px' width=100%>\n";
echo "<td style='text-align: center'><b>Beginstand op $nlstartdatum</b></td></tr>\n";
echo "<table style='border:1px solid black; padding: 1px' width=100%>\n";
echo "   <tr>\n      <td>$veld[0]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $scl . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[1]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $sch . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[2]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $spl . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[3]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $sph . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[4]</td>\n      <td>: </td>\n      <td style='text-align: right'>" .$sgas . " m3&nbsp;</td>\n   </tr>\n";
echo "</table>\n\n";
//echo "<br>";
/*************************************
 *               Eindstand           *
 *************************************/
echo "<table style='border:1px solid with; padding: 2px' width=100%>\n"; "
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
$egas = $decdata[0]->CONSUMPTION_GAS_M3;
echo "<!-- Eindstand -->\n";
echo "<table style='border:1px solid black; padding: 1px' width=100%>\n";
echo "<td style='text-align: center'><b>Eindstand op $nleindcontract</b></td></tr>\n";
echo "<table style='border:1px solid black; padding: 0.1px' width=100%>\n";
echo "   <tr>\n      <td>$veld[0]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $ecl . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[1]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $ech . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[2]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $epl . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[3]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . $eph . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>$veld[4]</td>\n      <td>: </td>\n      <td style='text-align: right'>"  . $egas . " m3&nbsp</td>\n   </tr>\n";
echo "</table>\n\n";
/*************************************
 *          Netto resultaten         *
 ************************************/
echo "<table style='border:1px solid with; padding: 1px' width=100%>\n"; "
<!--*************************************
*             Netto resultaten          *
**************************************-->\n";
echo "<table style='border:1px solid with; padding: 1px' width=100%>\n";
//echo "<br>";
//echo "<br><b>Periode: $nlstartdatum tot $nleindcontract</b><br>\n";
echo "<table style='border:1px solid black; padding: 0,1px' width=100%>\n";
echo "<td style='text-align:center'><b>Berekeningen</b></td></tr>\n";
echo "<table style='border:1px solid black; padding: 0,1px' width=100%>\n";
echo "<td style='text-align: center'><b>Netto resultaat op $nleindcontract</b></td></tr>\n";
echo "<table style='border:1px solid black; padding: 0.1px' width=100%>\n";
echo "   <tr>\n      <td>$veld[0]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . ($ecl - $scl) . " kWh</td>\n    </tr>\n";
echo "   <tr>\n      <td>$veld[1]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . ($ech - $sch) . " kWh</td>\n    </tr>\n";
echo "   <tr>\n      <td>$veld[2]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . ($epl - $spl) . " kWh</td>\n    </tr>\n";
echo "   <tr>\n      <td>$veld[3]</td>\n      <td>: </td>\n      <td style='text-align: right'>" . ($eph - $sph) . " kWh</td>\n    </tr>\n";
echo "   <tr>\n      <td></td>\n      <td>" . "</td>\n    </tr>\n";
echo "   <tr>\n      <td>Netto $laag Verbr-Prod</td>\n      <td>: </td>\n      <td style='text-align: right'>" . (($ecl - $scl) - ($epl - $spl)) . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>Netto $hoog Verbr-Prod</td>\n      <td>: </td>\n      <td style='text-align: right'>" . (($ech - $sch) - ($eph - $sph)) . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>Gas gebruikt</td>\n      <td>: </td>\n      <td style='text-align: right'>" . ($egas - $sgas) . " m3&nbsp</td>\n   </tr>\n";
echo "<table>\n";
//echo "<br>\n";
/*************************************
 *                Totalen            *
 ************************************/
echo "<table style='border:1px solid with; padding: 2px' width=100%>\n"; "
<!--*************************************
*                 Totalen               *
**************************************-->\n";
echo "<table style='border:1px solid black; padding: 1px' width=100%>\n";
echo "<td style='text-align:center'><b>Totalen op $nleindcontract</b></td></tr>\n";
echo "<table style='border:1px solid black; padding: 1px' width=100%>\n";
echo "   <tr>\n      <td>Verbruik &nbsp;$laag+$hoog</td>\n      <td>: </td>\n      <td style='text-align: right'>"   . (($ech - $sch) + ($ecl - $scl)) . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>Produktie $laag+$hoog</td>\n      <td>: </td>\n      <td style='text-align: right'>"  . (($eph - $sph) + ($epl - $spl)) . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>Totaal Gasverbruik</td>\n        <td>:  </td>\n <td style='text-align: right'> " . ($egas - $sgas) . " m3&nbsp</td>\n </tr>\n";
echo "</table>\n\n";
//echo "<br>\n";
/*************************************
 *            Totaal score           *
 ************************************/
echo "<table style='border:1px solid with; padding: 2px' width=100%>\n"; "
<!--*************************************
*                Eindstand              *
**************************************-->\n";
echo "<table style='border:1px solid black; padding: 1px' width=100%>\n";
echo "<td style='text-align:center'><b>Eindstand</b></td></tr>\n";
echo "<table style='border:1px solid black; padding: 1px' width=100%>\n";

echo "   <tr>\n      <td>Totaal verbruik</td>\n      <td>: </td>\n  <td style='text-align: right'>" . ((($ech - $sch) + ($ecl - $scl)) - (($eph - $sph) + ($epl - $spl))) . " kWh</td>\n   </tr>\n";
echo "   <tr>\n      <td>Totaal Gasverbruik</td>\n   <td>: </td>\n  <td style='text-align: right'> " . ($egas - $sgas) . " m3&nbsp";
echo "</table>\n";
//echo "</td>\n   </tr>\n</td>\n <td style='text-align: center'>".'Huidige PHP versie: ' . phpversion() ." <tr><td>\n\n";
//echo "</td>\n   </tr>\n</td>\n <td style='text-align: center'>  $titel  Versie  $versie  <tr><td>\n\n";
echo "</table>";
/*************************************
 *               The End             *
 ************************************/
echo "<br></td></tr></table></body>\n</html>";
/*************************************
 *              Versies              *
 ************************************
V0.97 2024-03-25

Berekent einddatum contract.
    Indien start langer dan een jaar geleden, dan is einddatum de startdatum + 1 jaar.
    Anders wordt er met 'vandaag' gerekend.

Startdatum op te geven als parameter in URL:
    afrekening.php?s=2023-10-01

Benaming Hoog/Laag instelbaar.  &nbsp &nl2br

Layout aangepast.

 */
