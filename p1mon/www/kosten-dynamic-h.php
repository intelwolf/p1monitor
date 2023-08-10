<?php
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php';
include_once '/p1mon/www/util/page_menu_header_cost.php';
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/fullscreen.php';

if ( checkDisplayIsActive(19) == false) { return; }

?>
<!doctype html>
<html lang="nl">
<head>
<meta name="robots" content="noindex">
<title>P1monitor dyamische uur tarieven</title>
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
<script src="./js/moment-link/moment-with-locales.min.js"></script>

<script>

var recordsLoaded   = 0;
var initloadtimer;
var mins            = 1;  
var secs            = mins * 60;
var currentSeconds  = 0;
var currentMinutes  = 0;
var language_index  = '<?php echo config_read(148);?>'

var today_text      = '<?php echo strIdx(330);?>'
var yesterday_text  = '<?php echo strIdx(331);?>'
var tomorrow_text   = '<?php echo strIdx(332);?>'

var Gselected       = 1;
var GseriesVisibilty= [ true, true ];
var GkwhData      = [];
var GgasData      = [];

var displayPeriodList  =  [ yesterday_text, today_text, tomorrow_text ]
var displayPeriodID    =  1 // 0 = yesterday, 1=today, 2=tomorrow


/*
function decodeHtml(html) {
    var txt = document.createElement("textarea");
    txt.innerHTML = html;
    return txt.value;
}
*/

function set_language() {
    switch (language_index) {
        case '1':
            moment.locale('en');
            break;
        case '2':
            moment.locale('fr');
            break;
        default:
            moment.locale('nl');
    }
}

function readJsonApiTariffHour(){

    /* set period to retrieve */
    url = null
    var chartTitle = "" 
    if ( displayPeriodID == 0  ) {// yesterday
        url_parameters = "range=" + moment().add(-1, 'days').format('YYYY-MM-DD');
        chartTitle = moment().add(-1, 'days').format('dddd DD MMMM YYYY') + " (" + yesterday_text + ")"
    } 
    else if ( displayPeriodID == 1 ){ // today 
        url_parameters = "range=" + moment().format('YYYY-MM-DD');
        chartTitle = moment().format('dddd DD MMMM YYYY') + " (" + today_text + ")"
    }
    else if ( displayPeriodID == 2 ){ // tomorrow
        url_parameters = "range=" + moment().add(1, 'days').format('YYYY-MM-DD');
        chartTitle = moment().add(1, 'days').format('dddd DD MMMM YYYY') + " (" + tomorrow_text + ")"
    } else if ( url == null ) {
        url_parameters = "range=" + moment().format('YYYY-MM-DD'); // default failsave
        chartTitle = moment().format('dddd DD MMMM YYYY')
    }

    var chart = $('#TariffChart').highcharts();
    if( typeof(chart) !== 'undefined') {
        $('#TariffChart').highcharts().setTitle(
            { 
                text: chartTitle,
                style: {
                    color: '#6E797C',
                    fontSize: '26px',
                    fontFamily: 'robotomedium',
                    fontWeight: 'bold'
                },
            }
            );
    }

    //console.log( url_parameters )
    //console.log( displayPeriodID )

    $.getScript( "/api/v1/financial/dynamic_tariff?" + url_parameters , function( data, textStatus, jqxhr ) {
        try {
        var jsondata = JSON.parse(data); 
        var item;
        GkwhData.length = 0;
        GgasData.length = 0;
        recordsLoaded   = jsondata.length;
        for (var j = jsondata.length; j > 0; j--){
            item    = jsondata[ j-1 ];
            item[1] = item[1] * 1000; // highchart likes millisecs.
            GkwhData.push ( [item[1], item[2] ]);
            GgasData.push ( [item[1], item[3] ]);
        }
        updateData();
      } catch(err) {}
   });
}

function setDateRange( periodID ) {
    displayPeriodID = periodID
    //console.log( "setDateRange() displayPeriodID = " + periodID )
    readJsonApiTariffHour()
    toLocalStorage('cost-dynamic-h-day', displayPeriodID );
}


function updateData() {
    //console.log("updateData()");
    var chart = $('#TariffChart').highcharts();
    if( typeof(chart) !== 'undefined') {
        chart.series[0].setData( GkwhData );
        chart.series[1].setData( GgasData );
    }
}


// change items with the marker #PARAMETER
function createTariffChart() {
    //Highcharts.stockChart('TariffChart', {
    Highcharts.chart('TariffChart', {
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
            legend: {
                x: 0,
                y: 0,
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
            plotOptions :{
                series :{
                    minPointLength: 1, // hack to show tooltip in zero values.
                    events: {
                        legendItemClick: function (event) {
                            //console.log(this.index)
                            if  ( this.index === 0 ) {
                                toLocalStorage('cost-dynamic-h-day-kwh',!this.visible);  // #PARAMETER
                            }
                            if  ( this.index === 1 ) {
                                toLocalStorage('cost-dynamic-h-day-gas',!this.visible);  // #PARAMETER
                            }
                        }
                    }

                }
            },
            exporting: { enabled: false },
            xAxis: {
                labels: {
                    step: 1
                },
                minRange: 24,
                tickInterval:    3600000,
                type: 'datetime',
                dateTimeLabelFormats: {
                    day: '%H:%M',
                    hour: '%H:%M'
                },
                lineColor: '#6E797C',
                lineWidth: 1
            },
            yAxis:[ 
                {
                    tickInterval: 0.05,
                    title: false,
                    gridLineColor: '#6E797C',
                    gridLineDashStyle: 'longdash',
                    lineWidth: 0,
                    offset: 0,
                    opposite: false,
                    labels: {
                        //useHTML: true, //fix see through axis values.
                        format: '€ {value:.2f}',
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
                    title: false,
                    opposite: true,
                    gridLineDashStyle: 'longdash',
                    gridLineColor: '#6E797C',
                    gridLineWidth: 1,
                    labels: {
                    format: '{value}°C',
                        style: {
                            color: '#384042'
                        }
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

                    var s  = '<b>'+ Highcharts.dateFormat('%A<br>%Y-%m-%d %H:%M-%H:59', this.x) +'</b>';
                    var data_1 = this.series.chart.series[0].data;
                    var data_2 = this.series.chart.series[1].data;

                    var kwh_cost = gas_cost = null;
                   
                    for (var i=0, tot=GkwhData.length; i < tot; i++) {
                        if ( GkwhData[i][0] == this.key ) { //found time and dataset
                            kwh_cost = GkwhData[i][1]
                        break;
                        }
                    }

                    for (var i=0, tot=GgasData.length; i < tot; i++) {
                        if ( GgasData[i][0] == this.key ) { //found time and dataset
                            gas_cost = GgasData[i][1]
                        break;
                        }
                    }

                    if ( $('#TariffChart').highcharts().series[0].visible === true && kwh_cost != null ) {
                        s += '<br/><span style="color: #ff6f49;">kWh:&nbsp;</span>&nbsp;&euro;&nbsp' + kwh_cost.toFixed(2);
                    }

                    if ( $('#TariffChart').highcharts().series[1].visible === true && gas_cost != null) {
                        s += '<br/><span style="color: #cc5637;">Gas:&nbsp;</span>&nbsp;&euro;&nbsp' + gas_cost.toFixed(2);
                    }

                return s;
            },
            backgroundColor: '#F5F5F5',
            borderColor: '#DCE1E3',
            crosshairs: [true, true],
            borderWidth: 1
            },  
            series: [ 
                {
                    yAxis: 0,
                    id: 'verbruik',
                    visible: GseriesVisibilty[0],
                    name: 'kWh tarief',
                    color: '#ff6f49',
                    data: GkwhData,
                },{
                    yAxis: 0,
                    id: 'geleverd',
                    visible: GseriesVisibilty[1],
                    name: 'gas tarief',
                    color: '#cc5637',
                    data: GgasData,
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
        readJsonApiTariffHour();
    }
    // make chart only once and when we have data.
    x = $('#TariffChart').highcharts()
    if (recordsLoaded !== 0 && $('#TariffChart').highcharts() == null) {
      hideStuff('loading-data');
      createTariffChart();
      readJsonApiTariffHour();
    }
    setTimeout('DataLoop()', 1000 );
}

$(function() {
    set_language();
    toLocalStorage('cost-menu',window.location.pathname);
    if ( getLocalStorage('cost-dynamic-h-day') != null ) {
        displayPeriodID = getLocalStorage('cost-dynamic-h-day');
    }
    GseriesVisibilty[0] =JSON.parse(getLocalStorage('cost-dynamic-h-day-kwh'));  // #PARAMETER
    GseriesVisibilty[1] =JSON.parse(getLocalStorage('cost-dynamic-h-day-gas'));  // #PARAMETER

    Highcharts.setOptions({
    global: {
        useUTC: false
        }
    });
    secs = 0;
    screenSaver( <?php echo config_read(79);?> ); // to enable screensaver for this screen.
    DataLoop();

    // set buttons text in the right language
    document.getElementById("yesterday_button").innerHTML = yesterday_text;
    document.getElementById("today_button").innerHTML     = today_text;
    document.getElementById("tomorrow_button").innerHTML  = tomorrow_text; 

});

</script>
</head>
<body>

<?php page_header();?>

<div class="top-wrapper-2">
    <div class="content-wrapper pad-13">
       <!-- header 2 -->
       <?php pageclock(); ?>
       <?php page_menu_header_cost( 3 ); ?>
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
            <span class="text-2">Dynamische tarieven</span>&nbsp;<span class="text-2" id="title_date"></span>
            <span class="float-right">
            <button id="yesterday_button" onclick="setDateRange(0)" class="button-4 bold-font color-menu"></button>
            <button id="today_button"     onclick="setDateRange(1)" class="button-4 bold-font color-menu"></button>
            <button id="tomorrow_button"  onclick="setDateRange(2)" class="button-4 bold-font color-menu"></button>
        </span>
        </div>

        <div class="frame-2-bot"> 
        <div id="TariffChart" style="width:100%; height:480px;"></div>
        </div>
</div>
</div>
<div id="loading-data"><img src="./img/ajax-loader.gif" alt="Even geduld aub." height="15" width="128"></div>

</body>
</html>