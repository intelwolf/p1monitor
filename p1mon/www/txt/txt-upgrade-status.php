<?php
$fh = fopen('/p1mon/mnt/ramdisk/upgrade-assist.status','r') or die("Geen informatie beschikbaar<br>"); 		
while ($line = fgets($fh)) {
	echo str_replace(array("\r", "\n"), '<br>', $line);  						
}
fclose($fh);
?>