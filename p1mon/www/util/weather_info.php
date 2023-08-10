<?php
function weather_info(){

    // only show when API key is set.
    if ( strlen(config_read(13)) < 31 ) {
        return;
    }

    $text_timestamp         = ucfirst(strIdx( 345 ));
    $text_location          = ucfirst(strIdx( 346 ));
    $text_wind_direction    = ucfirst(strIdx( 347 ));
    $text_weer_conditie     = ucfirst(strIdx( 348 ));
    $text_temperature       = ucfirst(strIdx( 139 ));
    $text_wind_speed        = ucfirst(strIdx( 349 ));
    $text_unknown           = strIdx( 269 );
    $text_rises             = strIdx( 350 );
    $text_drops             = strIdx( 351 );
    $text_unchanged         = strIdx( 352 );
    
echo <<<"END"
                <!-- start weather part -->
                <link type="text/css" rel="stylesheet" href="./font/owfont-master/css/owfont-regular.css">
                <div id="weather" onMouseOver=show_weather_detail() onmouseout=hide_weather_detail(); class="weather_box display-none cursor-pointer">
                    <i id="wth_temp_icon" class="text-6 fas fa-thermometer-half"></i>
                    <span class="text-17" id="wth_temp_text">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="text-17">&deg;C</span>

                    <span class="fa-layers fa-fw color-text" >
                        <i class="fas fa-tint"               data-fa-transform="up-2 grow-4 left-2" ></i>
                        <i class="fa-inverse fas fa-percent" data-fa-transform="shrink-10 up-3 left-2" ></i>
                      </span>

                    <div class='content-wrapper'>
                        <span class="text-20" id="wth_humidity_text">&nbsp;&nbsp;</span>
                    </div>

                    <span class="fa-layers fa-fw color-text" >
                        <i class="fas fa-cloud" data-fa-transform="grow-1 up-1"></i>
                        <i class="fa-inverse fas fa-tachometer-alt" data-fa-transform="shrink-10" ></i>
                      </span>

                    <span class="text-17" id="wth_wind_speed_text">;</span>
                    <span class="text-17">Bft&nbsp;<i id="wth_wind_deg_arrow" class="fas fa-location-arrow" data-fa-transform="rotate-0"></i>&nbsp;</span> 

                    <i id="wth_pressure_icon" class="text-6 fas fa-tachometer-alt" data-fa-transform="shrink-2"></i>
                    
                    <span class="text-17" id="wth_pressure_text">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="text-17">&nbsp;hPa</span>
                    <div class='content-wrapper text-18'>
                        <i id='wth_condition_icon' class="owf owf-lg "></i>
                    </div>
                </div>
                
                <div class="cursor-pointer" id="weather_detail" onclick=hide_weather_detail(); > 
                    <div>$text_timestamp:&nbsp;<span id="wth_detail_timestamp"></span></div>
                    <div>$text_location:&nbsp;<span id="wth_detail_location"></span></div>
                    <div>$text_wind_direction:&nbsp;<span id="wth_detail_wind_deg"></span></div>
                    <div>$text_weer_conditie:&nbsp;<span id="wth_detail_condition"></span></div>
                    <div>$text_temperature:&nbsp;<span id="wth_detail_temperature"></span></div>
                    <div>$text_wind_speed:&nbsp;<span id="wth_detail_wind_speed"></span><span class="text-17">&nbsp;km/u</span></div>
                </div>
                
                <script>
                var weaterData      = [];
                var tempDirection   = 0;
                var globalWeatherTimer;
                var tempAnimationTimer;
                
                weatherLoop();

                function wind_speed_2_beaufort( wind_speed ) {
                    if  ( wind_speed < 1 ) { 
                        return 0; 
                    } else if ( wind_speed  >= 1 && wind_speed < 5.5 ) {
                        return 1;
                    } else if ( wind_speed  >=5.5  && wind_speed < 11.5 ) {
                        return 2;
                    } else if ( wind_speed  >=11.5  && wind_speed < 19.5 ) {
                        return 3;
                    } else if ( wind_speed  >=18.5  && wind_speed < 28.5 ) {
                        return 4;
                    } else if ( wind_speed  >=28.5  && wind_speed < 38.5 ) {
                        return 5;
                    } else if ( wind_speed  >=38.5  && wind_speed < 49.5 ) {
                        return 6;
                    } else if ( wind_speed  >=38.5  && wind_speed < 61.5 ) {
                        return 7;
                    } else if ( wind_speed  >=61.5  && wind_speed < 74.5 ) {
                        return 8;
                    } else if ( wind_speed  >=74.5  && wind_speed < 88.5 ) {
                        return 9;
                    } else if ( wind_speed  >=88.5  && wind_speed < 102.5 ) {
                        return 10;
                    } else if ( wind_speed  >=102.5  && wind_speed < 117.5 ) {
                        return 11;
                    } else if ( wind_speed  >=117.5 ) {
                        return 12;
                    } 
                }

                function show_weather_detail() {
                    $('#weather_detail').css({
                        left: $( "#weather" ).position().left+14, 
                        top:  $( "#weather" ).position().top+42
                    });
                    $('#weather_detail').show();
                    setTimeout( function() { hide_weather_detail(); }, 10000);
                }
                
                function hide_weather_detail() {
                    $('#weather_detail').hide();
                }

                function hasClassAndReplace(has, replace) {
                    if ( $('#wth_temp_icon').hasClass( has ) ) {
                            $('#wth_temp_icon').removeClass(has);
                            $('#wth_temp_icon').addClass( replace);
                            return true;
                    }
                    return false;
                } 
                
                /*
                function tempertatureAnimation() {
                    
                    clearInterval(tempAnimationTimer);

                    // when 0 stop else animate
                    //fa-thermometer-empty, fa-thermometer-quarter,fa-thermometer-half,fa-thermometer-three-quarters, fa-thermometer-full   

                    if (tempDirection == 0 ) {
                        $('#wth_temp_icon').removeClass();
                        $('#wth_temp_icon').addClass( "text-6 fas fa-thermometer-half" );
                        return;
                     }
                    
                    tempAnimationTimer = setTimeout(tempertatureAnimation, 500); // was 300 orgineel, test of 500 beter gaat.

                    if (tempDirection == 1) {
                        if (hasClassAndReplace("fa-thermometer-empty","fa-thermometer-quarter")){return;}
                        if (hasClassAndReplace("fa-thermometer-quarter","fa-thermometer-half")){return;}
                        if (hasClassAndReplace("fa-thermometer-half","fa-thermometer-three-quarters")){return;}
                        if (hasClassAndReplace("fa-thermometer-three-quarters", "fa-thermometer-full")){return;}
                        if (hasClassAndReplace("fa-thermometer-full","fa-thermometer-empty")){return;}
                     } 
                     
                     if (tempDirection == -1) {
                        if (hasClassAndReplace("fa-thermometer-full","fa-thermometer-three-quarters")){return;}
                        if (hasClassAndReplace("fa-thermometer-three-quarters","fa-thermometer-half")){return;}
                        if (hasClassAndReplace("fa-thermometer-half","fa-thermometer-quarter")){return;}
                        if (hasClassAndReplace("fa-thermometer-quarter","fa-thermometer-empty")){return;}
                        if (hasClassAndReplace("fa-thermometer-empty","fa-thermometer-full")){return;}
                        }
                }
                */

                function processJsonWeatherData(){

                    if ( weaterData[0][4] < 0 ) { 
                         $( '#wth_temp_text').html(weaterData[0][4].toFixed(1) );
                    } else {
                         $( '#wth_temp_text').html('&nbsp;'+weaterData[0][4].toFixed(1) );
                    } 

                    tempDirection = 0;
                    if ( weaterData[0][4] > weaterData[1][4] ) { tempDirection =  1 } // temperature is rising
                    if ( weaterData[0][4] < weaterData[1][4] ) { tempDirection = -1 } // temperature is falling

                    if ( tempDirection == 0 ) { 
                        //clearInterval(tempAnimationTimer);
                        $('#wth_detail_temperature').text( '$text_unchanged' );
                        //tempertatureAnimation();
                    } else {
                        //tempertatureAnimation();
                    }
                    
                    $('#wth_humidity_text').text( weaterData[0][8]+'%' );
                    $('#wth_wind_speed_text').text( wind_speed_2_beaufort( weaterData[0][9]*3.6 ) );
                    $('#wth_detail_wind_speed').text( (weaterData[0][9]*3.6).toFixed(1) );

                    $('#wth_pressure_text').text( weaterData[0][7].toFixed(0) );
                
                    $('#wth_detail_timestamp').text( weaterData[0][0] );
                    $('#wth_detail_location').text( weaterData[0][3] );
                    
                    //weaterData[0][10] = 360

                    if ( weaterData[0][10] > -1 && weaterData[0][10] < 361 ) {
                        $('#wth_detail_wind_deg').html( weaterData[0][10] +"<span>&deg;&nbsp</span>");
                        // compensation for default degree of icon by adding 135.
                        rotation_value =  "rotate-" + (weaterData[0][10] + 135)
                        var wind_arrow = document.getElementById("wth_wind_deg_arrow")
                        //console.log( wind_arrow.dataset.faTransform )
                        // fix for mobile browsers that don't work well with setAttribute
                        wind_arrow.dataset.faTransform = rotation_value
                        //console.log( wind_arrow.dataset.faTransform )
                        document.getElementById("wth_wind_deg_arrow").setAttribute("data-fa-transform", rotation_value );
                        $('#wth_wind_deg_arrow').show();
                    }  else {
                        $('#wth_detail_wind_deg').text( '$text_unknown' );
                        $('#wth_wind_deg_arrow').hide();
                    }

                    $('#wth_detail_condition').text( weaterData[0][5] );

                    if ( tempDirection == 1) { 
                        $('#wth_detail_temperature').text( '$text_rises' );
                    }
                    if ( tempDirection == -1) { 
                        $('#wth_detail_temperature').text( '$text_drops' );
                    }

                    $('#wth_condition_icon').removeClass();
                    $('#wth_condition_icon').addClass( "owf owf-lg owf-"+weaterData[12] );
                    $('#weather').removeClass('display-none');
                    
                }
                
                function readJsonApiWeatherWithID( id ){ 
                    $.getScript( "/api/v1/configuration/" + id, function( data, textStatus, jqxhr ) {
                      try {
                        var jsondata = JSON.parse(data); 
                        //console.log( jsondata[0][1] )
                        readJsonApiWeather ( jsondata[0][1] )
                      } catch(err) {}
                   });
                }
                
                function readJsonApiWeather( weatherCityID ){ 
                    $.getScript( "./api/v1/weather?limit=50", function( data, textStatus, jqxhr ) {
                      try {
                        var jsonarr = JSON.parse(data); 
                        for (var j=0; j < jsonarr.length; j++ ){    
                            item = jsonarr[ j ];
                            //console.log ( item[0], item[2], weatherCityID  )
                            if ( weatherCityID == item[2] ) {
                                weaterData[0] = jsonarr[j];
                                if ( jsonarr.length > 1 ) {
                                    weaterData[1] = jsonarr[j+1];
                                } else {
                                    weaterData[1] = jsonarr[j];
                                }
                                processJsonWeatherData();
                                break;
                            }
                        }  
                      } catch(err) {
                          console.log( err );
                      }
                   });
                }

                function weatherLoop() {
                    //console.log('loop');
                    clearInterval(tempAnimationTimer);
                    readJsonApiWeatherWithID( 25 );
                }
                setTimeout(weatherLoop, 100); // Run again in 0.1 sec to optimize for mobile
                globalWeatherTimer = setInterval( weatherLoop, 60000); // Run again in 1 min.
                </script>
                <!-- stop weather part -->
END;
}
?>