<?php
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php';  
include_once '/p1mon/www/util/page_menu_header_watermeter.php'; 
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/fullscreen.php';
include_once '/p1mon/www/util/highchart.php';

if ( checkDisplayIsActive( 102 ) == false) { return; }
?>
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title>P1-monitor <?php echo strIdx( 444 )?></title>
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

const text_days     = "<?php echo strIdx( 122 );?>"
const text_week     = "<?php echo strIdx( 144 );?>"
const text_month    = "<?php echo strIdx( 131 );?>"
const text_months   = "<?php echo strIdx( 123 );?>"

var recordsLoaded   = 0;
var initloadtimer;
var mins            = 1;  
var secs            = mins * 60;
var currentSeconds  = 0;
var currentMinutes  = 0;
var Gselected       = 0;
var GselectText     = [ '1 '+text_week, '14 '+text_days, '1 '+text_month , '2 '+text_months]; // #PARAMETER
var GseriesVisibilty= [true];
var GverbrData      = [];
var GgelvrData      = [];
var GnettoData      = [];
//var maxrecords      = 366;

var maxDataIsOn     = false
var maxDataText     = ['MAX. data','MIN. data']
var maxDataCount    = [ 36000, 366 ]
var maxrecords      = maxDataCount[1];

function readJsonApiHistoryDay( cnt ){ 
    $.getScript( "/api/v2/watermeter/day?limit=" + cnt, function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        var item;
        recordsLoaded       = jsondata.length;
        GverbrData.length   = 0;
        
        for (var j = jsondata.length; j > 0; j--){    
            item    = jsondata[ j-1 ];
            item[1] = item[1] * 1000; // highchart likes millisecs.
            GverbrData.push ( [item[1], item[4] ]);
        }  
        updateData();
      } catch(err) {}
   });
}

/* preload */
//readJsonApiHistoryDay( maxrecords );

// change items with the marker #PARAMETER
function createWaterUsageChart() {
    Highcharts.stockChart('WaterUsageChart', {
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
                            console.log(this.index)
                            if  ( this.index === 0 ) {
                                toLocalStorage('watermeter-d-verbr-visible',!this.visible);  // #PARAMETER
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
                    text: "-",
                    events: {
                        click: function () {
                            
                            maxDataIsOn = !maxDataIsOn;
                            setHCButtonText( $('#WaterUsageChart').highcharts().rangeSelector.buttons[0], maxDataText, maxDataIsOn );
                            
                            if ( maxDataIsOn == true ) {
                                maxrecords = maxDataCount[0]
                            } else {
                                maxrecords = maxDataCount[1]
                            }
                            //console.log( "maxrecords=" + maxrecords )
                            readJsonApiHistoryDay( maxrecords );
                            toLocalStorage('watermeter-d-max-data-on',maxDataIsOn );  // #PARAMETER
                            return false
                        }
                    }
                },

                {
                    type: 'day',   // #PARAMETER
                    count: 7,      // #PARAMETER
                    text: GselectText[0]
                },{
                    type: 'day',   // #PARAMETER
                    count: 14,     // #PARAMETER
                    text: GselectText[1]
                },{
                    type: 'month', // #PARAMETER
                    count: 1,      // #PARAMETER
                    text: GselectText[2]
                }, {
                    type: 'month', // #PARAMETER
                    count: 2,      // #PARAMETER
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
                                toLocalStorage('watermeter-d-select-index',j+1); // PARAMETER
                                break;
                            }
                        }
                    }
                }
            },   
            minTickInterval: 1 * 24 * 3600000, // PARAMETER
            range:          31 * 24 * 3600000, // PARAMETER
            minRange:       7  * 24 * 3600000, // PARAMETER
            maxRange:       61 * 24 * 3600000, // PARAMETER
            type: 'datetime',
            dateTimeLabelFormats: {
                minute: '%H:%M',
                hour: '%H:%M',
                day: "%a.<br>%e %b.",
                month: '%b.<br>%y',
                year: '%y'
            },
            lineColor: '#6E797C',
            lineWidth: 1
            },
            yAxis: {
                gridLineColor: '#6E797C',
                gridLineDashStyle: 'longdash',
                lineWidth: 0,
                offset: 0,
                opposite: false,
                labels: {
                    useHTML: true,
                    format: '{value} L',
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
            useHTML: false,
                style: {
                    padding: 3,
                    color: '#6E797C'
                },
            formatter: function() {
                //var s = '<b>'+ Highcharts.dateFormat('%A, %Y-%m-%d %H:%M-%H:59', this.x) +'</b>';
                var s = '<b>'+ Highcharts.dateFormat('%A, %Y-%m-%d', this.x) +'</b>';

                var d = this.points;
                var verbruikt   = "<?php echo strIdx( 340 );?>";
                var d       = this.points;

                var Pverbruik = 0;
            
                for (var i=0,  tot=d.length; i < tot; i++) {
                    //console.log (d[i].series.userOptions.id);
                    if  ( d[i].series.userOptions.id === 'verbruik') {
                        Pverbruik = d[i].y;
                    }
                }
                
                if ( $('#WaterUsageChart').highcharts().series[0].visible === true ) {
                    verbruikt = Pverbruik.toFixed(1)+" Liter";
                }
                
                s += '<br/><span style="color: #6699ff;"><?php echo strIdx( 354 );?>:&nbsp;</span>' + verbruikt + " (" + (parseFloat(verbruikt)/1000).toFixed(3) + " m<sup>3</sup>) <?php echo strIdx( 220 );?>";
                return s;

            },
            backgroundColor: '#F5F5F5',
            borderColor: '#DCE1E3',
            crosshairs: [true, true],
            borderWidth: 1
            },  
            navigator: {
                xAxis: {
                    //min: 915145200000, //vrijdag 1 januari 1999 00:00:00 GMT+01:00
                    minTickInterval:       24 * 3600000,  
                    maxRange:         30 * 24 * 3600000,
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
                id: 'verbruik',
                visible: GseriesVisibilty[0],
                name: '<?php echo strIdx( 440 );?>',
                color: '#6699ff',
                data: GverbrData 
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
  // can only set text when chart is made.
  setHCButtonText( $('#WaterUsageChart').highcharts().rangeSelector.buttons[0], maxDataText, maxDataIsOn );
}

function updateData() {
    //console.log("updateData()");
    var chart = $('#WaterUsageChart').highcharts();
    if( typeof(chart) !== 'undefined') {
        chart.series[0].setData( GverbrData );
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
        readJsonApiHistoryDay( maxrecords );
    }
    // make chart only once and when we have data.
    if (recordsLoaded !== 0 &&  $('#WaterUsageChart').highcharts() == null) {
      hideStuff('loading-data');
      createWaterUsageChart();
    }
    setTimeout('DataLoop()',1000);
}

$(function() {
    toLocalStorage('watermeter-menu',window.location.pathname);
    Gselected = parseInt( getLocalStorage('watermeter-h-select-index'), 10 );
    GseriesVisibilty[0] =JSON.parse( getLocalStorage('watermeter-d-verbr-visible') );  // #PARAMETER
    maxDataIsOn = JSON.parse(getLocalStorage('watermeter-d-max-data-on'));            // #PARAMETER
    //console.log( "maxDataIsON(1)=" + maxDataIsOn )

    if ( (maxDataIsOn == null) || (maxDataIsOn == false) ) {
        maxDataIsOn = false;
        maxrecords = maxDataCount[1]
    } else {
        maxrecords = maxDataCount[0]
    }

    Highcharts.setOptions({
        global: {
            useUTC: false
        },
        lang: <?php hc_language_json();?>
    });

    secs = 0;
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
       <?php page_menu_header_watermeter( 1 ); ?>
       <?php weather_info(); ?>
    </div>
</div>

<div class="mid-section">
    <div class="left-wrapper">
        <?php page_menu( 9 ); ?>
        <div id="timerText" class="pos-8 color-timer"></div>
        <?php fullscreen(); ?>
    </div> 
    <div class="mid-content-2 pad-13">
    <!-- links -->
        <div class="frame-2-top">
            <span class="text-2"><?php echo strIdx( 443 );?></span>
        </div>
        <div class="frame-2-bot"> 
        <div id="WaterUsageChart" style="width:100%; height:480px;"></div>
        </div>
</div>
</div>
<div id="loading-data"><img src="./img/ajax-loader.gif" alt="<?php echo strIdx( 295 );?>" height="15" width="128"></div>

</body>
</html>