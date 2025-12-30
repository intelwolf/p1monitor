<?php
function pageZoom(){

$title = strIdx( 767 );

echo <<<"END"
    <!-- page zoom code -->
    <div id="set_zoom" class="pos-57 cursor-pointer" title="$title">
        <div class="text-22"><i id="zoom_icon" class="fa-solid fa-magnifying-glass" data-fa-transform="grow-8 right-16"></i></div>
    </div>
    <div id="slidecontainer_zoom">
        <input type="range" min="50" max="300" value="100" class="slider" id="zoom_slider"> <div class="text-16 width-30" id="zoom_value"></div>
    </div>
    <!-- end of page zoom code -->
END;
}
?>