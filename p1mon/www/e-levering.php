<?php 
include '/p1mon/www/util/page_header.php'; 
include '/p1mon/www/util/p1mon-util.php';
include '/p1mon/www/util/page_menu.php';
include '/p1mon/www/util/page_menu_header_actual.php';
#include '/p1mon/www/util/config_read.php';
include '/p1mon/www/util/check_display_is_active.php';
include '/p1mon/www/util/weather_info.php';
include '/p1mon/www/util/pageclock.php';
include '/p1mon/www/util/fullscreen.php';

if ( checkDisplayIsActive(18) == false) { return; }
?>
<!doctype html>
<html lang="nl">
<head>
<title>P1monitor actueel levering</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css"/>
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/highstock-link/highstock.js"></script>
<script src="./js/highstock-link/highcharts-more.js"></script>
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
var currentWattageMaxValue = <?php echo config_read(23); ?>;
var currentKWhMaxValue = <?php echo config_read(56); ?>;
var currentWattageMinValue = 0;
var aninmateCurrentWattageTimer = 0;

function readJsonApiSmartMeter(){ 
    $.getScript( "./api/v1/smartmeter?limit=1440", function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        var item;
        GData10sec.length = 0;

        for ( var j = jsondata.length; j > 0; j-- ) {    
            item = jsondata[ j-1 ];
            item[1] = item[1] * 1000; // highchart likes millisecs.
            GData10sec.push( [ item[1], item[9]/1000 ]  );
        }

        $("#vermogenMeterGrafiekVerbruik").highcharts().series[0].update({
            pointStart: GData10sec[0][0],
            data: GData10sec
        }, true);
         $("#vermogenMeterGrafiekVerbruik").highcharts().redraw();

        currentWattage = ( jsondata[0][9] ); 
        
        if ( currentWattage < 0 || currentWattage > 30000 ) {
           return; //fail save for error values. 
        }
        //console.log(currentWattage);
        
        if  ( currentWattage < currentWattageMinValue ) currentWattage = currentWattageMinValue
        if  ( currentWattage > currentWattageMaxValue ) currentWattage = currentWattageMaxValue
                
        if (previousWattage < 0) { // init
            var point = $("#currentuse").highcharts().series[0].points[0];
            point.update(currentWattage, true, true, true);    
         } else  {
            //console.log("step1 currentWattage="+currentWattage+" previousWattage="+previousWattage);
            if ( currentWattage !==  previousWattage ){
                aninmateCurrentWattage() 
            }
         }
        previousWattage = currentWattage;

      } catch(err) {}
   });
}

function readJsonApiHistoryDay(){ 
    $.getScript( "/api/v1/powergas/day?limit=1", function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        var point = $("#dailyuse").highcharts().series[0].points[0];
        point.update( jsondata[0][7], true, true, true );
      } catch(err) {}
   });
}

function readJsonApiFinancial(){ 
    $.getScript( "./api/v1/financial/day?limit=1", function( data, textStatus, jqxhr ) {
        try {
            var jsondataCost = JSON.parse(data); 
            gelvrKosten = jsondataCost[0][4] + jsondataCost[0][5];
            $("#dailycosttext").text(padXX( parseFloat( gelvrKosten ), 2, 2) );
        } catch(err) {}
    });
}

function aninmateCurrentWattage() {
    // failsave for async problenms
    if ( aninmateCurrentWattageTimer != 0 ) {
        return; // still busy with prevous run.
    }

    var stepSize = (currentWattage - previousWattage)/ 19 ; 
    var looptime = 500;
    var totalTimeMax = 9500
    var looptimeTotal = 0 ;
    var value = previousWattage;
    
    //console.log("currentWattage="+currentWattage+" previousWattage="+previousWattage+ " stepSize="+stepSize+" looptime="+looptime);
    
    aninmateCurrentWattageTimer = setTimeout(function next() {
        //console.log("aninmateCurrentWattageTimer="+aninmateCurrentWattageTimer);
        looptimeTotal += looptime;
                    
        if (looptimeTotal >= totalTimeMax) {
            updatePoint(currentWattage)             
            //console.log("final currentWattage="+currentWattage+" previousWattage="+previousWattage+ " stepSize="+stepSize+" looptime="+looptime+" value="+value);
            //console.log("Done.");
            clearTimeout(aninmateCurrentWattageTimer);
            aninmateCurrentWattageTimer = 0;
            //console.log("aninmateCurrentWattageTimer Done="+aninmateCurrentWattageTimer);
            return;
        }
                    
        value = Math.floor(value+stepSize);
        //console.log("currentWattage="+currentWattage+" previousWattage="+previousWattage+ " stepSize="+stepSize+" looptime="+looptime+" value="+value);
                    
        if (stepSize < 0 && value < currentWattage ) {
            value = currentWattage
            //console.log("minvalue reached");
            updatePoint(value);
            clearTimeout(aninmateCurrentWattageTimer);
            aninmateCurrentWattageTimer = 0;
            //console.log("aninmateCurrentWattageTimer minvalue="+aninmateCurrentWattageTimer);
            return;
        }
                    
        if (stepSize > 0 && value > currentWattage ) {
            value = currentWattage
            //console.log("maxvalue reached");
            updatePoint(value);
            clearTimeout(aninmateCurrentWattageTimer);
            aninmateCurrentWattageTimer = 0;
            //console.log("aninmateCurrentWattageTimer maxvalue="+aninmateCurrentWattageTimer);
            return;
        }
                    
        updatePoint(value)
            aninmateCurrentWattageTimer = setTimeout(next, looptime);
        }, looptime);          
    }  
            
function updatePoint(val) {
    val = Number.parseInt( Number.parseFloat(val.toFixed(1) ) );
    if  ( val < currentWattageMinValue ) val = currentWattageMinValue;
    if  ( val > currentWattageMaxValue ) val = currentWattageMaxValue;
    var point = $("#currentuse").highcharts().series[0].points[0];
    point.update(val, true, true, true);    
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
            s += "<br/><span style='color: #98D023;'>Watt geleverd: </span>" + (this.y*1000).toFixed(0);
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
                return (this.value * 1000) + " W"
            }
        }
    },
    plotOptions: {
        series: {
            color: "#98D023",
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
                [0.1, "#ddf3d8"], // light green
                [0.5, "#9ADB8A"], // medium green
                [0.9, "#55BF3B"], // high green
            ],
            lineWidth: 0,
            minorTickInterval: null,
            tickPixelInterval: 500,
            tickAmount: 0,
            tickWidth: 0,
            title: {
            y: 105,
            text: "kWh",
            style: {
                color: "#6E797C",
                fontWeight: "bold",
                fontSize: "32px"
            },
        },
        labels: {
            style: {
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
            format: "{point.y:000.1f}",
            borderColor: null,
            padding: 4,
            borderRadius: 5,
            verticalAlign: "center",
            y: 20,
            color: "#6E797C",
            style: {
                fontWeight: "bold",
                fontSize: "60px"
            }
        },
        data: [{
            y: parseFloat(GdailyKWh)
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
                [0.1, "#ddf3d8"], // light green
                [0.5, "#9ADB8A"], // medium green
                [0.9, "#55BF3B"], // high green
            ],
        lineWidth: 1,
        minorTickInterval: null,
        tickPixelInterval: 1000,
        tickWidth: 0,
        title: {
            y: 165,
            text: "watt",
            style: {
                color: "#6E797C",
                    fontWeight: "bold",
                    fontSize: "42px"
                },
            },
            labels: {
                color: "#6E797C",
                formatter: function () {
                    return this.value 
                },
                style: {
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
            format: "{point.y:0000f}",
            borderColor: null,
            //borderColor: '#384042',
            padding: 4,
            borderRadius: 5,
            verticalAlign: "center",
            y: 20,
            color: "#6E797C",
            style: {
                fontWeight: "bold",
                fontSize: "92px"
            }
            },
            data: [{
                y: parseFloat(currentWattage)
            }]
        }]
    });
}
        
function DataLoop10Sec() {
    secs--;
    if( secs < 0 ) { 
        secs = 10; 
        readJsonApiSmartMeter();
        readJsonApiFinancial();
        readJsonApiHistoryDay();
    }
    setTimeout('DataLoop10Sec()',1000);
    document.getElementById("timerText").innerHTML = "00:" + zeroPad(secs,2);
}

$(function () {
    toLocalStorage('actual-menu',window.location.pathname);
    Highcharts.setOptions({
        global: {
            useUTC: false
        }
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
                 <?php page_menu_header_actual(1); ?>
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
                        <span class="text-2">actuele levering</span>
                    </div>
                    <div class="frame-2-bot">
                        <div id="currentuse"></div>
                    </div>
                </div>

                <div class="pos-23 pad-1">
                    <div class="frame-2-top">
                        <span class="text-2">totaal vandaag</span>
                    </div>
                    <div class="frame-2-bot pos-24">
                        <div id="dailyuse"></div>
                        <div id='dailycost' class="text-13 display-none"><i class="fas fa-euro-sign"></i>&nbsp;<span id="dailycosttext">0</span></div>
                    </div>

                </div>
                <div class="pos-25">
                    <div class="frame-3-top">
                        <span class="text-3">laatste vier uur levering</span>
                    </div>
                    <div class="frame-2-bot">
                        <div id="vermogenMeterGrafiekVerbruik" class="pos-26"></div>
                    </div>
                </div>

            </div>
        </div>
    </body>

    </html>