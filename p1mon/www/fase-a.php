<?php 
include_once '/p1mon/www/util/page_header.php'; 
include_once '/p1mon/www/util/p1mon-util.php';
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/page_menu_header_fase.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/fullscreen.php';
include_once '/p1mon/www/util/textlib.php';

if ( checkDisplayIsActive(61) == false) { return; }
?>
<!doctype html>
<html lang="nl">
<head>
<title>P1monitor actueel fase</title>
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

var maxAmperageFromConfig = <?php echo config_read( 123 ) . ";\n"?>
var maxWattFromConfig     = <?php echo config_read( 124 ) . ";\n"?>
var graphIdArray =  [ 'L1Watt',    'L1Amperage', 'L1Voltage', 'L2Watt',    'L2Amperage', 'L2Voltage', 'L3Watt',    'L3Amperage', 'L3Voltage' ]
var buttonIdArray = [ 'L1WButton', 'L1AButton',  'L1VButton', 'L2WButton', 'L2AButton',  'L2VButton', 'L3WButton', 'L3AButton',  'L3VButton' ]

function readJsonApiPhaseInformationFromStatus(){ 

    $.getScript( "./api/v1/status", function( data, textStatus, jqxhr ) {
      try {

        var jsondata = JSON.parse(data); 
        var L1Wconsumption  = 0;
        var L2Wconsumption  = 0;
        var L3Wconsumption  = 0;
        var L1Wproduction   = 0;
        var L2Wproduction   = 0;
        var L3Wproduction   = 0;
        var L1A             = 0;
        var L2A             = 0;
        var L3A             = 0;
        var L1V             = 0;
        var L2V             = 0;
        var L3V             = 0;
        
        for (var j=73;  j < jsondata.length; j++){  
            //console.log( jsondata[j][0] + ' - ' + jsondata[j][1] )
            if ( j > 105 ) break; // loop only when needed
            if ( jsondata[j][0] == 74 ) {
                L1Wconsumption = Math.ceil( jsondata[j][1] * 1000 );
                //L1Wconsumption = 6000
                continue;
            }
            if ( jsondata[j][0] == 75 ) {
                L2Wconsumption = Math.ceil(  jsondata[j][1] * 1000 );
                continue;
            }
            if ( jsondata[j][0] == 76 ) {
                L3Wconsumption = Math.ceil( jsondata[j][1] * 1000 );
                continue;
            }
            if ( jsondata[j][0] == 77  ) {
                L1Wproduction = Math.ceil( jsondata[j][1] * 1000 );
                continue;
            }
            if ( jsondata[j][0] == 78  ) {
                L2Wproduction = Math.ceil( jsondata[j][1] * 1000 );
                continue;
            }
            if ( jsondata[j][0] == 79 ) {
                L3Wproduction = Math.ceil( jsondata[j][1] * 1000 );
                continue;
            }
            if ( jsondata[j][0] == 100 ) {
                L1A = jsondata[j][1];
                //L1A = 5
                continue;
            }
            if ( jsondata[j][0] == 101 ) {
                L2A = jsondata[j][1];
                continue;
            }
            if ( jsondata[j][0] == 102 ) {
                L3A = jsondata[j][1];
                continue;
            }
            if ( jsondata[j][0] == 103 ) {
                L1V = jsondata[j][1];
                continue;
            }
            if ( jsondata[j][0] == 104 ) {
                L2V = jsondata[j][1];
                continue;
            }
            if ( jsondata[j][0] == 105 ) {
                L3V = jsondata[j][1];
                continue;
            }
        }


    // DEBUG
    
    // 10 
    /*
    L1A = 1
    L2A = 8
    L3A = 16
    */
    // 16 
    /*
    L1A = 0
    L2A = 15
    L3A = 22
    */

    // 25
    /*
    L1A = 8
    L2A = 20
    L3A = 27
    */

    // 35
    /*
    L1A = 1
    L2A = 17,5
    L3A = 37
    */

    //40
    /*
    L1A = 2
    L2A = 20
    L3A = 43
    */

    //50
    /*
    L1A = 5
    L2A = 25
    L3A = 55
    */

    //63
    /*
    L1A = 6
    L2A = 45
    L3A = 77
    */

    //80
    /*
    L1A = 4
    L2A = 70
    L3A = 101
    */


        /*
        console.log ( ' -------------- ' );
        console.log ( L1Wconsumption );
        console.log ( L2Wconsumption );
        console.log ( L3Wconsumption );
        console.log ( L1Wproduction );
        console.log ( L2Wproduction );
        console.log ( L3Wproduction );
        console.log ( ' ############### ' );
        */
        
        // consumption and production adaption.
        // L1 Watt
        if ( L1Wconsumption > L1Wproduction ) {
            $('#L1Watt').highcharts().series[0].data[0].color = '#F2BA0F';
            $('#L1Watt').highcharts().yAxis[0].setTitle({text: "verbruik"});
            $('#L1Watt').highcharts().series[0].points[0].update( parseInt( L1Wconsumption ), true, true, true );
            $('#L1Amperage').highcharts().yAxis[0].setTitle({text: "verbruik"});

        } else {
            $('#L1Watt').highcharts().series[0].data[0].color = '#98D023';
            $('#L1Watt').highcharts().yAxis[0].setTitle({text: "levering"});
            $('#L1Watt').highcharts().series[0].points[0].update( parseInt( L1Wproduction ), true, true, true );
            $('#L1Amperage').highcharts().yAxis[0].setTitle({text: "levering"});
        }
        // L1 Amperage
        $('#L1Amperage').highcharts().series[0].points[0].update( parseInt( L1A ), true, true, true );
        // L1 Voltage
        $('#L1Voltage').highcharts().series[0].points[0].update( parseFloat( L1V ), true, true, true );
    
        // consumption and production adaption.
        // L2 Watt
        if ( L2Wconsumption > L2Wproduction ) {
            $('#L2Watt').highcharts().series[0].data[0].color = '#F2BA0F';
            $('#L2Watt').highcharts().yAxis[0].setTitle({text: "verbruik"});
            $('#L2Watt').highcharts().series[0].points[0].update( parseInt( L2Wconsumption ), true, true, true );
            $('#L2Amperage').highcharts().yAxis[0].setTitle({text: "verbruik"});
        } else {
            $('#L2Watt').highcharts().series[0].data[0].color = '#98D023';
            $('#L2Watt').highcharts().yAxis[0].setTitle({text: "levering"});
            $('#L2Watt').highcharts().series[0].points[0].update( parseInt( L2Wproduction ), true, true, true );
            $('#L2Amperage').highcharts().yAxis[0].setTitle({text: "levering"});
        }
        // L2 Amperage
        $('#L2Amperage').highcharts().series[0].points[0].update( parseInt( L2A ), true, true, true );
        // L2 Voltage
        $('#L2Voltage').highcharts().series[0].points[0].update( parseFloat( L2V ), true, true, true );
    
        // consumption and production adaption.
        // L3 Watt
        if ( L3Wconsumption > L3Wproduction ) {
            $('#L3Watt').highcharts().series[0].data[0].color = '#F2BA0F';
            $('#L3Watt').highcharts().yAxis[0].setTitle({text: "verbruik"});
            $('#L3Watt').highcharts().series[0].points[0].update( parseInt( L3Wconsumption ), true, true, true );
            $('#L3Amperage').highcharts().yAxis[0].setTitle({text: "verbruik"});
        } else {
            $('#L3Watt').highcharts().series[0].data[0].color = '#98D023';
            $('#L3Watt').highcharts().yAxis[0].setTitle({text: "levering"});
            $('#L3Watt').highcharts().series[0].points[0].update( parseInt( L3Wproduction ), true, true, true );
            $('#L3Amperage').highcharts().yAxis[0].setTitle({text: "levering"});
        }
        // L3 Amperage
        $('#L3Amperage').highcharts().series[0].points[0].update( parseInt( L3A ), true, true, true );
        // L3 Voltage
        $('#L3Voltage').highcharts().series[0].points[0].update( parseFloat(  L3V ), true, true, true );
        

      } catch(err) {
          console.log( err );
      }
   });
}

function DataLoop() {
    readJsonApiPhaseInformationFromStatus();
    setTimeout('DataLoop()',3000);
}

$(function () {
    toLocalStorage('fase-menu',window.location.pathname);
    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });
    screenSaver( <?php echo config_read(79);?> ); // to enable screensaver for this screen.
    DataLoop(); 

}); 

function toggleButtonAndGraphView( graph, button ) {
    //console.log (  graph, button );
    button = '#' + button  // jquery id fix
    //console.log( $( button ).hasClass( "color-menu" ) )
    if ( $( button ).hasClass( "color-menu" ) ) { 
        $( button ).removeClass( 'color-menu' ); // hide / not active
        hideStuff( graph );
        toLocalStorage( 'phase-a-' + graph , false );
    } else {
        $( button ).addClass( 'color-menu' );    // show / active
        showStuff( graph );
        toLocalStorage( 'phase-a-' + graph , true );
    }

}

function readGraphVisiabilityFromBrowserMemory(){
    
    for ( var j=0;  j < graphIdArray.length; j++ ){ 

        var status = JSON.parse( getLocalStorage( 'phase-a-' + graphIdArray[ j ] ) )  // helper var, to make and reduce parsing.
        
        if ( status == null || status === true ) { // show /active
            showStuff( graphIdArray[ j ] );
            $( '#' + buttonIdArray[ j ] ).addClass( 'color-menu' );
        } else { // hide / not active
            hideStuff( graphIdArray[ j ] );
            $( '#' + buttonIdArray[ j ] ).removeClass( 'color-menu' ); 
        }

    }

}

</script>

    </head>
    <body>

        <?php page_header();?>

        <div class="top-wrapper-2">
            <div class="content-wrapper pad-13">
                    <!-- header 2 --> 
                    <?php pageclock(); ?>
                    <?php page_menu_header_fase( 0 ); ?>
                    <?php weather_info(); ?>
                </div>
            </div>
        </div>

        
        <div class="mid-section">
            <div class="left-wrapper pad-34">
                <?php page_menu( 10 ); ?>
                <?php fullscreen(); ?>
            </div>

            <div class="container" title="<?php echo strIdx(77);?>">
               
                <div class="pad-6">
                    <div class="frame-5-top">
                       <span class="text-2">L1</span>
                        <div class="float-right">
                            <button id="L1WButton" onclick="toggleButtonAndGraphView( graphIdArray[0], buttonIdArray[0] )" class="button-2 bold-font">W</button>
                            <button id="L1AButton" onclick="toggleButtonAndGraphView( graphIdArray[1], buttonIdArray[1] )" class="button-2 bold-font">A</button>
                            <button id="L1VButton" onclick="toggleButtonAndGraphView( graphIdArray[2], buttonIdArray[2] )" class="button-2 bold-font">V</button>
                        </div>
                   </div>
                    <div class="frame-5-bot"> 
                        <div id="L1Watt"     class="pad-38"></div>
                        <div id="L1Amperage" class="pad-38"></div>
                        <div id="L1Voltage"></div>
                    </div>
                </div>

                <div>
                    <div class="frame-5-top">
                        <span class="text-2">L2</span>
                        <div class="float-right">
                            <button id="L2WButton" onclick="toggleButtonAndGraphView( graphIdArray[3], buttonIdArray[3] )" class="button-2 bold-font">W</button>
                            <button id="L2AButton" onclick="toggleButtonAndGraphView( graphIdArray[4], buttonIdArray[4] )" class="button-2 bold-font">A</button>
                            <button id="L2VButton" onclick="toggleButtonAndGraphView( graphIdArray[5], buttonIdArray[5] )" class="button-2 bold-font">V</button>
                        </div>
                    </div>
                    <div class="frame-5-bot"> 
                        <div id="L2Watt"     class="pad-38"></div>
                        <div id="L2Amperage" class="pad-38"></div>
                        <div id="L2Voltage"></div>
                    </div>
                </div>  

                 <div>
                    <div class="frame-5-top">
                        <span class="text-2">L3</span>
                        <div class="float-right">
                            <button id="L3WButton" onclick="toggleButtonAndGraphView( graphIdArray[6], buttonIdArray[6] )"  class="button-2 bold-font">W</button>
                            <button id="L3AButton" onclick="toggleButtonAndGraphView( graphIdArray[7], buttonIdArray[7] )"  class="button-2 bold-font">A</button>
                            <button id="L3VButton" onclick="toggleButtonAndGraphView( graphIdArray[8], buttonIdArray[8] )"  class="button-2 bold-font">V</button>
                        </div>
                    </div>
                    <div class="frame-5-bot"> 
                        <div id="L3Watt"     class="pad-38"></div>
                        <div id="L3Amperage" class="pad-38"></div>
                        <div id="L3Voltage"></div>
                    </div>
                </div>  
            </div>

        </div>
<script>


    

    readGraphVisiabilityFromBrowserMemory();

    var gaugeOptions = {
        chart: {
            type: 'solidgauge',
            width:260,
            height: 150,
            margin: [0, 0, 0, 0]
        },
        title: null,
        pane: {
            center: ['53%', '85%'],
            size: '160%',
            startAngle: -90,
            endAngle: 90,
            background: {
                backgroundColor: '#F5F5F5',
                innerRadius: '60%',
                outerRadius: '100%',
                shape: 'arc'
            }
        },
        yAxis: {
            lineWidth: 0,
            tickWidth: 0,
            minorTickInterval: null,
            tickAmount: 2,
            title: {
                y: 26,
                text: 'onbekend',
                style: {
                    fontWeight: 'bold',
                    fontSize: '20px'
                },
            },
            labels: {
                formatter: function () {
                    return this.value;
                },
                style: {
                    fontWeight: 'bold',
                    fontSize: '16px'
                },
                y: 16
            }
        },
        tooltip: {
            enabled: false
        },
        plotOptions: {
            solidgauge: {
                dataLabels: {
                    y: 10,
                    borderWidth: 0,
                    useHTML: true,
                }
            }
        }
    };

    var gaugeOptionsAmperage = {
        chart: {
            type: 'solidgauge',
            width:260,
            height: 150,
            margin: [0, 0, 0, 0]
        },
        series: [{
            data: [
                {
                color: '#CC6600',
                y: 0
                }
            ],
            dataLabels: {
                y: -30,
                color: '#6E797C',
                format:
                    '<div style="text-align:center">' +
                    '<span style="font-size:25px">{point.y} A</span><br/>' +
                    '</div>',
            },
        }],
        title: null,
        pane: {
            center: ['53%', '85%'],
            size: '160%',
            startAngle: -90,
            endAngle: 90,
            background: {
                backgroundColor: '#F5F5F5',
                innerRadius: '60%',
                outerRadius: '100%',
                shape: 'arc'
            }
            
        },
        yAxis: {
            min: 0,
            max: maxAmperageFromConfig,
            lineWidth: 0,
            tickWidth: 0,
            minorTickInterval: null,
        
            //tickAmount: 10,
            minTickInterval: 80,
            title: {
                y: 26,
                text: 'onbekend',
                style: {
                    fontWeight: 'bold',
                    fontSize: '20px'
                },
            },
            labels: {
                enabled: false
            },
        },
        tooltip: {
            enabled: false
        },
        plotOptions: {
            solidgauge: {
                dataLabels: {
                    y: 10,
                    borderWidth: 0,
                    useHTML: true,
                }
            }
        }
    };

    var gaugeOptionsVoltage = 
    {
        plotOptions: {
            gauge: {
                pivot: {
                    radius: 8,
                    borderWidth: 1,
                    backgroundColor: '#6E797C',
                },
                dial: {
                    radius: '55%',
                    backgroundColor: '#384042',
                    borderWidth: 1,
                    baseWidth: 15,
                    topWidth: 1,
                    baseLength: '1%', // of radius
                    rearLength: '1%'
                },
            }
        },
        chart: {
            width: 260,
            height: 190,
            type: 'gauge',
            plotBackgroundColor: null,
            plotBackgroundImage: null,
            plotBorderWidth: 0,
            plotShadow: false,
            //backgroundColor: '#ff0000',
        },
        title: null,
        pane: {
            center: ['53%', '75%'],
            startAngle: -90,
            endAngle: 90,
            size: '150%',
            background: [{
                outerRadius: '0%',
            }],
        },
        // the value axis
        yAxis: {
            min: 160,
            max: 300,
            minorTickWidth: 0,
            tickWidth: 0,
            //tickAmount: 0,
            //tickInterval: 0,
            //showFirstLabel: true,
            //showLastLabel: true,
            title: null,
            labels: {
                enabled: false
            },
            plotBands: 
            [  
                {
                    borderColor: '#DF5353',
                    borderWidth: 1,
                    innerRadius: '60%',
                    outerRadius: '100%',
                    from: 160,
                    to: 206,
                    color: '#DF5353' // red
                }, {
                    borderWidth: 1,
                    borderColor: '#55BF3B',
                    innerRadius: '60%',
                    outerRadius: '100%',
                    from: 207,
                    to: 253,
                    color: '#55BF3B' // green
                }, {
                    borderWidth: 1,
                    borderColor: '#DF5353',
                    innerRadius: '60%',
                    outerRadius: '100%',
                    from: 254,
                    to: 300,
                    color: '#DF5353' // red
                }
            ],
        },
        tooltip: {
            enabled: false
        },
        series: [{
            overshoot: 0,
            data: [{
                color: '#F2BA0F',
                y: 0
            }],
            dataLabels: {
                borderWidth: 0,
                y: 60,
                color: '#6E797C',
                format:
                    '<div style="text-align:center">' +
                    '<span style="font-size:25px">{point.y} V</span><br/>' +
                    '</div>',
            },
        }]
    }

    var L1WattChart = Highcharts.chart( graphIdArray[0], Highcharts.merge( gaugeOptions, 
    {
        yAxis: {
            min: 0,
            max: maxWattFromConfig
        },
        series: [{
            data: [
                {
                color: '#F2BA0F',
                y: 0
                }
            ],
            dataLabels: {
                y: -30,
                color: '#6E797C',
                format:
                    '<div style="text-align:center">' +
                    '<span style="font-size:25px">{point.y} W</span><br/>' +
                    '</div>',
            },
        }]
    }));

    var L1AmperageChart = Highcharts.chart( graphIdArray[1], Highcharts.merge( gaugeOptionsAmperage, 
    {
        
    }));

    var L1VoltageChart = Highcharts.chart( graphIdArray[2], Highcharts.merge( gaugeOptionsVoltage, 
    {
    }));

    var L2WattChart = Highcharts.chart( graphIdArray[3], Highcharts.merge( gaugeOptions, 
    {
        yAxis: {
            min: 0,
            max: maxWattFromConfig
        },
        series: [{
            data: [
                {
                color: '#F2BA0F',
                y: 0
                }
            ],
            dataLabels: {
                y: -30,
                color: '#6E797C',
                format:
                    '<div style="text-align:center">' +
                    '<span style="font-size:25px">{point.y} W</span><br/>' +
                    '</div>',
            },
        }]
    }));

    var L2AmperageChart = Highcharts.chart( graphIdArray[4], Highcharts.merge( gaugeOptionsAmperage, 
    {
    }));

    var L2VoltageChart = Highcharts.chart( graphIdArray[5], Highcharts.merge( gaugeOptionsVoltage, 
    {
    }));

    var L3WattChart = Highcharts.chart( graphIdArray[6], Highcharts.merge( gaugeOptions, 
    {
        yAxis: {
            min: 0,
            max: maxWattFromConfig
        },
        series: [{
            data: [
                {
                color: '#F2BA0F',
                y: 0
                }
            ],
            dataLabels: {
                y: -30,
                color: '#6E797C',
                format:
                    '<div style="text-align:center">' +
                    '<span style="font-size:25px">{point.y} W</span><br/>' +
                    '</div>',
            },
        }]
    }));

    var L3AmperageChart = Highcharts.chart( graphIdArray[7], Highcharts.merge( gaugeOptionsAmperage, 
    {
    }));

    var L3VoltageChart = Highcharts.chart( graphIdArray[8], Highcharts.merge( gaugeOptionsVoltage, 
    {
    }));


    L1AmperageChart.renderer.text('0',35, 150)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

    L2AmperageChart.renderer.text('0',35, 150)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

    L3AmperageChart.renderer.text('0',35, 150)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

    L1AmperageChart.renderer.text( maxAmperageFromConfig, 225, 150 )
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();
    
    L2AmperageChart.renderer.text( maxAmperageFromConfig, 225, 150 )
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();
    
    L3AmperageChart.renderer.text( maxAmperageFromConfig, 225, 150)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

    L1VoltageChart.renderer.text('160',20, 150)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();
        

    L1VoltageChart.renderer.text('300',220, 150)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

    L2VoltageChart.renderer.text('160',20, 150)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

    L2VoltageChart.renderer.text('300',220, 150)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();


    L3VoltageChart.renderer.text('160',20, 150)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

    L3VoltageChart.renderer.text('300',220, 150)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

</script>
</body>
</html>