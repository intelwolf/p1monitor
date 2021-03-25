<!doctype html>
<html lang="nl">
<head>
<title>Demo custom UI</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<script src="../js/jquery.min.js"></script>

<style>
body {
    margin: 0px;
    padding: 0px;
    width: 100%;
    height: 100%;
    background-color: #dddddd;
    color: #384042;
    font-family:Courier New;
}

h1 {
    color: #0C7DAD;
    margin-left: 10px;
    font-size: 1.5em;
} 

p {
    margin-left: 10px;
    font-size: 1.2em;
    color: #384042;
}

.waarde {
    margin-left: 10px;
    font-size: 1em;
    color: #228B22;
    display: inline-block;
    font-weight: bold;
}

.hide {
    display: none;
}

</style>

</head>
<body id='custombody'>
<script>

    function showStuff(boxid){document.getElementById(boxid).style.display="block";}
    function hideStuff(boxid){document.getElementById(boxid).style.display="none";}

    function readJsonApiSmartMeter(){ 
    $.getScript( "../api/v1/smartmeter?limit=60", function( data, textStatus, jqxhr ) {
      try {
    
        var jsondata = JSON.parse(data); 

        console.log( jsondata[0] );

        if (data != null ) {
                showStuff('dynamic_content');
                hideStuff('api_off');
                document.getElementById("t1").innerHTML = jsondata[0][0] //+ " kWh";
                document.getElementById("v3").innerHTML = jsondata[0][8]+" W";
                document.getElementById("v1").innerHTML = jsondata[0][4]+" kWh";
                document.getElementById("v2").innerHTML = jsondata[0][3]+" kWh";
        } else {
            hideStuff('dynamic_content');
            showStuff('api_off');
        }

      } catch(err) {}
   });
}


window.onload = function() {
    readJsonApiSmartMeter(); // set quick for the first time.
    initloadtimer = setInterval(function(){ readJsonApiSmartMeter();}, 4000);
};

</script>

<h1>Welkom bij de demo pagina van de persoonlijke userinterface van de P1 monitor.</h1><br>
<h1>Waarom</h1>
<p>
We kregen verzoeken om een eigen userinterface te maken en willen de P1 monitor zo flexibel<br>
als mogelijk maken. 
</p>
<h1>Hoe:</h1>
<p>
Als je in de UI config pagina de optie “eigen userinterface gebruiken” kiest dan wordt standaard<br>
de pagina /custom/p1mon.php geladen. Dit is je startpunt om een eigen UI te maken.<br>
Pas deze pagina aan naar believen.  
</p>
<h1>Toepassen</h1>
<p>
Maak alleen gebruik van de API’s en hergebruik geen middelen uit de standaard userinterface.<br>
Zoals CSS, jQuery, enz. De standaard userinterface en de JSON-calls kunnen per versie verschillen<br>
en we kunnen geen rekening  houden met alle mogelijke varianten. Dit moet je zelf beheren.
</p>
<h1>Updates</h1>
<p>
In de exportfunctie wordt geprobeerd alle bestanden en folders onder het path /p1mon/www/custom mee te nemen.<br>
Er kan geen garantie worden gegeven dat een import altijd kan lukken.  Bij een upgrade hieraan denken! 
</p>

<div id='dynamic_content' class='hide'>
<h1>Demo dynamische verwerking (auto update).</h1>
    <div class='waarde'>Tijdstip verwerking</div><div id="t1" class='waarde'></div><br>
    <div class='waarde'>Huidige verbruik electrisch vermogen</div><div id="v3" class='waarde'></div><br>
    <div class='waarde'>Meterstand dag/piek verbruik electrisch vermogen</div> <div id="v1" class='waarde'></div><br>
    <div class='waarde'>Meterstand nacht/dal verbruik electrisch vermogen</div><div id="v2" class='waarde'></div><br>
</div> 

<h1 id='api_off' class='hide'>API STAAT UIT AANZETTEN IN SETUP SCHERM</h1>
<br>
<br>
<p>
    <button type="button" onclick="document.location='../config-ui.php'"  >klik hier om naar de setup pagina's te gaan</button>
</p>
<br>
<br>
</body>
</html>
