<?php
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php'; 
include_once '/p1mon/www/util/page_menu_header_cost.php';
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/fullscreen.php';
include_once '/p1mon/www/util/highchart.php';
include_once '/p1mon/www/util/highchart_cost_tooltip.php';

if ( checkDisplayIsActive(21) == false) { return; }
?>
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title>P1-monitor <?php echo strIdx( 506 )?></title>
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

const text_years                    = "<?php echo strIdx( 124 );?>";
const text_unknown                  = "<?php echo strIdx( 269 );?>";
const text_peak_consumption_tariff  = "<?php echo strIdx( 494 );?>";
const text_low_consumption_tariff   = "<?php echo strIdx( 495 );?>";
const text_gas_cost_consumption     = "<?php echo strIdx( 496 );?>";
const text_water_cost_consumption   = "<?php echo strIdx( 497 );?>";
const text_total_consumed           = "<?php echo strIdx( 498 );?>";
const text_total_produced           = "<?php echo strIdx( 499 );?>";
const text_low_tariff_production    = "<?php echo strIdx( 500 );?>";
const text_high_tariff_production   = "<?php echo strIdx( 501 );?>";
const text_net_cost                 = "<?php echo strIdx( 502 );?>";
const text_net_revenue              = "<?php echo strIdx( 503 );?>";
const text_consumption              = "<?php echo strIdx( 354 );?>";
const text_production               = "<?php echo strIdx( 368 );?>";

var GpiekDataVerbr  = [];
var GdalDataVerbr   = [];
var GpiekDataGelvr  = [];
var GdalDataGelvr   = [];
var GGasDataGelvr   = [];
var GExtraData      = [];
var GNettoCost      = [];
var GWaterDataGelvr = [];

//var seriesOptions   = [];
var GseriesVisibilty    = [true,true,true,true,true,true,true, true]; 
var recordsLoaded   = 0;
var initloadtimer;
var Gselected       = 0;
var GselectText     = [ '5 '+text_years, '10 '+text_years, '15 '+text_years, '20 '+text_years ]; // #PARAMETER
var mins            = 1;  
var secs            = mins * 60;
var currentSeconds  = 0;
var currentMinutes  = 0;
var maxrecords      = 30;
var costLimit       = 0;

const HC_local_timestamp  ='%Y';

function readJsonApiConfig( id ){ 
    $.getScript( "/api/v1/configuration/" + id, function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        costLimit =  parseFloat ( (parseFloat( jsondata[0][1] ) * 12 ).toFixed(2) ) //PARAMETER
      } catch(err) {}
   });
}

function readJsonApiFinancial( cnt ){ 
    $.getScript( "./api/v1/financial/year?limit=" + cnt, function( data, textStatus, jqxhr ) {
        try {
            var jsondata = JSON.parse(data); 

            recordsLoaded           = jsondata.length;
            GpiekDataVerbr.length   = 0;
            GdalDataVerbr.length    = 0; 
            GpiekDataGelvr.length   = 0;
            GdalDataGelvr.length    = 0;
            GGasDataGelvr.length    = 0;
            GNettoCost.length       = 0;
            GWaterDataGelvr.length  = 0;
            GExtraData.length       = 0;

        for (var j = jsondata.length; j > 0; j--){    
            item = jsondata[ j-1 ];
            item[1] = item[1] * 1000; // highchart likes millisecs.
            GpiekDataVerbr.push  ( [item[1], item[2] ]);
            GdalDataVerbr.push   ( [item[1], item[3] ]);
            GpiekDataGelvr.push  ( [item[1], item[4] * -1]);
            GdalDataGelvr.push   ( [item[1], item[5] * -1 ]);
            GGasDataGelvr.push   ( [item[1], item[6] ]);
            GNettoCost.push      ( [item[1], ( item[2] + item[3] + item[6] + item[7] ) - ( item[4] +item[5] ) ]); 
            GWaterDataGelvr.push ( [item[1], item[7] ]); // water added
            GExtraData.push( [item[1], costLimit, -1, -1, -1, -1 ] ); //NEW
        }  

        readJsonApiPowerGas( cnt );
        //updateData();

        } catch(err) {
            console.error( err )
        }
    });
}

function readJsonApiPowerGas( cnt ){ 
    $.getScript( "/api/v1/powergas/year?limit=" + cnt, function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 

        for (var j = 0; j < jsondata.length; j++){    
            var item = jsondata[ j ];
            for ( var k=0 ; k < GpiekDataVerbr.length; k++ ) {
                if ( GpiekDataVerbr[k][0] == item[1] * 1000 ) {
                    GExtraData[k][2] = item[6]
                    GExtraData[k][3] = item[7]
                    GExtraData[k][4] = item[9]
                    break;
                }
            }
        }

        readJsonApiWater ( cnt );
      } catch(err) {}
   });
}

function readJsonApiWater( cnt ){ 
    $.getScript( "/api/v2/watermeter/year?limit=" + cnt, function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
          
        for (var j = 0; j < jsondata.length; j++){    
            var item = jsondata[ j ];
            for ( var k=0 ; k < GpiekDataVerbr.length; k++ ) {
                if ( GpiekDataVerbr[k][0] == item[1] * 1000 ) {
                    GExtraData[k][5] = item[3]
                    break;
                }
            }
        }

        updateData();
      } catch(err) {}
   });
}

// change items with the marker #PARAMETER
function createCostChart() {
    Highcharts.stockChart('CostChartVerbr', {
    chart: {
        marginTop: 46,
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
            series: {
                showInNavigator: true,
                events: {
                legendItemClick: function (event) {
                        //console.log(event);
                        
                        if  ( this.index === 0 ) {
                            toLocalStorage('cost-j-verbr-piek-visible',!this.visible); // #PARAMETER
                        }
                        if  ( this.index === 1 ) {
                            toLocalStorage('cost-j-verbr-dal-visible',!this.visible); // #PARAMETER
                        }
                        if  ( this.index === 2 ) {
                            toLocalStorage('cost-j-gelvr-piek-visible',!this.visible); // #PARAMETER
                        }
                        if  ( this.index === 3 ) {
                            toLocalStorage('cost-j-gelvr-dal-visible',!this.visible); // #PARAMETER
                        }
                        if  ( this.index === 4 ) {
                            toLocalStorage('cost-j-gelvr-gas-visible',!this.visible); // #PARAMETER
                        }
                        if  ( this.index === 5 ) {
                            toLocalStorage('cost-j-gelvr-water-visible',!this.visible); // #PARAMETER
                        }
                        if  ( this.index === 6 ) {
                            toLocalStorage('cost-j-max-cost-visible',!this.visible); // #PARAMETER
                        }  
                        if  ( this.index === 7 ) {
                            toLocalStorage('cost-j-netto-cost-visible',!this.visible); // #PARAMETER
                        } 
                        //updateData();  
                    }
                }
           },
            column :{
                stacking: 'normal',
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
                type: 'year',  // #PARAMETER
                count: 5,
                text: GselectText[0]
            },{
                type: 'year', // #PARAMETER
                count: 10,
                text: GselectText[1]
            },{
                type: 'year', // #PARAMETER 
                count: 15,
                text: GselectText[2] 
            },{
                type: 'year', // #PARAMETER
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
                                toLocalStorage('kosten-j-select-index',j+1); // PARAMETER
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
        yAxis: {
            zIndex: 0,
            gridLineColor: '#6E797C',
            gridLineDashStyle: 'longdash',
            lineWidth: 0,
            offset: 0,
            opposite: false,
            labels: {
                //useHTML: true,
                format: '€ {value}',
                style: {
                    color: '#6E797C'
                }
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#6E797C'
            }]
        },
        navigator: {
            xAxis: {
                min: 915145200000, //vrijdag 1 januari 1999 00:00:00 GMT+01:00
                minTickInterval:  5 *    365 * 24 * 3600000, 
                maxRange:       30 * 365 * 24 * 3600000,
                type: 'datetime',
                dateTimeLabelFormats: {
                    day: '%B<br/>%Y',
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
            series: {
                color: '#10D0E7'
            }
        },
        series: [ 
        {
            id: 'piek_ver',
            visible: GseriesVisibilty[0],
            name: "<?php echo strIdx( 508 )?>",
            color: '#FFC311',
            data: GpiekDataVerbr 
        }, 
        {
            id: 'dal_ver',
            visible: GseriesVisibilty[1],
            name: "<?php echo strIdx( 509 )?>",
            color: '#CEA731',
            data: GdalDataVerbr
        }, 
        {
            id: 'piek_gel',
            visible: GseriesVisibilty[2],
            name: "<?php echo strIdx( 510 )?>",
            color: '#98D023',
            data: GpiekDataGelvr
        },
        {
            id: 'dal_gel',
            visible: GseriesVisibilty[3],
            name: "<?php echo strIdx( 511 )?>",
            color: '#7FAD1D',
            data: GdalDataGelvr
        },{
            id: 'gas_ver',
            visible: GseriesVisibilty[4],
            name: "<?php echo strIdx( 512 )?>",
            color: '#507ABF',
            data: GGasDataGelvr
        }, 
        {
            id: 'water_ver',
            visible: GseriesVisibilty[5],
            name: "<?php echo strIdx( 513 )?>",
            color: '#6699ff',
            data: GWaterDataGelvr
        },
        {
            id: 'cost_max',
            visible: GseriesVisibilty[6],
            type: 'line',
            color: 'red',
            name: "<?php echo strIdx( 514 )?>",
            data: GExtraData,
            dashStyle: 'ShortDashDotDot',
            lineWidth: 1,
            marker: {
                enabled: false,
                states: {
                    hover: {
                        enabled: false
                    }
                }
            }
        },{
            id: 'cost_netto',
            visible: GseriesVisibilty[7],
            type: 'spline',
            color: 'black',
            name: "<?php echo strIdx( 515 )?>",
            data: GNettoCost,
            dashStyle: 'ShortDashDotDot',
            lineWidth: 1,
            marker: {
                enabled: false,
                states: {
                    hover: {
                        enabled: false
                    }
                }
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
    var chart = $('#CostChartVerbr').highcharts();
    if( typeof(chart) !== 'undefined') {

      chart.series[0].update({
       data: GpiekDataVerbr
      });
      chart.series[1].update({
        data: GdalDataVerbr
      });
      chart.series[2].update({
       data: GpiekDataGelvr
      });
      chart.series[3].update({
       data: GdalDataGelvr
      });
      chart.series[4].update({
       data: GGasDataGelvr
      });
      chart.series[5].update({
       data: GWaterDataGelvr
      });
      chart.series[6].update({
       data: GExtraData
      });
      chart.series[7].update({
       data: GNettoCost
      });

      chart.redraw();
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
        readJsonApiConfig ( 39 ) // financiele max. grens waarde.
        readJsonApiFinancial( maxrecords );
    }
    // make chart only once and when we have data.
    if (recordsLoaded !== 0 &&  $('#CostChartVerbr').highcharts() == null) {
        hideStuff('loading-data');
        createCostChart();
    }
    setTimeout('DataLoop()',1000);
}


$(function() {
    toLocalStorage('cost-menu',window.location.pathname);
    Gselected = parseInt(getLocalStorage('kosten-j-select-index'),10); // #PARAMETER
    GseriesVisibilty[0] =JSON.parse(getLocalStorage('cost-j-verbr-piek-visible'));  // #PARAMETER
    GseriesVisibilty[1] =JSON.parse(getLocalStorage('cost-j-verbr-dal-visible'));   // #PARAMETER
    GseriesVisibilty[2] =JSON.parse(getLocalStorage('cost-j-gelvr-piek-visible'));  // #PARAMETER
    GseriesVisibilty[3] =JSON.parse(getLocalStorage('cost-j-gelvr-dal-visible'));   // #PARAMETER
    GseriesVisibilty[4] =JSON.parse(getLocalStorage('cost-j-gelvr-gas-visible'));   // #PARAMETER
    GseriesVisibilty[5] =JSON.parse(getLocalStorage('cost-j-gelvr-water-visible')); // #PARAMETER
    GseriesVisibilty[6] =JSON.parse(getLocalStorage('cost-j-max-cost-visible'));    // #PARAMETER
    GseriesVisibilty[7] =JSON.parse(getLocalStorage('cost-j-netto-cost-visible'));  // #PARAMETER
    
    Highcharts.setOptions({
        global: {
            useUTC: false
        },
        lang: <?php hc_language_json(); ?>,
        <?php hc_cost_tooltip(); ?>
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
       <?php page_menu_header_cost( 2 ); ?>
       <?php weather_info(); ?>
    </div>
</div>

<div class="mid-section">
    <div class="left-wrapper">
        <?php page_menu(4); ?>
        <div id="timerText" class="pos-8 color-timer"></div>
        <?php fullscreen(); ?>
    </div> 
    <div class="mid-content-2 pad-13">
    <!-- links -->
        <div class="frame-2-top">
            <span class="text-2"><?php echo strIdx( 507 )?></span>
        </div>
        <div class="frame-2-bot"> 
        <div id="CostChartVerbr" style="width:100%; height:500px;"></div>
        </div>
</div>
</div>
<div id="loading-data"><img src="./img/ajax-loader.gif" alt="<?php echo strIdx( 295 )?>" height="15" width="128"></div>

</body>
</html>