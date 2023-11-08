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
<html lang="<?php echo strIdx( 531 )?>">
<head>
<meta name="robots" content="noindex">
<title>P1-monitor <?php echo strIdx( 114 )?></title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css">
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css">

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/highstock-link/highstock.js"></script>
<script src="./js/highstock-link/highcharts-more.js"></script>
<script src="./js/highstock-link/modules/solid-gauge.js"></script>
<script src="./js/highstock-link/modules/accessibility.js"></script>
<script src="./js/hc-global-options.js"></script>
<script src="./js/p1mon-util.js"></script>

<script>

const on_text   = "<?php echo strIdx( 192 );?>";
const off_text  = "<?php echo strIdx( 193 );?>";
const yes_text  = "<?php echo strIdx( 606 );?>";
const no_text   = "<?php echo strIdx( 607 );?>";

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
var showDynamicsPricingInfo          = <?php if ( config_read( 204 ) > 0  ) { echo "true;"; } else { echo "false;"; } echo"\n";?>

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
                    case 11:
                        $('#ne7v').text( jsonarr[j][1] );
                    case 128:
                        $('#sy10v').text( jsonarr[j][1] );
                    case 133:
                        $('#sy11v').text(jsonarr[j][1]);
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

        for (var j=0;  j<jsonarr.length; j++){   
                switch(jsonarr[j][0]) {
                    case 5:
                        $('#pr1v').text(jsonarr[j][1]);
                    break;
                    case 6:   
                        $('#pr2v').text(jsonarr[j][1]);
                    break;
                    case 7:
                        $('#db2v').text(jsonarr[j][1]);
                    break;
                    case 12:
                        $('#db3v').text(jsonarr[j][1]);
                        break;
                    case 13:
                        $('#db4v').text(jsonarr[j][1]);
                        break;
                    case 14:
                        $('#db5v').text(jsonarr[j][1]);
                        break;
                    case 15:
                        $('#db6v').text(jsonarr[j][1]);
                        break;
                    case 16:
                        $('#db1v').text(jsonarr[j][1]);
                        break;
                    case 17:
                        $('#pr3v').text(jsonarr[j][1]);
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
                        break;
                    case 20:
                        if (jsonarr[j][1].length === 0) {
                            hideStuff('ne5b');
                            hideStuff('ne5v');
                            hideStuff('ne5t');
                        } else {
                            $('#ne5v').text(jsonarr[j][1]);
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
                        break;
                    case 23:
                        if (jsonarr[j][1].length === 0) {
                            hideStuff('ne4b');
                            hideStuff('ne4v');
                            hideStuff('ne4t');
                        } else {
                            $('#ne4v').text(jsonarr[j][1]);
                        }
                        break;
                    case 24:
                        if ( jsonarr[j][1].length === 0 ) {
                            hideStuff('ne1b');
                            hideStuff('ne1v');
                            hideStuff('ne1t');
                        } else {
                            if ( jsonarr[j][1] === "ja" ) {
                                $('#ne1v').text( yes_text );
                            } else {
                                $('#ne1v').text( no_text );
                            }
                        }
                        break;
                    case 25:
                        $('#sy3v').text(jsonarr[j][1]);
                        break;
                    case 26:
                        $('#ne2v').text(jsonarr[j][1]);
                        break;
                    case 27:
                        $('#ne3v').text(jsonarr[j][1]);
                        break;
                    case 28:
                        if (jsonarr[j][1].length === 0) {
                            hideStuff('ne6b');
                            hideStuff('ne6v');
                            hideStuff('ne6t');
                        } else {
                            $('#ne6v').text(jsonarr[j][1]);
                        }
                        break;
                case 29:
                    $('#db7v').text(jsonarr[j][1]);
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
                    break;
                case 42:
                    $('#ne8v').text(jsonarr[j][1]);
                    break;
                case 45:
                    $('#db9v').text(jsonarr[j][1]);
                    break;  
                case 49:
                    $('#db10v').text(jsonarr[j][1]);
                    break;
                case 51:
                    $('#sy5v').text(jsonarr[j][1]);
                    break;
                case 52:
                    $('#sy6v').text(jsonarr[j][1]);
                    break;
                case 53:
                    $('#sy7v').text(jsonarr[j][1]);
                    break;
                case 55:
                    $('#sy9v').text(jsonarr[j][1]);
                    break;
                case 56:
                    $('#pr4v').text(jsonarr[j][1]);
                    break;  
                case 57:
                    $('#db11v').text(jsonarr[j][1]);
                    break;
                case 58:
                    $('#db12v').text(jsonarr[j][1]);
                    break;
                case 60:
                    $('#db13v').text(jsonarr[j][1]);
                    break;
                case 63:
                    $('#db14v').text(jsonarr[j][1]);
                    break;
                case 65:
                    $('#pr5v').text(jsonarr[j][1]);
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
                    break;
                case 71:
                    $('#db15v').text(jsonarr[j][1]);
                    break;
                case 72:
                    if (jsonarr[j][1].length === 0) {
                        hideStuff('ne9b');
                        hideStuff('ne9v');
                        hideStuff('ne9t');
                    } else {
                        $('#ne9v').text(jsonarr[j][1]);
                    }
                    break;
                case 73:
                    if (jsonarr[j][1].length === 0) {
                        hideStuff('ne10b');
                        hideStuff('ne10v');
                        hideStuff('ne10t');
                    } else {
                        $('#ne10v').text(jsonarr[j][1]);
                    }
                    break;
                case 82:
                    $('#db16v').text(jsonarr[j][1]);
                    break;
                case 84:
                    $('#db17v').text(jsonarr[j][1]);
                    break;
                case 88:
                    $('#db18v').text(jsonarr[j][1]);
                    break;
                case 90:
                    $('#db19v').text(jsonarr[j][1]);
                    break;
                case 93:
                    $('#db20v').text(jsonarr[j][1]);
                    break;
                case 94:
                    $('#db21v').text(jsonarr[j][1]);
                    break;
                case 95:
                    $('#pr7v').text(jsonarr[j][1]);
                    break;
                case 96:
                    $('#db22v').text(jsonarr[j][1]);
                    break;
                case 98:
                    $('#pr8v').text(jsonarr[j][1]);
                 case 99:
                    $('#pr9v').text(jsonarr[j][1]);
                    break;
                case 108:
                    $('#pr10v').text(jsonarr[j][1]);
                    break;
                case 109:
                    $('#db23v').text(jsonarr[j][1]);
                    break;
                case 111:
                    $('#db24v').text(jsonarr[j][1]);
                    break;
                case 123:
                    if ( jsonarr[j][1] == '0') {
                            hideStuff('serial_ok'); 
                            showStuff('serial_nok');
                            if( !soundPlayed ) {
                                soundPlayed = true;
                                PlaySound();
                            }
                        } else {
                            hideStuff('serial_nok'); 
                            showStuff('serial_ok');
                            if( soundPlayed ) soundPlayed = false; // reset
                        }
                    break;
                case 124:
                    //console.log( jsonarr[j] )
                    ntpArr = JSON.parse(jsonarr[j][1]); 

                    if ( ntpArr['ntp'] ) {
                        $('#ntp1').text( on_text );
                    } else {
                        $('#ntp1').text( off_text );
                    }

                    if ( ntpArr['ntp_synchronized'] ) {
                        $('#ntp2').text( on_text );
                    } else {
                        $('#ntp2').text( off_text );
                    }

                    $('#ntp3').text(ntpArr['ntp_last_timestamp']);
                    $('#ntp5').text(ntpArr['ntp_server_name']);
                    $('#ntp6').text(ntpArr['ntp_server_ip']);
                    $('#ntp7').text(ntpArr['timezone']);
                    break;
                case 125:
                    $('#sm1v').text(jsonarr[j][1]);
                    break;
                case 126:
                    $('#pr11v').text(jsonarr[j][1]);
                    break;
                case 129:
                    $('#db25v').text(jsonarr[j][1]);
                    //$('#db25t').text(jsonarr[j][2]);
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
    $.getScript( "./api/v1/p1port/telegram", function( data, textStatus, jqxhr ) {
      try {
        var jsonarr = JSON.parse(data); 
        if (jsonarr[2] == 'valid') {
            $("#slimmemeter").html( jsonarr[3].split("\n").join("<br />") )
        } else {
            $("#slimmemeter").html('Slimme meter data niet beschikbaar(1).');
        }
      } catch(err) {
          console.log( err );
          $("#slimmemeter").html('Slimme meter data niet beschikbaar(2).');
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
            useHTML: true,
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
            useHTML: true,
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
            useHTML: true,
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
            useHTML: true,
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
                    <span class="text-2"><?php echo strIdx( 546 );?></span>
                </div>
                  <div class="frame-2-bot">
                     <div class="text-9"><?php echo strIdx( 551 );?>:</div><div id="db1v" class="text-9"></div><br>
                     <div class="text-9"><?php echo strIdx( 552 );?>:</div><div id="db2v" class="text-9"></div><br>
                     <div class="text-9"><?php echo strIdx( 553 );?>:</div><div id="db3v" class="text-9"></div><br>
                     <div class="text-9"><?php echo strIdx( 554 );?>:</div><div id="db4v" class="text-9"></div><br>
                     <div class="text-9"><?php echo strIdx( 555 );?>:</div><div id="db5v" class="text-9"></div><br>
                     <div class="text-9"><?php echo strIdx( 556 );?>:</div><div id="db6v" class="text-9"></div><br>
                     <div class="text-9"><?php echo strIdx( 557 );?>:</div><div id="db9v" class="text-9"></div><br>
                     <div class="text-9"><?php echo strIdx( 558 );?>:</div><div id="db7v" class="text-9"></div><br>
                     <div class="text-9"><?php echo strIdx( 559 );?>:</div><div id="db8v" class="text-9"></div><br>
                     <div class="text-9"><?php echo strIdx( 560 );?>:</div><div id="db10v" class="text-9"></div><br>
                     <div id="heating">
                        <div class="text-9"><?php echo strIdx( 561 );?>:</div><div id="db11v" class="text-9"></div><br>
                        <div class="text-9"><?php echo strIdx( 562 );?>:</div><div id="db12v" class="text-9"></div><br>
                    </div>
                    <div class="text-9"><?php echo strIdx( 563 );?>:</div><div id="db13v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 564 );?>:</div><div id="db14v" class="text-9"></div><br>
                    <div id="udpBroadcast">
                        <div class="text-9"><?php echo strIdx( 565 );?>:</div><div id="db15v" class="text-9"></div><br>
                    </div>
                    <div class="text-9"><?php echo strIdx( 566 );?>:</div><div id="db16v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 567 );?>:</div><div id="db17v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 568 );?>:</div><div id="db18v" class="text-9"></div><br>
                    <div id="watermeter">
                        <div class="text-9"><?php echo strIdx( 569 );?>:</div><div id="db19v" class="text-9"></div><br>
                    </div>
                    <!--
                    <div class="text-9"><?php echo strIdx( 570 );?>:</div><div id="db20v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 571 );?>:</div><div id="db21v" class="text-9"></div><br>
                    -->
                    <div class="text-9"><?php echo strIdx( 572 );?>:</div><div id="db22v" class="text-9"></div><br>
                    <div id="powerProductionS0">
                        <div class="text-9"><?php echo strIdx( 573 );?>:</div><div id="db23v" class="text-9"></div><br>
                    </div>
                    <div id="powerProductionSolarEdge">
                        <div class="text-9"><?php echo strIdx( 574 );?>:</div><div id="db24v" class="text-9"></div><br>
                    </div>
                    <div id="dynamicsPricing">
                        <div class="text-9"><?php echo strIdx( 608 );?>:</div><div id="db25v" class="text-9"></div><br>
                    </div>
                 </div>
                 <br>
                 <div class="frame-2-top">
                    <span class="text-2"><?php echo strIdx( 547 );?></span>
                </div>
                  <div class="frame-2-bot">
                    <div class="text-9"><?php echo strIdx( 575 );?>:</div><div id="pr1v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 576 );?>:</div><div id="pr2v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 577 );?>:</div><div id="pr3v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 578 );?>:</div><div id="pr4v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 579 );?>:</div><div id="pr5v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 580 );?>:</div><div id="pr6v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 581 );?>:</div><div id="pr7v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 582 );?>:</div><div id="pr8v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 583 );?>:</div><div id="pr9v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 584 );?>:</div><div id="pr10v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 585 );?>:</div><div id="pr11v" class="text-9"></div><br>
                 </div>
                 <br>
                     <div class="frame-2-top">
                    <span class="text-2"><?php echo strIdx( 548 );?></span>
                    <div title="<?php echo strIdx( 98 );?>" class="pos-43">
                        <button onclick="copyClipboard('systeem')" class="input-4 pos-31 cursor-pointer">
                            <i class="color-menu fas fa-clipboard"></i>&nbsp;<span class="color-menu"><?php echo strIdx( 550 );?></span>
                        </button>
                   </div>
                </div>
                  <div id="systeem" class="frame-2-bot">
                    <div class="text-9"><?php echo strIdx( 586 );?>:</div><div id="sy1v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 587 );?>:</div><div id="sy2v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 588 );?>:</div><div id="sy3v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 589 );?>:</div><div id="sy4v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 590 );?>:</div><div id="sy10v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 591 );?>:</div><div id="sy11v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 592 );?>:</div><div id="sy5v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 593 );?>:</div><div id="sy6v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 594 );?>:</div><div id="sy7v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 595 );?>:</div><div id="sy9v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 297 );?>:</div><div id="ntp1" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 298 );?>:</div><div id="ntp2" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 299 );?>:</div><div id="ntp3" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 300 );?>:</div><div id="ntp5" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 301 );?>:</div><div id="ntp6" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 302 );?>:</div><div id="ntp7" class="text-9"></div><br>
                 </div>
                 <br>
                 <div class="frame-2-top">
                    <span class="text-2"><?php echo strIdx( 213 );?></span>
                </div>
                  <div class="frame-2-bot">
                    <div class="text-9"><?php echo strIdx( 596 );?>:</div><div id="ne1v" class="text-9"></div><div><br id="ne1b"></div>
                    <div class="text-9"><?php echo strIdx( 597 );?>:</div><div id="ne2v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 598 );?>:</div><div id="ne3v" class="text-9"></div><br>
                    <div class="text-9"><?php echo strIdx( 599 );?>:</div><div id="ne4v" class="text-9"></div><div><br id="ne4b"></div>
                    <div class="text-9"><?php echo strIdx( 600 );?>:</div><div id="ne5v" class="text-9"></div><div><br id="ne5b"></div>
                    <div class="text-9"><?php echo strIdx( 601 );?>:</div><div id="ne9v" class="text-9"></div><div><br id="ne9b"></div>
                    <div class="text-9"><?php echo strIdx( 602 );?>:</div><div id="ne6v" class="text-9"></div><div><br id="ne6b"></div>
                    <div class="text-9"><?php echo strIdx( 603 );?>:</div><div id="ne7v" class="text-9"></div><div><br id="ne7b"></div>
                    <div class="text-9"><?php echo strIdx( 604 );?>:</div><div id="ne8v" class="text-9"></div><div><br id="ne8b"></div>
                    <div class="text-9"><?php echo strIdx( 605 );?>:</div><div id="ne10v" class="text-9"></div><div><br id="ne10b"></div>
                 </div>

                 <br>
                 <div class="frame-2-top">
                    <span class="text-2"><?php echo strIdx( 549);?></span>
                    <div title="<?php echo strIdx( 98 );?>" class="pos-43">
                        <button onclick="copyClipboard('slimmemeter')" class="input-4 pos-31 cursor-pointer">
                            <i class="color-menu fas fa-clipboard"></i>&nbsp;<span class="color-menu"><?php echo strIdx( 550 );?></span>
                        </button>
                   </div>
                </div>
                  <div class="frame-2-bot">
                        <div title='<?php echo strIdx( 304 );?>' class="text-9"><?php echo strIdx( 303 );?>:</div><div id="sm1v" class="text-9"></div><br>
                        <hr class="margin-7">
                        <div id="slimmemeter" class="text-9">
                        <br>
                    </div>
                 </div>
                 
                 
             </div> 
              <!-- rechter kant van mid sectie -->
              <div class="pos-15">
                 
                 <div class="frame-2-top">

                    <div class="text-2 content-wrapper"><?php echo strIdx( 539 )?>&nbsp;</div>

                    <div class="content-wrapper" title="geluid uit" onclick="soundOn()" id="sound_off" style="display:none">
                            <span class="fa-layers fa-fw fa-2x color-menu cursor-pointer">
                                <i class="fas fa-ban"></i>
                                <i class="fas fa-volume-up color-error" data-fa-transform="shrink-6 right-0"></i>
                            </span>
                    </div>

                    <div class="content-wrapper"title="geluid aan" onclick="soundOff()" id="sound_on" style="display:none">
                            <span class="fa-layers fa-fw fa-2x color-menu cursor-pointer">
                                <i class="fas fa-volume-up" data-fa-transform="shrink-0 right-2"></i>
                            </span>
                    </div>

                </div>
                  <div class="frame-2-bot">
                      <div class="pad-11" id="p1status" title="<?php echo strIdx(2);?>">
                        
                        <div style="display:none" id="serial_ok" >
                            <label  class="text-11" ><?php echo strIdx( 540 );?>&nbsp;</label> 
                            <i      class="color-ok fa fa-2x fa-check-square" ></i>
                        </div>
                        
                        <div style="display:none" id="serial_nok">
                            <label class="text-11"><?php echo strIdx( 541 );?>&nbsp;</label>
                            <i     class="color-error fa fa-2x fa-exclamation-triangle"></i>
                        </div>

                    </div>
                  </div>
                  <br>
                 
                  <div class="frame-2-top">
                    <span class="text-2"><?php echo strIdx( 542 );?></span>
                </div>
                  <div class="frame-2-bot">
                      <div id="cpuload"></div>
                  </div>
                <br>
                <div class="frame-2-top">
                    <span class="text-2"><?php echo strIdx( 543 );?></span>
                </div>
                  <div class="frame-2-bot">
                      <div id="cputemp"></div>
                  </div>
                <br>
                  <div class="frame-2-top">
                    <span class="text-2"><?php echo strIdx( 544 );?></span>
                </div>
                  <div class="frame-2-bot">
                      <div id="ramdiskload"></div>
                  </div>
                  <br>
                  <div class="frame-2-top">
                    <span class="text-2"><?php echo strIdx( 545 );?></span>
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

if ( showDynamicsPricingInfo == false ){
    $('#dynamicsPricing').hide();
}

</script>
</body>
</html>