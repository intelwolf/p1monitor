<?php
$filename = '/p1mon/mnt/ramdisk/patch.status';
$fh = fopen($filename,'r') or die("Even geduld aub, verwerking start over enkele seconden.<br>");
while ($line = fgets($fh)) {
    echo str_replace(array("\r", "\n"), '<br>', $line);
}
fclose($fh);
?>