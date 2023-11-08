<?php
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php';  
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/page_menu_header_fase.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/fullscreen.php';
include_once '/p1mon/www/util/highchart.php';

if ( checkDisplayIsActive( 61 ) == false) { return; }
?>
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title>P1-monitor <?php echo strIdx( 531 )?> A</title>
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

const text_days                     = "<?php echo strIdx( 122 );?>";
const text_week                     = "<?php echo strIdx( 144 );?>";
const text_month                    = "<?php echo strIdx( 131 );?>";
const text_months                   = "<?php echo strIdx( 123 );?>";
const text_year                     = "<?php echo strIdx( 132 );?>";
const text_years                    = "<?php echo strIdx( 124 );?>";

var Grange_L1A       = [];
var Grange_L2A       = [];
var Grange_L3A       = [];

var seriesOptions    = [];
var recordsLoaded    = 0;
var initloadtimer;
var Gselected        = 0;
var GselectText      = [ '1 '+text_week, '14 '+text_days, '1 '+text_month, '2 '+text_months, '1 '+text_year, '3 '+text_years ]; // #PARAMETER
var GseriesVisibilty = [ true, true, true ];
var GserieNames      = [ "L1", "L2", "L3" ]
var mins             = 1;
var secs             = mins * 60;
var currentSeconds   = 0;
var currentMinutes   = 0;
var maxrecords       = 1096; // number of records to read

var L1_color = '#CC6600';
var L2_color = '#8C4600';
var L3_color = '#6E3700';

/*
function getRandomIntInclusive(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1) + min); //The maximum is inclusive and the minimum is inclusive
}
*/

function readJsonPhaseMinMax( cnt ){
    //console.log(" readJsonPhaseMinMax ")
    $.getScript( "./api/v1/phaseminmax/day?limit=" + cnt , function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        var item;
        recordsLoaded = jsondata.length;
        Grange_L1A.length = 0;
        Grange_L2A.length = 0;
        Grange_L3A.length = 0;

        for (var j = jsondata.length; j > 0; j--){
            item=jsondata[j-1];
            item[1] = item[1]*1000; // highcharts likes millisecs.

            /*
            item[12] = getRandomIntInclusive(5,16)
            item[24] = item[12] - getRandomIntInclusive(0,2)
            item[13] = getRandomIntInclusive(5,16)
            item[25] = item[13] - getRandomIntInclusive(0,2)
            */

            Grange_L1A.push( [item[1], item[23], item[11] ]);  // timestamp, max A , min A
            Grange_L2A.push( [item[1], item[24], item[12]  ]); // timestamp, max A , min A
            Grange_L3A.push( [item[1], item[25], item[13] ]);  // timestamp, max A , min A

        }

        updateData();
      } catch( err ) {}
   });
}

// change items with the marker #PARAMETER
function createChart() {
    Highcharts.stockChart('ampChart', {
        exporting: { enabled: false },
        lang: {
            noData: "<?php echo ucfirst(strIdx( 425 ))?>"
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
        },
        xAxis: {
            type: 'datetime', 
            minTickInterval: 24 *  3600000, 
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
                                toLocalStorage( 'fase-uiterste-d-select-volt-index', j ); // #PARAMETER
                                break;
                            }
                        }
                    }
                }
            },
        },
        yAxis: [{
            //min: 0,
            tickInterval: 5,
            opposite: false,
            gridLineDashStyle: 'longdash',
            gridLineColor: '#6E797C',
            gridLineWidth: 0.5,
            labels: {
                format: '{value} A',
                style: {
                    color: '#384042'
                }
            },
            title: {
                text: null, 
            },
        }],
    tooltip: {
        useHTML: false,
        style: {
            padding: 3,
            color: '#6E797C'
        },
        formatter: function() {
            
            var s = '<b>'+ Highcharts.dateFormat('%A, %Y-%m-%d', this.x) +'</b>'; //parameter
            var d = this.points;
            var max
            var min
            var delta
            var txt

            for ( var i = 0; i < d.length; i++) { 

                if ( d[i].series.name == GserieNames[0] && d[i].series.visible == true) {
                    max = d[i].point.high;
                    min = d[i].point.low;
                    delta = Math.abs( d[i].point.high - d[i].point.low );
                    txt = '<br/><span style="color: ' + L1_color + '"><b>' + GserieNames[0] + ' ( maximum delta ' + delta.toFixed(1) +' A ) :</b></span>';
                    s += txt;
                    s += '<br/><span style="color: ' +  L1_color + '">Maximum: </span>'+max.toFixed(1)+" A ";
                    s += '<span style="color: ' +  L1_color + '">Minimum: </span>'+min.toFixed(1)+" A";
                }

                if ( d[i].series.name == GserieNames[1] && d[i].series.visible == true) {
                    max = d[i].point.high;
                    min = d[i].point.low;
                    delta = Math.abs( d[i].point.high - d[i].point.low );
                    txt = '<br/><span style="color: ' + L2_color + '"><b>' + GserieNames[1] + ' ( maximum delta ' + delta.toFixed(1) +' A ) :</b></span>';
                    s += txt;
                    s += '<br/><span style="color: ' +  L2_color + '">Maximum: </span>'+max.toFixed(1)+" A ";
                    s += '<span style="color: ' +  L2_color + '">Minimum: </span>'+min.toFixed(1)+" A";
                }

                if ( d[i].series.name == GserieNames[2] && d[i].series.visible == true) {
                    max = d[i].point.high;
                    min = d[i].point.low;
                    delta = Math.abs( d[i].point.high - d[i].point.low );
                    txt = '<br/><span style="color: ' + L3_color + '"><b>' + GserieNames[2] + ' ( maximum delta ' + delta.toFixed(1) +' A ) :</b></span>';
                    s += txt;
                    s += '<br/><span style="color: ' + L3_color + '">Maximum: </span>'+max.toFixed(1)+" A ";
                    s += '<span style="color: ' + L3_color + '">Minimum: </span>'+min.toFixed(1)+" A";
                }
            }

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
        buttons: [{
            type: 'day',
            count: 7,
            text: GselectText[0]
        },{
            type: 'day',
            count: 14,
            text: GselectText[1]
        },{
            type: 'month',
            count: 1,
            text: GselectText[2]
        },{
            type: 'month',
            count: 2,
            text: GselectText[3]
        },{
            type: 'year',
            count: 1,
            text: GselectText[4]
        },{
            type: 'year',
            count: 3,
            text: GselectText[5]
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
    series: [{
            showInNavigator: true,
            yAxis: 0,
            dashStyle: 'Solid',
            visible: GseriesVisibilty[0],
            name: GserieNames[0],
            data: Grange_L1A,
            type: 'areasplinerange',
            lineWidth: 1,
            color: L1_color,
            fillOpacity: 0.33,
        },{
            showInNavigator: true,
            yAxis: 0,
            dashStyle: 'ShortDot',
            visible: GseriesVisibilty[1],
            name: GserieNames[1],
            data: Grange_L2A,
            type: 'areasplinerange',
            lineWidth: 1,
            color: L2_color,
            fillOpacity: 0.33,
        },{
            showInNavigator: true,
            yAxis: 0,
            dashStyle: 'ShortDash',
            visible: GseriesVisibilty[2],
            name: GserieNames[2],
            data: Grange_L3A,
            type: 'areasplinerange',
            lineWidth: 0.5,
            color: L3_color,
            fillOpacity: 0.33,
        }],
        plotOptions: {
            series: {
                softThreshold: true,
                showInNavigator: true,
                events: {
                    legendItemClick: function () {
                        // console.log('legendItemClick index='+this.index);
                        if ( this.index === 0 ) {
                            toLocalStorage('fase-uiterste-d-a-L1',!this.visible); // #PARAMETER
                        }
                        if ( this.index === 1 ) {
                            toLocalStorage('fase-uiterste-d-a-L2',!this.visible); // #PARAMETER
                        }
                        if ( this.index === 2 ) {
                            toLocalStorage('fase-uiterste-d-a-L3',!this.visible); // #PARAMETER
                        }
                    }
                }
            } 
        },
    });
}

function updateData() {
    var chart = $('#ampChart').highcharts();
    if( typeof(chart) !== 'undefined') {
        chart.series[0].setData( Grange_L1A )
        chart.series[1].setData( Grange_L2A )
        chart.series[2].setData( Grange_L3A )
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
        colorFader("#timerText","#0C7DAD");
        readJsonPhaseMinMax( maxrecords );
    }

    if (recordsLoaded !== 0 && $('#ampChart').highcharts() == null ) {
      hideStuff('loading-data');
      createChart();
      updateData();
    }
    setTimeout('DataLoop()',1000);
}

$(function() {
    toLocalStorage('fase-menu',window.location.pathname);
    GseriesVisibilty[0] = JSON.parse(getLocalStorage('fase-uiterste-d-a-L1'));
    GseriesVisibilty[1] = JSON.parse(getLocalStorage('fase-uiterste-d-a-L2'));
    GseriesVisibilty[2] = JSON.parse(getLocalStorage('fase-uiterste-d-a-L3'));
    Gselected = parseInt(getLocalStorage('fase-uiterste-d-select-a-index'),10);

    Highcharts.setOptions({
        global: {
            useUTC: false
        },
        lang: <?php hc_language_json(); ?>
    });

    screenSaver( <?php echo config_read(79);?> ); // to enable screensaver for this screen.
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
        <?php page_menu_header_fase(3); ?>
        <?php weather_info(); ?>
    </div>
</div>

<div class="mid-section">
    <div class="left-wrapper">
        <?php page_menu( 10 ); ?>
        <div id="timerText" class="pos-8 color-timer"></div>
        <?php fullscreen(); ?>
    </div> 
    <div class="mid-content-2 pad-13">
        <div class="frame-2-top">
            <span class="text-2"><?php echo strIdx( 533 )?> A</span>
        </div>
        <div class="frame-2-bot">
        <div id="ampChart" style="width:100%; height:480px;"></div>
        </div>
</div>
</div>
<div id="loading-data">
    <img src="./img/ajax-loader.gif" alt="<?php echo strIdx( 295 )?>" height="15" width="128">
</div>
</body>
</html>