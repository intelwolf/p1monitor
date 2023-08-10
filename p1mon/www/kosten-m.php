<?php
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php'; 
include_once '/p1mon/www/util/page_menu_header_cost.php';
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/js_tooltip_kosten.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/fullscreen.php';

if ( checkDisplayIsActive(21) == false) { return; }
?>
<!doctype html>
<html lang="nl">
<head>
<meta name="robots" content="noindex">
<title>P1monitor kosten per maand</title>
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
<script src="./js/highchart-options.js"></script>

<script> 
var GpiekDataVerbr  = [];
var GdalDataVerbr   = [];
var GpiekDataGelvr  = [];
var GdalDataGelvr   = [];
var GGasDataGelvr   = [];
var GExtraData      = [];
var GNettoCost      = [];
var GWaterDataGelvr = [];

//var seriesOptions   = [];
var GseriesVisibilty= [true,true,true,true,true,true,true, true]; 
var recordsLoaded   = 0;
var initloadtimer;
var Gselected       = 0;
var GselectText     = ['6 maanden','12 maanden','2 jaar','5 jaar' ]; // #PARAMETER
var mins            = 1;  
var secs            = mins * 60;
var currentSeconds  = 0;
var currentMinutes  = 0;
//var maxrecords      = 120;
var costLimit       = 0;

var maxDataIsOn     = false
var maxDataText     = ['MAX. data','MIN. data']
var maxDataCount    = [ 36000, 366 ]
var maxrecords      = maxDataCount[1];

const HC_local_timestamp  ='%B, %Y';

function readJsonApiConfig( id ){ 
    $.getScript( "/api/v1/configuration/" + id, function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        costLimit =  parseFloat ( parseFloat( jsondata[0][1]).toFixed( 2 ) ) //PARAMETER
      } catch(err) {}
   });
}

function readJsonApiFinancial( cnt ){ 
    $.getScript( "./api/v1/financial/month?limit=" + cnt, function( data, textStatus, jqxhr ) {
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

        } catch(err) {
            console.error( err )
        }
    });
}

function readJsonApiPowerGas( cnt ){ 
    $.getScript( "/api/v1/powergas/month?limit=" + cnt, function( data, textStatus, jqxhr ) {
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
    $.getScript( "/api/v2/watermeter/month?limit=" + cnt, function( data, textStatus, jqxhr ) {
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


// readJsonApiFinancial( maxrecords );

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
                            toLocalStorage('cost-m-verbr-piek-visible',!this.visible); // #PARAMETER
                        }
                        if  ( this.index === 1 ) {
                            toLocalStorage('cost-m-verbr-dal-visible',!this.visible); // #PARAMETER
                        }
                        if  ( this.index === 2 ) {
                            toLocalStorage('cost-m-gelvr-piek-visible',!this.visible); // #PARAMETER
                        }
                        if  ( this.index === 3 ) {
                            toLocalStorage('cost-m-gelvr-dal-visible',!this.visible); // #PARAMETER
                        }
                        if  ( this.index === 4 ) {
                            toLocalStorage('cost-m-gelvr-gas-visible',!this.visible); // #PARAMETER
                        }
                        if  ( this.index === 5 ) {
                            toLocalStorage('cost-m-gelvr-water-visible',!this.visible); // #PARAMETER
                        }
                        if  ( this.index === 6 ) {
                            toLocalStorage('cost-m-max-cost-visible',!this.visible); // #PARAMETER
                        }  
                        if  ( this.index === 7 ) {
                            toLocalStorage('cost-m-netto-cost-visible',!this.visible); // #PARAMETER
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
            y: -43,
            padding: 8,
            alignColumns: false,
            symbolHeight: 10,
            symbolWidth: 10,
            symbolRadius: 3,
            borderRadius: 5,
            borderWidth: 1,
            backgroundColor: '#DCE1E3',
            symbolPadding: 3,
            enabled: true,
            align: 'left',
            verticalAlign: 'top',
            layout: 'horizontal',
            floating: true,
            x: 0,
            itemStyle: {
                color: '#6E797C'
            },
            itemHoverStyle: {
                color: '#10D0E7'
            },
            itemDistance: 3
        },
        exporting: { enabled: false },
        rangeSelector: {
            inputEnabled: false,
            buttonSpacing: 5, 
            selected : Gselected,
            buttons: [
            {
                text: "-",
                events: {
                    click: function () {
                        
                        maxDataIsOn = !maxDataIsOn;
                        setHCButtonText( $('#CostChartVerbr').highcharts().rangeSelector.buttons[0], maxDataText, maxDataIsOn );
                        if ( maxDataIsOn == true ) {
                            maxrecords = maxDataCount[0]
                        } else {
                            maxrecords = maxDataCount[1]
                        }
                        readJsonApiFinancial( maxrecords );
                        toLocalStorage('cost-m-max-data-on',maxDataIsOn );  // #PARAMETER
                        return false

                    }
                }
            },
            {
                type: 'month',  // #PARAMETER
                count: 6,
                text: GselectText[0]
            },{
                type: 'month', // #PARAMETER
                count: 12,
                text: GselectText[1]
            },{
                type: 'year', // #PARAMETER 
                count: 2,
                text: GselectText[2] 
            },{
                type: 'year', // #PARAMETER
                count: 5,
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
                                toLocalStorage('kosten-m-select-index',j+1); // PARAMETER
                                break;
                            }
                        }
                    }
                }
            },   
            minTickInterval:       30 * 24 * 3600000, 
            range:           60  * 30 * 24 * 3600000,
            minRange:        6   * 30 * 24 * 3600000,
            maxRange:        120 * 30 * 24 * 3600000,
            type: 'datetime',
            dateTimeLabelFormats: {
                day: '%a.<br>%d %B<br/>%Y'
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
                minTickInterval:       30 * 24 * 3600000,  
                maxRange:        120 * 30 * 24 * 3600000,
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
                name: 'Piek verbruik elek.',
                color: '#FFC311',
                data: GpiekDataVerbr 
            }, 
            {
                id: 'dal_ver',
                visible: GseriesVisibilty[1],
                name: 'Dal verbruik elek.',
                color: '#CEA731',
                data: GdalDataVerbr
            }, 
            {
                id: 'piek_gel',
                visible: GseriesVisibilty[2],
                name: 'Piek geleverd elek.',
                color: '#98D023',
                data: GpiekDataGelvr
            },
            {
                id: 'dal_gel',
                visible: GseriesVisibilty[3],
                name: 'Dal geleverd elek.',
                color: '#7FAD1D',
                data: GdalDataGelvr
            },{
                id: 'gas_ver',
                visible: GseriesVisibilty[4],
                name: 'Verbruik gas',
                color: '#507ABF',
                data: GGasDataGelvr
            }, 
            {
                id: 'water_ver',
                visible: GseriesVisibilty[5],
                name: 'Verbruik water',
                color: '#6699ff',
                data: GWaterDataGelvr
            },
            {
                id: 'cost_max',
                visible: GseriesVisibilty[6],
                type: 'line',
                color: 'red',
                name: 'Grens kost.',
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
                name: 'Netto kost.',
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
            noData: "Geen gegevens beschikbaar."
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

  // can only set text when chart is made.
  setHCButtonText( $('#CostChartVerbr').highcharts().rangeSelector.buttons[0], maxDataText, maxDataIsOn );
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

       // load shared options
       var initOptions = $('#CostChartVerbr').highcharts().options
        optionsNew = Highcharts.merge(initOptions, HC_costToolTip);
        $('#CostChartVerbr').highcharts(optionsNew);
    }
    setTimeout('DataLoop()',1000);
}


$(function() {
    toLocalStorage('cost-menu',window.location.pathname);
    Gselected = parseInt(getLocalStorage('kosten-m-select-index'),10); // #PARAMETER
    GseriesVisibilty[0] =JSON.parse(getLocalStorage('cost-m-verbr-piek-visible'));  // #PARAMETER
    GseriesVisibilty[1] =JSON.parse(getLocalStorage('cost-m-verbr-dal-visible'));   // #PARAMETER
    GseriesVisibilty[2] =JSON.parse(getLocalStorage('cost-m-gelvr-piek-visible'));  // #PARAMETER
    GseriesVisibilty[3] =JSON.parse(getLocalStorage('cost-m-gelvr-dal-visible'));   // #PARAMETER
    GseriesVisibilty[4] =JSON.parse(getLocalStorage('cost-m-gelvr-gas-visible'));   // #PARAMETER
    GseriesVisibilty[5] =JSON.parse(getLocalStorage('cost-m-gelvr-water-visible')); // #PARAMETER
    GseriesVisibilty[6] =JSON.parse(getLocalStorage('cost-m-max-cost-visible'));    // #PARAMETER
    GseriesVisibilty[7] =JSON.parse(getLocalStorage('cost-m-netto-cost-visible'));  // #PARAMETER

    maxDataIsOn = JSON.parse(getLocalStorage('cost-m-max-data-on'));                // #PARAMETER
   
    if ( (maxDataIsOn == null) || (maxDataIsOn == false) ) {
        maxDataIsOn = false;
        maxrecords = maxDataCount[1]
    } else {
        maxrecords = maxDataCount[0]
    }

    Highcharts.setOptions({
    global: {
        useUTC: false
        }
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
       <?php page_menu_header_cost( 1 ); ?>
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
            <span class="text-2">Euro per maand</span>
        </div>
        <div class="frame-2-bot"> 
        <div id="CostChartVerbr" style="width:100%; height:500px;"></div>
        </div>
</div>
</div>
<div id="loading-data"><img src="./img/ajax-loader.gif" alt="Even geduld aub." height="15" width="128"></div>

</body>
</html>