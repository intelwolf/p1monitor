<?php 
include_once '/p1mon/www/util/page_header.php'; 
include_once '/p1mon/www/util/p1mon-util.php';
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/page_menu_header_actual.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/fullscreen.php';
include_once '/p1mon/www/util/textlib.php';
include_once '/p1mon/www/util/highchart.php';

if ( checkDisplayIsActive(18) == false) { return; }
?>
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title>P1-monitor <?php echo strIdx( 403 )?></title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css">
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css">

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/highstock-link/highstock.js"></script>
<script src="./js/highstock-link/highcharts-more.js"></script>
<script src="./js/highstock-link/modules/accessibility.js"></script>
<script src="./js/highstock-link/modules/solid-gauge.js"></script>
<script src="./js/hc-global-options.js"></script>
<script src="./js/p1mon-util.js"></script>

<script>
var progressCnt     = 1;
var progressTimer   = 0;
var currentWattage  = 0;
var previousWattage = -1; 
var secs            = 10;

var GdailyKWh       = 0;
var GData10sec      = [];

var currentWattageMaxValue      = <?php echo config_read( 24  ); ?>;
var currentKWhMaxValue          = <?php echo config_read( 57  ); ?>;
var useKw                       = <?php echo config_read( 180 ); ?>;
var currentWattageMinValue      = 0
var aninmateCurrentWattageTimer = 0;
var p1TelegramMaxSpeedIsOn      = <?php if ( config_read( 154 ) == 1 ) { echo "true;"; } else { echo "false;"; } echo"\n";?> 

if ( useKw ) {
    var wattText = 'kW'
    currentWattageMaxValue = currentWattageMaxValue/1000
} else {
    var wattText = 'watt'
}

Number.prototype.countDecimals = function () {

    if (Math.floor(this.valueOf()) === this.valueOf()) return 0;

    var str = this.toString();
    if (str.indexOf(".") !== -1 && str.indexOf("-") !== -1) {
        return str.split("-")[1] || 0;
    } else if (str.indexOf(".") !== -1) {
        return str.split(".")[1].length || 0;
    }
    return str.split("-")[1] || 0;
}


function readJsonApiSmartMeter(){ 
    $.getScript( "./api/v1/smartmeter?limit=720", function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        var item;
        GData10sec.length = 0;

        for ( var j = jsondata.length; j > 0; j-- ) {    
            item = jsondata[ j-1 ];
            item[1] = item[1] * 1000; // highchart likes millisecs.
            GData10sec.push( [ item[1], item[8]/1000 ] );
        }

        $("#vermogenMeterGrafiekVerbruik").highcharts().series[0].update({
            pointStart: GData10sec[0][0],
            data: GData10sec
        }, true);
         $("#vermogenMeterGrafiekVerbruik").highcharts().redraw();

        if ( useKw ) { 
            currentWattage = ( jsondata[0][8] / 1000 );
        } else { 
            currentWattage = ( jsondata[0][8] );
        }

        if ( currentWattage.countDecimals() == 0 ) {
            currentWattage = parseInt( currentWattage ) // remove trailing zero's when the are 0
        }

        var point = $("#currentuse").highcharts().series[0].points[0];
        point.update( currentWattage, true, true, true );

      } catch(err) {}
   });
}

function readJsonApiHistoryDay(){ 
    $.getScript( "/api/v1/powergas/day?limit=1", function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        var point = $("#dailyuse").highcharts().series[0].points[0];
        point.update( jsondata[0][6], true, true, true );
      } catch(err) {}
   });
}

function readJsonApiFinancial(){ 
    $.getScript( "./api/v1/financial/day?limit=1", function( data, textStatus, jqxhr ) {
        try {
            var jsondataCost = JSON.parse(data); 
            verbrKosten = jsondataCost[0][2] + jsondataCost[0][3];
            $("#dailycosttext").text(padXX(parseFloat(verbrKosten), 3, 2));
        } catch(err) {}
    });
}

function createChartVerbruikGrafiek() {
    $("#vermogenMeterGrafiekVerbruik").highcharts({
    chart: {
        type: "areaspline",
        spacingLeft: 44
    },
    legend: {
        enabled: false
    },
    exporting: {
        enabled: false
    },
    credits: {
        enabled: false
    },
    title: {
        text: null
    },
    tooltip: {
        useHTML: true,
        style: {
            padding: 3,
            color: "#6E797C"
        },
        formatter: function () {
            var s = "<b>" + Highcharts.dateFormat("%A %H:%M:%S", this.x) + "</b>";
            if ( useKw ) {
                s += "<br/><span style='color: #F2BA0F;'><?php echo strIdx( 404 )?>: </span>" + (this.y );
            } else {
                s += "<br/><span style='color: #F2BA0F;'><?php echo strIdx( 405 )?>: </span>" + (this.y * 1000).toFixed(0);
            }
            return s;
        },
        backgroundColor: "#F5F5F5",
        borderColor: "#DCE1E3",
        crosshairs: [true, true],
        borderWidth: 1
    },
    xAxis: {
        type: "datetime",
        lineColor: "#6E797C",
        lineWidth: 1
    },
    yAxis: {
        gridLineColor: "#6E797C",
        gridLineDashStyle: "longdash",
        floor: 0,
        title: {
            text: null
        },
        labels: {
            style: {
                fontSize: "10px"
            },
            y: 2,
            x: -40,
            align: "left",
            distance: 0,
            formatter: function () {
                if ( useKw ) {
                    return ( this.value ) + " kW"
                } else {
                    return ( this.value * 1000 ) + " W"
                }
            }
        }
    },
    plotOptions: {
        series: {
            color: "#F2BA0F",
            states: {
                hover: {
                    enabled: false
                }
            },
            marker: {
                enabled: false
            }
        }
    },
    series: [{
        data: GData10sec
    }]
  });
}

function createDailytUseChart() {
    $("#dailyuse").highcharts({
        chart: {
            type: "solidgauge",
            width: 330,
            height: 200,
            margin: [-10, 0, 0, 0]
        },
        title: null,
        credits: {
            enabled: false
        },
        pane: {
            center: ["50%", "85%"],
            size: "150%",
            startAngle: -90,
            endAngle: 90,
            background: {
                backgroundColor: "#F5F5F5",
                innerRadius: "60%",
                outerRadius: "100%",
                shape: "arc"
            }
        },
        tooltip: {
            enabled: false
        },
        yAxis: {
            max: currentKWhMaxValue,
            min: 0,
            stops: [
                [0.1, "#55BF3B"], // green
                [0.5, "#DDDF0D"], // yellow
                [0.9, "#DF5353"] // red
            ],
            lineWidth: 0,
            minorTickInterval: null,
            tickPixelInterval: 500,
            tickAmount: 0,
            tickWidth: 0,
            title: {
            y: 30,
            text: "kWh",
            style: {
                color: "#6E797C",
                fontWeight: "bold",
                fontSize: "36px"
            },
        },
        labels: {
            format: '{value:.0f}',
            style: {
                color: "#6E797C",
                fontWeight: "bold",
                fontSize: "28px"
            },
            y: 30,
            x: 0,
            align: "center",
            distance: -35
            }
        },
        series: [{
            animation: true,
            dataLabels: {
                useHTML: true,
                format: "{point.y:000.1f}",
                borderColor: null,
                padding: 4,
                borderRadius: 5,
                verticalAlign: "center",
                y: 0,
                color: "#6E797C",
                style: {
                    fontWeight: "bold",
                    fontSize: "45px"
                }
            },
        data: [{
            y: parseFloat( GdailyKWh )
        }]
        }]
    });
}

function creatCurrentUseChart() {
    $("#currentuse").highcharts({
    chart: {
        type: "solidgauge",
        width: 600,
        height: 310,
        margin: [0, 0, 0, -26]
    },
    title: "null",
    credits: {
        enabled: false
    },
    pane: {
        center: ["50%", "85%"],
        size: "165%",
        startAngle: -90,
        endAngle: 90,
        background: {
            backgroundColor: "#F5F5F5",
            innerRadius: "60%",
            outerRadius: "100%",
            shape: "arc"
        }
    },
    tooltip: {
        enabled: false
    },
    yAxis: {
        max: currentWattageMaxValue,
        min: currentWattageMinValue,
        stops: [
            [0.1, "#55BF3B"], // green
            [0.5, "#DDDF0D"], // yellow
            [0.9, "#DF5353"]  // red
        ],
        lineWidth: 0,
        minorTickInterval: null,
        tickPixelInterval: 1000,
        tickWidth: 0,
        title: {
            y: 50,
            text: wattText,
            style: {
                color: "#6E797C",
                    fontWeight: "bold",
                    fontSize: "60px"
                },
            },
            labels: {
                color: "#6E797C",
                formatter: function () {
                    return this.value 
                },
                style: {
                    color: "#6E797C",
                    fontWeight: "bold",
                    fontSize: "26px"
                },
                y: 30,
                x: 0,
                align: "center",
                distance: -50
            }
        },
        series: [{
            animation: true,
            dataLabels: {
                useHTML: true,
                format: "{point.y:0000f}",
                borderColor: null,
                //borderColor: '#384042',
                padding: 4,
                borderRadius: 5,
                verticalAlign: "center",
                y: 0,
                color: "#6E797C",
                style: {
                    fontWeight: "bold",
                    fontSize: "72px"
                }
            },
            data: [{
                y: parseFloat( currentWattage )
            }]
        }]
    });
}

function DataLoop() {

    if ( p1TelegramMaxSpeedIsOn == true ) {
        secs = -1
    }

    secs--;
    if( secs < 0 ) { 
        secs = 10; 
        readJsonApiSmartMeter();
        readJsonApiFinancial();
        readJsonApiHistoryDay();
    }

    setTimeout( 'DataLoop()', 1000 );
    document.getElementById("timerText").innerHTML = "00:" + zeroPad( secs,2 );
}

$(function () {
    toLocalStorage('actual-menu',window.location.pathname);
    Highcharts.setOptions({
        global: {
            useUTC: false
        },
        lang: <?php hc_language_json(); ?>
    });

    creatCurrentUseChart();
    createDailytUseChart();
    createChartVerbruikGrafiek();
    $('#dailycost').removeClass('display-none');
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
                 <?php page_menu_header_actual(0); ?>
                 <?php weather_info(); ?>
            </div>
        </div>

        <div class="mid-section">
            <div class="left-wrapper">
                <?php page_menu(6); ?>
                <div id="timerText" class="pos-8 color-timer"></div>
                <?php fullscreen(); ?>
            </div>

            <div>

                <div class="mid-content-3 pad-13">
                    <div class="frame-2-top">
                        <span class="text-2"><?php echo strIdx( 403 )?></span>
                    </div>
                    <div class="frame-2-bot">
                        <div id="currentuse"></div>
                    </div>
                </div>

                <div class="pos-23 pad-1">
                    <div class="frame-2-top">
                        <span class="text-2"><?php echo strIdx( 358 )?></span>
                    </div>
                    <div class="frame-2-bot pos-24">
                        <div id="dailyuse"></div>
                        <div id='dailycost' class="text-13 display-none"><i class="fas fa-euro-sign"></i>&nbsp;<span id="dailycosttext">0</span></div>
                    </div>

                </div>
                <div class="pos-25">
                    <div class="frame-3-top">
                        <span class="text-3"><?php echo strIdx( 406 )?></span>
                    </div>
                    <div class="frame-2-bot">
                        <div id="vermogenMeterGrafiekVerbruik" class="pos-26"></div>
                    </div>
                </div>

            </div>
        </div>

        <script>
            if ( p1TelegramMaxSpeedIsOn == true ){ 
                $('#timerText').hide();
            } else {
                $('#timerText').show();
            }
        </script>

    </body>

    </html>