<?php
// needs config_read.php!

function page_header() {
    $xmas  = $newversion = '';
    $day   = intval(date ('j'));
    $month = intval(date ('n'));

    // echo config_read( 134 );
    // 1 means hide the header -> don't generate code.
    if ( config_read( 134 ) == 1 ) {
        return;
    }
    //$day = 31;
    //$month =12;

    if ($day >= 24 and $day <= 26 and $month == 12) { // xmas launch date
        $xmas = '<div class="pos-38 content-wrapper"><img alt="Happy Christmas from securitybrother" src="/img/xmas.png" height="45"></div>';
    }
    
    if  ( strlen( readStatusDb(66)) > 0 ) {
        $ttext = 'Versie '. readStatusDb(66) . '&#10;' . "datum: ". readStatusDb(67); 
        $download_url = readStatusDb(86);
        $newversion = '<a target="_blank" href="'. $download_url .'"><div title="'. $ttext . '" class="pos-42 content-wrapper"><span class="fa-layers fa-fw"><i class="fas fa-certificate color-warning fa-3x"></i><span class="fa-layers-text" data-fa-transform="right-13 shrink-6 rotate-330" style="font-weight:300">nieuwe versie</span></span></div></a>';
    }

echo <<< EOT
<div class="top-wrapper">
    <div class="content-wrapper">
        <img class="pos-1" alt="The P1-monitor logo is shown here." src="./img/p1mon-logo.svg" width="50" height="45">
        <span class="text-1">P1-monitor</span>
        $newversion
        $xmas
    </div>
</div>
EOT;
}
?>
