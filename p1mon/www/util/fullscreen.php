<?php
function fullscreen(){

echo <<<"END"
        <!-- full screen code -->
        <script src="./js/mobile-detect/mobile-detect.min.js"></script>
        <script src="./js/screenfull/dist/screenfull.min.js"></script>
        <div id="fscr_request" class="pos-41 cursor-pointer"><div class="text-22"><i id="fscr_icon" class="fas fa-expand" data-fa-transform="grow-8 right-16"></i></div></div>
        <script>
            var md = new MobileDetect(window.navigator.userAgent);
            if ( md.mobile() == null ) {  // not a mobile device.
                 showStuff('fscr_request');
            }
            $('#fscr_request').click(function () {
                screenfull.toggle($(document.body)[0]);
                if (screenfull.isFullscreen) {
                    $('#fscr_icon').removeClass( "fa-compress" );
                    $('#fscr_icon').addClass( "fa-expand" );
                    $("html").css("background-color", "#dddddd");
                    $("body").css("background-color", "#dddddd");
                } else {
                    $('#fscr_icon').removeClass( "fa-expand" );
                    $('#fscr_icon').addClass( "fa-compress" );
                    $("html").css("background-color", "#EDF0F1");
                    $("body").css("background-color", "#EDF0F1");
                }
        });
        </script>
        <!-- end of full screen code -->
END;
}
?>