
// note this code is dependent on the follow libs make sure the are include on the page
// ./js/mobile-detect/mobile-detect.min.js
// ./util/p1mon-pagezoom.php uses this code


    function getZoomStorageID(){
        return window.location.pathname.replace('/','zoom-value-').replace('.php','')
    }

    function zoomSetPageFromStorage() {
        var loaded_storage_value = getLocalStorage( getZoomStorageID() );
        var zoom_text_value      = document.getElementById("zoom_value");
        var slider               = document.getElementById("zoom_slider");

        if ( loaded_storage_value != null ) {
            //console.log("set value with value = " + loaded_storage_value );
            document.body.style.zoom = loaded_storage_value;
            slider.value = loaded_storage_value * 100;
            zoom_text_value.innerHTML = slider.value; // text percentage.
        }
    }

    function zoomSetPage() {
        var local_storage_id = getZoomStorageID();
        var zoom_text_value  = document.getElementById("zoom_value");
        var slider           = document.getElementById("zoom_slider");
       
        if ( md.mobile() !== null ) {
            document.getElementById('set_zoom').style.display = "none";
        }

        zoom_text_value.innerHTML = slider.value;
        slider.oninput = function() {
            zoom_text_value.innerHTML = this.value;
        }

        document.getElementById("set_zoom").onclick = function () {
            console.log( document.getElementById("slidecontainer_zoom").style.display );

            if ( document.getElementById("slidecontainer_zoom").style.display == "block" )  {
                document.getElementById('slidecontainer_zoom').style.display = "none";
                document.body.style.zoom = slider.value/100; // it is a precentage
                toLocalStorage(local_storage_id , slider.value/100);
            } else {

                var md = new MobileDetect(window.navigator.userAgent);
                if ( md.mobile() == null ) {  // not a mobile device.
                    document.getElementById('slidecontainer_zoom').style.display = "block"; // show only on non mobile devices
                }
            }
            };
    }


