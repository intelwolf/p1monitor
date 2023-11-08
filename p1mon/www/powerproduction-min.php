<?php
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php';  
include_once '/p1mon/www/util/page_menu_header_powerproduction.php'; 
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/fullscreen.php';
include_once '/p1mon/www/util/textlib.php';
include_once '/p1mon/www/util/highchart.php';

if ( checkDisplayIsActive( 129 ) == false) { return; }
?>
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title>P1-monitor <?php echo strIdx( 426 )?></title>
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
var GselectText              = ['15 '+text_min_short,'30 '+text_min_short,'1 '+text_hour,'8 '+text_hours,'12 '+text_hours,'24 '+text_hours]; // #PARAMETER
var GseriesVisibilty         = [true,true, true, true];
var GHighTariffData          = [];
var GLowTariffData           = [];
var GHighTariffDataPrognose  = [];
var GLowTariffDataPrognose   = [];
var maxrecords               = 1442;
var high_tariff_color        = '#98D023';
var low_tariff_color         = '#7FAD1D';

function readJsonApiHistoryPowerMin( cnt ){ 
    $.getScript( "/api/v1/powerproduction/minute?limit=" + cnt, function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        var item;
        recordsLoaded       = jsondata.length;
        GHighTariffData.length         = 0;
        GLowTariffData.length          = 0; 
        GHighTariffDataPrognose.length = 0;
        GLowTariffDataPrognose.length  = 0;

        for ( var j = jsondata.length; j > 0; j-- ) {
            item = jsondata[ j-1 ];
            item[1] = item[1] * 1000;                     // highchart likes millisecs.
            GHighTariffData.push ( [item[1], item[4] ] ); // kWh during the period for the high tariff
            GLowTariffData.push  ( [item[1], item[5] ] );  // kWh during the period for the low tariff
            GHighTariffDataPrognose.push ( [item[1], item[4] * 60 ] ); // kWh during the period for the high tariff prognose
            GLowTariffDataPrognose.push  ( [item[1], item[5] * 60 ] ); // kWh during the period for the low tariff prognose
        }  
        updateData();
      } catch(err) {}
   });
}

/* preload */
readJsonApiHistoryPowerMin( maxrecords )

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
                            if  ( this.index === 0 ) {
                                toLocalStorage('powerprod-min-high-tariff-visible',!this.visible);  // #PARAMETER
                            }
                            if  ( this.index === 1 ) {
                                toLocalStorage('powerprod-min-low-tariff-visible',!this.visible);  // #PARAMETER
                            }
                            if  ( this.index === 2 ) {
                                toLocalStorage('powerprod-min-high-prognose-tariff-visible',!this.visible);  // #PARAMETER
                            }
                            if  ( this.index === 3 ) {
                                toLocalStorage('powerprod-min-low-prognose-tariff-visible',!this.visible);  // #PARAMETER
                            }
                        }
                    }
                },
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
                                toLocalStorage('powerprod-min-select-index',j); // PARAMETER
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
            /*
            dateTimeLabelFormats: {
                day: '%a.<br>%d %B<br/>%Y',
                hour: '%a.<br>%H:%M'
            },
            */
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
                    var hoogTarief          = "<?php echo strIdx( 340 );?>";
                    var laagTarief          = hoogTarief 
                    var hoogTariefPrognose  = hoogTarief 
                    var laagTariefPrognose  = hoogTarief 

                    for (var i=0,  tot=d.length; i < tot; i++) {
                        //console.log (d[i].series.userOptions.id);

                        if  ( d[i].series.userOptions.id === 'hightariff') {
                            hoogTarief = d[i].y.toFixed(4) + " kWh";
                        }
                        if  ( d[i].series.userOptions.id === 'lowtariff') {
                            laagTarief = d[i].y.toFixed(4) + " kWh";
                        }
                        if  ( d[i].series.userOptions.id === 'hightariffprognose') {
                            hoogTariefPrognose = d[i].y.toFixed(3) + " kWh";
                        }
                        if  ( d[i].series.userOptions.id === 'lowtariffprognose') {
                            laagTariefPrognose = d[i].y.toFixed(3) + " kWh";
                        }
                    }

                    s += '<br/><span style="color: #F2BA0F;"><?php echo strIdx( 126 );?>: </span>' + hoogTarief;
                    s += '<br/><span style="color: #98D023;"><?php echo strIdx( 127 );?>: : </span>' + laagTarief; 
                    s += '<br/><span style="color: #F2BA0F;"><?php echo strIdx( 428 );?>: </span>' + hoogTariefPrognose;
                    s += '<br/><span style="color: #98D023;"><?php echo strIdx( 429 );?>: </span>' + laagTariefPrognose; 

                    return s;

                },
                backgroundColor: '#F5F5F5',
                borderColor: '#DCE1E3',
                crosshairs: [true, true],
                borderWidth: 1
            },  
            navigator: {
                xAxis: {
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
                id: 'hightariff',
                yAxis: 0,
                type: 'areaspline',
                visible: GseriesVisibilty[0],
                name: '<?php echo strIdx( 126 );?>',
                color: high_tariff_color,
                data: GHighTariffData 
            },
            {
                id: 'lowtariff',
                yAxis: 0,
                type: 'areaspline',
                visible: GseriesVisibilty[1],
                name: '<?php echo strIdx( 127 );?>',
                color: low_tariff_color,
                data: GLowTariffData
            },
            {
                id: 'hightariffprognose',
                yAxis: 1,
                type: 'areaspline',
                //dashStyle: 'ShortDot',
                visible: GseriesVisibilty[2],
                name: '<?php echo strIdx( 428 );?>',
                color: high_tariff_color,
                data: GHighTariffDataPrognose, 
            }, 
            {
                id: 'lowtariffprognose',
                yAxis: 1,
                type: 'areaspline',
                //dashStyle: 'ShortDot',
                visible: GseriesVisibilty[3],
                name: '<?php echo strIdx( 429 );?>',
                color: low_tariff_color,
                data: GLowTariffDataPrognose
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
    var chart = $('#KwhChart').highcharts();
    chart.series[0].setData( GHighTariffData );
    chart.series[1].setData( GLowTariffData );
    chart.series[2].setData( GHighTariffDataPrognose );
    chart.series[3].setData( GLowTariffData );
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
        readJsonApiHistoryPowerMin( maxrecords )
    }
    // make chart only once and when we have data.
    if (recordsLoaded !== 0 &&  $('#KwhChart').highcharts() == null) {
      hideStuff('loading-data');
      createKwhChart();
    }
    setTimeout('DataLoop()',1000);
}


$(function() {
    toLocalStorage('powerproduction-menu', window.location.pathname );
    Gselected = parseInt( getLocalStorage('powerprod-min-select-index'), 10 );
    GseriesVisibilty[0] =JSON.parse(getLocalStorage('powerprod-min-high-tariff-visible'));  // #PARAMETER
    GseriesVisibilty[1] =JSON.parse(getLocalStorage('powerprod-min-low-tariff-visible') );  // #PARAMETER
    GseriesVisibilty[2] =JSON.parse(getLocalStorage('powerprod-min-high-prognose-tariff-visible') );  // #PARAMETER
    GseriesVisibilty[3] =JSON.parse(getLocalStorage('powerprod-min-low-prognose-tariff-visible') );  // #PARAMETER

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
       <?php page_menu_header_powerproduction( 0 ); ?>
       <?php weather_info(); ?>
    </div>
</div>

<div class="mid-section">
    <div class="left-wrapper">
        <?php page_menu( 11 ); ?>
        <div id="timerText" class="pos-8 color-timer"></div>
        <?php fullscreen(); ?>
    </div> 
    <div class="mid-content-2 pad-13">
    <!-- links -->
        <div class="frame-2-top">
            <span class="text-2"><?php echo strIdx( 427 );?></span> 
                <div class="content-wrapper" id="help_icon" onMouseOver="show_help_detail()" >
                    <i class="color-menu fas fa-question-circle" data-fa-transform="grow-10 right-20 up-4"></i>
                    <div class="cursor-pointer" id="help_detail" onclick="$('#help_detail').hide();">
                        <span><?php echo strIdx(75);?>"</span>
                </div>
            </div>
        </div>
        <div class="frame-2-bot"> 
        <div id="KwhChart" style="width:100%; height:480px;"></div>
        </div>
</div>
</div>
<div id="loading-data"><img src="./img/ajax-loader.gif" alt="<?php echo strIdx( 295 );?>" height="15" width="128"></div>

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