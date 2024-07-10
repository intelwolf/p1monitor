<?php 
include_once '/p1mon/www/util/page_header.php'; 
include_once '/p1mon/www/util/p1mon-util.php';
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/page_menu_header_actual.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/fullscreen.php';
include_once '/p1mon/www/util/highchart.php';

if ( checkDisplayIsActive(18) == false) { return; }
?>
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title>P1-monitor <?php echo strIdx( 411 )?></title>
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
var currentGasUsage         = 0;
var previousGasUsage        = -1;
var secs                    = 10;

var GDailyGasM3             = 0;
var GdataHourGas            = [];
var currentGasUsageMaxValue = <?php echo config_read( 41 ); ?>;
var dayGasUsageMaxValue     = <?php echo config_read( 207 ); ?>;
var predictionInOn          = <?php echo config_read( 59 ); ?>;
var currentGasUsageMinValue = 0;
var currentGasUsage         = 0;
var aninmatecurrentGasUsageTimer = 0;
var gasCount                = 25;
var Gaverage_gas_value      = 0;

function readJsonApiSmartMeter( cnt ){ 
    $.getScript( "./api/v1/powergas/hour?limit=" + cnt, function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        var item;
        GdataHourGas.length   = 0;
        for (var j = jsondata.length; j > 0; j--){
            item = jsondata[ j-1 ];
            item[1] = item[1] * 1000; // highchart likes millisecs.
            if ( Gaverage_gas_value > 0 && predictionInOn == 1 && j==1  ) { 
                //console.log (" push it " + Gaverage_gas_value)
                GdataHourGas.push ( [item[1], Gaverage_gas_value ]);
            } else {
                GdataHourGas.push ( [item[1], item[10] ]);
            }
        }

        $("#gasMeterGrafiekVerbruik").highcharts().series[0].update({
            pointStart: GdataHourGas[0][0],
            data: GdataHourGas
        }, true);

        $("#gasMeterGrafiekVerbruik").highcharts().redraw();
        

      } catch(err) {}
   });
}

function readJsonApiHistoryDay(){ 
    $.getScript( "/api/v1/powergas/day?limit=1", function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse( data ); 
        //var point = $("#dailyuse").highcharts().series[0].points[0];
        //point.update( jsondata[0][9], true, true, true );

        var point = $("#dailyuse").highcharts().series[0].points[0];
        point.update( parseFloat( jsondata[0][9] ), true, true, true );

      } catch(err) {}
   });
}

function readJsonApiHistoryHour(){ 
    $.getScript( "/api/v1/powergas/hour?limit=4", function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        var item;
        recordsLoaded     = jsondata.length;
        //console.log( "jsondata = "+ jsondata  );
        //GdataHourGas.length   = 0;
        dataHourGasBuf = [];
        for (var j = jsondata.length; j > 0; j--){    
            item = jsondata[j-1];
            item[1] = item[1]*1000; // highchart likes millisecs.
            dataHourGasBuf.push ( [item[1], item[10] ]);
        } 
        currentGasUsage =  dataHourGasBuf[jsondata.length-1][1]
        //console.log( "currentGasUsage = "+ currentGasUsage  );

        //console.log( "gaugeDataGasVerbruik = "+ gaugeDataGasVerbruik  );
        //console.log( "gaugeDataGasVerbruik[0]= "+ gaugeDataGasVerbruik[1] );
        
        //gaugeDataGasVerbruik[1] = 0;
        //console.log ( "currentGasUsage = " + currentGasUsage )
        if (currentGasUsage == 0 && predictionInOn == 1 ) {
            if ( dataHourGasBuf.length > 3 ) { 
                //console.log( "currentGasUsage =aangepast, voorspelling actief." )
                Gaverage_gas_value = (
                    dataHourGasBuf[dataHourGasBuf.length-2][1] + 
                    dataHourGasBuf[dataHourGasBuf.length-3][1] + 
                    dataHourGasBuf[dataHourGasBuf.length-4][1]) / 3;
                
                if ( Gaverage_gas_value > 0 ) {
                    currentGasUsage = Gaverage_gas_value;
                    showStuff('gasVoorspelling');
                 } else {
                    hideStuff('gasVoorspelling');
                    Gaverage_gas_value = 0;
                 }
                } 
            } else {
                    hideStuff('gasVoorspelling');
                    Gaverage_gas_value = 0;
            }

            //currentGasUsage = Number.parseFloat( parseFloat( jsondata[j][1] ).toFixed(1) );
            
            var point = $("#currentuse").highcharts().series[0].points[0];
            point.update( Number.parseFloat( Number.parseFloat( currentGasUsage.toFixed(2)) ), true, true, true);  

            readJsonApiSmartMeter( gasCount );

      } catch(err) {
        console.log( err )
      }
   });
}

function readJsonApiFinancial(){ 
    $.getScript( "./api/v1/financial/day?limit=1", function( data, textStatus, jqxhr ) {
        try {
            var jsondataCost = JSON.parse(data); 
            verbrGasKosten = jsondataCost[0][6]
            $("#dailycosttext").text(padXX( parseFloat( verbrGasKosten ), 2, 2));
        } catch(err) {}
    });
}

function createChartVerbruikGrafiek() {
    $("#gasMeterGrafiekVerbruik").highcharts({
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
            s += "<br/><span style='color: #507ABF;'>m<sup>3</sup> <?php echo strIdx( 359 )?>: </span>" + this.y.toFixed(2);
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
            useHTML: true,
            style: {
                fontSize: "10px"
            },
            y: 2,
            x: -40,
            align: "left",
            distance: 0,
            formatter: function () {
                return (this.value ) + " m<sup>3</sup>"
            }
        }
    },
    plotOptions: {
        series: {
            color: "#507ABF",
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
        data: GdataHourGas
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
            max: dayGasUsageMaxValue,
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
            useHTML: true,
            text: "m<sup>3</sup>/dag",
            style: {
                color: "#6E797C",
                fontWeight: "bold",
                fontSize: "26px"
            },
        },
        labels: {
            style: {
                color: "#6E797C",
                fontWeight: "bold",
                fontSize: "28px"
            },
            y: 30,
            x: 0,
            align: "center",
            distance: -30
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
                y: parseFloat( GDailyGasM3 )
            }
        ]
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
        max: currentGasUsageMaxValue,
        min: currentGasUsageMinValue,
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
            y: 40,
            useHTML: true,
            text: "m<sup>3</sup>/uur",
            style: {
                color: "#6E797C",
                fontWeight: "bold",
                fontSize: "55px"
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
                y: parseFloat( currentGasUsage )
            }]
        }]
    });
}
        
function DataLoop10Sec() {
    secs--;
    if( secs < 0 ) { 
        secs = 10; 
        //readJsonApiSmartMeter( gasCount );
        readJsonApiFinancial();
        readJsonApiHistoryDay();
        readJsonApiHistoryHour();
    }
    setTimeout('DataLoop10Sec()',1000);
    document.getElementById("timerText").innerHTML = "00:" + zeroPad(secs,2);
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
    DataLoop10Sec(); 
});


</script>
    </head>
    <body>

        <?php page_header();?>

        <div class="top-wrapper-2">
            <div class="content-wrapper pad-13">
                <!-- header 2 --> 
                 <?php pageclock(); ?>
                 <?php page_menu_header_actual(2); ?>
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
                        <span class="text-2"><?php echo strIdx( 411)?></span> <span class="text-25" id="gasVoorspelling" style="display: none">(<?php echo strIdx( 365 )?>)</span>
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
                        <span class="text-3"><?php echo strIdx( 412 )?></span>
                    </div>
                    <div class="frame-2-bot">
                        <div id="gasMeterGrafiekVerbruik" class="pos-26"></div>
                    </div>
                </div>

            </div>
        </div>
    </body>
    </html>