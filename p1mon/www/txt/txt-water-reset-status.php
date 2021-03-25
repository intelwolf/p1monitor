<?php
$filename = '/p1mon/mnt/ramdisk/watermeter-counter-reset.status';
$fh = fopen($filename,'r') or die("Geen informatie beschikbaar<br>");
while ($line = fgets($fh)) {
    echo str_replace(array("\r", "\n"), '<br>', $line);
}
fclose($fh);
?>