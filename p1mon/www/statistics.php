<?php
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php'; 
include_once '/p1mon/www/util/page_menu.php';
include_once '/p1mon/www/util/textlib.php';
include_once '/p1mon/www/util/check_display_is_active.php';
include_once '/p1mon/www/util/weather_info.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/highchart.php';

if ( checkDisplayIsActive(22) == false) { return; }

?> 
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title>P1-monitor <?php echo strIdx( 737 )?></title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css">
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css">
<link type="text/css" rel="stylesheet" href="./css/p1mon-1-tabulator.css" >

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/highstock-link/highstock.js"></script>
<script src="./js/highstock-link/highcharts-more.js"></script>
<script src="./js/p1mon-util.js"></script>
<script src="./js/p1mon-selectors.js"></script>
<script src="./js/tabulator-dist/js/tabulator.min.js"></script>


<script>

    const TabulatorRound = (n, decimals = 0) => Number(`${Math.round(`${n}e${decimals}`)}e-${decimals}`);

    let languageIndex = <?php echo languageIndex();?>;
    var mylocale = 'nl';
    
    if ( languageIndex == 1) {
        mylocale = null
    }
    if ( languageIndex == 2) {
        mylocale = 'fr'
    }

tableColumns = 
        [{
            title:"ID",
            field:"ID", 
            width:50,
            headerTooltip: "<?php echo strIdx( 742 )?>",
            tooltip:function(e, cell, onRendered){
                return "<?php echo strIdx( 742 )?> :" + cell.getValue()
            },
        },
        {title:"Type#",
            field:"DATA_ID",
            visible:false
        },
        {title:"type",
            field:"type_set",
            tooltip:function(e, cell, onRendered){
                return cell.getValue();
            },
            width:160,
            headerTooltip: "<?php echo strIdx( 743 )?>",
        },
        {title:"<?php echo strIdx( 170 )?>",
            field:"TIMESTAMP_START",
            width: 145,
            headerTooltip: "<?php echo strIdx( 744 )?>",
            tooltip:function(e, cell, onRendered){
                return cell.getValue()
            },
        },
        {title:"<?php echo strIdx( 380 )?>",
            field:"TIMESTAMP_STOP", 
            width: 145,
            headerTooltip: "<?php echo strIdx( 745 )?>",
            tooltip:function(e, cell, onRendered){
                return cell.getValue()
            },
        },
        { title:"mode",
            field:"mode_set" ,
            width:95,
            tooltip:function(e, cell, onRendered){
                return cell.getValue();
            },
            headerTooltip: "<?php echo strIdx( 746 )?>",
        },
        { title:"<?php echo strIdx( 752)?>",
            field:"VALUE",
            width:90,
            headerTooltip: "<?php echo strIdx( 747 )?>",
            tooltip:function(e, cell, onRendered){
                return TabulatorRound(cell.getValue(), 3)
            },
            formatter:function(cell, formatterParams, onRendered){
                return TabulatorRound(cell.getValue(), 3)
            },
        },
        { title:"<?php echo strIdx( 750 )?>",
            field:"UPDATED",
            headerTooltip: "<?php echo strIdx( 750 )?>",
            width:160,
            tooltip:function(e, cell, onRendered){
                return cell.getValue()
            },
        },
        {title:"",
            field:"ACTIVE",
            headerTooltip: "<?php echo strIdx( 748 )?>",
            tooltip:function(e, cell, onRendered){
                if ( cell.getValue() == 1 ) {
                    return "<?php echo strIdx( 172 )?>";
                } else {
                        return "<?php echo strIdx( 749 )?>";
                }
            },
            width:40,
            hozAlign: "center",
            formatter:"tickCross",
            formatterParams:{
                crossElement:"<i class='fa-solid fa-gear color-settings'></i>",
                tickElement: "<i class='fa-solid fa-gear fa-spin color-ok-2'></i>"
            },
        },
    ]

    function rowSetter( row ){

                var data = row.getData(); //get data object for row
                row.getCell( "mode_set" ).setValue( selectorModeToText( mode=data.MODE, languageIndex=languageIndex ), true );
                row.getCell( "type_set" ).setValue( selectorTypeToText( mode=data.DATA_ID, languageIndex=languageIndex ), true );
                if ( row.getCell("TIMESTAMP_START").getValue() !== undefined ) {
                    row.getCell( "TIMESTAMP_START" ).setValue(data.TIMESTAMP_START.substring(0, 16));
                }
                if ( row.getCell("TIMESTAMP_STOP").getValue() !== undefined ) {
                    row.getCell( "TIMESTAMP_STOP" ).setValue(data.TIMESTAMP_STOP.substring(0, 16));
                }
                if ( row.getCell("UPDATED").getValue() !== undefined ) {
                    row.getCell( "UPDATED" ).setValue(data.UPDATED.substring(0, 16));
                }
            }
            

    function buildTableKwh() {

       tabualtorkWh= new Tabulator("#kwh-table", {
            rowFormatter: function( row ){
                rowSetter( row );
            },
            tooltips:true,
            tooltipGenerationMode:"hover",
            ajaxURL:"./api/v1/statistics?json=object", 
            layout:"fitDataFill",
            maxHeight:"410px",
            columns: tableColumns
        });
    
        tabualtorkWh.on("tableBuilt", function(){
            tabualtorkWh.setFilter([
                {field:"DATA_ID", type:"<", value:11},
                {field:"DATA_ID", type:">", value:0},
           ]);
           setInterval( function() { 
                tabualtorkWh.replaceData() 
            } 
            , 30000 ); // reload
        });
    
    }

    function buildTableGas() {

       tabualtorGas = new Tabulator("#gas-table", {
           
            rowFormatter: function( row ){
                rowSetter( row );
            },
            tooltips:true,
            tooltipGenerationMode:"hover",
            ajaxURL:"./api/v1/statistics?json=object", 
            layout:"fitDataFill",
            maxHeight:"410px",
            columns: tableColumns
        });
    
        tabualtorGas.on("tableBuilt", function(){
            tabualtorGas.setFilter([
                {field:"DATA_ID", type:"<", value:15},
                {field:"DATA_ID", type:">", value:10},
           ]);
           setInterval( function() { 
                tabualtorGas.replaceData() 
            } 
            , 30000 ); // reload
        });
    
    }


     function buildTableWater() {

       tabualtorWater = new Tabulator("#water-table", {
           
            rowFormatter: function( row ){
                rowSetter( row );
            },
            tooltips:true,
            tooltipGenerationMode:"hover",
            ajaxURL:"./api/v1/statistics?json=object", 
            layout:"fitDataFill",
            maxHeight:"410px",
            columns: tableColumns
        });
    
        tabualtorWater.on("tableBuilt", function(){
            tabualtorWater.setFilter([
                {field:"DATA_ID", type:"<", value:20},
                {field:"DATA_ID", type:">", value:14},
           ]);
           setInterval( function() { 
                tabualtorWater.replaceData() 
            } 
            , 30000 ); // reload
        });
    
    }



    $(function () {
        buildTableKwh();
        buildTableGas();
        buildTableWater();

        screenSaver( <?php echo config_read(79);?> ); // to enable screensaver for this screen.
    });

</script>
</head>
<body>

<?php page_header();?>

<div class="top-wrapper-2">
    <div class="content-wrapper pad-13">
       <!-- header 2 -->
       <?php pageclock(); ?>
       &nbsp;
       <?php weather_info(); ?>
    </div>
</div>


<div class="mid-section">
    <div class="left-wrapper">
        <?php page_menu(13); ?>
    </div> 
    
    <div class="mid-content-2 pad-13">
    <!-- links -->
        
        <div> <!-- right block -->
            
            <div class="frame-4-top">
                <span class="text-15">kWh <?php echo strIdx( 737 )?></span>
            </div>
            <div class="frame-4-bot">
                <div class="float-left" >
                    <div id="kwh-table"></div>
                    <p></p>
                </div>
            </div>

            <p></p>

            <div class="frame-4-top">
                <span class="text-15"><?php echo strIdx( 336 )?> <?php echo strIdx( 737 )?></span>
            </div>
            <div class="frame-4-bot">
                <div class="float-left" >
                    <div id="gas-table"></div>
                    <p></p>
                </div>
            </div>

            <p></p>

            <div class="frame-4-top">
                <span class="text-15"><?php echo strIdx( 220 )?> <?php echo strIdx( 737 )?></span>
            </div>
            <div class="frame-4-bot">
                <div class="float-left" >
                    <div id="water-table"></div>
                    <p></p>
                </div>
            </div>

    </div>


</div>
    
</div>

</body>
</html>