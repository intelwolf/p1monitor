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
var alive_cnt = 0;

function readJsonApiSmartMeter(){ 
    $.getScript( "./api/v1/smartmeter?limit=1", function( data, textStatus, jqxhr ) {
      try {
        if (typeof data !== 'undefined') {
                    var count = Object.keys(data).length;
                    if ( count > 32 ) { // ok 
                        //console.log('alive count=' + alive_cnt);
                        alive_cnt+=1;
                        if (alive_cnt > 30) {
                            window.location="/home.php";
                        }
                    }
                }
      } catch(err) {}
   });
}

 
	function loadData() {
		clearTimeout(initloadtimer);
		//console.log('check');
		
		if ( $('#indicator').hasClass('color-ok') ) {
			$('#indicator').removeClass('color-ok');
			$('#indicator').addClass('color-warning');
		} else {
			$('#indicator').removeClass('color-warning');
			$('#indicator').addClass('color-ok');
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
   <center>
		<img id='logo' alt="ztatz logo" src="./img/p1mon-logo.svg" width="512" height="512">
   </center>
</body>
</html>
