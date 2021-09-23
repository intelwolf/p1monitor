<?php 
include_once '/p1mon/www/util/config_read.php';
?>
<!doctype html>
<html lang="nl">
<head>
<meta name="robots" content="noindex">
<title>P1 monitor screensaver</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css"     rel="stylesheet"    href="./css/p1mon.css" />
<link type="text/css"     rel="stylesheet"    href="./font/roboto/roboto.css"/>
<script defer src="./font/awsome/js/all.js"></script>
<script defer src="./js/p1mon-util.js"></script>
<script src="./js/jquery.min.js"></script>
</head>
<body id='logo'>
<script>
    var initloadtimer
    var delay_counter = parseInt( <?php echo config_read(80);?>); //default sec before returing to previous screen.

    function readJsonApiweather() {
		$.getScript( "./api/v1/weather?limit=1", function( data, textStatus, jqxhr ) {
			try {
				weaterData = JSON.parse(data);
                document.getElementById("weather_info_location").innerHTML = weaterData[0][3];
                document.getElementById("weather_info").innerHTML = weaterData[0][4].toFixed(1) + '&deg;C&nbsp;' + weaterData[0][5];
				} catch(err) {
                    console.log( err )
                }
        });
    }

    function goBack() { // check go to home when there is no history.
        returPathUrl = getLocalStorage( 'screensaver-href' );
        if (returPathUrl == null ) { // set default path as failsave
            returPathUrl = location.protocol + "//" + location.host + "/home.php";
        }
        //console.log ( "returPathUrl=" +  returPathUrl );
        window.location.assign( returPathUrl );
    }

    function loadData() {
        //console.log ( "delay_counter(init)=" + delay_counter )
        clearTimeout(initloadtimer);
        if ( delay_counter > 0 ) {
            delay_counter--;
            //console.log ( "delay_counter=" + delay_counter )
            if ( delay_counter == 0 ) {
                //console.log ( "screenSaverTimeout reset end of timer" ); 
                goBack(); 
            }
        }

        readJsonApiweather();

        var today = new Date();
        var date = today.getFullYear() + '-' + zeroPad((today.getMonth()+1),2) + '-' + zeroPad(today.getDate(),2);
        var time = zeroPad(today.getHours(),2) + ":" + zeroPad(today.getMinutes(),2)  + ":" + zeroPad(today.getSeconds(),2);
        document.getElementById("timestamp_logo").innerHTML = date + ' ' + time;

        if ( today.getSeconds() % 10 == 0) { // shift every 10 seconds
            document.getElementById("block_1").style.top  = randomIntFromInterval(0, Math.abs( window.innerHeight-656 ) )+"px"; // including top text.
            document.getElementById("block_1").style.left = randomIntFromInterval(0, Math.abs( window.innerWidth-512 ) )+"px";
        }
        initloadtimer = setInterval(function(){loadData();}, 1000);
    }

    $(function () {
        loadData();
        document.addEventListener('mouseover', function(){
            //console.log ( "screenSaverTimeout reset (mouseover)." );
            goBack();
        });

    });

</script>
    <div id="block_1" class="pos-50">
        <div id='weather' class="content-wrapper">
            <div id="weather_info_location" class="text-26"></div>
            <div id="weather_info" class="text-26"></div>
            <div id="timestamp_logo" class="text-26"></div>
            <img id='logo_img' alt="ztatz logo" src="./img/p1mon-logo.svg" width="512" height="512">
        </div>
        
    </div>
</body>
</html>
