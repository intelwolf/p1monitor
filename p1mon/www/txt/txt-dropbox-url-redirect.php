<?php
$fh = fopen('/p1mon/mnt/ramdisk/dbx_auth_redirect.txt','r') or die("");
while ($line = fgets($fh)) {
    echo str_replace(array("\r", "\n"), '', $line);
}
fclose($fh);
?> 