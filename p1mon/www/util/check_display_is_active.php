<?php
function checkDisplayIsActive($id) {
if ( config_read($id) == 0 ) {

echo <<< EOT
<!doctype html>
<html lang="nl">
<title>P1 monitor scherm gedactiveerd</title>
<link type="text/css" rel="stylesheet" href="./css/p1mon.css">
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css">

<script src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/p1mon-util.js"></script>

</head>
<body>
<div id="dialog" class="display-nonex">	
	Scherm gedeactiveerd.<br><br>
	Activeren via configuratie optie display.<br><br>
	<button onclick="window.location.href = 'home.php'" class="input-2 but-1" name="submit" type="submit" value="go_home">
		<i class="color-settings fa fa-3x fas fa-home"></i>
		<span class="color-settings text-7">home</span>
	</button>
</div>
</body>
<script>
$(document).ready(function () {
    centerPosition('#dialog');
    //showStuff('dialog');
});
</script>
</html>
EOT;
return false;	
} 
return true;
}
?>
