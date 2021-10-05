<?php
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php'; 
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/textlib.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';

if ( checkDisplayIsActive(22) == false) { return; }
?> 
<!doctype html>
<html lang="nl">
<head>
<meta name="robots" content="noindex">
<title>P1monitor informatie</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css"/>
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/highstock-link/highstock.js"></script>
<script src="./js/highstock-link/highcharts-more.js"></script>
<script src="./js/highstock-link/modules/solid-gauge.js"></script>
<script src="./js/hc-global-options.js"></script>
<script src="./js/p1mon-util.js"></script>

<script>
//var initloadtimer;
var CPUload                   = 0;
var Ramdiskload               = 0;
var Ramload                   = 0;
var CPUtemperature            = 0;
var soundPlayed               = false;
var soundIsOn                 = true;

var showHeatingInfo                  = <?php if ( config_read( 46  ) == 1 ) { echo "true;"; } else { echo "false;"; } echo"\n";?>
var showUDPbroadcastInfo             = <?php if ( config_read( 55  ) == 1 ) { echo "true;"; } else { echo "false;"; } echo"\n";?>
var showWatermeterInfo               = <?php if ( config_read( 102 ) == 1 ) { echo "true;"; } else { echo "false;"; } echo"\n";?>
var showProductionPowerS0Info        = <?php if ( config_read( 129 ) == 1 ) { echo "true;"; } else { echo "false;"; } echo"\n";?>
var showProductionPowerSolarEdgeInfo = <?php if ( config_read( 147 ) == 1 ) { echo "true;"; } else { echo "false;"; } echo"\n";?>
var p1TelegramMaxSpeedIsOn           = <?php if ( config_read( 155 ) == 1 ) { echo "true;"; } else { echo "false;"; } echo"\n";?> 

function PlaySound() {
    if ( soundIsOn === true ) {
        var sound = document.getElementById("audio");
        sound.play()
    }
}       

function soundOn() {
    //console.log("on")
    soundIsOn = true
    $('#sound_off').hide();
    $('#sound_on').show();
    toLocalStorage('info-sound-on',true); 
}

function soundOff() {
    //console.log("off")
    soundIsOn = false
    $('#sound_on').hide();
    $('#sound_off').show();
    toLocalStorage('info-sound-on',false); 
}

function readJsonApiConfiguration(){ 
    $.getScript( "./api/v1/configuration", function( data, textStatus, jqxhr ) {
      try {
        var jsonarr = JSON.parse(data); 
        for (var j=0;  j<jsonarr.length; j++){   
                switch(jsonarr[j][0]) {
                    case 0:
                        $('#sy4v').text( jsonarr[j][1] );
                        $('#sy4t').text( jsonarr[j][2] );
                    case 11:
                        $('#ne7v').text( jsonarr[j][1] );
                        $('#ne7t').text( jsonarr[j][2] );
                    case 128:
                        $('#sy10v').text( jsonarr[j][1] );
                        $('#sy10t').text( jsonarr[j][2] );
                    case 133:
                        $('#sy11v').text(jsonarr[j][1]);
                        $('#sy11t').text(jsonarr[j][2]);  
                    default:
                        break;
            }
        }
      } catch(err) {
          console.log( err );
      }
   });
}

function readJsonApiStatus(){ 
    $.getScript( "./api/v1/status", function( data, textStatus, jqxhr ) {
      try {
        var jsonarr = JSON.parse(data); 
        
        if ( jsonarr[45][1] == '0') {
                hideStuff('serial_ok'); 
                showStuff('serial_nok');
                if(!soundPlayed) {
                    soundPlayed = true;
                    PlaySound();
                    console.log("playing")
                }
            } else {
                hideStuff('serial_nok'); 
                showStuff('serial_ok');
                if(soundPlayed) soundPlayed = false; // reset
            }
                   
        for (var j=0;  j<jsonarr.length; j++){   
                switch(jsonarr[j][0]) {
                    case 5:
                        $('#pr1v').text(jsonarr[j][1]);
                        $('#pr1t').text(jsonarr[j][2]);
                    break;
                    case 6:   
                        $('#pr2v').text(jsonarr[j][1]);
                        $('#pr2t').text(jsonarr[j][2]);
                    break;
                    case 7:
                        $('#db2v').text(jsonarr[j][1]);
                        $('#db2t').text(jsonarr[j][2]);
                    break;
                    case 12:
                        $('#db3v').text(jsonarr[j][1]);
                        $('#db3t').text(jsonarr[j][2]);
                        break;
                    case 13:
                        $('#db4v').text(jsonarr[j][1]);
                        $('#db4t').text(jsonarr[j][2]);
                        break;
                    case 14:
                        $('#db5v').text(jsonarr[j][1]);
                        $('#db5t').text(jsonarr[j][2]);
                        break;
                    case 15:
                        $('#db6v').text(jsonarr[j][1]);
                        $('#db6t').text(jsonarr[j][2]);
                        break;
                    case 16:
                        $('#db1v').text(jsonarr[j][1]);
                        $('#db1t').text(jsonarr[j][2]);
                        break;
                    case 17:
                        $('#pr3v').text(jsonarr[j][1]);
                        $('#pr3t').text(jsonarr[j][2]);
                        break;
                    case 18:
                        try {
                            CPUload = jsonarr[j][1]; 
                            point = $('#cpuload').highcharts().series[0].points[0];
                            point.update(parseFloat(CPUload), true, true, true);  
                        } catch(err) {}            
                        break;
                    case 19:
                        $('#sy1v').text(jsonarr[j][1]);
                        $('#sy1t').text(jsonarr[j][2]);
                        break;
                    case 20:
                        if (jsonarr[j][1].length === 0) {
                            hideStuff('ne5b');
                            hideStuff('ne5v');
                            hideStuff('ne5t');
                        } else {
                            $('#ne5v').text(jsonarr[j][1]);
                            $('#ne5t').text(jsonarr[j][2]);
                        }
                        break;
                    case 21:
                        try {
                            Ramdiskload = jsonarr[j][1]; 
                            point = $('#ramdiskload').highcharts().series[0].points[0];
                            point.update(parseFloat(Ramdiskload), true, true, true);  
                        } catch(err) {}    
                        break;
                    case 22:
                        $('#sy2v').text(jsonarr[j][1]);
                        $('#sy2t').text(jsonarr[j][2]);
                        break;
                    case 23:
                        if (jsonarr[j][1].length === 0) {
                            hideStuff('ne4b');
                            hideStuff('ne4v');
                            hideStuff('ne4t');
                        } else {
                            $('#ne4v').text(jsonarr[j][1]);
                            $('#ne4t').text(jsonarr[j][2]);
                        }
                        break;
                    case 24:
                        if (jsonarr[j][1].length === 0) {
                            hideStuff('ne1b');
                            hideStuff('ne1v');
                            hideStuff('ne1t');
                        } else {
                            $('#ne1v').text(jsonarr[j][1]);
                            $('#ne1t').text(jsonarr[j][2]);
                        }
                        break;
                    case 25:
                        $('#sy3v').text(jsonarr[j][1]);
                        $('#sy3t').text(jsonarr[j][2]);
                        break;
                    case 26:
                        $('#ne2v').text(jsonarr[j][1]);
                        $('#ne2t').text(jsonarr[j][2]);
                        break;
                    case 27:
                        $('#ne3v').text(jsonarr[j][1]);
                        $('#ne3t').text(jsonarr[j][2]);
                        break;
                    case 28:
                        if (jsonarr[j][1].length === 0) {
                            hideStuff('ne6b');
                            hideStuff('ne6v');
                            hideStuff('ne6t');
                        } else {
                            $('#ne6v').text(jsonarr[j][1]);
                            $('#ne6t').text(jsonarr[j][2]);
                        }
                        break;
                case 29:
                    $('#db7v').text(jsonarr[j][1]);
                    $('#db7t').text(jsonarr[j][2]);
                    break; 
                case 31:
                    try {
                        Ramload = jsonarr[j][1];
                        point = $('#ramload').highcharts().series[0].points[0];
                        point.update(parseFloat(Ramload), true, true, true);  
                    } catch(err) {}    
                    break; 
                case 41:
                    $('#db8v').text(jsonarr[j][1]);
                    $('#db8t').text(jsonarr[j][2]);
                    break;
                case 42:
                    $('#ne8v').text(jsonarr[j][1]);
                    $('#ne8t').text(jsonarr[j][2]);
                    break;
                case 45:
                    $('#db9v').text(jsonarr[j][1]);
                    $('#db9t').text(jsonarr[j][2]);
                    break;  
                case 49:
                    $('#db10v').text(jsonarr[j][1]);
                    $('#db10t').text(jsonarr[j][2]);
                    break;
                case 51:
                    $('#sy5v').text(jsonarr[j][1]);
                    $('#sy5t').text(jsonarr[j][2]);
                    break;
                case 52:
                    $('#sy6v').text(jsonarr[j][1]);
                    $('#sy6t').text(jsonarr[j][2]);
                    break;
                case 53:
                    $('#sy7v').text(jsonarr[j][1]);
                    $('#sy7t').text(jsonarr[j][2]);
                    break;
                case 55:
                    $('#sy9v').text(jsonarr[j][1]);
                    $('#sy9t').text(jsonarr[j][2]);
                    break;
                case 56:
                    $('#pr4v').text(jsonarr[j][1]);
                    $('#pr4t').text(jsonarr[j][2]); 
                    break;  
                case 57:
                    $('#db11v').text(jsonarr[j][1]);
                    $('#db11t').text(jsonarr[j][2]);
                    break;
                case 58:
                    $('#db12v').text(jsonarr[j][1]);
                    $('#db12t').text(jsonarr[j][2]);
                    break;
                case 60:
                    $('#db13v').text(jsonarr[j][1]);
                    $('#db13t').text(jsonarr[j][2]);
                    break;
                case 63:
                    $('#db14v').text(jsonarr[j][1]);
                    $('#db14t').text(jsonarr[j][2]);
                    break;
                case 65:
                    $('#pr5v').text(jsonarr[j][1]);
                    $('#pr5t').text(jsonarr[j][2]);
                    break;
                case 69:
                        try {
                            CPUtemperature = jsonarr[j][1]; 
                            point = $('#cputemp').highcharts().series[0].points[0];
                            point.update(parseFloat(CPUtemperature), true, true, true); 
                        } catch(err) {}    
                        break;
                case 70:
                    $('#pr6v').text(jsonarr[j][1]);
                    $('#pr6t').text(jsonarr[j][2]);
                    break;
                case 71:
                    $('#db15v').text(jsonarr[j][1]);
                    $('#db15t').text(jsonarr[j][2]);
                    break;
                case 72:
                    if (jsonarr[j][1].length === 0) {
                        hideStuff('ne9b');
                        hideStuff('ne9v');
                        hideStuff('ne9t');
                    } else {
                        $('#ne9v').text(jsonarr[j][1]);
                        $('#ne9t').text(jsonarr[j][2]);
                    }
                    break;
                case 73:
                    if (jsonarr[j][1].length === 0) {
                        hideStuff('ne10b');
                        hideStuff('ne10v');
                        hideStuff('ne10t');
                    } else {
                        $('#ne10v').text(jsonarr[j][1]);
                        $('#ne10t').text(jsonarr[j][2]);
                    }
                    break;
                case 82:
                    $('#db16v').text(jsonarr[j][1]);
                    $('#db16t').text(jsonarr[j][2]);
                    break;
                case 84:
                    $('#db17v').text(jsonarr[j][1]);
                    $('#db17t').text(jsonarr[j][2]);
                    break;
                case 88:
                    $('#db18v').text(jsonarr[j][1]);
                    $('#db18t').text(jsonarr[j][2]);
                    break;
                case 90:
                    $('#db19v').text(jsonarr[j][1]);
                    $('#db19t').text(jsonarr[j][2]);
                    break;
                case 93:
                    $('#db20v').text(jsonarr[j][1]);
                    $('#db20t').text(jsonarr[j][2]);
                    break;
                case 94:
                    $('#db21v').text(jsonarr[j][1]);
                    $('#db21t').text(jsonarr[j][2]);
                    break;
                case 95:
                    $('#pr7v').text(jsonarr[j][1]);
                    $('#pr7t').text(jsonarr[j][2]);
                    break;
                case 96:
                    $('#db22v').text(jsonarr[j][1]);
                    $('#db22t').text(jsonarr[j][2]);
                    break;
                case 98:
                    $('#pr8v').text(jsonarr[j][1]);
                    $('#pr8t').text(jsonarr[j][2]);
                 case 99:
                    $('#pr9v').text(jsonarr[j][1]);
                    $('#pr9t').text(jsonarr[j][2]);
                    break;
                case 108:
                    $('#pr10v').text(jsonarr[j][1]);
                    $('#pr10t').text(jsonarr[j][2]);
                    break;
                case 109:
                    $('#db23v').text(jsonarr[j][1]);
                    $('#db23t').text(jsonarr[j][2]);
                    break;
                case 111:
                    $('#db24v').text(jsonarr[j][1]);
                    $('#db24t').text(jsonarr[j][2]);
                    break;  
                default:
                    break;
            }
        }


      } catch(err) {
          console.log( err );
      }
   });
}

function readTextMeterTelegram(){ 
    $('#slimmemeter').load( "/txt/txt-meter.php", function( response, status, xhr ) {
        if ( status == "error" ) {
            $("#slimmemeter").html('Slimme meter data niet beschikbaar.');
        }
    });  
}

function getFormattedDate() {
    var date = new Date();

    var month = date.getMonth() + 1;
    var day = date.getDate();
    var hour = date.getHours();
    var min = date.getMinutes();
    var sec = date.getSeconds();

    month = (month < 10 ? "0" : "") + month;
    day = (day < 10 ? "0" : "") + day;
    hour = (hour < 10 ? "0" : "") + hour;
    min = (min < 10 ? "0" : "") + min;
    sec = (sec < 10 ? "0" : "") + sec;

    var str = date.getFullYear() + "-" + month + "-" + day + " " +  hour + ":" + min + ":" + sec;

    return str;
}


function createChartCpuTemperature() {    
    $('#cputemp').highcharts({

    chart: {
        type: 'solidgauge',
        width: 300,
        height: 155,
        margin: [-10, 0, 0, 0]
    },
    title: null,
    credits: { enabled: false },
    pane: {
        center: ['50%', '85%'],
        size: '150%',
        startAngle: -90,
        endAngle: 90,
        background: {
             backgroundColor: '#F5F5F5',
            innerRadius: '60%',
            outerRadius: '100%',
            shape: 'arc'
        }
       
    },
    tooltip: {
        enabled: false
    },
    yAxis: {
        max: 100,
        min: 0,
        stops: [
            [0.1, '#55BF3B'], // green
            [0.7, '#DDDF0D'], // yellow
            [0.8, '#DF5353']  // red
        ],
        lineWidth: 0,
        minorTickInterval: null,
        tickPixelInterval: 400,
        tickWidth: 0,
        title: {
            y: -70
        },
        labels: {
            style: {
                fontWeight: 'bold',
                fontSize: '13px'       
            },
            y: 16
        }
    },
    series: [{
        animation: true,
        dataLabels: {
            format: '{point.y:.2f}°C',
            borderColor: '#384042',
            padding: 4,
            borderRadius: 5,
            verticalAlign: 'center',
            y: -30,
            color: "#6E797C",
            style: {
                fontWeight: 'bold',
                fontSize: '13px'       
            }
        },
        data: [{
            y: parseFloat(CPUtemperature)
        }]
    }]
});
}

function createChartCpuLoad() {    
    $('#cpuload').highcharts({

    chart: {
        type: 'solidgauge',
        width: 300,
        height: 155,
        margin: [-10, 0, 0, 0]
    },
    title: null,
    credits: { enabled: false },
    pane: {
        center: ['50%', '85%'],
        size: '150%',
        startAngle: -90,
        endAngle: 90,
        background: {
             backgroundColor: '#F5F5F5',
            innerRadius: '60%',
            outerRadius: '100%',
            shape: 'arc'
        }
       
    },
    tooltip: {
        enabled: false
    },
    yAxis: {
        
        max: 100,
        min: 0,
        stops: [
            [0.1, '#55BF3B'], // green
            [0.5, '#DDDF0D'], // yellow
            [0.9, '#DF5353']  // red
        ],
        lineWidth: 0,
        minorTickInterval: null,
        tickPixelInterval: 400,
        tickWidth: 0,
        title: {
            y: -70
        },
        labels: {
            style: {
                fontWeight: 'bold',
                fontSize: '13px'       
            },
            y: 16
        }
    },
    series: [{
        animation: true,
        dataLabels: {
            format: '{point.y:.1f} %',
            borderColor: '#384042',
            padding: 4,
            borderRadius: 5,
            verticalAlign: 'center',
            y: -30,
            color: "#6E797C",
            style: {
                fontWeight: 'bold',
                fontSize: '13px'       
            }
        },
        data: [{
            y: parseFloat(CPUload)
        }]
    }]
});
}

function createChartRamdiskLoad() {    
    $('#ramdiskload').highcharts({

    chart: {
        type: 'solidgauge',
        width: 300,
        height: 155,
        margin: [-10, 0, 0, 0]
    },
    title: null,
    credits: { enabled: false },
    pane: {
        center: ['50%', '85%'],
        size: '150%',
        startAngle: -90,
        endAngle: 90,
        background: {
             backgroundColor: '#F5F5F5',
            innerRadius: '60%',
            outerRadius: '100%',
            shape: 'arc'
        }
       
    },
    tooltip: {
        enabled: false
    },
    yAxis: {
        
        max: 100,
        min: 0,
        stops: [
            [0.1, '#55BF3B'], // green
            [0.5, '#DDDF0D'], // yellow
            [0.9, '#DF5353']  // red
        ],
        lineWidth: 0,
        minorTickInterval: null,
        tickPixelInterval: 400,
        tickWidth: 0,
        title: {
            y: -70
        },
        labels: {
            style: {
                fontWeight: 'bold',
                fontSize: '13px'       
            },
            y: 16
        }
    },
    series: [{
        animation: true,
        dataLabels: {
            format: '{point.y:.1f} %',
            borderColor: '#384042',
            padding: 4,
            borderRadius: 5,
            verticalAlign: 'center',
            y: -30,
            color: "#6E797C",
            style: {
                fontWeight: 'bold',
                fontSize: '13px'       
            }
        },
        data: [{
            y: parseFloat(Ramdiskload)
        }]
    }]
});
}

function createChartRamLoad() {    
    $('#ramload').highcharts({

    chart: {
        type: 'solidgauge',
        width: 300,
        height: 155,
        margin: [-10, 0, 0, 0]
    },
    title: null,
    credits: { enabled: false },
    pane: {
        center: ['50%', '85%'],
        size: '150%',
        startAngle: -90,
        endAngle: 90,
        background: {
             backgroundColor: '#F5F5F5',
            innerRadius: '60%',
            outerRadius: '100%',
            shape: 'arc'
        }
       
    },
    tooltip: {
        enabled: false
    },
    yAxis: {
        
        max: 100,
        min: 0,
        stops: [
            [0.1, '#55BF3B'], // green
            [0.90, '#DDDF0D'], // yellow
            [0.97, '#DF5353']  // red
        ],
        lineWidth: 0,
        minorTickInterval: null,
        tickPixelInterval: 400,
        tickWidth: 0,
        title: {
            y: -70
        },
        labels: {
            style: {
                fontWeight: 'bold',
                fontSize: '13px'       
            },
            y: 16
        }
    },
    series: [{
        animation: true,
        dataLabels: {
            format: '{point.y:.1f} %',
            borderColor: '#384042',
            padding: 4,
            borderRadius: 5,
            verticalAlign: 'center',
            y: -30,
            color: "#6E797C",
            style: {
                fontWeight: 'bold',
                fontSize: '13px'       
            }
        },
        data: [{
            y: parseFloat(Ramload)
        }]
    }]
});
}

function DataLoop() {
    readJsonApiStatus();
    readJsonApiConfiguration();
    readTextMeterTelegram();
    if ( p1TelegramMaxSpeedIsOn == true ) {
        setTimeout( 'DataLoop()', 1000 );
    } else {
        setTimeout( 'DataLoop()', 2000 );
    }

}

$(function () {

    if ( getLocalStorage('info-sound-on') === 'true' ) {
        //console.log("storage is on")
        soundIsOn = true;
        $('#sound_on').show();
        $('#sound_off').hide();
    } else {
        //console.log("storage is off")
        soundIsOn = false;
        $('#sound_on').hide();
        $('#sound_off').show();
    }
    createChartCpuLoad();
    createChartCpuTemperature();
    createChartRamdiskLoad();
    createChartRamLoad();
    screenSaver( <?php echo config_read(79);?> ); // to enable screensaver for this screen.
    DataLoop();
});

</script>
</head>
<body>
<audio id="audio" src="./sound/beep-04.wav"></audio>

<?php page_header();?>

<div class="top-wrapper-2">
    <div class="content-wrapper pad-13">
       <!-- header 2 -->
       <?php pageclock(); ?>
       &nbsp; &nbsp;
       <?php weather_info(); ?>
    </div>
</div>


<div class="mid-section">
    <div class="left-wrapper">
        <?php page_menu(3); ?>
    </div> 
    
    <div class="mid-content">
    <!-- links -->
        
    </div>
    <!-- rechts -->
    
    <div class="right-wrapper pad-1">
    
        <div class="mid-content-2">
            <!-- linker kant van mid sectie --> 
            <div class="pos-14"> 
                 <div class="frame-2-top">
                    <span class="text-2">database</span>
                </div>
                  <div class="frame-2-bot">        
                     <div id="db1t" class="text-9"></div><div id="db1v" class="text-9"></div><br>
                     <div id="db2t" class="text-9"></div><div id="db2v" class="text-9"></div><br>
                     <div id="db3t" class="text-9"></div><div id="db3v" class="text-9"></div><br>
                     <div id="db4t" class="text-9"></div><div id="db4v" class="text-9"></div><br>
                     <div id="db5t" class="text-9"></div><div id="db5v" class="text-9"></div><br>
                     <div id="db6t" class="text-9"></div><div id="db6v" class="text-9"></div><br>
                    <div id="db9t" class="text-9"></div><div id="db9v" class="text-9"></div><br>
                     <div id="db7t" class="text-9"></div><div id="db7v" class="text-9"></div><br>
                     <div id="db8t" class="text-9"></div><div id="db8v" class="text-9"></div><br>
                    <div id="db10t" class="text-9"></div><div id="db10v" class="text-9"></div><br>
                    <div id="heating">
                        <div id="db11t" class="text-9"></div><div id="db11v" class="text-9"></div><br>
                        <div id="db12t" class="text-9"></div><div id="db12v" class="text-9"></div><br>
                    </div>
                    <div id="db13t" class="text-9"></div><div id="db13v" class="text-9"></div><br>
                    <div id="db14t" class="text-9"></div><div id="db14v" class="text-9"></div><br>
                    <div id="udpBroadcast">
                        <div id="db15t" class="text-9"></div><div id="db15v" class="text-9"></div><br>
                    </div>
                    <div id="db16t" class="text-9"></div><div id="db16v" class="text-9"></div><br>
                    <div id="db17t" class="text-9"></div><div id="db17v" class="text-9"></div><br>
                    <div id="db18t" class="text-9"></div><div id="db18v" class="text-9"></div><br>
                    <div id="watermeter">
                        <div id="db19t" class="text-9"></div><div id="db19v" class="text-9"></div><br>
                    </div>
                    <div id="db20t" class="text-9"></div><div id="db20v" class="text-9"></div><br>
                    <div id="db21t" class="text-9"></div><div id="db21v" class="text-9"></div><br>
                    <div id="db22t" class="text-9"></div><div id="db22v" class="text-9"></div><br>
                    <div id="powerProductionS0">
                        <div id="db23t" class="text-9"></div><div id="db23v" class="text-9"></div><br>
                    </div>
                    <div id="powerProductionSolarEdge">
                        <div id="db24t" class="text-9"></div><div id="db24v" class="text-9"></div><br>
                    </div>
                 </div>
                 <br>
                 <div class="frame-2-top">
                    <span class="text-2">processen</span>
                </div>
                  <div class="frame-2-bot">        
                     <div id="pr1t" class="text-9"></div><div id="pr1v" class="text-9"></div><br>
                     <div id="pr2t" class="text-9"></div><div id="pr2v" class="text-9"></div><br>
                     <div id="pr3t" class="text-9"></div><div id="pr3v" class="text-9"></div><br>
                    <div id="pr4t" class="text-9"></div><div id="pr4v" class="text-9"></div><br>
                    <div id="pr5t" class="text-9"></div><div id="pr5v" class="text-9"></div><br>
                    <div id="pr6t" class="text-9"></div><div id="pr6v" class="text-9"></div><br>
                    <div id="pr7t" class="text-9"></div><div id="pr7v" class="text-9"></div><br>
                    <div id="pr8t" class="text-9"></div><div id="pr8v" class="text-9"></div><br>
                    <div id="pr9t" class="text-9"></div><div id="pr9v" class="text-9"></div><br>
                    <div id="pr10t" class="text-9"></div><div id="pr10v" class="text-9"></div><br>
                 </div>
                 <br>
                     <div class="frame-2-top">
                    <span class="text-2">systeem</span>
                    <div title="<?php strIdx( 98 );?>" class="pos-43">
                        <button onclick="copyClipboard('systeem')" class="input-4 pos-31 cursor-pointer">
                            <i class="color-menu fas fa-clipboard"></i>&nbsp;<span class="color-menu">clipboard</span>
                        </button>
                   </div>
                </div>
                  <div id="systeem" class="frame-2-bot">
                    <div id="sy1t" class="text-9"></div><div id="sy1v" class="text-9"></div><br>
                    <div id="sy2t" class="text-9"></div><div id="sy2v" class="text-9"></div><br>
                    <div id="sy3t" class="text-9"></div><div id="sy3v" class="text-9"></div><br>
                    <div id="sy4t" class="text-9"></div><div id="sy4v" class="text-9"></div><br>
                    <div id="sy10t" class="text-9"></div><div id="sy10v" class="text-9"></div><br>
                    <div id="sy11t" class="text-9"></div><div id="sy11v" class="text-9"></div><br>
                    <div id="sy5t" class="text-9"></div><div id="sy5v" class="text-9"></div><br>
                    <div id="sy6t" class="text-9"></div><div id="sy6v" class="text-9"></div><br>
                    <div id="sy7t" class="text-9"></div><div id="sy7v" class="text-9"></div><br>
                    <div id="sy9t" class="text-9"></div><div id="sy9v" class="text-9"></div><br>
                 </div>
                 <br>
                 <div class="frame-2-top">
                    <span class="text-2">netwerk</span>
                </div>
                  <div class="frame-2-bot">
                     <div id="ne1t" class="text-9"></div><div id="ne1v" class="text-9"></div><div><br id="ne1b"></div>
                     <div id="ne2t" class="text-9"></div><div id="ne2v" class="text-9"></div><br>
                     <div id="ne3t" class="text-9"></div><div id="ne3v" class="text-9"></div><br>
                     <div id="ne4t" class="text-9"></div><div id="ne4v" class="text-9"></div><div><br id="ne4b"></div>
                    <div id="ne5t" class="text-9"></div><div id="ne5v" class="text-9"></div><div><br id="ne5b"></div>
                    <div id="ne9t" class="text-9"></div><div id="ne9v" class="text-9"></div><div><br id="ne9b"></div>
                     <div id="ne6t" class="text-9"></div><div id="ne6v" class="text-9"></div><div><br id="ne6b"></div>
                    <div id="ne7t" class="text-9"></div><div id="ne7v" class="text-9"></div><div><br id="ne7b"></div>
                    <div id="ne8t" class="text-9"></div><div id="ne8v" class="text-9"></div><div><br id="ne8b"></div>
                    <div id="ne10t" class="text-9"></div><div id="ne10v" class="text-9"></div><div><br id="ne10b"></div>
                 </div>
                 
                 <br>
                 <div class="frame-2-top">
                    <span class="text-2">slimme meter</span>
                    <div title="<?php strIdx( 98 );?>" class="pos-43">
                        <button onclick="copyClipboard('slimmemeter')" class="input-4 pos-31 cursor-pointer">
                            <i class="color-menu fas fa-clipboard"></i>&nbsp;<span class="color-menu">clipboard</span>
                        </button>
                   </div>
                </div>
                  <div class="frame-2-bot">        
                     <div id="slimmemeter" class="text-9">
                     <br>
                    </div>
                 </div>
                 
                 
             </div> 
              <!-- rechter kant van mid sectie -->
              <div class="pos-15">
                 
                 <div class="frame-2-top">
                    <span class="text-2">P1 poort status</span>
                </div>
                  <div class="frame-2-bot">
                      <div class="pad-11" id="p1status" title="<?php strIdx(2);?>">
                        
                        <div style="display:none" id="serial_ok" >
                            <label  class="float-left text-11" >&nbsp;&nbsp;&nbsp;in orde&nbsp;</label>
                            <i      class="float-left color-ok fa fa-2x fa-check-square" ></i>
                        </div>
                        
                        <div style="display:none" id="serial_nok">
                            <label class="float-left text-11" >geen data&nbsp;</label>
                            <i     class="float-left color-error fa fa-2x fa-exclamation-triangle"></i>
                        </div>

                        <div title="geluid uit" onclick="soundOn()" id="sound_off" style="display:none">
                            <span class="fa-layers fa-fw fa-2x color-menu cursor-pointer">
                                <i class="fas fa-ban"></i>
                                <i class="fas fa-volume-up color-error" data-fa-transform="shrink-6 right-0"></i>
                            </span>
                        </div>

                        <div title="geluid aan" onclick="soundOff()" id="sound_on" style="display:none">
                            <span class="fa-layers fa-fw fa-2x color-menu cursor-pointer">
                                <i class="fas fa-volume-up" data-fa-transform="shrink-0 right-2"></i>
                            </span>
                        </div>

                    </div>
                  </div>
                  <br>
                 
                  <div class="frame-2-top">
                    <span class="text-2">CPU belasting</span>
                </div>
                  <div class="frame-2-bot">
                      <div id="cpuload"></div>
                  </div>
                <br>
                <div class="frame-2-top">
                    <span class="text-2">CPU temperatuur</span>
                </div>
                  <div class="frame-2-bot">
                      <div id="cputemp"></div>
                  </div>
                <br>
                  <div class="frame-2-top">
                    <span class="text-2">database belasting</span>
                </div>
                  <div class="frame-2-bot">
                      <div id="ramdiskload"></div>
                  </div>
                  <br>
                  <div class="frame-2-top">
                    <span class="text-2">geheugen belasting</span>
                </div>
                  <div class="frame-2-bot">
                      <div id="ramload"></div>
                  </div>        
                      
                      
              </div>
        </div>
    </div>
</div>
<script>

if ( showHeatingInfo == false ){
    $('#heating').hide();
}

if ( showUDPbroadcastInfo == false ){
    $('#udpBroadcast').hide();
}

if ( showWatermeterInfo  == false ){
    $('#watermeter').hide();
}

if ( showProductionPowerS0Info == false ){
    $('#powerProductionS0').hide();
}

if ( showProductionPowerSolarEdgeInfo == false ){
    $('#powerProductionSolarEdge').hide();
}

</script>
</body>
</html>