<?php
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php';  
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/page_menu_header_gas.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/fullscreen.php';
include_once '/p1mon/www/util/textlib.php';
include_once '/p1mon/www/util/highchart.php';

if ( checkDisplayIsActive(20) == false) { return; }

?>
<!doctype html>
<html lang="nl">
<head>
<meta name="robots" content="noindex">
<!-- historie uur gas -->
<title>P1monitor <?php echo strIdx(344)." ".strIdx(129)." ".strIdx(336);?></title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css">
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css">

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/highstock-link/highstock.js"></script>
<script src="./js/highstock-link/highcharts-more.js"></script>
<script src="./js/highstock-link/modules/accessibility.js"></script>
<script src="./js/hc-global-options.js"></script>
<script src="./js/p1mon-util.js"></script>

<script>
"use strict"; 

var tmp = "<?php echo strIdx( 335 );?>"
const text_graaddagen = tmp.charAt(0).toUpperCase() + tmp.slice(1)
tmp = "<?php echo strIdx( 139 );?>"
const text_temperature = tmp.charAt(0).toUpperCase() + tmp.slice(1)
const text_gas = "<?php echo strIdx( 336 );?>"
const text_temp_min = "<?php echo strIdx( 339 );?>"
const text_temp_avg = "<?php echo strIdx( 338 );?>"
const text_temp_max = "<?php echo strIdx( 337 );?>"
const text_hidden   = "<?php echo strIdx( 340 );?>"
const text_hidden_unkown = "<?php echo strIdx( 341 );?>"
const text_gas_consumed = "<?php echo strIdx( 342 );?>"
const text_hour = "<?php echo strIdx( 129 );?>"
const text_day  = "<?php echo strIdx( 135 );?>"
const text_days = "<?php echo strIdx( 122 );?>"

var GverbrData      = [];
var Granges         = [];
var Gaverages       = [];
var GDegreeDays     = [];

var seriesOptions   = [];
var recordsLoaded   = 0;
var initloadtimer;
var Gselected       = 0;
var GselectText     = ["12 "+text_hour, "1 "+text_day, "3 "+text_days, "5 "+text_days] // #PARAMETER
var GseriesVisibilty= [true,true,true,true];
var mins            = 1;
var secs            = mins * 60;
//var maxrecords      = 768; // number of records to read 
var currentSeconds  = 0;
var currentMinutes  = 0;

var maxDataIsOn     = false
var maxDataText     = ['MAX. data','MIN. data']
var maxDataCount    = [ 26034, 744 ]
var maxrecords      = maxDataCount[1];

function readJsonApiHistoryHour( cnt ){
    //console.log( "readJsonApiHistoryHour()" )
    $.getScript( "/api/v1/powergas/hour?limit=" + cnt, function( data, textStatus, jqxhr ) {
      try {
        var jsondata  = JSON.parse(data); 
        recordsLoaded = jsondata.length;

        //empty the array.
        GverbrData.length  = 0;
        Granges.length     = 0;
        Gaverages.length   = 0;
        GDegreeDays.length = 0;

        for (var j = jsondata.length; j > 0; j--){ 
            //continue;
            //if ( j == 2 ) continue; //DEBUG
            var item = jsondata[ j-1 ];
            item[1]  = item[1] * 1000; // highchart likes millisecs.
            GverbrData.push( [item[1], item[10] ]   );
            //GverbrData.push( [item[1], 10 ]   );
            Granges.push     ( [item[1], null, null ] );
            Gaverages.push   ( [item[1], null ]       );
            GDegreeDays.push ( [item[1], null ]       );
        } 

        readJsonApiWeatherHistoryHour( cnt ) 
      } catch(err) {
        console.log( err )
      }
   });
}

function readJsonApiWeatherHistoryHour( cnt ){ 
    //console.log( "readJsonApiWeatherHistoryHour" )
    $.getScript( "/api/v1/weather/hour?limit=" + cnt, function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        //var t0 = performance.now();
        //for (var j = jsondata.length; j > 0; j--){
        //    var item = jsondata[ j-1 ];
        for (var j = 0; j < jsondata.length; j++){
            var item = jsondata[ j ];
            //console.log( GverbrData.length )
            for ( var k=0 ; k < GverbrData.length; k++ ) {
                //console.log( "timestamp gaswaarde=" + GverbrData[k][0] + " gaswaarde=" + GverbrData[0][1] );
                //console.log( "k=" + k + " item[1]=" + item[1] * 1000  );
                if ( GverbrData[k][0] == item[1] * 1000 ) {
                    //continue;
                    //console.log( "timestamp komt overeen, range waarde =" + item[4] + " k=" + k + "DG=" + item[19]);
                    //if ( k == 2 ) continue; //DEBUG
                    Granges[k][1]     = item[4]
                    Granges[k][2]     = item[6]
                    Gaverages[k][1]   = item[5]
                    GDegreeDays[k][1] = item[19]
                    break;
                }
                
            }
        }  
        //var t1 = performance.now();
        //console.log("Call to process took " + (t1 - t0) + " milliseconds.")

        updateData()
      } catch(err) {
        console.log( err )
      }
   });
}


// change items with the marker #PARAMETER
function createGasChart() {
    Highcharts.stockChart('GasChart', {
        exporting: { enabled: false },
        lang: {
            noData: "Geen gegevens beschikbaar."
        },
        noData: {
            style: { 
            fontFamily: 'robotomedium',
                fontWeight: 'bold',
                fontSize: '25px',
                color: '#10D0E7'
        }
        },
        chart: {
            style: {
                fontFamily: 'robotomedium',
                fontSize: '14px'
            },
            backgroundColor: '#ffffff',
            borderWidth: 0
        },
        title: {
            text: null
        },
        navigator: {
            xAxis: {
            //min: 915145200000, //vrijdag 1 januari 1999 00:00:00 GMT+01:00
            //minTickInterval:       24 * 3600000,  
            //maxRange:         30 * 24 * 3600000,
            type: 'datetime',
            dateTimeLabelFormats: {
                day: '%a.<br>%d %B<br/>%Y',
                month: '%B<br/>%Y',
                year: '%Y'
            }
            },
            enabled: true,
            outlineColor: '#384042',
            outlineWidth: 1,
            handles: {
            backgroundColor: '#384042',
            borderColor: '#6E797C'
            },
            series:[ 
                {
                    color: '#507ABF'
                }, 
                {
                    color: '#384042'
                }
            ]
        },
        xAxis: {
            type: 'datetime',
            /*
            minTickInterval:        3600000, 
            range:           60   * 3600000,
            minRange:        12   * 3600000,
            maxRange:        31 * 24 * 3600000,
            */
            minTickInterval:           3600000, 
            minRange:        1      * 3600000,
            maxRange:        5 * 24 * 3600000,
            dateTimeLabelFormats: {
                minute: '%H:%M',
                hour: '%H:%M',
                day: "%a.<br>%e %b.",
                month: '%b.<br>%y',
                year: '%y'
            },
            lineColor: '#6E797C',
            lineWidth: 1, 
            events: {
                setExtremes: function(e) {
                    if(typeof(e.rangeSelectorButton)!== 'undefined') {
                        for (var j = 0;  j < GselectText.length; j++){
                            if ( GselectText[j] == e.rangeSelectorButton.text ) {
                                toLocalStorage('stat-h-select-gas-index',j+1); // #PARAMETER
                                break;
                            }
                        }
                    }
                }
            },
        },
        yAxis: [
            { // gas axis
                tickAmount: 7,
                opposite: false,
                offset: 0,
                labels: {
                //useHTML: true,
                format: '{value} m<sup>3</sup>',
                    style: {
                    color: '#507ABF',
                    },
                }
            },
            { // temp axis
                tickAmount: 7,
                opposite: true,
                gridLineDashStyle: 'longdash',
                gridLineColor: '#6E797C',
                gridLineWidth: 1,
                labels: {
                    format: '{value}°C',
                        style: {
                        color: '#384042',
                        
                        }
                    },
                title: {
                    text: null, 
                },
            },
        { // degree days
            tickAmount: 7,
            opposite: true,
            gridLineDashStyle: 'longdash',
            gridLineColor: '#6E797C',
            gridLineWidth: 1,
            labels: {
                format: '{value} gd',
                    style: {
                    color: '#384042'
                    }
                },
            title: {
                text: null, 
            },
        }
        ],
        tooltip: {
            useHTML: false,
            style: {
                padding: 3,
                color: '#6E797C'
            },
            formatter: function() {

                var s = '<b>'+ Highcharts.dateFormat('%A, %Y-%m-%d %H:%M-%H:59', this.x) +'</b>';
                var d = this.points;
                
                // find timestamp and add data points
                for (var i=0,  tot=GverbrData.length; i < tot; i++) {
                    if ( GverbrData[i][0] == d[0].key ) { //found time and dataset
                        var var_verbruikt_gas = GverbrData[i][1];
                        var var_min_temp      = Granges[i][1];
                        var var_max_temp      = Granges[i][2];
                        var var_avg_temp      = Gaverages[i][1]
                        var var_degreedays    = GDegreeDays[i][1]
                        
                        /*
                        console.log ( GverbrData[i][1] )
                        console.log ( Granges[i][1]    )
                        console.log ( Granges[i][2]    )
                        console.log ( Gaverages[i][1]  )
                        console.log ( GDegreeDays[i][1])
                        */
                        break; 
                    }
                }
            

                var verbruikt_gas=text_hidden;
                if ( $('#GasChart').highcharts().series[0].visible === true ){ // Gas
                    verbruikt_gas = var_verbruikt_gas.toFixed(3)+" m<sup>3</sup>";
                }
                s += '<br/><span style="color: #507ABF">' + text_gas_consumed + ': </span>'+verbruikt_gas;
                
                var degreedays = text_hidden_unkown;
                if ( $('#GasChart').highcharts().series[3].visible === true ){ // Gas
                    if ( var_degreedays != null ) {
                        degreedays = var_degreedays.toFixed(3);
                    }
                }
                s += '<br/><span style="color: #450F3F">' + text_graaddagen + ': </span>' + degreedays;

                var max_temp = text_hidden;
                var avg_temp = text_hidden;
                var min_temp = text_hidden;

                if ( $('#GasChart').highcharts().series[1].visible === true && $('#GasChart').highcharts().series[0].visible === true ){
                    try {
                        avg_temp = var_avg_temp.toFixed(1)+" °C";
                        max_temp = var_max_temp.toFixed(1)+" °C";
                        min_temp = var_min_temp.toFixed(1)+" °C";
                    } catch(err) {} // suppress console error
                }

                if ( $('#GasChart').highcharts().series[1].visible === true && $('#GasChart').highcharts().series[0].visible === false ){
                    try {
                        avg_temp = var_avg_temp.toFixed(1)+" °C";
                        max_temp = var_max_temp.toFixed(1)+" °C";
                        min_temp = var_min_temp.toFixed(1)+" °C";
                    } catch(err) {} // suppress console error
                }

                var max_temp_color = '#FF0000';
                var min_temp_color = '#0088FF';
                s += '<br/><span style="color: '+ max_temp_color +'">' + text_temp_max + ': </span>'+ max_temp;
                s += '<br/><span style="color: #384042">' + text_temp_avg + ': </span>'+ avg_temp;
                s += '<br/><span style="color: '+ min_temp_color +'">' + text_temp_min + ': </span>'+ min_temp;
                return s;
            },
            backgroundColor: '#F5F5F5',
            borderColor: '#DCE1E3',
            crosshairs: [true, true],
            borderWidth: 1
        },
        rangeSelector: {
            inputEnabled: false,
            buttonSpacing: 5, 
            selected : Gselected,
            buttons: [
                {
                    text: "-",
                    events: {
                        click: function () {
                            
                            maxDataIsOn = !maxDataIsOn;
                            setHCButtonText( $('#GasChart').highcharts().rangeSelector.buttons[0], maxDataText, maxDataIsOn );

                            if ( maxDataIsOn == true ) {
                                maxrecords = maxDataCount[0]
                            } else {
                                maxrecords = maxDataCount[1]
                            }

                            readJsonApiHistoryHour( maxrecords );
                            toLocalStorage('stat-h-gas-max-data-on',maxDataIsOn );  // #PARAMETER
                            return false
                        }
                    }
                },

            {
                type: 'hour',
                count: 12,
                text: GselectText[0]
            },{
                type: 'day',
                count: 1,
                text: GselectText[1]
            },{
                type: 'day',
                count: 3,
                text: GselectText[2]
            }, {
                type: 'day',
                count: 5,
                text: GselectText[3]
            }],
            buttonTheme: { 
                r: 3,
                fill: '#F5F5F5',
                stroke: '#DCE1E3',
                'stroke-width': 1,
                width: 65,
                style: {
                color: '#6E797C',
                fontWeight: 'normal'
                },
                states: {
                hover: {
                    fill: '#F5F5F5',
                    style: {
                    color: '#10D0E7'
                    }
                },
                select: {
                    fill: '#DCE1E3',
                    stroke: '#DCE1E3',
                    'stroke-width': 1,
                    style: {
                    color: '#384042',
                    fontWeight: 'normal'
                    }
                }
                }
            }  
        },
        legend: {
            y: -38,
            symbolHeight: 12,
            symbolWidth: 12,
            symbolRadius: 3,
            borderRadius: 5,
            borderWidth: 1,
            backgroundColor: '#DCE1E3',
            symbolPadding: 3,
            enabled: true,
            align: 'right',
            verticalAlign: 'top',
            floating: true,
            itemStyle: {
                color: '#6E797C'
            },
            itemHoverStyle: {
                color: '#10D0E7'
            },
            itemDistance: 5
        },
        series: [ 
        {
            yAxis: 0,
            visible: GseriesVisibilty[0],
            showInNavigator: true,
            name: 'm3 ' + text_gas,
            type: 'column',
            color: '#507ABF',
            data: GverbrData,
            zIndex: 0,
        },
        {
            yAxis: 1,
            visible: GseriesVisibilty[1],
            showInNavigator: true,
            name: text_temperature,
            data: Gaverages,
            type: 'spline',
            zIndex: 2,
            color: '#384042',
            lineWidth: 1,
            marker: {
                fillColor: 'white',
                lineWidth: 1,
                lineColor: '#384042'
            }
        },
        {
            yAxis: 1,
            dashStyle: 'ShortDot',
            visible: GseriesVisibilty[1],
            name: 'Range',
            data: Granges,
            type: 'areasplinerange',
            lineWidth: 1,
            linkedTo: ':previous',
            color: '#ff0000',
            negativeColor: '#0088FF',
            fillOpacity: 0.3,
            zIndex: 1,
            marker: {
                fillColor: 'white',
                lineWidth: 1,
                lineColor: '#ff0000'
            }
        },
        {
            yAxis: 2,
            visible: GseriesVisibilty[3],
            showInNavigator: false,
            name: text_graaddagen,
            data: GDegreeDays,
            type: 'spline',
            zIndex: 2,
            color: '#450f3f',
            lineWidth: 1,
            marker: {
                fillColor: 'white',
                lineWidth: 1,
                lineColor: '#384042'
            }
        }
        ],
        plotOptions: {
            series: {
                showInNavigator: true,
                events: {
                    legendItemClick: function () {
                        // console.log('legendItemClick index='+this.index);
                        if ( this.index === 0 ) {
                        toLocalStorage('stat-h-gas-visible',!this.visible); // #PARAMETER
                        }
                        if ( this.index === 1 ) {
                        toLocalStorage('stat-h-gas-temp-visible',!this.visible); // #PARAMETER
                        }
                        if ( this.index === 3 ) {
                        toLocalStorage('stat-h-gas-graaddagen-visible',!this.visible); // #PARAMETER
                        }
                    }
                }
            }
        },
  });
  // can only set text when chart is made.
  setHCButtonText( $('#GasChart').highcharts().rangeSelector.buttons[0], maxDataText, maxDataIsOn );
}


function updateData() {
    //console.log("updateData()");
    if (recordsLoaded !== 0 ) {
      hideStuff('loading-data');
    }
    var chart = $('#GasChart').highcharts();
    if( typeof(chart) !== 'undefined') {
        chart.series[0].setData( GverbrData );
        chart.series[1].setData( Gaverages );
        chart.series[2].setData( Granges );
        chart.series[3].setData( GDegreeDays );
        //chart.redraw();
    }
}


function DataLoop() {
    currentMinutes = Math.floor(secs / 60);
    currentSeconds = secs % 60;
    if(currentSeconds <= 9) { currentSeconds = "0" + currentSeconds; } 
    secs--;
    document.getElementById("timerText").innerHTML = zeroPad(currentMinutes,2) + ":" + zeroPad(currentSeconds,2);
    if(secs < 0 ) { 
        mins = 1;  
        secs = mins * 60;
        currentSeconds = 0;
        currentMinutes = 0;
        //console.log("DataLoop()")
        colorFader("#timerText","#0C7DAD");
        readJsonApiHistoryHour( maxrecords );
    }
    setTimeout('DataLoop()',3000);
}


$(function() {
    toLocalStorage('stats-menu-gas',window.location.pathname);

    GseriesVisibilty[0] = JSON.parse(getLocalStorage('stat-h-gas-visible'));
    GseriesVisibilty[1] = JSON.parse(getLocalStorage('stat-h-gas-temp-visible'));
    GseriesVisibilty[3] = JSON.parse(getLocalStorage('stat-h-gas-graaddagen-visible'));

    Gselected           = parseInt(getLocalStorage('stat-h-select-gas-index'),10);

    maxDataIsOn = JSON.parse(getLocalStorage('stat-h-gas-max-data-on'));           // #PARAMETER
    //console.log( "maxDataIsON(1)=" + maxDataIsOn )

    if ( (maxDataIsOn == null) || (maxDataIsOn == false) ) {
        maxDataIsOn = false;
        maxrecords = maxDataCount[1]
    } else {
        maxrecords = maxDataCount[0]
    }


    Highcharts.setOptions({
        global: {
            useUTC: false
            },
            lang: <?php hc_language_json(); ?>
    });

    screenSaver( <?php echo config_read(79);?> ); // to enable screensaver for this screen.
    createGasChart();
    secs = 0;
    DataLoop();
});

</script>
</head>
<body>

<?php page_header();?>

<div class="top-wrapper-2">
    <div class="content-wrapper pad-13">
       <!-- header 2 -->
        <?php pageclock(); ?>
        <?php page_menu_header_gas(3); ?>
        <?php weather_info(); ?>
    </div>
</div>

<div class="mid-section">
    <div class="left-wrapper">
        <?php page_menu(5); ?>
        <div id="timerText" class="pos-8 color-timer"></div>
        <?php fullscreen(); ?>
    </div> 
    <div class="mid-content-2 pad-13">
    <!-- links -->
        <div class="frame-2-top">
            <span class="text-2"><?php echo strIdx(121);?> (m<sup>3</sup> <?php echo strIdx(336);?>)</span>
        </div>
        <div class="frame-2-bot"> 
        <div id="GasChart" style="width:100%; height:480px;"></div>    
        </div>
</div>
</div>
<div id="loading-data"><img src="./img/ajax-loader.gif" alt="Even geduld aub." height="15" width="128"></div>

</body>
</html>
