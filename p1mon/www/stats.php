<?php
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php';  
include_once '/p1mon/www/util/page_menu_header.php'; 
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/fullscreen.php';
include_once '/p1mon/www/util/textlib.php';
include_once '/p1mon/www/util/highchart.php';

if ( checkDisplayIsActive(19) == false) { return; }
?>
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title>P1-monitor <?php echo strIdx( 413 )?></title>
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

const text_min_short    = "<?php echo strIdx( 128 );?>"
const text_hour         = "<?php echo strIdx( 129 );?>"
const text_hours        = "<?php echo strIdx( 121 );?>"


var recordsLoaded            = 0;
var initloadtimer;
var mins                     = 1;  
var secs                     = mins * 60;
var currentSeconds           = 0;
var currentMinutes           = 0;
var Gselected                = 0;
var GselectText              = ['15 '+text_min_short ,'30 '+text_min_short ,'1 '+text_hour,'8 '+text_hours,'12 '+text_hours,'24 '+text_hours]; // #PARAMETER
var GseriesVisibilty         = [true,true, true, true];
var GverbrData               = [];
var GgelvrData               = [];
var GConsumptionPrognoseData = [];
var GProductionPrognoseData  = [];
var maxrecords               = 1442;


function readJsonApiHistoryMin( cnt ){ 
    $.getScript( "/api/v1/powergas/minute?limit=" + cnt, function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        var item;
        recordsLoaded  = jsondata.length;

        GverbrData.length               = 0;
        GgelvrData.length               = 0; 
        GConsumptionPrognoseData.length = 0;
        GProductionPrognoseData.length  = 0;

        for ( var j = jsondata.length; j > 0; j-- ){    
            item = jsondata[ j-1 ];
            item[1] = item[1] * 1000; // highchart likes millisecs.
            GverbrData.push               ( [item[1], item[6]       ] ); 
            GgelvrData.push               ( [item[1], item[7] * -1  ] ); 
            GConsumptionPrognoseData.push ( [item[1], item[6] * 60  ] );
            GProductionPrognoseData.push  ( [item[1], item[7] * -60 ] );
        }
        updateData();
      } catch(err) {}
   });
}

/* preload */
readJsonApiHistoryMin( maxrecords )

// change items with the marker #PARAMETER
function createKwhChart() {
    Highcharts.stockChart('KwhChart', {
        chart: {
            marginTop: 46, // make room for the wide legend
            style: {
                fontFamily: 'robotomedium',
                fontSize: '14px'
            },
            backgroundColor: '#ffffff',
            renderTo: 'container',
            type: 'areaspline',
            borderWidth: 0
            },
            plotOptions :{
                series :{
                    showInNavigator: true,
                    events: {
                        legendItemClick: function (event) {
                            //console.log( event );

                            if  ( this.index === 0 ) {
                                toLocalStorage('stat-verbr-visible',!this.visible);  // #PARAMETER
                            }

                            if  ( this.index === 1 ) {
                                toLocalStorage('stat-gelvr-visible',!this.visible);  // #PARAMETER
                            }

                            if  ( this.index === 2 ) {
                                toLocalStorage('stat-verbr-visible-prognose',!this.visible);
                            }

                            if  ( this.index === 3 ) {
                                toLocalStorage('stat-gelvr-visible-prognose',!this.visible);
                            }
                        }
                    }
                }
            },
            legend: {
                y: -40,
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
                    type: 'hour',
                    count: 0.25,
                    text: GselectText[0]
                },{
                    type: 'hour',
                    count: 0.50,
                    text: GselectText[1]
                },{
                    type: 'hour',
                    count: 1,
                    text: GselectText[2]
                }, {
                    type: 'hour',
                    count: 8,
                    text: GselectText[3]
                }, {
                    type: 'hour',
                    count: 12,
                    text: GselectText[4]
                }, {
                    type: 'hour',
                    count: 24,
                    text: GselectText[5]
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
                                    toLocalStorage('stat-select-index',j); // PARAMETER
                                    break;
                                }
                            }
                        }
                    }
                },   
                minTickInterval:            60000, 
                range:           60      *  60000,
                minRange:        12      *  60000,
                maxRange:        24      *  60000,
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
            yAxis: [{
                gridLineColor: '#6E797C',
                gridLineDashStyle: 'longdash',
                lineWidth: 0,
                opposite: false,
                labels: {
                    //useHTML: true, fix seethrough tooltip
                    format: '{value} kWh',
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
            {
                opposite: false,
                labels: {
                    //useHTML: true, fix seethrough tooltip
                    format: '{value} kWh',
                    style: {
                        color: '#6E797C'
                    },
                },
            }
            ],
            tooltip: {
                useHTML: false,
                    style: {
                        padding: 3,
                        color: '#6E797C'
                    },
                formatter: function() {
                    var s = '<b>'+ Highcharts.dateFormat('%A, %Y-%m-%d %H:%M', this.x) +'</b>';

                    var d = this.points;
                    
                    var consumption         = "<?php echo strIdx( 340 )?>";
                    var production          = "<?php echo strIdx( 340 )?>";
                    var consumptionPrognose = "<?php echo strIdx( 340 )?>";
                    var productionPrognose  = "<?php echo strIdx( 340 )?>";

                    for (var i=0,  tot=d.length; i < tot; i++) {
                        //console.log (d[i].series.userOptions.id);

                        if  ( d[i].series.userOptions.id === 'consumption') {
                            consumption = d[i].y.toFixed(3) + " kWh";
                        }
                        if  ( d[i].series.userOptions.id === 'production') {
                            production = (-1 * d[i].y).toFixed(3) + " kWh";
                        }
                        if  ( d[i].series.userOptions.id === 'consumptionPrognose') {
                            consumptionPrognose = d[i].y.toFixed(3) + " kWh";
                        }
                        if  ( d[i].series.userOptions.id === 'productionPrognose') {
                            productionPrognose = (-1 * d[i].y).toFixed(3) + " kWh";
                        }
                    }

                    s += '<br/><span style="color: #F2BA0F;"><?php echo strIdx( 359 )?>: </span>' + consumption;
                    s += '<br/><span style="color: #98D023;"><?php echo strIdx( 360 )?>: </span>' + production; 
                    s += '<br/><span style="color: #F2BA0F;"><?php echo strIdx( 414 )?>: </span>' + consumptionPrognose;
                    s += '<br/><span style="color: #98D023;"><?php echo strIdx( 415 )?>: </span>' + productionPrognose; 

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
                    //range:                6000 * 3600000,
                    //minTickInterval:      60 * 60000,  
                    //maxRange:             24 * 60 * 60000,
                    dateTimeLabelFormats: {
                        day: '%d %B'
                    }
                },
                enabled: true,
                outlineColor: '#384042',
                outlineWidth: 1,
                handles: {
                    backgroundColor: '#384042',
                    borderColor: '#6E797C',
                    enabled: false
                },
                series: {
                    color: '#10D0E7'
                }
            },
            series: [ 
            {
                id: 'consumption',
                yAxis: 0,
                visible: GseriesVisibilty[0],
                name: '<?php echo strIdx( 416 )?>',
                color: '#F2BA0F',
                data: GverbrData, 
            }, 
            {
                id: 'production',
                yAxis: 0,
                visible: GseriesVisibilty[1],
                name: '<?php echo strIdx( 417 )?>',
                color: '#98D023',
                data: GgelvrData
            },
            {
                id: 'consumptionPrognose',
                yAxis: 1,
                type: 'areaspline',
                //dashStyle: 'ShortDot',
                visible: GseriesVisibilty[2],
                name: '<?php echo strIdx( 414 )?>',
                color: '#F2BA0F',
                data: GConsumptionPrognoseData, 
            }, 
            {
                id: 'productionPrognose',
                yAxis: 1,
                type: 'areaspline',
                //dashStyle: 'ShortDot',
                visible: GseriesVisibilty[3],
                name: '<?php echo strIdx( 415 )?>',
                color: '#98D023',
                data: GProductionPrognoseData
            }],
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
    var chart = $('#KwhChart').highcharts();

    chart.series[0].setData( GverbrData );
    chart.series[1].setData( GgelvrData );
    chart.series[2].setData( GConsumptionPrognoseData  );
    chart.series[3].setData( GProductionPrognoseData );

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
        readJsonApiHistoryMin( maxrecords )
    }
    // make chart only once and when we have data.
    if (recordsLoaded !== 0 &&  $('#KwhChart').highcharts() == null) {
      hideStuff('loading-data');
      createKwhChart();
    }
    setTimeout('DataLoop()',1000);
}

$(function() {
    toLocalStorage('stats-menu',window.location.pathname);
    Gselected = parseInt(getLocalStorage('stat-select-index'),10);
    GseriesVisibilty[0] = JSON.parse(getLocalStorage('stat-verbr-visible'));  // #PARAMETER
    GseriesVisibilty[1] = JSON.parse(getLocalStorage('stat-gelvr-visible'));  // #PARAMETER
    GseriesVisibilty[2] = JSON.parse(getLocalStorage('stat-verbr-visible-prognose'));  // ONLY for minute chart
    GseriesVisibilty[3] = JSON.parse(getLocalStorage('stat-gelvr-visible-prognose'));  // ONLY for minute chart
    Highcharts.setOptions({
        global: {
            useUTC: false
        },
        lang: <?php hc_language_json(); ?>
    });
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
       <?php page_menu_header(0); ?>
       <?php weather_info(); ?>
    </div>
</div>

<div class="mid-section">
    <div class="left-wrapper">
        <?php page_menu(1); ?>
        <div id="timerText" class="pos-8 color-timer"></div>
        <?php fullscreen(); ?>
    </div> 
    <div class="mid-content-2 pad-13">
    <!-- links -->
        <div class="frame-2-top">
            <span class="text-2"><?php echo strIdx( 120 )?> (kWh)</span> 
                <div class="content-wrapper" id="help_icon" onMouseOver="show_help_detail()" >
                    <i class="color-menu fas fa-question-circle" data-fa-transform="grow-10 right-20 up-4"></i>
                    <div class="cursor-pointer" id="help_detail" onclick="$('#help_detail').hide();">
                        <span>"<?php echo strIdx(75);?>"</span>
                </div>
            <!-- </span> -->
        </div>
        <div class="frame-2-bot">
        <div id="KwhChart" style="width:100%; height:480px;"></div>
        </div>
        </div>
</div>
</div>
<div id="loading-data"><img src="./img/ajax-loader.gif" alt="<?php echo strIdx(295);?>" height="15" width="128"></div>

<script>
function show_help_detail() {
    $('#help_detail').css({
       left: $( "#help_icon" ).position().left+14, 
       top:  $( "#help_icon" ).position().top+20
    });
    $('#help_detail').show();
    setTimeout( function() { $('#help_detail').hide(); },10000);
}
</script>

</body>
</html>