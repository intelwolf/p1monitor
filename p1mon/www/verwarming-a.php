<?php
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php';  
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/page_menu_header_heating.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/fullscreen.php';
include_once '/p1mon/www/util/highchart.php';

if ( checkDisplayIsActive(46) == false) { return; }
?>
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title>P1-monitor <?php echo strIdx( 187 )?></title>
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

var GhistoryIn       = [];
var recordsLoaded   = 0;
var initloadtimer;
//var Gselected       = 0;
var mins            = 1;
var secs            = mins * 60;
var currentSeconds  = 0;
var currentMinutes  = 0;
var maxrecords      = 61; // number of records to read

var ui_in_label     = "<?php echo config_read( 121 ); ?>"; 
var ui_uit_label    = "<?php echo config_read( 122 ); ?>";

function setLabels() {
    if ( ui_in_label.length == 0 ) {
        ui_in_label = "<?php echo strIdx( 452 )?>";
    }
    if ( ui_uit_label.length == 0 ) {
        ui_uit_label = "<?php echo strIdx( 453 )?>";
    }
}


function readJsonIndoorTemperature( cnt ){ 
    $.getScript( "./api/v1/indoor/temperature?limit=" + cnt , function( data, textStatus, jqxhr ) {
      try {

        var jsondata = JSON.parse(data); 
        var item;
        recordsLoaded = jsondata.length;
        GhistoryIn.length = 0;

        for (var j = jsondata.length; j > 0; j--){
          item = jsondata[j-1];
          item[1] = item[1]*1000; // highcharts likes millisecs.
          GhistoryIn.push ( [item[1], item[5], item[9]] ); //in max, out min
        } 
        
        $("#grafiekTemp").highcharts().series[0].setData( GhistoryIn )
        $("#tempChartIn").highcharts().series[0].points[0].update( GhistoryIn[GhistoryIn.length-1][1],  true, true, true);
        $("#tempChartOut").highcharts().series[0].points[0].update( GhistoryIn[GhistoryIn.length-1][2], true, true, true);

        $("#tempChartIn").highcharts().redraw();
        $("#tempChartOut").highcharts().redraw();

        //console.log( "in=" + GhistoryIn[GhistoryIn.length-1][1] + " out=" + GhistoryIn[GhistoryIn.length-1][2] )

        var deltatemp = Math.abs( GhistoryIn[GhistoryIn.length-1][1] - GhistoryIn[GhistoryIn.length-1][2] ).toFixed(1);
        //console.log( deltatemp )
        $('#deltatemp').text( deltatemp );

      } catch(err) {}
   });
}

function createChartIn() {

    $('#tempChartIn').highcharts({
        exporting: { enabled: false },
        tooltip: { enabled: false },
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
        title: {
        text: null
        },
        chart: {
            style: {
                fontFamily: 'robotomedium',
                fontSize: '14px'
            },
            backgroundColor: '#ffffff',
            borderWidth: 0,
                type: 'gauge',
                plotBorderWidth: 0,
                plotBackgroundImage: null,
                width: 450,
                height: 390,
                spacingTop: 50
        },
        pane: [{
            startAngle: -120,
            endAngle: 120,
            size: 360,
            background: [{
                    backgroundColor: '#F5F5F5',
                    borderWidth: 2,
                    outerRadius: '78%',
                    
                }],
        }, {
            startAngle: -120,
            endAngle: 120,
            background: null,
            center: ['75%', '60%'],
            //size: 380,
            background: [{
                    backgroundColor: '#F5F5F5',
                    borderWidth: 2,
                    outerRadius: '78%'
                }],
        }],
        yAxis: [{
            min: -30,
            //max: 60,
            max: 90,
            minorTickPosition: 'inside',
            minorTickLength: 30,
            minorTickColor: '#F5F5F5',
            tickPosition: 'inside',
            tickLength: 35,
            tickColor: '#F5F5F5',
            tickInterval: 10,
            labels: {
                rotation: 'auto',
                distance: 10,
                format: '{value}°C',
                style: {
                    color: '#6E797C',
                    fontSize:'15px'
                }
            },
            plotBands: [{
                innerRadius: '80%',
                outerRadius: '100%',
                from: -30,
                to: 90,
                color: {
                    linearGradient:  { x1: 0, x2: 0, y1: 0, y2: 1 },
                    stops: [
                    [0.4, '#55BF3B'], // green
                    [0.5, '#DDDF0D'], // yellow
                    [0.99, '#DF5353'] // red
                    ]
                }
                } 
            ],
            pane: 0,
            title: {
                text: '<span style="font-size:20px">' + ui_in_label + '<br></span>',
                y: 130,
                x: 0
            }
        }
    
        ],
        plotOptions: {
        gauge: {
            pivot: {
                radius: 8,
                borderWidth: 1,
                backgroundColor: '#384042',
                borderColor: '#F5F5F5'
            },
            dataLabels: {
                useHTML: true,
                format: '{point.y:.1f}°C',
                borderColor: '#384042',
                padding: 5,
                borderRadius: 5,
                verticalAlign: 'center',
                y: 45,
                x: 0,
                style: {
                    fontWeight: 'bold',
                    fontSize: '40px',
                    color: "#6e797c"
                    }
            },
            dial: {
                radius: '75%',
                backgroundColor: '#384042',
                borderWidth: 1,
                baseWidth: 15,
                topWidth: 1,
                baseLength: '1%', // of radius
                rearLength: '1%'
            },
        }
        },
        series: [{
        data: [10],
        yAxis: 0
        }]
    });
}

function createChartOut() {

    $('#tempChartOut').highcharts({
        exporting: { enabled: false },
        tooltip: { enabled: false },
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
    title: {
        text: null
    },
    chart: {
        style: {
            fontFamily: 'robotomedium',
            fontSize: '14px'
        },
        backgroundColor: '#ffffff',
        borderWidth: 0,
        type: 'gauge',
        plotBorderWidth: 0,
        plotBackgroundImage: null,
        width: 450,
        height: 390,
        spacingTop: 50
    },
    pane: [{
        startAngle: -120,
        endAngle: 120,
        //background: null,
        //center: ['25%', '60%'],
        //size: 380,
        size: 360,

        background: [{
            backgroundColor: '#F5F5F5',
            borderWidth: 2,
            outerRadius: '78%',
        }],
    }, {
        startAngle: -120,
        endAngle: 120,
        background: null,
        center: ['75%', '60%'],
        //size: 380,
        background: [{
            backgroundColor: '#F5F5F5',
            borderWidth: 2,
            outerRadius: '78%'
        }],
    }],
    yAxis: [{
        min: -30,
        max: 90,

        minorTickPosition: 'inside',
        minorTickLength: 30,
        minorTickColor: '#F5F5F5',

        tickPosition: 'inside',
        tickLength: 35,
        tickColor: '#F5F5F5',
        tickInterval: 10,

        labels: {
            rotation: 'auto',
            distance: 10,
            format: '{value}°C',
            style: {
                color: '#6E797C',
                fontSize:'15px'
            }
        },
        plotBands: [{
            innerRadius: '80%',
            outerRadius: '100%',
            from: -30,
            to: 90,
            color: {
                linearGradient:  { x1: 0, x2: 0, y1: 0, y2: 1 },
                stops: [
                    [0.4, '#55BF3B'], // green
                    [0.5, '#DDDF0D'], // yellow
                    [0.99, '#DF5353'] // red
                ]
            }
            }
        ],
        pane: 0,
        title: {
          text: '<span style="font-size:20px">' + ui_uit_label + '<br></span>',
          y: 130,
          x: 0
        }
        }
        ],
        plotOptions: {
            gauge: {
                pivot: {
                    radius: 8,
                    borderWidth: 1,
                    backgroundColor: '#384042',
                    borderColor: '#F5F5F5'
                },
                dataLabels: {
                    useHTML: true,
                    format: '{point.y:.1f}°C',
                    borderColor: '#384042',
                    padding: 5,
                    borderRadius: 5,
                    verticalAlign: 'center',
                    y: 45,
                    x: 0,
                    style: {
                        fontWeight: 'bold',
                        fontSize: '40px',
                        color: "#6e797c"
                    }
                },
            dial: {
                radius: '75%',
                backgroundColor: '#384042',
                borderWidth: 1,
                baseWidth: 15,
                topWidth: 1,
                baseLength: '1%', // of radius
                rearLength: '1%'
            },
        }
        },
        series: [{
        data: [10],
        yAxis: 0
        }]
    }); 
}

function createChartGrafiek() { 
    $('#grafiekTemp').highcharts({
        chart: {
            type: 'areasplinerange'
        },
        legend: { enabled: false },
            exporting: { enabled: false },
            credits: { enabled: false },
            title: { text: null },
            tooltip: {
                useHTML: false,
                style: {
                    padding: 3,
                    color: '#6E797C'
                },
                formatter: function() {
                    var t_high  = 0;
                    var t_low   = 0;
                    var t_delta = 0;

                    t_high = this.point.low;
                    t_low  = this.point.high;
                    t_delta = Math.abs(t_high - t_low);

                    var s = '<b>'+ Highcharts.dateFormat('%A %H:%M:%S', this.x) +'</b>';
                        s += '<br/><span style="color: #FF0000;">'+ ui_in_label + ':' + t_high.toFixed(1) + '°C</span>'
                        s += '<br/><span style="color: #0000FF;">' + ui_uit_label + ':' + t_low.toFixed(1)+'°C</span>';
                        s += '<br/><span style="color: #333"><b></b><?php echo strIdx( 450 )?>:</b></span>';
                        s += '<br/><span style="color: #3333FF">' + ui_in_label + ' - ' + ui_uit_label + ':'+t_delta.toFixed(1)+"°C</span>";
                            return s;
                    },
                    backgroundColor: '#F5F5F5',
                    borderColor: '#DCE1E3',
                    crosshairs: [true, true],
                    borderWidth: 1
        },
        xAxis: {
            type: 'datetime',
            lineColor: '#6E797C',
            lineWidth: 1
        },
        yAxis: {
          //tickAmount: 7,
          tickInterval: 0.8,
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
                text: null
          }
        },
      series: [{
      dashStyle: 'ShortDot',
      name: 'verschil',
      data: GhistoryIn,
      type: 'areasplinerange',
      lineWidth: 1,
      color: '#FF0000',
      negativeColor: '#0088FF',
      fillOpacity: 0.3,
      zIndex: 1,
      marker: {
            enabled: false
        }
      }
      ]
  });
}

function DataLoop() {
    //readJsonData(maxrecords);
    readJsonIndoorTemperature( maxrecords )
    setTimeout('DataLoop()',1000);
}

$(function() {
    setLabels();
    toLocalStorage('verwarming-menu',window.location.pathname);
    Highcharts.setOptions({
        global: {
            useUTC: false
        },
        lang: <?php hc_language_json(); ?>
    });
    createChartIn();
    createChartOut();
    createChartGrafiek();

    screenSaver( <?php echo config_read(79);?> ); // to enable screensaver for this screen.
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
        <?php page_menu_header_heating(0); ?>  <!-- parameter -->
        <?php weather_info(); ?>
    </div>
</div>

<div class="mid-section">
    <div class="left-wrapper">
        <?php page_menu(7); ?>
        <!-- <div id="timerText" class="pos-8 color-timer"></div> -->
        <?php fullscreen(); ?>
    </div> 
    <div class="mid-content-2 pad-13">
    <!-- links -->
        <div class="frame-2-top">
            <span class="text-2"><?php echo strIdx( 449 )?></span>
        </div>
        <div class="frame-2-bot"> 
        
          <div class="content-wrapper">
            <div style="width: 50%; float:left">
              <div id="tempChartIn" ></div>
            </div>

            <div style="width: 50%; float:left">
              <div id="tempChartOut" ></div>
            </div>
          </div>

          <div class="center text-31">
              <span><?php echo strIdx( 450 )?>&nbsp;</span><span id='deltatemp'>-</span><span>°C</span>
         </div>

          <div class="pad-3" style="float:left;">
                <div class="frame-3-top">
                <span class="text-3"><?php echo strIdx( 451 )?></span>
                </div>
                <div class="frame-2-bot">
                  <div id="grafiekTemp" style="width:880px; height:110px;"></div>
                </div>
            </div>
        </div>
</div>
</div>
</body>
</html>