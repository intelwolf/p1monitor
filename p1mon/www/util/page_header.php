<?php
// needs config_read.php!

//include_once '/p1mon/www/util/textlib.php';

function page_header() {

    $xmas  = $newversion = $newpatch = '';
    $day   = intval(date ('j'));
    $month = intval(date ('n'));

    // echo config_read( 134 );
    // 1 means hide the header -> don't generate code.
    if ( config_read( 134 ) == 1 ) {
        return;
    }

    //$day = 25;
    //$month = 11;

    if ($day >= 24 and $day <= 26 and $month == 12) { // xmas launch date
        $xmas = '<div class="content-wrapper pos-56"  title="'  .  strIdx( 736) . '"><img alt="' .  strIdx( 736) . '" src="/img/xmas.png" height="45"></div>';
    }

    // check if the watchdog has set an new version available
    if  ( readStatusDb(136) == 1 ) {
        $text = ucfirst(strIdx( 375 )) . '&#10;' .  ucfirst( strIdx( 733 )) . ' '. readStatusDb(66) . '&#10;' . ucfirst(strIdx( 734 )) . ": ". readStatusDb(67); 
        $download_url = readStatusDb(86);
        $newversion = '<a target="_blank" href="'. $download_url .'">
        <div title="'. $text . '">
             <span class="fa-stack fa-2x">
                    <i class="fa-solid fa-floppy-disk fa-stack-1x color-menu" data-fa-transform="up-4 grow-5 up-3"></i>
                    <i class="fa-solid fa-file-arrow-down fa-stack-1x fa-bounce color-back" style="--fa-bounce-start-scale-x: 1;--fa-bounce-start-scale-y: 1;--fa-bounce-jump-scale-x: 1;--fa-bounce-jump-scale-y: 1;--fa-bounce-land-scale-x: 1;--fa-bounce-land-scale-y: 1;--fa-bounce-rebound: 0; --fa-bounce-height: -10px" data-fa-transform="up-8 right-6 down-5 shrink-9"></i>
                </span>
        </div></a>';
    }

    // check if the watchdog has an new PATCH version available
    if  ( readStatusDb(137) == 1 )  { 
        $text =  ucfirst(strIdx( 735 )) . ' '. readStatusDb(133) . '&#10;'; 
        $download_url = readStatusDb(134);
        $newpatch = 
        '<a target="_blank" href="'. $download_url .'">
            <div title="'. $text . '">
                <span class="fa-stack fa-2x">
                    <i class="fa-solid fa-bandage fa-stack-1x color-menu" data-fa-transform="up-4 grow-12 up-3"></i>
                     <i class="fa-solid fa-file-arrow-down fa-stack-1x fa-bounce color-back" style="--fa-bounce-start-scale-x: 1;--fa-bounce-start-scale-y: 1;--fa-bounce-jump-scale-x: 1;--fa-bounce-jump-scale-y: 1;--fa-bounce-land-scale-x: 1;--fa-bounce-land-scale-y: 1;--fa-bounce-rebound: 0; --fa-bounce-height: -10px" data-fa-transform="up-8 right-14 down-5 shrink-9"></i>
                </span>
            </div>
        <a/>';
    }

   
echo <<< EOT
<div class="top-wrapper">
    <div class="content-wrapper">

        <div class="rTable">
            <div class="rTableRow">

                <div class="rTableCell">
                       <img class="pos-1" alt="The P1-monitor logo is shown here." src="./img/p1mon-logo.svg" width="50" height="45">
                </div>

                <div class="rTableCell width-160">
                    <span class="text-1">P1-monitor</span>
                </div>

                <div class="rTableCell width-58">
                       $newversion
                </div>

                 <div class="rTableCell width-58">
                       $newpatch
                </div>

                 <div class="rTableCell">
                        $xmas
                </div>

            </div>
        </div>


    </div>
</div>
EOT;
}
?>
