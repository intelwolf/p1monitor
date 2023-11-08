<?php
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php';
include_once '/p1mon/www/util/page_menu_header_api_powerproduction.php'; 
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/fullscreen.php';
include_once '/p1mon/www/util/textlib.php';

if ( checkDisplayIsActive( 147 ) == false) { return; }
?>
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title><?php echo strIdx(133);?></title>
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
var min_text        = '<?php echo strIdx(128);?>'
var hour_text       = '<?php echo strIdx(129);?>'
var kwh_high_tariff = '<?php echo strIdx(126);?>'
var kwh_low_tariff  = '<?php echo strIdx(127);?>'

var recordsLoaded            = 0;
var initloadtimer;
var mins                     = 1;  
var secs                     = mins * 60;
var currentSeconds           = 0;
var currentMinutes           = 0;
var Gselected                = 0;
var GselectText              = ['15 '+ min_text,'30 '+min_text,'1 '+hour_text,'8 '+hour_text,'12 '+hour_text,'24 '+hour_text]; // #PARAMETER
var GseriesVisibilty         = [true,true, true, true];
var GHighTariffData          = [];
var GLowTariffData           = [];
var maxrecords               = 361; // max records is 360 due to 15 minutes samples
var high_tariff_color        = '#98D023';
var low_tariff_color         = '#7FAD1D';

// check if the record for epoch time exists
// if not add else add the values high and low to
// the array's
function updateOrInsertDataSets( item ) {
    // check if timestamp exists in the list
    timestamp = item[1] * 1000;
    for ( var i=0; i< GHighTariffData.length; i++ ) {
        if ( timestamp == GHighTariffData[i][0] ) { // timestamp allready exist
            //console.log( "start");
            GHighTariffData[i][1]         = GHighTariffData[i][1] + item[4]; // kWh during the period for the high tariff
            GLowTariffData[i][1]          = GLowTariffData[i][1]  + item[5]; // kWh during the period for the low tariff
            return
        }
    }

    GHighTariffData.push         ( [timestamp, item[4] ] ); // kWh during the period for the high tariff
    GLowTariffData.push          ( [timestamp, item[5] ] ); // kWh during the period for the low tariff
}

function readJsonApiHistoryPowerMin( cnt , db_index ){ 

    $.getScript( "/api/v1/powerproductionsolar/minute/1/" + db_index+ "?limit=" + cnt, function( data, textStatus, jqxhr ) {
      try {
        
        var jsondata = JSON.parse(data); 
        var item;
        recordsLoaded = jsondata.length;

        for ( var j = jsondata.length; j > 0; j-- ) {
            item = jsondata[ j-1 ];
            updateOrInsertDataSets( item )
        }


      } catch(err) {}
   });
   
}

function readJsonActiveDbSiteIndices( cnt ) {

    $.getScript( "/api/v1/configuration/140", function( data, textStatus, jqxhr ) {
      try {

        GHighTariffData.length = 0;
        GLowTariffData.length  = 0; 

        var jsondata = JSON.parse( data );
        json_data2   = JSON.parse( jsondata[0][1] )

        db_indeces_list = []
        for ( var i=0;  i<json_data2.length; i++ ) { 
            if ( json_data2[i]["SITE_ACTIVE"] == true ) {
                db_indeces_list.push( json_data2[i]["DB_INDEX"] )
            }
        }

        for ( var i=0;  i<db_indeces_list.length; i++ ) {
            readJsonApiHistoryPowerMin( cnt , db_indeces_list[i] );
        }
       
        updateData();

      } catch(err) {
          console.log("error = " + err )
      }
    });
} 

// change items with the marker #PARAMETER
function createKwhChart() {
    Highcharts.stockChart('KwhChart', {
        chart: {
            //marginTop: 46, // make room for the wide legend
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
                                toLocalStorage('powerprod-api-min-high-tariff-visible',!this.visible);  // #PARAMETER
                            }
                            if  ( this.index === 1 ) {
                                toLocalStorage('powerprod-api-min-low-tariff-visible',!this.visible);  // #PARAMETER
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
                                toLocalStorage('powerprod-api-min-select-index',j); // PARAMETER
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
                    var hoogTarief          = "verborgen";
                    var laagTarief          = "verborgen";

                    for (var i=0,  tot=d.length; i < tot; i++) {
                        //console.log (d[i].series.userOptions.id);

                        if  ( d[i].series.userOptions.id === 'hightariff') {
                            hoogTarief = d[i].y.toFixed(4) + " kWh";
                        }
                        if  ( d[i].series.userOptions.id === 'lowtariff') {
                            laagTarief = d[i].y.toFixed(4) + " kWh";
                        }
                    }

                    s += '<br/><span style="color: ' + high_tariff_color + ';">' + kwh_high_tariff + ': </span>' + hoogTarief;
                    s += '<br/><span style="color: ' + low_tariff_color + ';">'  + kwh_low_tariff  + ': </span>' + laagTarief; 
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
                name: kwh_high_tariff ,
                color: high_tariff_color,
                data: GHighTariffData 
            },
            {
                id: 'lowtariff',
                yAxis: 0,
                type: 'areaspline',
                visible: GseriesVisibilty[1],
                name: kwh_low_tariff ,
                color: low_tariff_color,
                data: GLowTariffData
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

function updateData() {
    if ( GHighTariffData == 0 ) { // only update if we have data, when there is no data retry after 1 second.
        setTimeout('updateData()',1000);
        //console.log(" timer")
        return
    }
    //console.log( "update")
    var chart = $('#KwhChart').highcharts();
    if( typeof(chart) !== 'undefined') {
        chart.series[0].setData( GHighTariffData );
        chart.series[1].setData( GLowTariffData );
    }


}

function DataLoop() {
    currentMinutes = Math.floor(secs / 60);
    currentSeconds = secs % 60;
    if(currentSeconds <= 9) { currentSeconds = "0" + currentSeconds; }
    secs--;
    document.getElementById("timerText").innerHTML = zeroPad(currentMinutes,2) + ":" + zeroPad(currentSeconds,2);
    if( secs < 0 ) {
        mins = 1;  
        secs = mins * 60; 
        currentSeconds = 0;
        currentMinutes = 0;
        colorFader("#timerText","#0C7DAD");
        readJsonActiveDbSiteIndices( maxrecords )
    }

    // make chart only once and when we have data.
    if (recordsLoaded !== 0 &&  $('#KwhChart').highcharts() == null) {
      hideStuff('loading-data');
      createKwhChart();
    }
    setTimeout('DataLoop()',1000);
}


$(function() {
    toLocalStorage('powerproduction-api-menu', window.location.pathname ); // #PARAMETER
    Gselected = parseInt( getLocalStorage('powerprod-api-min-select-index'), 10 );
    GseriesVisibilty[0] =JSON.parse(getLocalStorage('powerprod-api-min-high-tariff-visible'));  // #PARAMETER
    GseriesVisibilty[1] =JSON.parse(getLocalStorage('powerprod-api-min-low-tariff-visible') );  // #PARAMETER
    Highcharts.setOptions({
    global: {
        useUTC: false
        }
    });

    // get language settings from config database and set HighChart
    setHighChartLanguageOptions( <?php echo languageIndex();?> );

    secs = -1;
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
       <?php page_menu_header_api_powerproduction( 0 ); ?>
       <?php weather_info(); ?>
    </div>
</div>

<div class="mid-section">
    <div class="left-wrapper">
        <?php page_menu( 12 ); ?>
        <div id="timerText" class="pos-8 color-timer"></div>
        <?php fullscreen(); ?>
    </div> 
    <div class="mid-content-2 pad-13">
    <!-- links -->
        <div class="frame-2-top">
            <span class="text-2"><?php echo strIdx(125);?></span>
        </div>
        <div class="frame-2-bot">
        <div id="KwhChart" style="width:100%; height:480px;"></div>
        </div>
</div>
</div>
<div id="loading-data"><img src="./img/ajax-loader.gif" alt="Even geduld aub." height="15" width="128"></div>
</body>
</html>