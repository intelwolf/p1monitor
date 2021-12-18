<?php
$fh = fopen('/p1mon/mnt/ramdisk/upgrade-aide.status','r') or die("Even geduld aub.<br>");
while ($line = fgets($fh)) {
    echo str_replace(array("\r", "\n"), '<br>', $line);
}
fclose($fh);
?>