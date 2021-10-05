
<?php
	$command = '/p1mon/scripts/p1monExec -p "/p1mon/scripts/P1DropBoxAuth.py -u"'; 
	exec( $command ,$arr_execoutput, $exec_ret_value );
	#echo $arr_execoutput[0];
	$url = "Location: ".$arr_execoutput[0];
	#echo $url;
	header($url); /* Redirect browser */
	#header("Location: https://www.dropbox.com/oauth2/authorize?response_type=code&client_id=sefdetwey2877wd");
	#exit();
?>
