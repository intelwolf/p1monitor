<?php 

// sets the Highcharts.setOptions lang: attribute
function hc_language_json() {

    // read the set language
    // depends on the external PHP file www/util/config_read.php
    $language_index = config_read( 148 );
    
    // default Dutch
    $str = "{ 
        months: ['Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni',  'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December'],
        weekdays: ['Zondag', 'Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag'],
        shortMonths: ['Jan', 'Feb', 'Mrt', 'Apr', 'Mei', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec'],
        shortWeekdays: ['zo', 'ma', 'di', 'wo', 'do', 'vr', 'za']
    }";

    if(!isset($language_index) ) {
        $language_index = 0; // FAILSAVE does the job for index numbers to high
    }

    if ( $language_index == 1 ) { // UK
        $str = "{
            months: [ 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
            weekdays: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday','Saturday'],
            shortMonths: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            shortWeekdays: ['su', 'mo', 'tu', 'we', 'th', 'fr', 'sa']
        }";
    }

    if ( $language_index == 2 ) { // French 
        $str = "{
            months: [ 'Janvier', 'Février', 'Mars', 'Avril','Mai', 'Juin', 'Juillet', 'Août','Septembre', 'Octobre', 'Novembre', 'Décembre'],
            weekdays: ['Dimanche', 'Lundi', 'Mardi', 'Mercredi','Jeudi', 'Vendredi', 'Samedi'],
            shortMonths: ['jan', 'fév', 'mars', 'avr', 'mai', 'juin', 'juil', 'août', 'sept', 'oct', 'nov', 'dec'],
            shortWeekdays: ['di', 'lu', 'ma', 'me', 'je', 've', 'sa']
        }";
    }

    echo $str;

}

?>