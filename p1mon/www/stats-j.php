<?php
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php';  
include_once '/p1mon/www/util/page_menu_header.php'; 
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/fullscreen.php';
include_once '/p1mon/www/util/highchart.php';

if ( checkDisplayIsActive(19) == false) { return; }
?>
<!doctype html>
<html lang="<?php echo strIdx( 531 )?>">
<head>
<meta name="robots" content="noindex">
<title>P1-monitor <?php echo strIdx( 424 )?></title>
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

const text_years    = "<?php echo strIdx( 124 );?>"

var recordsLoaded   = 0;
var initloadtimer;
var mins            = 1;  
var secs            = mins * 60;
var currentSeconds  = 0;
var currentMinutes  = 0;
var Gselected       = 0;
var GselectText     = [ '5 '+text_years, '10 '+text_years, '15 '+text_years, '20 '+text_years ];    // #PARAMETER
var GseriesVisibilty= [true,true,true, true];
var GverbrData      = [];
var GgelvrData      = [];
var GnettoData      = [];
var Granges         = [];
var Gaverages       = [];

var maxrecords      = 100; // number of records to read 

function readJsonApiHistoryYear( cnt ){ 
    $.getScript( "/api/v1/powergas/year?limit=" + cnt, function( data, textStatus, jqxhr ) {
        try {
        var jsondata = JSON.parse(data); 
        var item;
        recordsLoaded       = jsondata.length;
        GverbrData.length   = 0;
        GgelvrData.length   = 0; 
        GnettoData.length   = 0;
        Granges.length      = 0;
        Gaverages.length    = 0;

        for (var j = jsondata.length; j > 0; j--){    
            item    = jsondata[ j-1 ];
            item[1] = item[1] * 1000; // highchart likes millisecs.
            GverbrData.push ( [item[1], item[6] ]);
            GgelvrData.push ( [item[1], item[7] ]);
            GnettoData.push ( [item[1], item[6] + (item[7]*-1) ] );
            // temperature
            Granges.push    ( [item[1], null, null ] );
            Gaverages.push  ( [item[1], null ]       );
        }
        readJsonApiWeatherHistoryYear( maxrecords )
      } catch(err) {}
   });
}

function readJsonApiWeatherHistoryYear( cnt ){ 
    $.getScript( "/api/v1/weather/year?limit=" + cnt, function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        
        for (var j = 0; j < jsondata.length; j++){    
            var item = jsondata[ j ];
            for ( var k=0 ; k < GverbrData.length; k++ ) {
                if ( GverbrData[k][0] == item[1] * 1000 ) {
                    Granges[k][1]   = item[4]
                    Granges[k][2]   = item[6]
                    Gaverages[k][1] = item[5]
                    break;
                }
            }
        }  
        updateData();
      } catch(err) {
        console.log( err )
      }
   });
}


/* preload */
readJsonApiHistoryYear( maxrecords );

// change items with the marker #PARAMETER
function createKwhChart() {
    Highcharts.stockChart('KwhChart', {
        chart: {
            style: {
                fontFamily: 'robotomedium',
                fontSize: '14px'
            },
            backgroundColor: '#ffffff',
            renderTo: 'container',
            type: 'column',
            borderWidth: 0
            },
            plotOptions :{
                series :{
                    showInNavigator: true,
                    events: {
                        legendItemClick: function (event) {
                            if  ( this.index === 0 ) {
                                toLocalStorage('stat-j-verbr-visible',!this.visible);  // #PARAMETER
                            }
                            if  ( this.index === 1 ) {
                                toLocalStorage('stat-j-gelvr-visible',!this.visible);  // #PARAMETER
                            }
                            if  ( this.index === 2 ) {
                                toLocalStorage('stat-j-netto-visible',!this.visible);  // #PARAMETER
                            }
                            if  ( this.index === 3 ) {
                                toLocalStorage('stat-j-temp-visible',!this.visible);  // #PARAMETER
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
                layout: 'horizontal',
                floating: true,
                itemStyle: {
                    color: '#6E797C'
                },
                itemHoverStyle: {
                    color: '#10D0E7'
                },
                itemDistance: 5
            },
            exporting: { enabled: false },
            rangeSelector: {
                inputEnabled: false,
                buttonSpacing: 5, 
                selected : Gselected,
                buttons: [
                {
                    type: 'year',
                    count: 5,
                    text: GselectText[0]
                },{
                    type: 'year',
                    count: 10,
                    text: GselectText[1]
                },{
                    type: 'year',
                    count: 15,
                    text: GselectText[2]
                }, {
                    type: 'year',
                    count: 20,
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
            xAxis: {
            events: {
                setExtremes: function(e) {  	
                    if(typeof(e.rangeSelectorButton)!== 'undefined') {
                        for (var j = 0;  j < GselectText.length; j++){    
                            if ( GselectText[j] == e.rangeSelectorButton.text ) {
                                toLocalStorage('stat-j-select-index',j); // PARAMETER
                                break;
                            }
                        }
                    }
                }
            },   
            minTickInterval:     365 * 24 * 3600000, 
            range:          15 * 365 * 24 * 3600000,
            minRange:       5  * 365 * 24 * 3600000,
            maxRange:       30 * 365 * 24 * 3600000,
            type: 'datetime',
            dateTimeLabelFormats: {
                minute: '%H:%M',
                hour: '%H:%M',
                day: "%a.<br>%e %b.",
                month: '%b.<br>%y',
                year: '%Y'
            },
            lineColor: '#6E797C',
            lineWidth: 1
            },
            yAxis:[ 
                { // kWh
                gridLineColor: '#6E797C',
                gridLineDashStyle: 'longdash',
                lineWidth: 0,
                offset: 0,
                opposite: false,
                labels: {
                    //useHTML: true, //fix see through axis values.
                    format: '{value} kWh',
                    style: {
                        color: '#6E797C'
                    },
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#6E797C'
                }]
                },
                { // temp axis
                //tickAmount: 7,
                opposite: true,
                gridLineDashStyle: 'longdash',
                gridLineColor: '#6E797C',
                gridLineWidth: 1,
                labels: {
                format: '{value}°C',
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
                    color: '#6E797C',
                },
                formatter: function() {
                    var s = '<b>'+ Highcharts.dateFormat('%Y', this.x) +'</b>';
                    var d               = this.points;
                    var max_temp_color  = '#FF0000';
                    var avg_temp_color  = '#384042';
                    var min_temp_color  = '#0088FF';

                    var Pverbruik = Pgeleverd = Pnetto = Pavg_temp = Pmin_temp = Pmax_temp = 0;
                    var nettoIsOn = false;

                    // find timestamp and add data points
                    for (var i=0,  tot=GverbrData.length; i < tot; i++) {
                        if ( GverbrData[i][0] == d[0].key ) { //found time and dataset
                            Pverbruik    = GverbrData[i][1]
                            Pgeleverd    = GgelvrData[i][1]
                            Pnetto       = GnettoData[i][1]
                            Pmin_temp    = Granges[i][1];
                            Pmax_temp    = Granges[i][2];
                            Pavg_temp    = Gaverages[i][1]
                        break;
                        }
                    }

                    if ( $('#KwhChart').highcharts().series[0].visible === true ) {
                        s += '<br/><span style="color: #F2BA0F;"><?php echo strIdx( 359 )?>:&nbsp;</span>' + Pverbruik.toFixed(3) + " kWh";

                    }
                    if ( $('#KwhChart').highcharts().series[1].visible === true ) {
                        s += '<br/><span style="color: #98D023;"><?php echo strIdx( 360 )?>:&nbsp;</span>' + Pgeleverd.toFixed(3) + " kWh";;
                    }
                    if ( $('#KwhChart').highcharts().series[2].visible === true ) {
                        if  ( parseFloat( Pnetto ) == 0 ) {
                            s += '<br/><span style="color: black"><?php echo strIdx( 420 )?>.</span>'
                        } 
                        if  ( parseFloat( Pnetto ) < 0 ) {
                            s += '<br/><span style="color: black"><?php echo strIdx( 421 )?>: </span>' + ( Pnetto * -1).toFixed(3) + " kWh";
                        }
                        if  (parseFloat (Pnetto)  > 0 ) {
                            s += '<br/><span style="color: black"><?php echo strIdx( 422 )?>: </span>' + Pnetto.toFixed(3) + " kWh";
                        }
                    }
                    if ( $('#KwhChart').highcharts().series[3].visible === true ) {
                        if ( Pmax_temp != null ) {
                            s += '<br/><span style="color: ' + max_temp_color + '"><?php echo strIdx( 136 )?>: </span>'    + Pmax_temp.toFixed(1) + " °C";
                        }
                        if ( Pavg_temp != null ) {
                            s += '<br/><span style="color: ' + avg_temp_color + '"><?php echo strIdx( 137 )?>: </span>' + Pavg_temp.toFixed(1) + " °C";
                        }
                        if ( Pmin_temp != null ) {
                            s += '<br/><span style="color: ' + min_temp_color + '"><?php echo strIdx( 138 )?>: </span>'    + Pmin_temp.toFixed(1) + " °C";
                        }
                    }
              
                return s;
            },
            backgroundColor: '#F5F5F5',
            borderColor: '#DCE1E3',
            crosshairs: [true, true],
            borderWidth: 1
            },  
            navigator: {
                xAxis: {
                    minTickInterval:  5 * 365 * 24 * 3600000, 
                    maxRange:        30 * 365 * 24 * 3600000,
                    dateTimeLabelFormats: {
                        day: '%d %B'	
                    }    
                },
                enabled: true,
                outlineColor: '#384042',
                outlineWidth: 1,
                handles: {
                    backgroundColor: '#384042',
                    borderColor: '#6E797C'
                },
                series: {
                    color: '#10D0E7'
                }
            },
            series: [ 
                {
                    yAxis: 0,
                    id: 'verbruik',
                    visible: GseriesVisibilty[0],
                    name: '<?php echo strIdx( 416 )?>',
                    color: '#F2BA0F',
                    data: GverbrData 
                },{
                    yAxis: 0,
                    id: 'geleverd',
                    visible: GseriesVisibilty[1],
                    name: '<?php echo strIdx( 417 )?>',
                    color: '#98D023',
                    data: GgelvrData
                },{
                    yAxis: 0,
                    id: 'netto',
                    visible: GseriesVisibilty[2],
                    type: 'spline', 
                    color: 'black',
                    name: '<?php echo strIdx( 419 )?>',
                    data: GnettoData,
                    dashStyle: 'ShortDashDotDot',
                    lineWidth: 1
                },{
                    yAxis: 1,
                    visible: GseriesVisibilty[3],
                    showInNavigator: true,
                    id: 'temperatuur',
                    name: '<?php echo strIdx( 139 )?>',
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
                },{
                    yAxis: 1,
                    dashStyle: 'ShortDot',
                    visible: GseriesVisibilty[3],
                    id: 'temperatuurRange',
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
                }
            ],
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
            }
  });
}

function updateData() {
    //console.log("updateData()");
    var chart = $('#KwhChart').highcharts();
    if( typeof(chart) !== 'undefined') {
        chart.series[0].setData( GverbrData );
        chart.series[1].setData( GgelvrData );
        chart.series[2].setData( GnettoData );
        chart.series[3].setData( Gaverages );
        chart.series[4].setData( Granges );
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
        readJsonApiHistoryYear( maxrecords );
    }
    // make chart only once and when we have data.
    if (recordsLoaded !== 0 &&  $('#KwhChart').highcharts() == null) {
      hideStuff('loading-data');
      updateData();
      createKwhChart();
    }
    setTimeout('DataLoop()',1000);
}

$(function() {
    toLocalStorage('stats-menu',window.location.pathname);
    Gselected = parseInt(getLocalStorage('stat-j-select-index'),10);
    GseriesVisibilty[0] =JSON.parse(getLocalStorage('stat-j-verbr-visible'));  // #PARAMETER
    GseriesVisibilty[1] =JSON.parse(getLocalStorage('stat-j-gelvr-visible'));  // #PARAMETER
    GseriesVisibilty[2] =JSON.parse(getLocalStorage('stat-j-netto-visible'));  // #PARAMETER
    GseriesVisibilty[3] =JSON.parse(getLocalStorage('stat-j-temp-visible'));   // #PARAMETER
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
       <?php page_menu_header(4); ?>
	   <?php weather_info(); ?>
    </div>
</div>

<div class="mid-section">
    <div class="left-wrapper">
        <?php page_menu(1); ?>
        <div id="timerText" class="pos-8 color-timer"></div>
        <?php fullscreen(); ?>
    </div> 
    <div class="mid-content-2 pad-13">
    <!-- links -->
        <div class="frame-2-top">
            <span class="text-2"><?php echo strIdx( 124 )?> (kWh)</span>
        </div>
        <div class="frame-2-bot"> 
        <div id="KwhChart" style="width:100%; height:480px;"></div>
        </div>
</div>
</div>
<div id="loading-data"><img src="./img/ajax-loader.gif" alt="<?php echo strIdx( 295 )?>" height="15" width="128"></div>

</body>
</html>