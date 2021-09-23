<!doctype html>
<html>
<head>
<meta name="robots" content="noindex">
<title>P1 monitor</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css" />

<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>
<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
</head>
<body id='logo'>
<script>
var initloadtimer
var alive_cnt_max = 50;
var alive_cnt = alive_cnt_max 

function readJsonApiSmartMeter(){ 

    --alive_cnt;

    $.getScript( "./api/v1/smartmeter?limit=1", function( data, textStatus, jqxhr ) {
    try {
            if (typeof data !== 'undefined') {
                var count = Object.keys(data).length;
                alive_cnt = alive_cnt_max  
            }
        } catch(err) {
        }
   });
}

 
    function loadData() {
        clearTimeout(initloadtimer);
    
        if ( alive_cnt > 10 ) {
            console.log( "alive_cnt=" + alive_cnt )
            if ( $('#indicator').hasClass('color-ok') ) {

                $('#indicator').removeClass('color-ok');
                $('#indicator').addClass('color-warning');
            } else {
                $('#indicator').removeClass('color-warning');
                $('#indicator').addClass('color-ok');
            }
        } else {
                $('#indicator').removeClass('fa fa-spinner fa-pulse');
                $('#indicator').addClass('fas fa-power-off');
                $('#indicator').removeClass('color-warning');
                $('#indicator').addClass('color-ok');
                $('#text').html("De rpi is bijna klaar met de shutdown");
        }
        if ( alive_cnt < -5 ) {
            $('#indicator').removeClass('color-warning');
            $('#indicator').addClass('color-text');
            $('#text').html("Als de groene led op de RPI niet meer knippert dan is de shutdown gereed.");
        }


        readJsonApiSmartMeter();
        
        initloadtimer = setInterval(function(){loadData();}, 1000);
    }
    
    $(function () {
        loadData();
    });
    
</script>
  <p></p>
   <center><i id="indicator" class="fa fa-spinner fa-pulse fa-3x fa-fw" aria-hidden="true"></i></center>
   <p></p>
   <p></p>
   <center>
       <div id="text" class="text-30">Een moment a.u.b. Shutdown wordt uitgevoerd.<div>
   </center>
   <center>
        <img id='logo' alt="ztatz logo" src="./img/p1mon-logo.svg" width="512" height="512">
   </center>
   
</body>
</html>
