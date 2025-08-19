<?php
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php';  
include_once '/p1mon/www/util/page_menu_header_api_powerproduction.php';  
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/fullscreen.php';

if ( checkDisplayIsActive( 147 ) == false) { return; }
?>
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title><?php echo strIdx(147);?></title>
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

var year_text            = '<?php echo strIdx(132);?>'
var kwh_high_tariff_text = '<?php echo strIdx(126);?>'
var kwh_low_tariff_text  = '<?php echo strIdx(127);?>'
var min_temp_text        = '<?php echo strIdx(138);?>'
var avg_temp_text        = '<?php echo strIdx(137);?>'
var max_temp_text        = '<?php echo strIdx(136);?>'
var temp_text            = '<?php echo strIdx(139);?>'
var total_text           = '<?php echo strIdx(140);?>'

var recordsLoaded    = 0;
var initloadtimer;
var mins             = 1;  
var secs             = mins * 60;
var currentSeconds   = 0;
var currentMinutes   = 0;
var Gselected        = 0;
var GselectText      = ["5 "+year_text,"10 "+year_text,"15 "+year_text,"20 "+year_text] // #PARAMETER
var GseriesVisibilty = [true,true,true, true];
var GHighTariffData  = [];
var GLowTariffData   = [];
var GTotalData       = [];
var Granges          = [];
var Gaverages        = [];
var maxrecords       = 100; //PARAMETER

var max_temp_color    = '#FF0000';
var avg_temp_color    = '#384042';
var min_temp_color    = '#0088FF';
var high_tariff_color = '#98D023';
var low_tariff_color  = '#7FAD1D';

function readJsonApiWeatherHistoryYear( cnt ){ 
    $.getScript( "/api/v1/weather/year?limit=" + cnt, function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        //console.log( jsondata )
        for (var j = 0; j < jsondata.length; j++){    
            var item = jsondata[ j ];
            for ( var k=0 ; k < GHighTariffData.length; k++ ) {
                if ( GHighTariffData[k][0] == item[1] * 1000 ) {
                    Granges[k][1]   = item[4]
                    Granges[k][2]   = item[6]
                    Gaverages[k][1] = item[5]
                    break;
                }
            }
        }  
        updateData();
      } catch(err) {
        console.log( err )
      }
   });
}

// check if the record for epoch time exists
// if not add else add the values high and low to
// the array's
function updateOrInsertDataSets( item ) {
    // check if timestamp exists in the list
    timestamp = item[1] * 1000;
    for ( var i=0; i< GHighTariffData.length; i++ ) {
        if ( timestamp == GHighTariffData[i][0] ) { // timestamp allready exist
            //console.log( "start");
            GHighTariffData[i][1] = GHighTariffData[i][1] + item[4]; // kWh during the period for the high tariff
            GLowTariffData[i][1]  = GLowTariffData[i][1]  + item[5]; // kWh during the period for the low tariff
            GTotalData[i][1]      = GTotalData[i][1]  + item[4] + item[5]; // kWh low - kWh tariff total
            return
        }
    }

    GHighTariffData.push (  [timestamp,     item[4] ] ); // kWh during the period for the high tariff
    GLowTariffData.push (   [timestamp,     item[5] ] ); // kWh during the period for the low tariff
    GTotalData.push (       [timestamp,    (item[4] + item[5]) ] ); // kWh low - kWh tariff total
    Granges.push    (       [timestamp, null, null ] );
    Gaverages.push  (       [timestamp, null ]       );
}

function readJsonApiHistoryPowerYear( cnt, db_index ){ 

    $.getScript( "/api/v1/powerproductionsolar/year/1/" + db_index+ "?limit=" + cnt, function( data, textStatus, jqxhr ) {
      try {
        var jsondata    = JSON.parse(data); 
        recordsLoaded   = jsondata.length;

        for ( var j = jsondata.length; j > 0; j-- ) {
            item = jsondata[ j-1 ];
            updateOrInsertDataSets( item )
        }

        GHighTariffData.sort();
        GLowTariffData.sort();
        GTotalData.sort();
        Granges.sort();
        Gaverages.sort();

        readJsonApiWeatherHistoryYear( maxrecords )

      } catch(err) {}
   });

}


function readJsonActiveDbSiteIndices( cnt ) {
    $.getScript( "/api/v1/configuration/140", function( data, textStatus, jqxhr ) {
      try {

        GHighTariffData.length  = 0;
        GLowTariffData.length   = 0; 
        GTotalData.length       = 0;
        Granges.length          = 0;
        Gaverages.length        = 0;

        var jsondata  = JSON.parse( data );
        json_data2    = JSON.parse( jsondata[0][1] )
       
        db_indeces_list = []
        for ( var i=0;  i<json_data2.length; i++ ) {
            if ( json_data2[i]["SITE_ACTIVE"] == true ) {
                db_indeces_list.push(  json_data2[i]["DB_INDEX"] )
            }
        }

        for ( var i=0;  i<db_indeces_list.length; i++ ) {
            //console.log("db_indeces_list[i]=" + db_indeces_list[i] )
            readJsonApiHistoryPowerYear( cnt , db_indeces_list[i] );
        }

        // Weather 
        readJsonApiWeatherHistoryYear(cnt);

      } catch(err) {
          console.log("error = " + err )
      }
    });
}

// change items with the marker #PARAMETER
function createKwhChart() {
    Highcharts.stockChart('KwhChart', {
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
                            //console.log(this.index)
                            if  ( this.index === 0 ) {
                                toLocalStorage('powerprod-api-j-high-tariff-visible',this.visible);  // #PARAMETER
                            }
                            if  ( this.index === 1 ) {
                                toLocalStorage('powerprod-api-j-low-tariff-visible',this.visible);  // #PARAMETER
                            }
                            if  ( this.index === 2 ) {
                                toLocalStorage('powerprod-api-j-netto-visible',this.visible);  // #PARAMETER
                            }
                            if  ( this.index === 3 ) {
                                toLocalStorage('powerprod-api-j-temp-visible',this.visible);  // #PARAMETER
                            }
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
                    type: 'year',
                    count: 5,
                    text: GselectText[0]
                },{
                    type: 'year',
                    count: 10,
                    text: GselectText[1]
                },{
                    type: 'year',
                    count: 15,
                    text: GselectText[2]
                }, {
                    type: 'year',
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
                                toLocalStorage('powerprod-api-j-select-index',j); // PARAMETER
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
            yAxis:[ 
                { // kWh
                gridLineColor: '#6E797C',
                gridLineDashStyle: 'longdash',
                lineWidth: 0,
                offset: 0,
                opposite: false,
                labels: {
                    //useHTML: true, //fix see through axis values.
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
                { // temp axis
                //tickAmount: 7,
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
                title: {
                    text: null, 
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
                    var s = '<b>'+ Highcharts.dateFormat('%Y', this.x) +'</b>';
                    var d                   = this.points;

                    var PHighTariff = PLowTariff = Ptotal = Pavg_temp = Pmin_temp = Pmax_temp = 0;
                    //var totalIsOn = false;

                    // find timestamp and add data points
                    for (var i=0,  tot=GHighTariffData.length; i < tot; i++) {
                        if ( GHighTariffData[i][0] == d[0].key ) { //found time and dataset
                            PHighTariff  = GHighTariffData[i][1]
                            PLowTariff   = GLowTariffData[i][1]
                            Ptotal       = GTotalData[i][1]
                            Pmin_temp    = Granges[i][1];
                            Pmax_temp    = Granges[i][2];
                            Pavg_temp    = Gaverages[i][1]
                        break;
                        }
                    }

                    if ( $('#KwhChart').highcharts().series[0].visible === true ) {
                        s += '<br/><span style="color:' + high_tariff_color + '">' + kwh_high_tariff_text + ':&nbsp;</span>' + PHighTariff.toFixed(3) + " kWh";
                    }
                    if ( $('#KwhChart').highcharts().series[1].visible === true ) {
                        s += '<br/><span style="color:' + low_tariff_color + '">' + kwh_low_tariff_text + ':&nbsp;</span>' + PLowTariff.toFixed(3) + " kWh";;
                    }

                    if ( $('#KwhChart').highcharts().series[2].visible === true ) {
                        s += '<br/><span style="color:black">' + total_text + ':&nbsp;</span>' + Ptotal.toFixed(3) + " kWh";;
                    }

                    if ( $('#KwhChart').highcharts().series[3].visible === true ) {
                        if ( Pmax_temp != null ) {
                            s += '<br/><span style="color: ' + max_temp_color + '">' + max_temp_text + ': </span>'    + Pmax_temp.toFixed(1) + " °C"; 
                        }
                        if ( Pavg_temp != null ) {
                            s += '<br/><span style="color: ' + avg_temp_color + '">'+ avg_temp_text + ': </span>' + Pavg_temp.toFixed(1) + " °C";
                        }
                        if ( Pmin_temp != null ) {
                            s += '<br/><span style="color: ' + min_temp_color + '">' + min_temp_text + ': </span>'    + Pmin_temp.toFixed(1) + " °C";
                        }
                    }
              
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
                        second: '%H:%M:%S',
                        minute: '%H:%M',
                        hour: '%H:%M',
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
                    borderColor: '#6E797C',
                }
            },
            series: [ 
                {
                    yAxis: 0,
                    visible: GseriesVisibilty[0],
                    name: kwh_high_tariff_text,
                    color: high_tariff_color,
                    data: GHighTariffData 
                },{
                    yAxis: 0,
                    visible: GseriesVisibilty[1],
                    name: kwh_low_tariff_text,
                    color: low_tariff_color,
                    data: GLowTariffData
                },{
                    yAxis: 0,
                    visible: GseriesVisibilty[2],
                    type: 'spline', 
                    color: 'black',
                    name: total_text + ' kWh',
                    data: GTotalData,
                    dashStyle: 'ShortDashDotDot',
                    lineWidth: 1
                },{
                    yAxis: 1,
                    visible: GseriesVisibilty[3],
                    showInNavigator: true,
                    name: temp_text,
                    data: Gaverages,
                    type: 'spline',
                    zIndex: 2,
                    color: avg_temp_color,
                    lineWidth: 1,
                    marker: {
                        fillColor: 'white',
                        lineWidth: 1,
                        lineColor: '#384042'
                    }
                },{
                    yAxis: 1,
                    dashStyle: 'ShortDot',
                    visible: GseriesVisibilty[3],
                    //id: 'temperatuurRange',
                    name: 'Range',
                    data: Granges,
                    type: 'areasplinerange',
                    lineWidth: 1,
                    linkedTo: ':previous',
                    color: '#ff0000',
                    negativeColor: '#0088FF',
                    fillOpacity: 0.3,
                    zIndex: 1,
                    marker: {
                        fillColor: 'white',
                        lineWidth: 1,
                        lineColor: '#ff0000'
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
}

function updateData() {
    //console.log("updateData()");
    var chart = $('#KwhChart').highcharts();
    if( typeof(chart) !== 'undefined') {
        chart.series[0].setData( GHighTariffData );
        chart.series[1].setData( GLowTariffData );
        chart.series[2].setData( GTotalData );
        chart.series[3].setData( Gaverages );
        chart.series[4].setData( Granges );
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
        readJsonActiveDbSiteIndices(  maxrecords )
    }
    // make chart only once and when we have data.
    if (recordsLoaded !== 0 &&  $('#KwhChart').highcharts() == null) {
      hideStuff('loading-data');
      createKwhChart();
    }
    setTimeout('DataLoop()',1000);
}

$(function() {
    toLocalStorage('powerproduction-api-menu',window.location.pathname); // PARAMETER
    Gselected = parseInt(getLocalStorage('powerprod-j-select-index'),10);
    GseriesVisibilty[0] =JSON.parse(getLocalStorage('powerprod-api-j-high-tariff-visible'));  // #PARAMETER
    GseriesVisibilty[1] =JSON.parse(getLocalStorage('powerprod-api-j-low-tariff-visible'));  // #PARAMETER
    GseriesVisibilty[2] =JSON.parse(getLocalStorage('powerprod-api-j-netto-visible'));  // #PARAMETER
    GseriesVisibilty[3] =JSON.parse(getLocalStorage('powerprod-api-j-temp-visible'));   // #PARAMETER
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
       <?php page_menu_header_api_powerproduction( 4 ); ?>
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
            <span class="text-2"><?php echo strIdx(146);?></span>
        </div>
        <div class="frame-2-bot"> 
        <div id="KwhChart" style="width:100%; height:480px;"></div>    
        </div>
</div>
</div>
<div id="loading-data"><img src="./img/ajax-loader.gif" alt="Even geduld aub." height="15" width="128"></div>

</body>
</html>