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
include_once '/p1mon/www/util/highchart.php';

if ( checkDisplayIsActive(61) == false) { return; }
?>
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title>P1-monitor <?php echo strIdx( 528 )?></title>
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
const dataIndexOffset      = 50;

const text_unknown              = "<?php echo strIdx( 269 );?>";
const text_consumed             = "<?php echo strIdx( 359 );?>";
const text_produced             = "<?php echo strIdx( 360 );?>";
const text_waiting_for_data     = "<?php echo strIdx( 530 );?>";

var recordsLoaded          = 0;
var GWattDataL1Consumed    = [];
var GWattDataL1Produced    = [];
var GWattDataL2Consumed    = [];
var GWattDataL2Produced    = [];
var GWattDataL3Consumed    = [];
var GWattDataL3Produced    = [];
var GAmpereL1              = [];
var GAmpereL2              = [];
var GAmpereL3              = [];
var GVoltL1                = [];
var GVoltL2                = [];
var GVoltL3                = [];
var dataOffset             = dataIndexOffset;
var dataIndexStart         = 0;
var dataIndexStop          = dataOffset;
var jsondata               = []
var L1WIsVisible           = 1;
var L2WIsVisible           = 1;
var L3WIsVisible           = 1;
var L1AIsVisible           = 1;
var L2AIsVisible           = 1;
var L3AIsVisible           = 1;
var L1VIsVisible           = 1;
var L2VIsVisible           = 1;
var L3VIsVisible           = 1;
var faseDbIsActive         = <?php if ( config_read( 119 ) == 1 ) { echo "true;"; } else { echo "false;"; } echo "\n";?>
var p1TelegramMaxSpeedIsOn = <?php if ( config_read( 155 ) == 1 ) { echo "true;"; } else { echo "false;"; } echo "\n";?>
var useKw                  = <?php if ( config_read( 180 ) == 1 ) { echo "true;"; } else { echo "false;"; } echo "\n";?>

if ( useKw ) {
    var wattText = 'kW'
} else {
    var wattText = 'Watt'
}

function readJsonApiPhaseInformation(){ 
    $.getScript( "./api/v1/phase", function( data, textStatus, jqxhr ) {
      try {
        jsondata = JSON.parse(data); 
        setDataFromJson();
      } catch(err) {
          console.log( err );
      }
   });
}

function setDataFromJson() {

        try {

            if ( jsondata.length == 0  ) {
                return // do nothing due to a lack of data.
            }

            GWattDataL1Consumed.length  = 0; 
            GWattDataL1Produced.length  = 0;
            GWattDataL2Consumed.length  = 0;
            GWattDataL2Produced.length  = 0;
            GWattDataL3Consumed.length  = 0;
            GWattDataL3Produced.length  = 0;
            GAmpereL1.length            = 0;
            GAmpereL2.length            = 0;
            GAmpereL3.length            = 0;
            GVoltL1.length              = 0;
            GVoltL2.length              = 0;
            GVoltL3.length              = 0;

            dataIndexSanityCheck();
            
            //console.log( 'setDataFromJson() :dataIndexStart = ' + dataIndexStart );
            //console.log( 'setDataFromJson(): dataIndexStop = '  + dataIndexStop  );

            var divisor = 1
            if ( useKw ) {
                divisor = 1000
            }

            for ( var j = dataIndexStop ; j > dataIndexStart; j-- ) {    
                item    = jsondata[ j-1 ];
                item[1] = item[1] * 1000; // highchart likes millisecs.

                GWattDataL1Consumed.push( [ item[1], item[2] / divisor ] );
                GWattDataL1Produced.push( [ item[1], (item[5]*-1) / divisor] );

                GWattDataL2Consumed.push( [ item[1], item[3] / divisor ] );
                GWattDataL2Produced.push( [ item[1], (item[6]*-1) / divisor ] );

                GWattDataL3Consumed.push( [ item[1], item[4] / divisor ] );
                GWattDataL3Produced.push( [ item[1], (item[7]*-1) / divisor ] );

                GAmpereL1.push( [ item[1], item[11] ] );
                GAmpereL2.push( [ item[1], item[12] ] );
                GAmpereL3.push( [ item[1], item[13] ] );

                GVoltL1.push( [ item[1], item[8] ] );
                GVoltL2.push( [ item[1], item[9] ] );
                GVoltL3.push( [ item[1], item[10] ] );
                 
            }

            try { 
                L1WattChart.minimumTimestamp.attr(   { text: jsondata[ dataIndexStop  ][ 0 ] }) ;
                L1WattChart.maximumTimestamp.attr(   { text: jsondata[ dataIndexStart ][ 0 ] }) ;
                L2WattChart.minimumTimestamp.attr(   { text: jsondata[ dataIndexStop  ][ 0 ] }) ;
                L2WattChart.maximumTimestamp.attr(   { text: jsondata[ dataIndexStart ][ 0 ] }) ;
                L3WattChart.minimumTimestamp.attr(   { text: jsondata[ dataIndexStop  ][ 0 ] }) ;
                L3WattChart.maximumTimestamp.attr(   { text: jsondata[ dataIndexStart ][ 0 ] }) ;
                L1AmpereChart.minimumTimestamp.attr( { text: jsondata[ dataIndexStop  ][ 0 ] }) ;
                L1AmpereChart.maximumTimestamp.attr( { text: jsondata[ dataIndexStart ][ 0 ] }) ;
                L2AmpereChart.minimumTimestamp.attr( { text: jsondata[ dataIndexStop  ][ 0 ] }) ;
                L2AmpereChart.maximumTimestamp.attr( { text: jsondata[ dataIndexStart ][ 0 ] }) ;
                L3AmpereChart.minimumTimestamp.attr( { text: jsondata[ dataIndexStop  ][ 0 ] }) ;
                L3AmpereChart.maximumTimestamp.attr( { text: jsondata[ dataIndexStart ][ 0 ] }) ;
                L1VoltChart.minimumTimestamp.attr(   { text: jsondata[ dataIndexStop  ][ 0 ] }) ;
                L1VoltChart.maximumTimestamp.attr(   { text: jsondata[ dataIndexStart ][ 0 ] }) ;
                L2VoltChart.minimumTimestamp.attr(   { text: jsondata[ dataIndexStop  ][ 0 ] }) ;
                L2VoltChart.maximumTimestamp.attr(   { text: jsondata[ dataIndexStart ][ 0 ] }) ;
                L3VoltChart.minimumTimestamp.attr(   { text: jsondata[ dataIndexStop  ][ 0 ] }) ;
                L3VoltChart.maximumTimestamp.attr(   { text: jsondata[ dataIndexStart ][ 0 ] }) ;

            } catch{};

            recordsLoaded = 1;
            updateData();

        } catch(err) {
          console.log( err );
      }
}

function updateData() {

    if (recordsLoaded !== 0 ) {
      hideStuff('loading-data');
      //hideStuff('loading-fasedata');
    }

    $('#L1WattGraph').highcharts().series[0].setData( GWattDataL1Consumed, false );
    $('#L1WattGraph').highcharts().series[1].setData( GWattDataL1Produced, false );
    $('#L1WattGraph').highcharts().redraw( );

    $('#L2WattGraph').highcharts().series[0].setData( GWattDataL2Consumed, false ); 
    $('#L2WattGraph').highcharts().series[1].setData( GWattDataL2Produced, false );
    $('#L2WattGraph').highcharts().redraw();

    $('#L3WattGraph').highcharts().series[0].setData( GWattDataL3Consumed, false );
    $('#L3WattGraph').highcharts().series[1].setData( GWattDataL3Produced, false );
    $('#L3WattGraph').highcharts().redraw();

    $('#L1AmpereGraph').highcharts().series[0].setData( GAmpereL1, false );
    $('#L1AmpereGraph').highcharts().redraw();

    $('#L2AmpereGraph').highcharts().series[0].setData( GAmpereL2, false );
    $('#L2AmpereGraph').highcharts().redraw();

    $('#L3AmpereGraph').highcharts().series[0].setData( GAmpereL3, false );
    $('#L3AmpereGraph').highcharts().redraw();

    $('#L1VoltGraph').highcharts().series[0].setData( GVoltL1, false );
    $('#L1VoltGraph').highcharts().redraw();

    $('#L2VoltGraph').highcharts().series[0].setData( GVoltL2, false );
    $('#L2VoltGraph').highcharts().redraw();

    $('#L3VoltGraph').highcharts().series[0].setData( GVoltL3, false );
    $('#L3VoltGraph').highcharts().redraw();

    setButtonEvents( true ); 

}

function DataLoop() {
    readJsonApiPhaseInformation();
    if ( p1TelegramMaxSpeedIsOn == true ) {
        setTimeout( 'DataLoop()', 1000  );
    } else {
        setTimeout( 'DataLoop()', 10000 );
    }
}

$(function () {

    if ( faseDbIsActive == false ) {
        $('#loading-fasedata').show();
        centerPosition('#err_msg');
        showStuff('err_msg');
    } 

    toLocalStorage('fase-menu',window.location.pathname);

    if ( JSON.parse(getLocalStorage( 'phase-historie-offset')) != null ) {
        dataOffset = JSON.parse(getLocalStorage( 'phase-historie-offset') );
        //console.log( "dataOffset from memory =  " + dataOffset );
        document.getElementById("slider_datapunten_value").innerHTML = dataOffset;
        document.getElementById("datapoints_slider").value = dataOffset;
    }

    document.getElementById("datapunten-value").innerHTML = dataOffset;

    Highcharts.setOptions({
        global: {
            useUTC: false
        },
        lang: <?php hc_language_json(); ?>
    });

    dataIndexStart  = 0;
    dataIndexStop   = dataOffset;
    
    screenSaver( <?php echo config_read(79);?> ); // to enable screensaver for this screen.
    
    centerPosition('#slider_dialog');
    $('#slider_dialog_close').click(function() {    
        hideStuff('slider_dialog');
        //console.log( slider.value );
        var redraw_flag = false;
        if ( parseInt( slider.value ) < dataOffset ) { 
            redraw_flag = true; 
        } 
        dataIndexStop   = dataIndexStop - dataOffset; // reset from prevous value
        dataOffset      = parseInt( slider.value );
        dataIndexStop   = dataIndexStop + dataOffset

        document.getElementById("datapunten-value").innerHTML = dataOffset;
        toLocalStorage( 'phase-historie-offset', dataOffset );
        if ( redraw_flag ) {
            setDataFromJson();
        }
    });

    if ( JSON.parse( getLocalStorage( 'phase-L1WButton')) != null ) {  
        L1WIsVisible = JSON.parse( getLocalStorage( 'phase-L1WButton' ))
    } 
    
    if ( JSON.parse( getLocalStorage( 'phase-L2WButton' )) != null ) { 
        L2WIsVisible = JSON.parse( getLocalStorage( 'phase-L2WButton' )) 
    }

    if ( JSON.parse( getLocalStorage( 'phase-L3WButton' )) != null ) {  
        L3WIsVisible = JSON.parse( getLocalStorage( 'phase-L3WButton' ));;
    }

    if ( JSON.parse( getLocalStorage( 'phase-L1AButton')) != null ) {  
        L1AIsVisible = JSON.parse( getLocalStorage( 'phase-L1AButton' )) 
    } 

    if ( JSON.parse( getLocalStorage( 'phase-L2AButton')) != null ) {  
        L2AIsVisible = JSON.parse( getLocalStorage( 'phase-L2AButton' )) 
    } 

    if ( JSON.parse( getLocalStorage( 'phase-L3AButton')) != null ) {  
        L3AIsVisible = JSON.parse( getLocalStorage( 'phase-L3AButton' )) 
    } 

    if ( JSON.parse( getLocalStorage( 'phase-L1VButton')) != null ) {  
        L1VIsVisible = JSON.parse( getLocalStorage( 'phase-L1VButton' )) 
    } 

    if ( JSON.parse( getLocalStorage( 'phase-L2VButton')) != null ) {  
        L2VIsVisible = JSON.parse( getLocalStorage( 'phase-L2VButton' )) 
    } 

    if ( JSON.parse( getLocalStorage( 'phase-L3VButton')) != null ) {  
        L3VIsVisible = JSON.parse( getLocalStorage( 'phase-L3VButton' )) 
    }
    
    setButtonVisbilty();
    setChartTimestamps();
    DataLoop(); 
});

function toggleGraphView( tag_id ) {

    if ( tag_id == 'L1WButton' ) {
        L1WIsVisible ^= 1;
        toLocalStorage( 'phase-L1WButton', L1WIsVisible ); 
    }

    if ( tag_id == 'L2WButton' ) {
        L2WIsVisible ^= 1;
        toLocalStorage( 'phase-L2WButton', L2WIsVisible ); 
    }

    if ( tag_id == 'L3WButton' ) {
        L3WIsVisible ^= 1;
        toLocalStorage( 'phase-L3WButton', L3WIsVisible ); 
    }

    if ( tag_id == 'L1AButton' ) {
        L1AIsVisible ^= 1;
        toLocalStorage( 'phase-L1AButton', L1AIsVisible ); 
    }

    if ( tag_id == 'L2AButton' ) {
        L2AIsVisible ^= 1;
        toLocalStorage( 'phase-L2AButton', L2AIsVisible ); 
    }

    if ( tag_id == 'L3AButton' ) {
        L3AIsVisible ^= 1;
        toLocalStorage( 'phase-L3AButton', L3AIsVisible ); 
    }

    if ( tag_id == 'L1VButton' ) {
        L1VIsVisible ^= 1;
        toLocalStorage( 'phase-L1VButton', L1VIsVisible ); 
    }

    if ( tag_id == 'L2VButton' ) {
        L2VIsVisible ^= 1;
        toLocalStorage( 'phase-L2VButton', L2VIsVisible );
    }

    if ( tag_id == 'L3VButton' ) {
        L3VIsVisible ^= 1;
        toLocalStorage( 'phase-L3VButton', L3VIsVisible );
    }

    setButtonVisbilty();

}

function setButtonVisbilty() {

    if ( L1WIsVisible ) {
        $('#L1WButton').removeClass( 'color-text' );
        $('#L1WButton').addClass( 'color-menu' );
    } else {
        $('#L1WButton').removeClass( 'color-menu' );
        $('#L1WButton').addClass( 'color-text' );
    }

    if ( L2WIsVisible ) {
        $('#L2WButton').removeClass( 'color-text' );
        $('#L2WButton').addClass( 'color-menu' );
    } else {
        $('#L2WButton').removeClass( 'color-menu' );
        $('#L2WButton').addClass( 'color-text' );
    }

    if ( L3WIsVisible ) { 
        $('#L3WButton').removeClass( 'color-text' );
        $('#L3WButton').addClass( 'color-menu' );
    } else {
        $('#L3WButton').removeClass( 'color-menu' );
        $('#L3WButton').addClass( 'color-text' );
    }

    if ( L1AIsVisible ) {
        $('#L1AButton').removeClass( 'color-text' );
        $('#L1AButton').addClass( 'color-menu' );
    } else {
        $('#L1AButton').removeClass( 'color-menu' );
        $('#L1AButton').addClass( 'color-text' );
    }

    if ( L2AIsVisible ) {
        $('#L2AButton').removeClass( 'color-text' );
        $('#L2AButton').addClass( 'color-menu' );
    } else {
        $('#L2AButton').removeClass( 'color-menu' );
        $('#L2AButton').addClass( 'color-text' );
    }

    if ( L3AIsVisible ) {
        $('#L3AButton').removeClass( 'color-text' );
        $('#L3AButton').addClass( 'color-menu' );
    } else {
        $('#L3AButton').removeClass( 'color-menu' );
        $('#L3AButton').addClass( 'color-text' );
    }

    if ( L1VIsVisible ) {
        $('#L1VButton').removeClass( 'color-text' );
        $('#L1VButton').addClass( 'color-menu' );
    } else {
        $('#L1VButton').removeClass( 'color-menu' );
        $('#L1VButton').addClass( 'color-text' );
    }

    if ( L2VIsVisible ) {
        $('#L2VButton').removeClass( 'color-text' );
        $('#L2VButton').addClass( 'color-menu' );
    } else {
        $('#L2VButton').removeClass( 'color-menu' );
        $('#L2VButton').addClass( 'color-text' );
    }

    if ( L3VIsVisible ) {
        $('#L3VButton').removeClass( 'color-text' );
        $('#L3VButton').addClass( 'color-menu' );
    } else {
        $('#L3VButton').removeClass( 'color-menu' );
        $('#L3VButton').addClass( 'color-text' );
    }

    // hide or show graphs
    if ( L1WIsVisible ) { showStuff('L1WattGraph');     } else { hideStuff('L1WattGraph');   }
    if ( L2WIsVisible ) { showStuff('L2WattGraph');     } else { hideStuff('L2WattGraph');   }
    if ( L3WIsVisible ) { showStuff('L3WattGraph');     } else { hideStuff('L3WattGraph');   }
    if ( L1AIsVisible ) { showStuff('L1AmpereGraph');   } else { hideStuff('L1AmpereGraph'); }
    if ( L2AIsVisible ) { showStuff('L2AmpereGraph');   } else { hideStuff('L2AmpereGraph'); }
    if ( L3AIsVisible ) { showStuff('L3AmpereGraph');   } else { hideStuff('L3AmpereGraph'); }
    if ( L1VIsVisible ) { showStuff('L1VoltGraph');     } else { hideStuff('L1VoltGraph');   }
    if ( L2VIsVisible ) { showStuff('L2VoltGraph');     } else { hideStuff('L2VoltGraph');   }
    if ( L3VIsVisible ) { showStuff('L3VoltGraph');     } else { hideStuff('L3VoltGraph');   }

}


</script>

    </head>

    <body>

        <?php page_header();?>

        <div class="top-wrapper-2">
            <div class="content-wrapper pad-13">
                <!-- header 2 --> 
                <?php pageclock(); ?>
                <?php page_menu_header_fase( 1 ); ?>
                <!-- weather info removed due to lack of room version 1.7.0 > -->
            </div>

                <div class="content-wrapper">
                    <button id='button-back' class='button-1' title="<?php echo strIdx( 79 );?>">
                        <span class="color-menu" >
                            <i class="far fa-caret-square-left" data-fa-transform="grow-25"></i>
                        </span>
                    </button>
                </div>

                <div class="content-wrapper">
                    <button id='button-forward' class='button-1' title="<?php echo strIdx( 80 );?>">
                        <span class="color-menu" >
                            <i class="far fa-caret-square-right" data-fa-transform="grow-25"></i>
                        </span>
                    </button>
                </div>

                <div class="content-wrapper pad-36">
                    <button id='button-range_slider' class='button-1' title="<?php echo strIdx( 81 );?>">
                        <span class="color-menu" >
                            <i class="fas fa-ellipsis-h" data-fa-transform="grow-25"></i>
                        </span>
                    </button>
                </div>

                <div class="content-wrapper pad-36">
                    <span class="text-10"><?php echo strIdx( 529 );?>:&nbsp;</span><span class="text-10" id="datapunten-value"><?php echo strIdx( 269 );?></span>
                </div>


        </div>

        <div class="mid-section">
            <div class="left-wrapper pad-34">
                <?php page_menu( 10 ); ?>
                <div class="left-wrapper" title="<?php echo strIdx( 78 );?>">
                    <span class="fa-layers frame-7-top pad-14">
                        <button id="L1WButton" onclick="toggleGraphView('L1WButton')" class="button-1 bold-font">L1 W</button>
                    </span>
                    <span class="fa-layers fa-gw frame-7-mid">
                        <button id="L2WButton" onclick="toggleGraphView('L2WButton')" class="button-1 bold-font">L2 W</button>
                    </span>
                    <span class="fa-layers fa-gw frame-7-mid">
                        <button id="L3WButton" onclick="toggleGraphView('L3WButton')" class="button-1 bold-font">L3 W</button>
                    </span>

                    <span class="fa-layers fa-gw frame-7-mid">
                        <button id="L1AButton" onclick="toggleGraphView('L1AButton')" class="button-1 bold-font">L1 A</button>
                    </span>
                    <span class="fa-layers fa-gw frame-7-mid">
                        <button id="L2AButton" onclick="toggleGraphView('L2AButton')" class="button-1 bold-font">L2 A</button>
                    </span>
                    <span class="fa-layers fa-gw frame-7-mid">
                        <button id="L3AButton" onclick="toggleGraphView('L3AButton')" class="button-1 bold-font">L3 A</button>
                    </span>

                    <span class="fa-layers fa-gw frame-7-mid">
                        <button id="L1VButton" onclick="toggleGraphView('L1VButton')" class="button-1 bold-font">L1 V</button>
                    </span>
                    <span class="fa-layers fa-gw frame-7-mid">
                        <button id="L2VButton" onclick="toggleGraphView('L2VButton')" class="button-1 bold-font">L2 V</button>
                    </span>
                    <span class="fa-layers fa-gw frame-7-bot">
                        <button id="L3VButton" onclick="toggleGraphView('L3VButton')" class="button-1 bold-font">L3 V</button>
                    </span>
                  
                </div>
                
            </div>

            <div class="width-910 float-left"> 
                <div class="pad-35"></div>
                <div class="float-left"       id="L1WattGraph"></div>
                <div class="float-left"       id="L2WattGraph"></div>
                <div class="float-left"       id="L3WattGraph"></div>
                <div class="float-left"       id="L1AmpereGraph"></div>
                <div class="float-left"       id="L2AmpereGraph"></div>
                <div class="float-left"       id="L3AmpereGraph"></div>
                <div class="float-left"       id="L1VoltGraph"></div>
                <div class="float-left"       id="L2VoltGraph"></div>
                <div class="float-left"       id="L3VoltGraph"></div>
            </div>
            <div id="loading-data" >
                <img src="./img/ajax-loader.gif" alt="<?php echo strIdx(295);?>" height="15" width="128">
            </div>
            <div id="loading-fasedata">
                   <?php echo strIdx( 91 );?>
            </div>

        </div>


<script>

    var areaSplineOptions = {
        chart: {
            style: {
                fontFamily: 'robotomedium',
                fontSize: '14px'
            },
            type: 'areaspline',
            width: 904,
            height: 200
        },
        xAxis: {
            //minRange: 10000,
            //tickInterval: 10000,
            type: "datetime",
            lineColor: "#6E797C",
            lineWidth: 1,
            dateTimeLabelFormats: {
                minute: '%H:%M',
                hour: '%H:%M',
                day: "%a.<br>%e %b.",
                month: '%b.<br>%y',
                year: '%y'
            },
        },
        yAxis: {
            title: null,
            gridLineColor: '#6E797C',
            gridLineDashStyle: 'longdash',
            lineWidth: 0,
            offset: 0,
            opposite: false,
            labels: {
                useHTML: false,
                format: '{value}',
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
        tooltip: {
                useHTML: true,
                style: {
                    padding: 3,
                    color: '#6E797C'
                },
                backgroundColor: '#F5F5F5',
                borderColor: '#DCE1E3',
                crosshairs: [true, true],
                borderWidth: 1
            },  
        title: {
            text: null
        },
        legend: {
            enabled: false
        },
       
        plotOptions: {
            areaspline: {
                fillOpacity: 0.5
            },
            series: {
                pointInterval: 10000,
                marker: {
                    enabled: false
                }
            }
        }
    };
        
    var L1WattChart = Highcharts.chart('L1WattGraph', Highcharts.merge( areaSplineOptions, 
    {
        title: {
            text: 'L1 ' + wattText
        },
        tooltip: {
                formatter: function() {
                    var s = '<b>'+ Highcharts.dateFormat('%A, %Y-%m-%d %H:%M:%S', this.x ) +'</b>';

                    var verbruikt = text_unknown;
                    var geleverd  = text_unknown;
                    try {
                        for (var i=0,  tot=this.series.xData.length; i < tot; i++) {
                            if ( GWattDataL1Consumed[i][0] ==  this.x ) { // timestamp
                                if ( useKw ) {
                                    verbruikt = GWattDataL1Consumed[i][1].toFixed(1) + ' ' + wattText;
                                    geleverd  = (GWattDataL1Produced[i][1] * -1).toFixed(1) + ' ' + wattText;
                                } else { 
                                    verbruikt = GWattDataL1Consumed[i][1].toFixed(0) + ' ' + wattText;
                                    geleverd  = (GWattDataL1Produced[i][1] * -1).toFixed(0) + ' ' + wattText;
                                }
                                break;
                            }
                        }
                    } catch{};
                    s += '<br/><span style="color: #F2BA0F;">' + text_consumed + ' : </span>'+verbruikt;
                    s += '<br/><span style="color: #98D023;">' + text_produced + ' : </span>'+geleverd; 
                    return s;
                }
        },
        series: 
        [{
            color: '#F2BA0F',
            data: null
        }, 
        {
            color: '#98D023',
            data: null
        }],
    }));
    
    var L2WattChart = Highcharts.chart('L2WattGraph', Highcharts.merge( areaSplineOptions, 
    {
        title: {
            text: 'L2 ' + wattText
        },
        tooltip: {
                formatter: function() {
                    var s = '<b>'+ Highcharts.dateFormat('%A, %Y-%m-%d %H:%M:%S', this.x ) +'</b>';

                    var verbruikt = text_unknown;
                    var geleverd  = text_unknown;
                    try {
                        for (var i=0,  tot=this.series.xData.length; i < tot; i++) {
                            if ( GWattDataL2Consumed[i][0] ==  this.x ) { // timestamp
                                if ( useKw ) {
                                    verbruikt = GWattDataL2Consumed[i][1].toFixed(1) + ' ' + wattText;
                                    geleverd  = (GWattDataL2Produced[i][1] * -1).toFixed(1) + ' ' + wattText;
                                } else { 
                                    verbruikt = GWattDataL2Consumed[i][1].toFixed(0) + ' ' + wattText;
                                    geleverd  = (GWattDataL2Produced[i][1] * -1).toFixed(0) + ' ' + wattText;
                                }
                                break;
                            }
                        }
                    }catch{};
                    s += '<br/><span style="color: #F2BA0F;">' + text_consumed + ' : </span>'+verbruikt;
                    s += '<br/><span style="color: #98D023;">' + text_produced + ' : </span>'+geleverd; 
                    return s;
                }
        },
        series: 
        [{
            color: '#F2BA0F',
            data: GWattDataL2Consumed
        }, 
        {
            color: '#98D023',
            data: GWattDataL2Produced 
        }],
    }));

    var L3WattChart = Highcharts.chart('L3WattGraph', Highcharts.merge( areaSplineOptions, 
    {
        title: {
            text: 'L3 ' + wattText
        },
        tooltip: {
                formatter: function() {
                    var s = '<b>'+ Highcharts.dateFormat('%A, %Y-%m-%d %H:%M:%S', this.x ) +'</b>';

                    var verbruikt = text_unknown;
                    var geleverd  = text_unknown;
                    try {
                        for (var i=0,  tot=this.series.xData.length; i < tot; i++) {
                            if ( GWattDataL3Consumed[i][0] ==  this.x ) { // timestamp
                                if ( useKw ) {
                                    verbruikt = GWattDataL3Consumed[i][1].toFixed(1) + ' ' + wattText;
                                    geleverd  = (GWattDataL3Produced[i][1] * -1).toFixed(1) + ' ' + wattText;
                                } else { 
                                    verbruikt = GWattDataL3Consumed[i][1].toFixed(0) + ' ' + wattText;
                                    geleverd  = (GWattDataL3Produced[i][1] * -1).toFixed(0) + ' ' + wattText;
                                }
                                break;
                            }
                        }
                    } catch{}
                        s += '<br/><span style="color: #F2BA0F;">' + text_consumed + ' : </span>'+verbruikt;
                        s += '<br/><span style="color: #98D023;">' + text_produced + ' : </span>'+geleverd; 
                    return s;
                }
        },
        series: 
        [{
            color: '#F2BA0F',
            data: GWattDataL2Consumed
        }, 
        {
            color: '#98D023',
            data: GWattDataL2Produced 
        }],
    }));

    var L1AmpereChart = Highcharts.chart('L1AmpereGraph', Highcharts.merge( areaSplineOptions, 
    {
        title: {
            text: 'L1 Ampere'
        },
        tooltip: {
                formatter: function() {
                    var s = '<b>'+ Highcharts.dateFormat('%A, %Y-%m-%d %H:%M:%S', this.x ) +'</b>';

                    var ampere = text_unknown;
                    try {
                        for (var i=0,  tot=this.series.xData.length; i < tot; i++) {
                            if ( GAmpereL1[i][0] ==  this.x ) { // timestamp
                                ampere = GAmpereL1[i][1].toFixed(0) + " A";
                                break;
                            }
                        }
                    } catch{}
                        s += '<br/><span style="color: #CC6600;">ampere: </span>' + ampere;
                    return s;
                }
        },
        series: 
        [{
            color: '#CC6600',
            data: GAmpereL1
        }]
    }));

    var L2AmpereChart = Highcharts.chart('L2AmpereGraph', Highcharts.merge( areaSplineOptions, 
    {
        title: {
            text: 'L2 Ampere'
        },
        tooltip: {
                formatter: function() {
                    var s = '<b>'+ Highcharts.dateFormat('%A, %Y-%m-%d %H:%M:%S', this.x ) +'</b>';

                    var ampere = text_unknown;
                    try {
                        for (var i=0,  tot=this.series.xData.length; i < tot; i++) {
                            if ( GAmpereL2[i][0] ==  this.x ) { // timestamp
                                ampere = GAmpereL2[i][1].toFixed(0) + " A";
                                break;
                            }
                        }
                    } catch{}
                        s += '<br/><span style="color: #F2BA0F;">ampere: </span>' + ampere;
                    return s;
                }
        },
        series: 
        [{
            color: '#CC6600',
            data: GAmpereL2
        }]
    }));

    var L3AmpereChart = Highcharts.chart('L3AmpereGraph', Highcharts.merge( areaSplineOptions, 
    {
        title: {
            text: 'L3 Ampere'
        },
        tooltip: {
                formatter: function() {
                    var s = '<b>'+ Highcharts.dateFormat('%A, %Y-%m-%d %H:%M:%S', this.x ) +'</b>';

                    var ampere = text_unknown;
                    try {
                        for (var i=0,  tot=this.series.xData.length; i < tot; i++) {
                            if ( GAmpereL3[i][0] ==  this.x ) { // timestamp
                                ampere = GAmpereL3[i][1].toFixed(0) + " A";
                                break;
                            }
                        }
                    } catch{}
                        s += '<br/><span style="color: #CC6600;">ampere: </span>' + ampere;
                    return s;
                }
        },
        series: 
        [{
            color: '#CC6600',
            data: GAmpereL3
        }]
    }));

    var L1VoltChart = Highcharts.chart('L1VoltGraph', Highcharts.merge( areaSplineOptions, 
    {
        yAxis: {
            min: 160,
        },
        title: {
            text: 'L1 Volt'
        },
        tooltip: {
                formatter: function() {
                    var s = '<b>'+ Highcharts.dateFormat('%A, %Y-%m-%d %H:%M:%S', this.x ) +'</b>';
                    var volt = text_unknown;
                    try {
                        for (var i=0,  tot=this.series.xData.length; i < tot; i++) {
                            if ( GVoltL1[i][0] ==  this.x ) { // timestamp
                                volt = GVoltL1[i][1].toFixed(1) + " V";
                                break;
                            }
                        }
                    } catch{}
                        s += '<br/><span style="color: #55BF3B;">volt: </span>' + volt;
                    return s;
                }
        },
        series: 
        [{
            color: '#55BF3B',
            data: GVoltL1
        }]
    }));

    var L2VoltChart = Highcharts.chart('L2VoltGraph', Highcharts.merge( areaSplineOptions, 
    {
        yAxis: {
            min: 160,
        },
        title: {
            text: 'L2 Volt'
        },
        tooltip: {
                formatter: function() {
                    var s = '<b>'+ Highcharts.dateFormat('%A, %Y-%m-%d %H:%M:%S', this.x ) +'</b>';
                    var volt = text_unknown;
                    try {
                        for (var i=0,  tot=this.series.xData.length; i < tot; i++) {
                            if ( GVoltL2[i][0] ==  this.x ) { // timestamp
                                volt = GVoltL2[i][1].toFixed(1) + " V";
                                break;
                            }
                        }
                    } catch{}
                        s += '<br/><span style="color: #55BF3B;">volt: </span>' + volt;
                    return s;
                }
        },
        series: 
        [{
            color: '#55BF3B',
            data: GVoltL2
        }],
        

    }));

    var L3VoltChart = Highcharts.chart('L3VoltGraph', Highcharts.merge( areaSplineOptions, 
    {
        yAxis: {
            min: 160,
        },
        title: {
            text: 'L3 Volt'
        },
        tooltip: {
                formatter: function() {
                    var s = '<b>'+ Highcharts.dateFormat('%A, %Y-%m-%d %H:%M:%S', this.x ) +'</b>';
                    var volt = text_unknown;
                    try {
                        for (var i=0,  tot=this.series.xData.length; i < tot; i++) {
                            if ( GVoltL3[i][0] ==  this.x ) { // timestamp
                                volt = GVoltL3[i][1].toFixed(1) + " V";
                                break;
                            }
                        }
                    } catch{}
                        s += '<br/><span style="color: #55BF3B;">volt: </span>' + volt;
                    return s;
                }
        },
        series: 
        [{
            color: '#55BF3B',
            data: GVoltL3
        }]
    }));

   

function setChartTimestamps() {
    charts = [ L1WattChart, L2WattChart, L3WattChart, L1AmpereChart, L2AmpereChart, L3AmpereChart, L1VoltChart, L2VoltChart, L3VoltChart];
    charts.forEach( chartSetTimestamp);
}

function chartSetTimestamp( value, index, array ) {

    value.minimumTimestamp = value.renderer.text(text_waiting_for_data ,8, 20)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

    value.maximumTimestamp = value.renderer.text(text_waiting_for_data ,715, 20)
        .css({
            fontWeight: 'bold',
            color: '#6E797C',
            fontSize: '16px'
        })
        .add();

}

function dataIndexSanityCheck() {
    if ( dataIndexStop > jsondata.length || dataIndexStart  < 0) {
        dataIndexStop  = jsondata.length - 1;
        if (dataIndexStop < 0 ) { dataIndexStop = dataIndexOffset; }
        dataIndexStart = 0;
    }
}

function changeDataSet( direction ) {

    //console.log( direction );
    //console.log( "jsondata.length = "  + jsondata.length );
    
    if ( direction === 'back' ) {
        dataIndexStart = dataIndexStop ;
        dataIndexStop  = dataIndexStop + dataOffset;
        //fail save don't go past the index.
        if ( dataIndexStop > jsondata.length ) {
            dataIndexStop = jsondata.length-1;
            dataIndexStart = dataIndexStop - dataOffset;
        }
        //console.log( 'back processed');
    }

    if ( direction === 'forward' ) {
            if ( dataIndexStart == 0 ) {
                //console.log(' at the start of the data set' );
                return;
            }
            dataIndexStop = dataIndexStart;
            dataIndexStart = dataIndexStart - dataOffset;
            //fail save don't go past the index.
            if ( dataIndexStart < 0 ) {
                dataIndexStart = 0;
                dataIndexStop = dataIndexStop + dataOffset;
            }
        //console.log( 'forward processed');
    }

    //busyIndictor( 'start' );

    //console.log( 'changeDataSet() dataIndexStart = ' + dataIndexStart );
    //console.log( 'changeDataSet() dataIndexStop = '  + dataIndexStop );
    setButtonEvents( false );
    setDataFromJson();
}

function setButtonEvents( active ) {

    if ( active ) {
        //console.log( 'adding event handelers');
        setButtonEvents(false);
        $("#button-back").one("click",         function(){ changeDataSet('back');}      );
        $("#button-forward").one("click",      function(){ changeDataSet('forward');}   );
        $("#button-range_slider").on("click",  function(){ showStuff('slider_dialog');} );
    } else {
        $("#button-back").off( 'click'         );
        $("#button-forward").off( 'click'      );
        $("#button-range_slider").off( 'click' );
    }

}

</script>
    
    <div id="slider_dialog">
            <div class='close_button' id="slider_dialog_close">
                <i class="color-select fas fa-times-circle" data-fa-transform="grow-8 left-4 down-2" aria-hidden="true"></i>
            </div>
            <div class="slidecontainer">
                <input id="datapoints_slider" type="range" class="slider">
                    <p class="text-10"><?php echo strIdx( 529 );?>: <span id="slider_datapunten_value"></span></p>
            </div>
    </div>
    
    <script>
            var slider = document.getElementById("datapoints_slider");
            slider.step     = dataIndexOffset;
            slider.min      = dataIndexOffset;
            slider.max      = 3000;
            slider.value    = dataOffset;

            var output = document.getElementById("slider_datapunten_value");
            output.innerHTML = slider.value;

            slider.oninput = function() {
                output.innerHTML = this.value;
            }

    </script>
    </body>
    </html>