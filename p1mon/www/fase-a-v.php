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
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title>P1-monitor <?php echo strIdx( 527 )?></title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">

<link type="text/css" rel="stylesheet" href="./css/p1mon.css">
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css">

<script src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/highstock-link/highstock.js"></script>
<script src="./js/highstock-link/highcharts-more.js"></script>
<script src="./js/highstock-link/modules/solid-gauge.js"></script>
<script src="./js/highstock-link/modules/accessibility.js"></script>
<script src="./js/hc-global-options.js"></script>
<script src="./js/p1mon-util.js"></script>

<script>

const production_text  = "<?php echo strIdx( 368 );?>"
const consumption_text = "<?php echo strIdx( 354 );?>"

var maxAmperageFromConfig  = <?php echo config_read( 123 ) . ";\n"?>
var maxWattFromConfig      = <?php echo config_read( 124 ) . ";\n"?>
var useKw                  = <?php echo config_read( 180 ) . ";\n"?>
var graphIdArray           = [ 'L1Watt',    'L1Amperage', 'L1Voltage', 'L2Watt',    'L2Amperage', 'L2Voltage', 'L3Watt',    'L3Amperage', 'L3Voltage' ]
var buttonIdArray          = [ 'L1WButton', 'L1AButton',  'L1VButton', 'L2WButton', 'L2AButton',  'L2VButton', 'L3WButton', 'L3AButton',  'L3VButton' ]
var p1TelegramMaxSpeedIsOn = <?php if ( config_read( 155 ) == 1 ) { echo "true;"; } else { echo "false;"; } echo"\n";?> 
var gaugeHeight            = 145
var gaugeMinMaxYpos        = 140


if ( useKw ) {
    var wattText = 'kW'
    maxWattFromConfig =  maxWattFromConfig / 1000
} else {
    var wattText = 'W'
}

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
            if ( j > 105 ) break; // loop only what is needed.
            if ( jsondata[j][0] == 74 ) {
                if ( useKw ) {
                    L1Wconsumption  = parseFloat( jsondata[j][1] ).toFixed(1).toString()
                } else { 
                    L1Wconsumption  = Math.ceil( jsondata[j][1] * 1000 );
                }
                continue;
            }
            if ( jsondata[j][0] == 75 ) {
                if ( useKw ) {
                    L2Wconsumption = parseFloat( jsondata[j][1] ).toFixed(1).toString()
                } else { 
                    L2Wconsumption = Math.ceil( jsondata[j][1] * 1000 );
                }
                continue;
            }
            if ( jsondata[j][0] == 76 ) {
                if ( useKw ) {
                    L3Wconsumption = parseFloat( jsondata[j][1] ).toFixed(1).toString()
                } else { 
                    L3Wconsumption = Math.ceil( jsondata[j][1] * 1000 );
                }
                continue;
            }
            if ( jsondata[j][0] == 77  ) {
                if ( useKw ) {
                    L1Wproduction = parseFloat( jsondata[j][1] ).toFixed(1).toString()
                } else { 
                    L1Wproduction = Math.ceil( jsondata[j][1] * 1000 );
                }
                continue;
            }
            if ( jsondata[j][0] == 78  ) {
                if ( useKw ) {
                    L2Wproduction = parseFloat( jsondata[j][1] ).toFixed(1).toString()
                } else { 
                    L2Wproduction = Math.ceil( jsondata[j][1] * 1000 );
                }
                continue;
            }
            if ( jsondata[j][0] == 79 ) {
                if ( useKw ) {
                    L3Wproduction = parseFloat( jsondata[j][1] ).toFixed(1).toString()
                } else { 
                    L3Wproduction = Math.ceil( jsondata[j][1] * 1000 );
                }
                continue;
            }
            if ( jsondata[j][0] == 100 ) {
                L1A = jsondata[j][1];
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

        // consumption and production adaption.
        // L1 Watt
        if ( L1Wconsumption > L1Wproduction ) {
            $('#L1Watt').highcharts().series[0].data[0].color = '#F2BA0F';
            $('#L1Watt').highcharts().yAxis[0].setTitle({text: consumption_text});
            $('#L1Watt').highcharts().series[0].points[0].update( parseFloat( L1Wconsumption ), true, true, true );
            $('#L1Amperage').highcharts().yAxis[0].setTitle({text: consumption_text});
            $('#L1Amperage').highcharts().series[0].data[0].color = '#F2BA0F';
            if ( useKw ) {
                L1Caculated = L1Wconsumption * 1000 / L1V
            }  else {
                L1Caculated = L1Wconsumption / L1V
            }
        } else {
            $('#L1Watt').highcharts().series[0].data[0].color = '#98D023';
            $('#L1Watt').highcharts().yAxis[0].setTitle({text: production_text});
            $('#L1Watt').highcharts().series[0].points[0].update( parseFloat( L1Wproduction ), true, true, true );
            $('#L1Amperage').highcharts().yAxis[0].setTitle({text: production_text});
            $('#L1Amperage').highcharts().series[0].data[0].color = '#98D023';
            if ( useKw ) {
                L1Caculated = L1Wproduction * 1000 / L1V
            }  else {
                L1Caculated = L1Wproduction / L1V
            }
        }

        if ( L1Wconsumption == L1Wproduction ) {
            $('#L1Watt').highcharts().yAxis[0].setTitle({text: ""}); // er wordt niets verbruikt of geleverd
        }

        // L1 Amperage
        $('#L1Amperage').highcharts().series[0].points[0].update( parseInt( L1A ), true, true, true );
        // L1 Voltage
        
        $('#L1Voltage').highcharts().series[0].points[0].update( parseFloat( L1V ), true, true, true );
        if ( isNaN(L1Caculated) == false && L1V > 0) {
            //$("#L1Calc").text( L1Caculated.toFixed(2) + " A" )
            L1AmperageChart.L1ATextCalc.attr({
                text: '<div style="text-align:center"><i class="fas fa-calculator" data-fa-transform="shrink-6 down-1"></i>' + L1Caculated.toFixed(2) + ' A</div>'
            })
        }
        
        // consumption and production adaption.
        // L2 Watt
        if ( L2Wconsumption > L2Wproduction ) {
            $('#L2Watt').highcharts().series[0].data[0].color = '#F2BA0F';
            $('#L2Watt').highcharts().yAxis[0].setTitle({text: consumption_text});
            $('#L2Watt').highcharts().series[0].points[0].update( parseFloat( L2Wconsumption ), true, true, true );
            $('#L2Amperage').highcharts().yAxis[0].setTitle({text: consumption_text});
            $('#L2Amperage').highcharts().series[0].data[0].color = '#F2BA0F';
            if ( useKw ) {
                L2Caculated = L2Wconsumption * 1000 / L2V
            }  else {
                L2Caculated = L2Wconsumption / L2V
            }
        } else {
            $('#L2Watt').highcharts().series[0].data[0].color = '#98D023';
            $('#L2Watt').highcharts().yAxis[0].setTitle({text: production_text});
            $('#L2Watt').highcharts().series[0].points[0].update( parseFloat( L2Wproduction ), true, true, true );
            $('#L2Amperage').highcharts().yAxis[0].setTitle({text: production_text});
            $('#L2Amperage').highcharts().series[0].data[0].color = '#98D023';
            if ( useKw ) {
                L2Caculated = L2Wproduction * 1000 / L2V
            }  else {
                L2Caculated = L2Wproduction / L2V
            }
        }

        if ( L2Wconsumption == L2Wproduction ) {
            $('#L2Watt').highcharts().yAxis[0].setTitle({text: ""}); // er wordt niets verbruikt of geleverd
        }

        // L2 Amperage
        $('#L2Amperage').highcharts().series[0].points[0].update( parseInt( L2A ), true, true, true );
        // L2 Voltage
        $('#L2Voltage').highcharts().series[0].points[0].update( parseFloat( L2V ), true, true, true );
        if ( isNaN(L2Caculated) == false && L2V > 0) {
            //$("#L2Calc").text( L2Caculated.toFixed(2) + " A" )
            L2AmperageChart.L2ATextCalc.attr({
                text: '<div style="text-align:center"><i class="fas fa-calculator" data-fa-transform="shrink-6 down-1"></i>' + L2Caculated.toFixed(2) + ' A</div>'
            })
        }
     

        // consumption and production adaption.
        // L3 Watt
        if ( L3Wconsumption > L3Wproduction ) {
            $('#L3Watt').highcharts().series[0].data[0].color = '#F2BA0F';
            $('#L3Watt').highcharts().yAxis[0].setTitle({text: consumption_text});
            $('#L3Watt').highcharts().series[0].points[0].update( parseFloat( L3Wconsumption ), true, true, true );
            $('#L3Amperage').highcharts().yAxis[0].setTitle({text: consumption_text});
            $('#L3Amperage').highcharts().series[0].data[0].color = '#F2BA0F';
            if ( useKw ) {
                L3Caculated = L3Wconsumption * 1000 / L3V
            }  else {
                L3Caculated = L3Wconsumption / L3V
            }
        } else {
            $('#L3Watt').highcharts().series[0].data[0].color = '#98D023';
            $('#L3Watt').highcharts().yAxis[0].setTitle({text: production_text});
            $('#L3Watt').highcharts().series[0].points[0].update( parseFloat( L3Wproduction ), true, true, true );
            $('#L3Amperage').highcharts().yAxis[0].setTitle({text: production_text});
            $('#L3Amperage').highcharts().series[0].data[0].color = '#98D023';
            if ( useKw ) {
                L3Caculated = L3Wproduction * 1000 / L3V
            }  else {
                L3Caculated = L3Wproduction / L3V
            }
        }

        if ( L3Wconsumption == L3Wproduction ) {
            $('#L3Watt').highcharts().yAxis[0].setTitle({text: ""}); // er wordt niets verbruikt of geleverd
        }

        // L3 Amperage
        $('#L3Amperage').highcharts().series[0].points[0].update( parseInt( L3A ), true, true, true );
        // L3 Voltage
        $('#L3Voltage').highcharts().series[0].points[0].update( parseFloat( L3V ), true, true, true );
        if ( isNaN(L3Caculated) == false && L3V > 0) {
            //$("#L3Calc").text( L3Caculated.toFixed(2) + " A" )
            L3AmperageChart.L3ATextCalc.attr({
                text: '<div style="text-align:center"><i class="fas fa-calculator" data-fa-transform="shrink-6 down-1"></i>' + L3Caculated.toFixed(2) + ' A</div>'
            })
        }
       
      } catch(err) {
          console.log( err );
      }
   });
}

function DataLoop() {

    readJsonApiPhaseInformationFromStatus();

    if ( p1TelegramMaxSpeedIsOn == true ) {
        setTimeout( 'DataLoop()', 1000 );
    } else {
        setTimeout('DataLoop()', 3000);
    }
}

$(function () {
    toLocalStorage('fase-menu',window.location.pathname);
    toLocalStorage('phase-actual-orientation', window.location.pathname); //  only needed for the fase vertical / horizontale mode
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

    //toggelCalculatedAmpValues();

}

function readGraphVisibilityFromBrowserMemory(){

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
                    <?php page_menu_header_fase( 0 );?>
                    <?php weather_info(); ?>
            </div>
        </div>

        <div class="mid-section">
            <div class="left-wrapper pad-34">
                <?php page_menu( 10 ); ?>
                <?php fullscreen(); ?>
            </div>

            <div class="right-wrapper width-910" title="<?php echo strIdx(77);?>">

                <div class="row">
                    <div class="column-33pct">
                        <div class="frame-5-top"> 
                            <span class="text-2">L1</span>
                            <div class="float-right">
                                <button id="L1WButton" onclick="toggleButtonAndGraphView( graphIdArray[0], buttonIdArray[0] )" class="button-2 bold-font">W</button>
                                <button id="L1AButton" onclick="toggleButtonAndGraphView( graphIdArray[1], buttonIdArray[1] )" class="button-2 bold-font">A</button>
                                <button id="L1VButton" onclick="toggleButtonAndGraphView( graphIdArray[2], buttonIdArray[2] )" class="button-2 bold-font">V</button>
                            </div>
                        </div>
                        <div class="frame-5-bot">
                                <div id="L1Watt"></div>
                                <div id="L1Amperage"></div>
                                <div id="L1Voltage"></div>
                        </div>
                    </div>

                    <div class="column-33pct">
                        <div class="frame-5-top"> 
                            <span class="text-2">L2</span>
                            <div class="float-right">
                                <button id="L2WButton" onclick="toggleButtonAndGraphView( graphIdArray[3], buttonIdArray[3] )" class="button-2 bold-font">W</button>
                                <button id="L2AButton" onclick="toggleButtonAndGraphView( graphIdArray[4], buttonIdArray[4] )" class="button-2 bold-font">A</button>
                                <button id="L2VButton" onclick="toggleButtonAndGraphView( graphIdArray[5], buttonIdArray[5] )" class="button-2 bold-font">V</button>
                            </div>
                        </div>
                        <div class="frame-5-bot"> 
                            <div id="L2Watt"></div>
                            <div id="L2Amperage"></div>
                            <div id="L2Voltage"></div>
                        </div>
                    </div>

                    <div class="column-33pct">
                        <div class="frame-5-top"> 
                            <span class="text-2">L3</span>
                            <div class="float-right">
                                <button id="L3WButton" onclick="toggleButtonAndGraphView( graphIdArray[6], buttonIdArray[6] )"  class="button-2 bold-font">W</button>
                                <button id="L3AButton" onclick="toggleButtonAndGraphView( graphIdArray[7], buttonIdArray[7] )"  class="button-2 bold-font">A</button>
                                <button id="L3VButton" onclick="toggleButtonAndGraphView( graphIdArray[8], buttonIdArray[8] )"  class="button-2 bold-font">V</button>
                            </div>
                        </div>
                        <div class="frame-5-bot"> 
                            <div id="L3Watt"></div>
                            <div id="L3Amperage"></div>
                            <div id="L3Voltage"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

<script>

    readGraphVisibilityFromBrowserMemory();

    var gaugeOptions = {
        chart: {
            type: 'solidgauge',
            width:260,
            height: gaugeHeight,
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
                    //fontSize: '20px'
                    fontSize: '16px'
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
                y: 16,
                x: -3
            }
        },
        tooltip: {
            enabled: false
        },
        plotOptions: {
            solidgauge: {
                dataLabels: {
                    useHTML: true,
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
            height: gaugeHeight,
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
                useHTML: true,
                y: -37,
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
            minTickInterval: 80,
            title: {
                y: 26,
                text: 'onbekend',
                style: {
                    fontWeight: 'bold',
                    //fontSize: '20px'
                    fontSize: '16px'
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
                    useHTML: true,
                    y: 10,
                    borderWidth: 0,
                    useHTML: true,
                }
            }
        }
    };

    var gaugeOptionsVoltage = {
        chart: {
            type: 'solidgauge',
            width:260,
            height: gaugeHeight,
            margin: [0, 0, 0, 0]
        },
        series: [{
            data: [{
                color: {
                    linearGradient:  { x1: 0, x2: 0, y1: 0, y2: 1 },
                    stops: [
                    [0.042, '#55BF3B'], // green
                    [0.5,   '#DDDF0D'], // yellow
                    [0.958, '#DF5353']  // red
                    ]
                }
            }
            ],
            dataLabels: {
                useHTML: true,
                y: -37,
                color: '#6E797C',
                borderWidth: 0,
                format:
                    '<div style="text-align:center">' +
                    '<span style="font-size:25px">{point.y} V</span><br/>' +
                    '</div>'
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
            min: 200, // 207 is minmal voltage
            max: 260, // 253 is maximum voltage
            lineWidth: 0,
            tickWidth: 0,
            minorTickInterval: null,
            minTickInterval: 80,
            labels: {
                enabled: false
            },
        },
        tooltip: {
            enabled: false
        },
    };

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
                useHTML: true,
                y: -35,
                color: '#6E797C',
                format:
                    '<div style="text-align:center">' +
                    '<span style="font-size:25px">{point.y} '+ wattText + '</span><br/>' +
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
                y: -35,
                color: '#6E797C',
                format:
                    '<div style="text-align:center">' +
                    '<span style="font-size:25px">{point.y} '+ wattText + '</span><br/>' +
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
                useHTML: true,
                y: -35,
                color: '#6E797C',
                format:
                    '<div style="text-align:center">' +
                    '<span style="font-size:25px">{point.y} '+ wattText + '</span><br/>' +
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


    // need to allow non standard tags to be processed
    // by highchart
    Highcharts.AST.allowedTags.push('fas');
    Highcharts.AST.allowedTags.push('fa-calculator');
    Highcharts.AST.allowedAttributes.push('data-fa-transform');

    L1AmperageChart.L1ATextCalc = L1AmperageChart.renderer.text( "" ,92, gaugeMinMaxYpos - 2,true)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '25px'
        })
        .add();

    L2AmperageChart.L2ATextCalc = L2AmperageChart.renderer.text( "" ,92, gaugeMinMaxYpos - 2,true)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '25px'
        })
        .add();

    L3AmperageChart.L3ATextCalc = L3AmperageChart.renderer.text( "" ,92, gaugeMinMaxYpos - 2,true)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '25px'
        })
        .add();



    L1AmperageChart.renderer.text('0',35, gaugeMinMaxYpos)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();
    L2AmperageChart.renderer.text('0',35, gaugeMinMaxYpos)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

  
    L3AmperageChart.renderer.text('0',35, gaugeMinMaxYpos)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

    L1AmperageChart.renderer.text( maxAmperageFromConfig, 220, gaugeMinMaxYpos )
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();
    
    L2AmperageChart.renderer.text( maxAmperageFromConfig, 220, gaugeMinMaxYpos )
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();
    
    L3AmperageChart.renderer.text( maxAmperageFromConfig, 220, gaugeMinMaxYpos)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

   
    L1VoltageChart.renderer.text('200',35, gaugeMinMaxYpos)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

    L1VoltageChart.renderer.text('260',220, gaugeMinMaxYpos)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

    L2VoltageChart.renderer.text('200',35, gaugeMinMaxYpos)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

    L2VoltageChart.renderer.text('260',220, gaugeMinMaxYpos)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

    L3VoltageChart.renderer.text('200',35, gaugeMinMaxYpos)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

    L3VoltageChart.renderer.text('260',220, gaugeMinMaxYpos)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();
   
</script>
</body>
</html>