<?php 
include_once '/p1mon/www/util/p1mon-util.php';
include_once '/p1mon/www/util/page_header.php'; 
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/page_menu_header_main.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/textlib.php';
include_once '/p1mon/www/util/fullscreen.php';
include_once '/p1mon/www/util/highchart.php';

?> 
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title>P1-monitor <?php echo strIdx( 343 )?> 1</title>
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

var sqlData             = []; 
var verbrData10sec      = [];
var gelvrData10sec      = [];
var secs                = 10;
var gaugeDataVerbruik   = [];
var gaugeDataGeleverd   = [];
var verbrKosten         = 0;
var gelvrKosten         = 0;
var wattageMaxValueConsumption  = <?php echo config_read(52); ?>;
var wattageMaxValueProduction   = <?php echo config_read(53); ?>;
var showPhaseInformation        = <?php echo config_read(61); ?>;
//var faseVerbrTitle = 'fase<br>verdeling'
var consumptionPowerPhase   = [ [0],[0],[0] ];
var productionPowerPhase    = [ [0],[0],[0] ];
var watermeterRecords       = 1

var phaseCategories         = [ 'L1', 'L2', 'L3' ]
var p1TelegramMaxSpeedIsOn  = <?php if ( config_read( 154 ) == 1 ) { echo "true;"; } else { echo "false\n"; } ?>
var hideWaterUi             = <?php if ( config_read( 157 ) == 1 ) { echo "true;"; } else { echo "false\n"; } ?>
var hideGaSUi               = <?php if ( config_read( 158 ) == 1 ) { echo "true;"; } else { echo "false\n"; } ?>
var hidePeakKw              = <?php if ( config_read( 206 ) == 1 ) { echo "true;"; } else { echo "false\n"; } ?>

const power_text = "<?php echo strIdx( 361 );?>"

function readJsonApiWaterHistoryDay( cnt ){ 
    $.getScript( "/api/v2/watermeter/day?limit=" + cnt, function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        if ( jsondata.length == 0 ) {
            $('#verbruikWater').text( padXX( 0 ,5, 3 ) );
        } else {
            $('#verbruikWater').text( padXX( jsondata[0][5] ,5, 3 ) );
            // day value 
            if ( jsondata[0][0]. substr( 0, 10 ) == moment().format('YYYY-MM-DD') ) {
                $('#verbruikWaterDag').text( padXX( jsondata[0][4] ,8, 1 ) );
            } else {
                $('#verbruikWaterDag').text( padXX( 0 ,8, 1 ) );
            }
        }
      } catch(err) {
      }
   });
}

function readJsonApiHistoryDay(){ 
    $.getScript( "/api/v1/powergas/day?limit=1", function( data, textStatus, jqxhr ) {
      try {
        var jsondata = JSON.parse(data); 
        $('#verbruikDalEnPiekKW').text( padXX( jsondata[0][6] ,5, 3 ) +" kWh");
        $('#geleverdDalEnPiekKW').text( padXX( jsondata[0][7] ,5, 3 ) +" kWh");
        $('#verbruikGasDag').text( padXX( jsondata[0][9]      ,5, 3) );
      } catch(err) {}
   });
}

function readJsonApiSmartMeter(){ 
    //$.getScript( "./api/v1/smartmeter?limit=60", function( data, textStatus, jqxhr ) {
    $.getScript( "./api/v1/smartmeter?limit=60", function( data, textStatus, jqxhr ) {
      try {
    
        var jsondata = JSON.parse(data); 
        var item;

        verbrData10sec.length = 0;
        gelvrData10sec.length = 0;

        for (var j = jsondata.length; j > 0; j--){    
            item = jsondata[ j-1 ];
            item[0] = item[1]*1000; // highchart likes millisecs.

            verbrData10sec.push( [item[0], item[8]/1000] ); // Watt consumend
            gelvrData10sec.push( [item[0], item[9]/1000] ); // Watt produced
        }  
        
        gaugeDataVerbruik = parseFloat( verbrData10sec[ verbrData10sec.length-1 ][1] ); //[sqlData[0][7]];
        var point = $('#actVermogenMeterVerbruik').highcharts().series[0].points[0];
        point.update( gaugeDataVerbruik, true, true, true );

        //console.log ( gaugeDataVerbruik + " update gaugeDataVerbruik" )

        gaugeDataGeleverd = parseFloat( gelvrData10sec[ gelvrData10sec.length-1][1] ) ;
        point = $('#actVermogenMeterGeleverd').highcharts().series[0].points[0];
        point.update( gaugeDataGeleverd, true, true, true );
        //console.log ( gaugeDataGeleverd + " update gaugeDataGeleverd" )

        $('#verbruikDal').text ( padXX( jsondata[0][3]  ,5 ,3 )+" kWh")
        $('#verbruikPiek').text( padXX( jsondata[0][4]  ,5 ,3)+" kWh");
        $('#verbruikDGas').text( padXX( jsondata[0][10] ,5 ,3));
        $('#geleverdDal').text(  padXX( jsondata[0][5]  ,5 ,3 )+" kWh");
        $('#geleverdPiek').text( padXX( jsondata[0][6]  ,5 ,3)+" kWh");
        
        if ( jsondata[0][7] == 'P' ) {
            $("#verbruikPiekI").css("color","#F2BA0F");
            $("#geleverdPiekI").css("color","#98D023");
            $("#verbruikDalI" ).css("color","#6E797C");
            $("#geleverdDalI" ).css("color","#6E797C");
        } else {
            $("#verbruikPiekI").css("color","#6E797C");
            $("#geleverdPiekI").css("color","#6E797C");
            $("#verbruikDalI" ).css("color","#F2BA0F");
            $("#geleverdDalI" ).css("color","#98D023");
        }

        $("#actVermogenMeterGrafiekGeleverd").highcharts().series[0].update({
            pointStart: gelvrData10sec[0][0],
            data: gelvrData10sec
        }, false);
        $("#actVermogenMeterGrafiekGeleverd").highcharts().redraw();

        //$("#actVermogenMeterGrafiekGeleverd").highcharts().series[0].setData( gelvrData10sec )
        //$("#actVermogenMeterGrafiekGeleverd").highcharts().redraw();

        $("#actVermogenMeterGrafiekVerbruik").highcharts().series[0].update({
            pointStart: verbrData10sec[0][0],
            data: verbrData10sec
        }, true);
        $("#actVermogenMeterGrafiekVerbruik").highcharts().redraw();

        //$("#actVermogenMeterGrafiekVerbruik").highcharts().series[0].setData( verbrData10sec )

      } catch(err) {}
   });
}

function readJsonApiStatus(){ 
    
    $.getScript( "./api/v1/status", function( data, textStatus, jqxhr ) {
      try {

        var jsondata = JSON.parse(data); 
        var lowProductionKw = peakConsumptionKw = lowProductionKw = peakProductionKw = 0
        var peakConsumptionKwTimestamp = lowkProductionKwTimestamp = lowProductionTimestamp = peakProductionKwTimestamp = "??:??:??"

        for (var j=0;  j < jsondata.length; j++){  
            // console.log( jsondata[j][0] + ' - ' + jsondata[j][1] )
            if ( jsondata[j][0] == 1 ) {
                var peakConsumptionKw = padXX( jsondata[j][1], 2, 2 )
                continue;
            }
            if ( jsondata[j][0] == 2 ) {
                var peakConsumptionKwTimestamp = jsondata[j][1].substring( 11 );
                continue;
            }
            if ( jsondata[j][0] == 3 ) {
                var peakProductionKw = padXX( jsondata[j][1], 2, 2 )
                continue;
            }
            if ( jsondata[j][0] == 4 ) {
                var peakProductionKwTimestamp = jsondata[j][1].substring( 11 );
                continue;
            }
            
            if ( jsondata[j][0] == 8 ) { 
                $('#verbruikDalKW').text( padXX( jsondata[j][1], 5, 3 ) + " kWh" );
                //verbruikTotaal = verbruikTotaal + parseFloat( jsondata[j][1] );
                continue;
            }
            if ( jsondata[j][0] == 9 ) { 
                $('#verbruikPiekKW').text( padXX( jsondata[j][1], 5, 3 ) + " kWh" );
                //verbruikTotaal = verbruikTotaal + parseFloat( jsondata[j][1] );
                continue;
            }
            if ( jsondata[j][0] == 10 ) { 
                $('#geleverdDalKW').text( padXX( jsondata[j][1], 5, 3 ) + " kWh" );
                //geleverdTotaal = geleverdTotaal + parseFloat( jsondata[j][1] );
                continue;
            }
            if ( jsondata[j][0] == 11 ) { 
                $('#geleverdPiekKW').text( padXX( jsondata[j][1], 5, 3 ) + " kWh" );
                //geleverdTotaal = geleverdTotaal +  parseFloat( jsondata[j][1] );
                continue;
            }
            
            if ( jsondata[j][0] == 32 ) {
                $('#P_Q_kw').text( padXX( jsondata[j][1], 3, 3 ) );
                continue;
            }
            if ( jsondata[j][0] == 33 ) {
                $('#P_Q_timestamp').text(jsondata[j][1] );
                continue;
            }

            if ( jsondata[j][0] == 34 ) {
                $('#P_M_kw').text( padXX( jsondata[j][1], 3, 3 ) );
                continue;
            }
            if ( jsondata[j][0] == 35 ) {
                $('#P_M_timestamp').text(jsondata[j][1] );
                continue;
            }

            if ( jsondata[j][0] == 74 ) { 
                consumptionPowerPhase[0] = parseFloat( jsondata[j][1] )
                continue;
            }
            if ( jsondata[j][0] == 75 ) { 
                consumptionPowerPhase[1] = parseFloat( jsondata[j][1] )
                continue;
            }
            if ( jsondata[j][0] == 76 ) { 
                consumptionPowerPhase[2] = parseFloat( jsondata[j][1] )
                continue;
            }
            if ( jsondata[j][0] == 77) { 
                productionPowerPhase[0] = parseFloat( jsondata[j][1] )
                continue;
            }
            if ( jsondata[j][0] == 78 ) { 
                productionPowerPhase[1] = parseFloat( jsondata[j][1] )
                continue;
            }
            if ( jsondata[j][0] == 79 ) { 
                productionPowerPhase[2] = parseFloat( jsondata[j][1] )
                continue;
            }
            if ( jsondata[j][0] == 113 ) {
                var lowConsumptionKw = padXX( jsondata[j][1], 2, 2 )
                continue;
            }
            if ( jsondata[j][0] == 114 ) {
                var lowConsumptionKwTimestamp = jsondata[j][1].substring( 11 );
                continue;
            }
            if ( jsondata[j][0] == 115 ) {
                var lowProductionKw = padXX( jsondata[j][1], 2, 2 )
                continue;
            }
            if ( jsondata[j][0] == 116 ) {
                var lowProductionTimestamp = jsondata[j][1].substring( 11 );
                continue;
            }

         }

        $('#peakKWConsumption').text(" " + peakConsumptionKw + " kW " + peakConsumptionKwTimestamp );
        $('#lowKWConsumption').text(" " + lowConsumptionKw + " kW " + lowConsumptionKwTimestamp );
        $('#peakKWProduction').text(" " + peakProductionKw + " kW " + peakProductionKwTimestamp );
        $('#lowKWProduction').text(" " + lowProductionKw + " kW " + lowProductionTimestamp );

        //console.log( "consumptionPowerPhase="+consumptionPowerPhase )
        // check if there is phase information for consumption

        if ( showPhaseInformation != 0 ) {
            autoHideNonPresentPhaseInformation() 
        }

        if ( showPhaseInformation == 0 || consumptionPowerPhase[0] == 0 && consumptionPowerPhase[1] == 0 && consumptionPowerPhase[2] == 0 ) {
            $("#actVermogenFaseVerbruik").highcharts().series[0].hide();
        } else {
            $("#actVermogenFaseVerbruik").highcharts().series[0].show();
            $("#actVermogenFaseVerbruik").highcharts().series[0].setData( consumptionPowerPhase );
        }

        //console.log( "productionPowerPhase="+productionPowerPhase )
         // check if there is phase information for production
         if ( showPhaseInformation == 0 || showPhaseInformation == 0 || productionPowerPhase[0] == 0 && productionPowerPhase[1] == 0 && productionPowerPhase[2] == 0 ) {
            $("#actVermogenFaseLevering").highcharts().series[0].hide();
        } else {
            $("#actVermogenFaseLevering").highcharts().series[0].show();
            $("#actVermogenFaseLevering").highcharts().series[0].setData( productionPowerPhase );
        }
      } catch(err) {
          console.log( err)
      }
   });
}

function autoHideNonPresentPhaseInformation() {

    var tmpConsumptionPowerPhase = [ null, null, null ];
    var tmpConsumptionCategories = [ '','','' ]
    var tmpProductionPowerPhase  = [ null, null, null ];
    var tmpProductionCategories  = [ '','','' ]
    
    for ( var index=0;  index < consumptionPowerPhase.length; index++ ){  
        if ( consumptionPowerPhase[index] != 0 ) {
            tmpConsumptionCategories[ index ] = phaseCategories[ index ];
            tmpConsumptionPowerPhase[ index ] = consumptionPowerPhase[ index ];
        }
        if ( productionPowerPhase[index] != 0 ) {
            tmpProductionCategories[ index ] = phaseCategories[ index ];
            tmpProductionPowerPhase[ index ] = productionPowerPhase[ index ];
        }
    }

    consumptionPowerPhase = tmpConsumptionPowerPhase;
    productionPowerPhase  = tmpProductionPowerPhase;
    $("#actVermogenFaseVerbruik").highcharts().xAxis[0].setCategories( tmpConsumptionCategories );
    $("#actVermogenFaseLevering").highcharts().xAxis[0].setCategories( tmpProductionCategories );

}

function readJsonApiFinancial(){ 
    $.getScript( "./api/v1/financial/day?limit=1", function( data, textStatus, jqxhr ) {
        try {
            var jsondataCost = JSON.parse(data); 
            verbrKosten = jsondataCost[0][2] + jsondataCost[0][3] + jsondataCost[0][6] + jsondataCost[0][7];
            gelvrKosten = jsondataCost[0][4] + jsondataCost[0][5];
            $('#verbruikKosten').text(padXX(verbrKosten,2,2));
            $('#geleverdKosten').text(padXX(gelvrKosten,2,2));
        } catch(err) {}
    });
}

function createChartPhaseProduction(){
    $('#actVermogenFaseLevering').highcharts({
        chart: {
            margin: [0, 20, 0, 30],
            style: {
                fontFamily: 'robotomedium',
            },
            type: 'column',
            inverted: true,
            width: 200,
            height: 80
        },
        tooltip: { enabled: false },
        legend: { enabled: false },
        title: { text: null },
        xAxis: {
            categories: phaseCategories,
            lineWidth: 0,
            minorGridLineWidth: 0,
            lineColor: 'transparent',
            minorTickLength: 0,
            tickLength: 0,
        },
        yAxis: {
            title: { text: null },
            labels: { enabled: false },
            lineWidth: 0,
            minorGridLineWidth: 0,
            lineColor: 'transparent',
            minorTickLength: 0,
            tickLength: 0,
            gridLineColor: 'transparent',
        },
        plotOptions: {
            column: {
                dataLabels: {
                    useHTML: true,
                    enabled: true,
                    format: '{y:.3f} kW',
                    color: '#6E797C',
                }
            },
            series: {
                color: '#98D023',
                pointPadding: 0,
                groupPadding: 0
            }
        },
        series: [{
            data: productionPowerPhase
        }]
    });
}

function createChartPhaseConsuming(){
    $('#actVermogenFaseVerbruik').highcharts({
        chart: {
            margin: [0, 20, 0, 30],
            style: {
                fontFamily: 'robotomedium'
            },
            type: 'column',
            inverted: true,
            width: 200,
            height: 80
        },
        tooltip: { enabled: false },
        legend: { enabled: false },
        title: { text: null },
        xAxis: {
            categories: phaseCategories,
            lineWidth: 0,
            minorGridLineWidth: 0,
            lineColor: 'transparent',
            minorTickLength: 0,
            tickLength: 0
        },
        yAxis: {
            title: { text: null },
            labels: { enabled: false },
            lineWidth: 0,
            minorGridLineWidth: 0,
            lineColor: 'transparent',
            minorTickLength: 0,
            tickLength: 0,
            gridLineColor: 'transparent',
        },
        plotOptions: {
            column: {
                dataLabels: {
                    useHTML: true,
                    enabled: true,
                    format: '{y} kW',
                    color: '#6E797C',
                }
            },
            series: {
                color: '#F2BA0F',
                pointPadding: 0,
                groupPadding: 0
            }
        },
        series: [{
            data: consumptionPowerPhase
        }]
    });
}

function createChartGaugeVerbruik(){
    $('#actVermogenMeterVerbruik').highcharts({
        chart: {
            style: {
                fontFamily: 'robotomedium',
                fontSize: '14px'
            },
            type: 'gauge',
            plotBackgroundColor: null,
            plotBackgroundImage: null,
            plotBorderWidth: 0,
            plotShadow: false
        },
        exporting: { enabled: false },
        credits: { enabled: false },
        title: { text: null },
        tooltip: { enabled: false },
        pane: {
            startAngle: -150,
            endAngle: 150,
            background: [{
                backgroundColor: '#F5F5F5',
                borderWidth: 2,
                outerRadius: '109%'
            }]
        },
        yAxis: {
            lineWidth: 0,
            min: 0,
            max: wattageMaxValueConsumption, // dynamic
            labels: {
                distance: -27
            },
            minorTickInterval: 'auto',
            minorTickWidth: 11,
            minorTickLength: 18,
            minorTickPosition: 'inside',
            minorTickColor: '#F2BA0F',
            tickPixelInterval: 50,
            tickWidth: 11,
            tickPosition: 'inside',
            tickLength: 18,
            tickColor: '#F2BA0F',
            title: {
                useHTML: true,
                text: 'kW',
                x: 0,
                y: 160,
            },
        },
        plotOptions: {
            gauge: {
                dial: {
                    radius: '68%',
                    backgroundColor: '#384042',
                    borderWidth: 1,
                    baseWidth: 15,
                    topWidth: 1,
                    baseLength: '1%', // of radius
                    rearLength: '1%'
                },
                pivot: {
                    radius: 8,
                    borderWidth: 1,
                    backgroundColor: '#384042',
                    borderColor: '#F5F5F5'
                },
                dataLabels: {
                    useHTML: true,
                    format: '{point.y:.3f}',
                    borderColor: '#384042',
                    padding: 4,
                    borderRadius: 5,
                    verticalAlign: 'center',
                    y: 65,
                    style: {
                        fontWeight: 'bold',
                        fontSize: '13px',
                        color: "#6e797c"
                    }
                },
                wrap: false
            }
        },
        series: [{
            marker: {
                fillColor: '#384042',
                lineColor: '#384042'
            },
            data: [{
                color: '#384042',
                y: gaugeDataVerbruik
            }]
        }]
    });
}

function createChartGaugeGeleverd(){
    $('#actVermogenMeterGeleverd').highcharts({
        chart: {
        style: {
            fontFamily: 'robotomedium',
            fontSize: '14px'
            },
            type: 'gauge',
            plotBackgroundColor: null,
            plotBackgroundImage: null,
            plotBorderWidth: 0,
            plotShadow: false
        },
        exporting: { enabled: false },
        credits: { enabled: false },
        title: { text: null },
        tooltip: { enabled: false },
        pane: {
            startAngle: -150,
            endAngle: 150,
            background: [{
                backgroundColor: '#F5F5F5',
                borderWidth: 2,
                outerRadius: '109%'
            }]
        },
        yAxis: {
            lineWidth: 0,
            min: 0,
            max: wattageMaxValueProduction, // dynamic
            labels: {
                distance: -27
            },
            minorTickInterval: 'auto',
            minorTickWidth: 11,
            minorTickLength: 18,
            minorTickPosition: 'inside',
            minorTickColor: '#98D023',
            tickPixelInterval: 50,
            tickWidth: 11,
            tickPosition: 'inside',
            tickLength: 18,
            tickColor: '#98D023',
            title: {
                useHTML: true,
                text: 'kW',
                x: 0,
                y: 160,
            },    
        },
        plotOptions: {
            gauge: {
                dial: {
                    radius: '68%',
                    backgroundColor: '#384042',
                    borderWidth: 1,
                    baseWidth: 15,
                    topWidth: 1,
                    baseLength: '1%', // of radius
                    rearLength: '1%'
                },
                pivot: {
                    radius: 8,
                    borderWidth: 1,
                    backgroundColor: '#384042',
                    borderColor: '#F5F5F5'
                },
                dataLabels: {
                    useHTML: true,
                    format: '{point.y:.3f}',
                    borderColor: '#384042',
                    padding: 4,
                    borderRadius: 5,
                    verticalAlign: 'center',
                    y: 65,
                    style: {
                        fontWeight: 'bold',
                        fontSize: '13px',
                        color: "#6e797c"
                    }
                },
                wrap: false
            }
        },
        series: [{
            marker: {
                fillColor: '#384042',
                lineColor: '#384042'
            },
            /*
            animation: {
                duration: 1000
            }*/
            data: [{
                color: '#384042',
                y: gaugeDataGeleverd
            }]
        }]
    });
}

function createChartVerbruikGrafiek() {
    $('#actVermogenMeterGrafiekVerbruik').highcharts({
        chart: {
            type: 'areaspline',
            style: {
                fontFamily: 'robotomedium',
                //fontSize: '14px'
            },
        },
        legend: {
            enabled: false
        },
        exporting: { enabled: false },
        credits: { enabled: false },
        title: { text: null },
        tooltip: {
            useHTML: true,
            style: {
                 padding: 3,
                 color: '#6E797C'
             },
            formatter: function() {
                var s = '<b>'+ Highcharts.dateFormat('%A %H:%M:%S', this.x) +'</b>';
                s += '<br/><span style="color: #F2BA0F;">'+ power_text +' kW: </span>'+this.y.toFixed(3);
                return s;
            },
            backgroundColor: '#F5F5F5',
            borderColor: '#DCE1E3',
            crosshairs: [true, true],
            borderWidth: 1
        },  
        xAxis: {
            type: 'datetime',
            lineColor: '#6E797C',
            lineWidth: 1
        },
        yAxis: {
            gridLineColor: '#6E797C',
            gridLineDashStyle: 'longdash',
            floor: 0,
            title: { 
                text: null
            }
        },
        plotOptions: {
            series: {
            color: '#F2BA0F',
                states: {
                    hover: {
                        enabled: false
                    }
                },
                marker: {
                    enabled: false
                 }
            }
        },
        series: [{    
            data: verbrData10sec
        }]
    });
}

function createChartGeleverdGrafiek() {
    $('#actVermogenMeterGrafiekGeleverd').highcharts({
        chart: {
            type: 'areaspline',
            style: {
                fontFamily: 'robotomedium',
                //fontSize: '14px'
            },
        },
        legend: {
            enabled: false
        },
        exporting: { enabled: false },
        credits: { enabled: false },
        title: { text: null },
        tooltip: {
            useHTML: true,
            style: {
                 padding: 3,
                 color: '#6E797C'
             },
            formatter: function() {
                var s = '<b>'+ Highcharts.dateFormat('%A %H:%M:%S', this.x) +'</b>';
                s += '<br/><span style="color: #98D023;">' + power_text + ' kW: </span>'+this.y.toFixed(3);
                return s;
            },
            backgroundColor: '#F5F5F5',
            borderColor: '#DCE1E3',
            crosshairs: [true, true],
            borderWidth: 1
        },       
        xAxis: {           
            type: 'datetime',
            lineColor: '#6E797C',
            lineWidth: 1       
        },
        yAxis: {
            gridLineColor: '#6E797C',
            gridLineDashStyle: 'longdash',
            floor: 0,
            title: { 
                text: null
            }
        },
        plotOptions: {
            series: {
            color: '#98D023',
                states: {
                    hover: {
                        enabled: false
                    }
                },
                marker: {
                    enabled: false
                 }
            }
        },
        series: [{    
            data: gelvrData10sec
        }]
    });
}

function DataLoop() {

    if ( p1TelegramMaxSpeedIsOn == true ) {
        secs = -1
    }

    secs--;
    if( secs < 0 ) { 
        secs = 10
        readJsonApiSmartMeter();
        readJsonApiStatus();
        readJsonApiHistoryDay();
        readJsonApiFinancial();
        readJsonApiWaterHistoryDay( watermeterRecords );
    }

    setTimeout( 'DataLoop()', 1000 );
    document.getElementById("timerText").innerHTML = "00:" + zeroPad(secs,2);
}

function setDynamicTitles() {

    $.getScript( "./api/v1/configuration", function( data, textStatus, jqxhr ) {
    // emode is de wijze waarop de Belgische of Nederlands slimme meter met de 1.8.1 codes omgaan
    // 0 = Nederland
    // 1 = Belgie 
    var e_mode = -1

      try {
        var jsondata = JSON.parse(data); 
        for (var j=0;  j < jsondata.length; j++){  
            // console.log( jsondata[j][0] + ' - ' + jsondata[j][1] )
            if ( jsondata[j][0] == 78) {
                if ( jsondata[j][1] == "0" ) { e_mode = 0 }
                if ( jsondata[j][1] == "1" ) { e_mode = 1 }
                break;
            }
        }

      } catch(err) {
          console.log( err)
      }

      if ( e_mode == 0 ) { // set de titels for Nederlands slimme meters
        document.getElementById("meterstand_piek_verbruik_totaal").title = "<?php echo strIdx(24);?>"
        document.getElementById("meterstand_dal_verbruik_totaal").title  = "<?php echo strIdx(23);?>"
        document.getElementById("meterstand_piek_geleverd_totaal").title = "<?php echo strIdx(26);?>"
        document.getElementById("meterstand_dal_geleverd_totaal").title  = "<?php echo strIdx(25);?>"
        document.getElementById("meterstand_piek_verbruik_dag").title    = "<?php echo strIdx(24);?>"
        document.getElementById("meterstand_dal_verbruik_dag").title     = "<?php echo strIdx(23);?>"
        document.getElementById("meterstand_piek_geleverd_dag").title    = "<?php echo strIdx(26);?>"
        document.getElementById("meterstand_dal_geleverd_dag").title     = "<?php echo strIdx(25);?>"
      }

      if ( e_mode == 1 ) { // set de titels for Belgische slimme meters
        document.getElementById("meterstand_piek_verbruik_totaal").title = "<?php echo strIdx(65);?>"
        document.getElementById("meterstand_dal_verbruik_totaal").title  = "<?php echo strIdx(66);?>"
        document.getElementById("meterstand_piek_geleverd_totaal").title = "<?php echo strIdx(67);?>"
        document.getElementById("meterstand_dal_geleverd_totaal").title  = "<?php echo strIdx(68);?>"
        document.getElementById("meterstand_piek_verbruik_dag").title    = "<?php echo strIdx(65);?>"
        document.getElementById("meterstand_dal_verbruik_dag").title     = "<?php echo strIdx(66);?>"
        document.getElementById("meterstand_piek_geleverd_dag").title    = "<?php echo strIdx(67);?>"
        document.getElementById("meterstand_dal_geleverd_dag").title     = "<?php echo strIdx(68);?>"
      }
   });

}

$(function () {
    toLocalStorage('main-menu',window.location.pathname);
    createChartGaugeVerbruik();
    createChartGaugeGeleverd();
    createChartVerbruikGrafiek();
    createChartGeleverdGrafiek();
    createChartPhaseConsuming();
    createChartPhaseProduction();
    Highcharts.setOptions({
        global: {
            useUTC: false
        },
        lang: <?php hc_language_json(); ?>
    });

    setDynamicTitles();
    screenSaver( <?php echo config_read(79);?> ); // to enable screensaver for this screen.
    // initial load
    secs = 0
    DataLoop();
    // set dynamic titles

});

</script>
</head>
<body>

<?php page_header();?>

<div class="top-wrapper-2">
    <div class="content-wrapper pad-13">
        <!-- header 2 -->
        <?php pageclock(); ?>
        <?php page_menu_header_main(0); ?>
        <?php weather_info(); ?>
    </div>
</div>

<div class="mid-section">

    <div class="left-wrapper">
        <?php page_menu(0); ?> 
        <div id="timerText" class="pos-8 color-timer"></div> 
        <?php fullscreen(); ?>
    </div> 
    
    <!-- peak costs -->
    <div class="mid-content-5 pad-41" id="peak_info" title="<?php echo strIdx( 334 );?>">
        <div class="frame-2-top">
            <span class="text-2"><?php echo strIdx( 355 );?></span>
        </div>
        <div class="frame-4-bot pad-12">

            <div class="float-left pad-12">
                <div class="frame-3-top width-260"> <!-- piek kwartier kader -->
                    <label class="text-3"><?php echo strIdx( 356 );?></label>
                </div>
                <div class="frame-2-bot width-260">
                     <label class="text-4" id="P_Q_kw">0</label>
                     <label class="text-4">kW</label>
                     <label class="text-4" id="P_Q_timestamp"></label>
                </div>
            </div> 

            <div class="float-left pad-12">
                <div class="frame-3-top width-260"> <!-- piek maand kader -->
                    <label class="text-3"><?php echo strIdx( 131 );?></label>
                </div>
                <div class="frame-2-bot width-260">
                    <label class="text-4" id="P_M_kw">0</label>
                    <label class="text-4">kW</label>
                    <label class="text-4" id="P_M_timestamp"></label>
                </div>
            </div> 
    

        </div>
     
    </div>
    <!-- end peak costs -->

    <div class="mid-content">

    <!-- links -->
        <div class="frame-2-top">
            <span class="text-2"><?php echo strIdx( 354 );?></span>
        </div>
        <div class="frame-2b-bot"> 
            <div class="pos-2"  id="actVermogenMeterVerbruik"></div>
            <div class="pos-46" id="actVermogenFaseVerbruik"></div>
            <div class="pos-47 pad-2">
                <div class="frame-3-top">
                <span id="verbruikPiekHeader" class="text-3"><?php echo strIdx( 357 );?></span>
                </div>
                <div class="frame-2-bot"> 
                    <div id="meterstand_piek_verbruik_totaal" title="fout niet gezet.">
                    <span class="fa-layers fa-fw text-4">
                        <i class="fas fa-euro-sign" data-fa-transform="left-4"></i>
                        <i class="fas fa-long-arrow-alt-up" data-fa-transform="right-4 shrink-1"></i>
                      </span>
                    <span id="verbruikPiek" class="text-4"></span><br>
                    </div>

                    <div id="meterstand_dal_verbruik_totaal" title="fout niet gezet.">
                    <span class="fa-layers fa-fw text-4">
                        <i class="fas fa-euro-sign" data-fa-transform="left-4"></i>
                        <i class="fas fa-long-arrow-alt-down" data-fa-transform="right-4 shrink-1"></i>
                      </span>
                    <span id="verbruikDal" class="text-4 "></span>
                    </div>

                    <div id="gasDiv" title="<?php echo strIdx(38);?>">
                        <i class="pad-18 text-4 fab fa-gripfire">&nbsp;</i>&nbsp;<span id="verbruikDGas" class="text-4 pad-6"></span><span class="text-4"> m<sup>3</sup></span>
                    </div>
                    
                    <div id="watermeterDiv" title="<?php echo strIdx( 73 );?>">
                        <i class="pad-18 text-4 fas fa-tint">&nbsp;</i>&nbsp;<span id="verbruikWater" class="text-4 pad-6">00000.000</span><span class="text-4"> m<sup>3</sup></span>
                    </div>

                </div>
                <div class="pad-14"></div>
                <div class="frame-3-top">
                <span id="verbruikDalHeader" class="text-3"><?php echo strIdx( 330 );?></span>
                </div>
                <div class="frame-2-bot"> 
                    <!-- <i id="verbruikPiekI" class="pad-6 text-4 far fa-sun"> -->
                    <div id="meterstand_piek_verbruik_dag" title="fout niet gezet.">
                        <span id="verbruikPiekI" class="fa-layers fa-fw text-4" >
                            <i class="fas fa-euro-sign" data-fa-transform="left-4"></i>
                            <i class="fas fa-long-arrow-alt-up" data-fa-transform="right-4 shrink-1"></i>
                          </span>
                    <span id="verbruikPiekKW" class="text-4"></span><br></div>
                    <div id="meterstand_dal_verbruik_dag" title="fout niet gezet.">
                    <span id="verbruikDalI" class="fa-layers fa-fw text-4">
                        <i class="fas fa-euro-sign" data-fa-transform="left-4"></i>
                        <i class="fas fa-long-arrow-alt-down" data-fa-transform="right-4 shrink-1"></i>
                      </span>
                    
                    <span id="verbruikDalKW" class="text-4"></span><br></div>

                    <div title="<?php echo strIdx( 39 );?>">
                        <span><i class="pad-6 text-4 fas fa-arrow-circle-up">&nbsp;</i></span><span id="peakKWConsumption" class="text-4"></span>
                    </div>
                    <div title="<?php echo strIdx( 253 );?>">
                        <span><i class="pad-6 text-4 fas fa-arrow-circle-down">&nbsp;</i></span><span id="lowKWConsumption" class="text-4"></span>
                    </div>

                </div>
                <div class="pad-14"></div>
                <div class="frame-3-top">
                <span class="text-3"><?php echo strIdx( 358 );?></span>
                </div>
                <div class="frame-2-bot"> 
                    <div title="<?php echo strIdx( 41 );?>">
                        <i class="pad-6 text-4 fa fa-bolt"></i>&nbsp;<span id="verbruikDalEnPiekKW" class="text-4 pad-6"></span><br>
                        <div id="verbruikGasDagDiv">
                            <i class="text-4 fab fa-gripfire"></i>&nbsp;<span id="verbruikGasDag" class="text-4"></span><span class="text-4"> m<sup>3</sup></span><br>
                        </div>      
                        <div id="verbruikWaterDagDiv">
                            <i class="text-4 fas fa-tint"></i>&nbsp;<span id="verbruikWaterDag" class="text-4">000000000</span><span class="text-4"> <?php echo strIdx( 363 );?></span><br>
                        </div>
                    </div>
                    <div title="<?php echo strIdx( 42 );?>">
                        <i class="text-4 fas fa-euro-sign"></i>&nbsp;<span id="verbruikKosten" class="text-4 pad-6"></span>
                    </div>
                </div>    
            </div>        
            <div class="pos-48">
                <div class="frame-3-top">
                <span class="text-3">kW <?php echo strIdx( 359 );?></span>
                </div>
                <div class="frame-2-bot"> 
                    <div id="actVermogenMeterGrafiekVerbruik" class="pos-4"></div>
                </div>        
            </div>
        </div>
    </div>
    <!-- rechts -->
    <div class="right-wrapper pad-1">
        <div class="frame-2-top">
            <span class="text-2"><?php echo strIdx( 360 );?></span>
        </div>
        <div class="frame-2b-bot"> 
            <div class="pos-2" id="actVermogenMeterGeleverd"></div>
            <div class="pos-46" id="actVermogenFaseLevering"></div>
            <div class="pos-47 pad-2">
                <div class="frame-3-top">
                <span id="geleverdPiekHeader" class="text-3"><?php echo strIdx( 357 );?></span>
                </div>
                <div class="frame-2-bot"> 
                    <div id="meterstand_piek_geleverd_totaal" title="fout niet gezet.">
                
                    <span class="fa-layers fa-fw text-4">
                        <i class="fas fa-euro-sign" data-fa-transform="left-4"></i>
                        <i class="fas fa-long-arrow-alt-up" data-fa-transform="right-4 shrink-1"></i>
                      </span>
                    
                    <span id="geleverdPiek" class="text-4"></span>
                    </div>
                    <div id="meterstand_dal_geleverd_totaal" title="fout niet gezet.">
                    <span class="fa-layers fa-fw text-4">
                        <i class="fas fa-euro-sign" data-fa-transform="left-4"></i>
                        <i class="fas fa-long-arrow-alt-down" data-fa-transform="right-4 shrink-1"></i>
                      </span>
                    
                    <span id="geleverdDal" class="text-4 "></span>
                </div>

                </div>
                <div class="pad-14"></div>
                <div class="frame-3-top">
                <span id="geleverdDalHeader" class="text-3"><?php echo strIdx( 330 );?></span>
                </div>
                <div class="frame-2-bot"> 
                    <div id="meterstand_piek_geleverd_dag" title="fout niet gezet.">
                        <span id="geleverdPiekI" class="fa-layers fa-fw text-4">
                            <i class="fas fa-euro-sign" data-fa-transform="left-4"></i>
                            <i class="fas fa-long-arrow-alt-up" data-fa-transform="right-4 shrink-1"></i>
                          </span>
                        <span id="geleverdPiekKW" class="text-4"></span><br>
                    </div>
                    
                    <div id="meterstand_dal_geleverd_dag" title="fout niet gezet.">
                        <span id="geleverdDalI" class="fa-layers fa-fw text-4">
                            <i class="fas fa-euro-sign" data-fa-transform="left-4"></i>
                            <i class="fas fa-long-arrow-alt-down" data-fa-transform="right-4 shrink-1"></i>
                          </span>
                        <span id="geleverdDalKW" class="text-4"></span><br>
                    </div>

                    <div title="<?php echo strIdx( 254 );?>">
                        <span><i class="pad-6 text-4 fas fa-arrow-circle-up">&nbsp;</i></span><span id="peakKWProduction" class="text-4">x</span>
                    </div>
                    <div title="<?php echo strIdx( 255 );?>">
                        <span><i class="pad-6 text-4 fas fa-arrow-circle-down">&nbsp;</i></span><span id="lowKWProduction" class="text-4">x</span>
                    </div>

                </div>
                <div class="pad-14"></div>
                <div class="frame-3-top">
                      <span class="text-3"><?php echo strIdx( 358 );?></span>
                </div>
                <div class="frame-2-bot"> 
                <div title="<?php echo strIdx( 45 );?>">
                    <i class="pad-6 text-4 fa fa-bolt"></i>&nbsp;<span id="geleverdDalEnPiekKW" class="text-4"></span><br>
                </div>
                <div title="<?php echo strIdx( 46 );?>">
                    <i class="pad-6 text-4 fas fa-euro-sign"></i>&nbsp;<span id="geleverdKosten" class="text-4"></span>
                </div>
                </div>
            </div>
            <div class="pos-48">
                <div class="frame-3-top">
                <span class="text-3">kW <?php echo strIdx( 360 );?></span>
                </div>
                <div class="frame-2-bot"> 
                    <div id="actVermogenMeterGrafiekGeleverd" class="pos-4"></div>
                </div>
            </div>
        </div>
        <!-- <div class="pos-46x" id="actVermogenFaseLevering"></div> -->
    </div>
</div>

<script>


if ( hidePeakKw == true ){
    $('#peak_info').hide();
} else {
    $('#peak_info').show();
}

if ( hideWaterUi == true ){
    $('#verbruikWaterDagDiv').hide();
    $('#watermeterDiv').hide();
} else {
    $('#verbruikWaterDagDiv').show();
    $('#watermeterDiv').show();
}

if ( hideGaSUi == true ){
    $('#gasDiv').hide();
    $('#verbruikGasDagDiv').hide();
} else {
    $('#gasDiv').show();
    $('#verbruikGasDagDiv').show();
}

if ( p1TelegramMaxSpeedIsOn == true ){ 
    $('#timerText').hide();
} else {
    $('#timerText').show();
}

</script>
</body>
</html>