<?php
session_start(); #must be here for every page using login
include_once '/p1mon/www/util/auto_logout.php';
include_once '/p1mon/www/util/page_header.php';
include_once '/p1mon/www/util/p1mon-util.php';
include_once '/p1mon/www/util/menu_control.php';
include_once '/p1mon/www/util/p1mon-password.php';
include_once '/p1mon/www/util/config_buttons.php';
include_once '/p1mon/www/util/config_read.php';
include_once '/p1mon/www/util/textlib.php';
include_once '/p1mon/www/util/div_err_succes.php';
include_once '/p1mon/www/util/pageclock.php';
include_once '/p1mon/www/util/updateStatusDb.php';

//print_r($_POST);
loginInit();
passwordSessionLogoutCheck();

$noInetCheck = isInternetIPAllowed();
$localip     = validLocalIpAdress(getClientIP());
if( $localip == False ){ 
    if( $noInetCheck == False ) {
        die();
    }
}

$sw_off          = strIdx( 193 );
$sw_on           = strIdx( 192 );

if ( isset($_POST[ "records"]) ) {
    updateStatusDb("update status set status = '" . $_POST[ "records"] . "' where ID = 138");
}

?>
<!doctype html>
<html lang="<?php echo strIdx( 370 )?>">
<head>
<meta name="robots" content="noindex">
<title>P1-monitor <?php echo strIdx( 739 );?></title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css">
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css">
<link type="text/css" rel="stylesheet" href="./css/p1mon-1-tabulator.css" >
<link type="text/css" rel="stylesheet" href="./js/flatpickr-link/p1monitor.css">

<script src="./js/flatpickr-link/flatpickr.js"></script>
<script src="./js/flatpickr-link/fr.js"></script>
<script src="./js/flatpickr-link/nl.js"></script>
<script src="./font/awsome/js/all.js"></script>
<script src="./js/p1mon-selectors.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/p1mon-util.js"></script>
<script src="./js/tabulator-dist/js/tabulator.min.js"></script>

</head>
<body>
<script>
    var records_table;
    let records_edited = [];
    let languageIndex = <?php echo languageIndex();?>;
    var mylocale = 'nl';
    var dataProcessedCount = 0;
    

    if ( languageIndex == 1) {
        mylocale = null
    }
    if ( languageIndex == 2) {
        mylocale = 'fr'
    }

    function readJsonApiStatus(){ 
        $.getScript( "./api/v1/status/138", function( data, textStatus, jqxhr ) {
        try {
            const  jsonarr = JSON.parse(data);

            if ( jsonarr[0][1].length > 2 ) { // 2 is empty array
                //console.log("readJsonApiStatus array is not empty.")
                showStuff('processingdata');
                setTimeout( function() { readJsonApiStatus() }, 500 );
            } else {
                //console.log("readJsonApiStatus array empty.")
                setTimeout( function() { records_table.replaceData(); }, 3000 ); // delay to prevent error messages.
                setTimeout( function() { hideStuff('processingdata'); }, 5000 );
            }

            } catch(err) {
                console.log( err ); 
            }
        });
    }


    function buildTable() {

        const MyRound = (n, decimals = 0) => Number(`${Math.round(`${n}e${decimals}`)}e-${decimals}`);
        const modeValidationText = 'in:' + selectorModeToText( mode=1, languageIndex=languageIndex ) + '|' + selectorModeToText( mode=2, languageIndex=languageIndex ) + '|' + selectorModeToText( mode=3, languageIndex=languageIndex ) + '|' + selectorModeToText( mode=4, languageIndex=languageIndex )

         var dateEditor = (cell, onRendered, success, cancel, editorParams) => {

            var editor = document.createElement("input");
            editor.value = cell.getValue();

            var current_timestamp = null //editor.value
            if ( editor.value.length == 16 ) {
                current_timestamp = editor.value;
            }

            var datepicker = flatpickr( editor, {
                disableMobile: true,  // when set to true (default) on smaller devices the pickers does not show
                enableTime: true,
                dateFormat: "Y-m-d H:i",
                defaultDate: [current_timestamp],
                time_24hr: true,
                defaultHour: 0,
                locale:mylocale,
                onReady: function ( dateObj, dateStr, instance ) {
                    const $clear = $( '<div><button class="input-2-weg button-5"><i class="color-menu fas fa-xl fa-trash-alt"></i><br><span class="color-menu text-27">&nbsp;wissen</span></button></div>' )
                        .on( 'click', () => {
                            instance.clear();
                            instance.close();
                    } ).appendTo( $( instance.calendarContainer ) );
                },
             });

            onRendered(() => {
                editor.focus();
            });

            function successFunc(){

                if ( cell.getElement()== false ) {
                    console.log("debug: false cell");
                    return;
                }

                cell.setValue( editor.value );
                success( cell.getValue() );
            }

            function cancelFunction(){

            }

            editor.addEventListener("change", successFunc );
            editor.addEventListener("blur", cancelFunction );

            return editor;

        };

        
        var modeMutator = function(value, data, type, params, component ) {
            return selectorTextToMode(text=data.mode_set, languageIndex=languageIndex)
        }

        var typeMutator = function(value, data, type, params, component ) {
            return selectorTextToType(text=data.type_set, languageIndex=languageIndex)
        }

        //Build Tabulator
        records_table = new Tabulator("#stats-table", {
            // set the MODE text according to the number value of the MODE
            rowFormatter:function( row ){
                var data = row.getData(); //get data object for row
                row.getCell( "mode_set" ).setValue( selectorModeToText( mode=data.MODE, languageIndex=languageIndex ), true );
                row.getCell( "type_set" ).setValue( selectorTypeToText( mode=data.DATA_ID, languageIndex=languageIndex ), true );
                row.getCell( "DELETE" ).setValue( 0, true ); // 1 is delete the sucker.
                if ( row.getCell("TIMESTAMP_START").getValue() !== undefined ) {
                    row.getCell( "TIMESTAMP_START" ).setValue(data.TIMESTAMP_START.substring(0, 16));
                }
                if ( row.getCell("TIMESTAMP_STOP").getValue() !== undefined ) {
                    row.getCell( "TIMESTAMP_STOP" ).setValue(data.TIMESTAMP_STOP.substring(0, 16));
                }
            },
            tooltips:true,
            tooltipGenerationMode:"hover",
            ajaxURL:"./api/v1/statistics?json=object", 
            layout:"fitDataFill",
            maxHeight:"400px",
            //groupBy:"UPDATED",
            groupHeader: function(value, count, data, group){
                return "<?php echo strIdx( 750 )?> " + value + "<span style='color:#0C7DAD; margin-left:10px;'>" + count +  " <?php echo strIdx( 751 )?> " + "</span>";
            },
            columns:[
                {title:"temp_id",
                    field:"temp_id",
                    visible:false 
                },
                {
                    title:"ID",
                    field:"ID", 
                    width:50,
                    headerTooltip: "<?php echo strIdx( 742 )?>",
                    tooltip:function(e, cell, onRendered){
                        return "<?php echo strIdx( 742 )?> :" + cell.getValue()
                    },
                },
                {title:"Type #",
                    field:"DATA_ID",
                    mutatorEdit:typeMutator,
                    visible:false
                },
                {title:"type",
                    field:"type_set",
                    tooltip:function(e, cell, onRendered){
                        //return cell.getValue();
                        row = cell.getRow();
                        return cell.getValue() + "( Data ID: " + row.getCell("DATA_ID").getValue() + ")"
                    },
                    width:160,
                    headerTooltip: "<?php echo strIdx( 743 )?>",
                    mutateLink:"DATA_ID",
                    editor:"list", 
                        editorParams:{
                            values:[ 
                                selectorTypeToText(type=1, languageIndex=languageIndex),
                                selectorTypeToText(type=2, languageIndex=languageIndex),
                                selectorTypeToText(type=3, languageIndex=languageIndex),
                                selectorTypeToText(type=4, languageIndex=languageIndex),
                                selectorTypeToText(type=5, languageIndex=languageIndex),
                                selectorTypeToText(type=6, languageIndex=languageIndex),
                                selectorTypeToText(type=7, languageIndex=languageIndex),
                                selectorTypeToText(type=8, languageIndex=languageIndex),
                                selectorTypeToText(type=9, languageIndex=languageIndex),
                                selectorTypeToText(type=10, languageIndex=languageIndex),
                                selectorTypeToText(type=11, languageIndex=languageIndex),
                                selectorTypeToText(type=12, languageIndex=languageIndex),
                                selectorTypeToText(type=13, languageIndex=languageIndex),
                                selectorTypeToText(type=14, languageIndex=languageIndex),
                                selectorTypeToText(type=15, languageIndex=languageIndex),
                                selectorTypeToText(type=16, languageIndex=languageIndex),
                                selectorTypeToText(type=17, languageIndex=languageIndex),
                                selectorTypeToText(type=18, languageIndex=languageIndex),
                                selectorTypeToText(type=19, languageIndex=languageIndex),
                            ],
                        }
                },
                {title:"<?php echo strIdx( 170 )?>",
                    field:"TIMESTAMP_START",
                    width: 160,
                    headerTooltip: "<?php echo strIdx( 744 )?>",
                    editor:dateEditor,
                    cellEdited:function(cell){
                        dateFixer( cell );
                        checkTimestampSequence( cell );
                    },
                    tooltip:function(e, cell, onRendered){
                        return cell.getValue()
                    },
                },
                {title:"<?php echo strIdx( 380 )?>",
                    field:"TIMESTAMP_STOP", 
                    //editor:"datetime", 
                    width: 160,
                    headerTooltip: "<?php echo strIdx( 745 )?>",
                    editor:dateEditor,
                    cellEdited:function( cell ){
                        dateFixer( cell );
                        checkTimestampSequence( cell );
                    },
                    tooltip:function(e, cell, onRendered){
                        return cell.getValue()
                    },
                },
                { title:"Mode #",
                    field:"MODE" ,
                    mutatorEdit:modeMutator,
                    visible:false
                },
                { title:"mode",
                    field:"mode_set" ,
                    editor:"input",
                    width:95,
                    tooltip:function(e, cell, onRendered){
                        return cell.getValue();
                    },
                    headerTooltip: "<?php echo strIdx( 746 )?>",
                    mutateLink:"MODE",
                    editor:"list", 
                        editorParams:{
                            values:[ selectorModeToText(mode=1, languageIndex=languageIndex), selectorModeToText(mode=2,languageIndex=languageIndex), selectorModeToText(mode=3, languageIndex=languageIndex), selectorModeToText(mode=4,languageIndex=languageIndex)],
                        }
                },
                {title:"<?php echo strIdx( 752)?>",
                    field:"VALUE",
                    width:90,
                    headerTooltip: "<?php echo strIdx( 747 )?>",
                    tooltip:function(e, cell, onRendered){
                        //return MyRound(cell.getValue(), 3)
                        return MyRound(cell.getValue(), 3) + " (" + row.getCell("UPDATED").getValue() + ")"
                    },
                    formatter:function(cell, formatterParams, onRendered){
                        row = cell.getRow();
                        return MyRound(cell.getValue(), 3);
                    },
                },
                {title:"<?php echo strIdx( 750 )?>",
                    field:"UPDATED",
                    visible:false
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
                        crossElement:"<i class='fa-solid fa-ban       color-error'></i>",
                        tickElement: "<i class='fa-solid fa-power-off color-ok-2'></i>"
                    },
                    cellClick:function(e, cell) { 
                        row = cell.getRow();
                        if ( cell.getValue() == 1 ) {
                            cell.setValue( 0, true )
                        } else {
                            cell.setValue( 1, true )
                        }
                    },
                },
                {title: "",
                    field:"DELETE",
                    tooltip: "<?php echo strIdx( 173 )?>",
                    headerSort:false,
                    formatter:"tickCross",
                    formatterParams:{
                        crossElement:"<i class='far fas fa-trash-alt color-menu'></i>",
                        tickElement:" <i class='far fas fa-trash-alt color-error'></i>"
                    },
                    hozAlign: "center",
                    width:40,
                    cellClick:function(e, cell) { 
                        row = cell.getRow();
                        if ( cell.getValue() == 1 ) {
                            cell.setValue( 0, true )
                        } else {
                            cell.setValue( 1, true )
                        }
                    },
                    
                },
                
            ],
        });



        var dataProcessedEvent = function( data ){
                //data has been loaded
                dataProcessedCount++; 
    
                if ( dataProcessedCount > 1 ) { // only do if after the reload, so only the real changes are processed.
                    // only activated after the data is initially is loaded

                    records_table.on("cellEdited", function( cell) {
                      
                        //console.log( "dataProcessedEvent");

                        row = cell.getRow();

                        var start_timestamp = row.getCell("TIMESTAMP_START").getValue();
                        var stop_timestamp = row.getCell("TIMESTAMP_STOP").getValue();
                        if ( start_timestamp.length > 0) {
                            start_timestamp = start_timestamp + ":00";
                        }
                        if ( stop_timestamp.length > 0 ) {
                            stop_timestamp = stop_timestamp + ":00";
                        }
                        var record = {
                            "temp_id":row.getCell("temp_id").getValue(),
                            "ID":row.getCell("ID").getValue(),
                            "DATA_ID":row.getCell("DATA_ID").getValue(),
                            //"type_set":row.getCell("type_set").getValue(),
                            "TIMESTAMP_START":start_timestamp ,
                            "TIMESTAMP_STOP":stop_timestamp,
                            "MODE":row.getCell("MODE").getValue(),
                            //"VALUE":row.getCell("VALUE").getValue(),
                            //"UPDATED":row.getCell("UPDATED").getValue(),
                            "ACTIVE":row.getCell("ACTIVE").getValue(),
                            "DELETE":row.getCell("DELETE").getValue()
                        }
                        
                        var index = -1; // location of the record, if any

                        if ( record["ID"] !== undefined ) { // process existing records
                            // check if record all ready exist, if so replace otherwise add
                            // -1 means not found
                            index = records_edited.findIndex(x => x.ID === record["ID"]);
                        } else { // process new record, find the index if
                            index = records_edited.findIndex(x => x.temp_id === record["temp_id"]);
                        }

                        if ( index < 0 ) { // new record
                                records_edited.push( record )
                            } else {
                                records_edited.splice(index, 1); // remove record from index, because it already exist
                                records_edited.push( record )
                        }

                        if ( record["DELETE"] === 1 && record["temp_id"] !== undefined ) {
                            index = records_edited.findIndex(x => x.temp_id === record["temp_id"]);
                            if( index > -1 ) {
                                records_edited.splice(index, 1); // remove new record, marked for deletion.
                            }
                        }

                    });

                    

                }
        }

        records_table.on("dataProcessed", dataProcessedEvent);

    }


    // cut not needed timestamp values.
    function dateFixer( cell ) {
    
        try {
            row = cell.getRow();
             const data_id= row.getCell("DATA_ID").getValue()
             //console.log( data_id );

            var timestamp = cell.getValue();

            //console.log ( timestamp.length, timestamp  );

            if ( timestamp.length != 16) {
                return //not a valid timestamp 
            }

            if ( data_id == 4 || data_id == 9 || data_id == 13 || data_id == 18 ) { 
                //console.log("maand");
                cell.setValue( timestamp.substring(0, 7) + "-01 00:00");
            } else if ( data_id == 5 || data_id == 10 || data_id == 14 || data_id == 19 ) {
                //console.log("jaar");
                cell.setValue( timestamp.substring(0, 5) + "01-01 00:00");
            }  else if ( data_id == 3 || data_id == 8 || data_id == 12 || data_id == 17 ) {
                //console.log("dag");
                cell.setValue( timestamp.substring(0, 10) + " 00:00");
            } else if ( data_id == 2 || data_id == 7 || data_id == 11 || data_id == 16 ) {
                //console.log("uur");
                cell.setValue( timestamp.substring(0, 13) + ":00");
            } 
        } catch (error) {
            console.error(error);
        }
    }


    function checkTimestampSequence( cell ) {
        row = cell.getRow();

        cell_start = row.getCell("TIMESTAMP_START");
        cell_stop = row.getCell("TIMESTAMP_STOP");

        const start = cell_start.getValue();
        const stop  = cell_stop .getValue();
    
        


        if ( start.length == 0 || stop.length == 0 ) {
            return
        } 
        if ( stop < start ) { // swap start and stop
            cell_start.setValue( stop );
            cell_stop.setValue( start )
            return 
        } 
    }

    $(function () {

        centerPosition('#processingdata');
        //readJsonApiStatus();

        buildTable();

        document.getElementById("add_record_button").addEventListener("click", function(){
            event.preventDefault();
            records_table.addData([{
                temp_id: (new Date().valueOf()), // to identify new records
                DATA_ID:1,
                TIMESTAMP_START:"",
                TIMESTAMP_STOP:"",
                MODE:1,
                UPDATED:"<?php echo strIdx( 269 );?>",
                VALUE:0,
                ACTIVE:1,
                DELETE:0
            },], true);
    
        });

       $( "#formvalues" ).on( "submit", function( event ) {
            document.getElementById("records").value = JSON.stringify(records_edited)
        });

        readJsonApiStatus(); 
    });

</script>

        <?php page_header();?>

        <div class="top-wrapper-2">

            <div class="content-wrapper pad-13">
                <!-- header 2 -->
                <?php pageclock(); ?>
            </div>
            <?php config_buttons( 0 );?>
        </div> <!-- end top wrapper-2 -->

        <div class="mid-section">
            <div class="left-wrapper-config"> <!-- left block -->
                <?php menu_control(18);?>
            </div>

            <div id="right-wrapper-config"> <!-- right block -->
            <!-- inner block right part of screen -->
                <div id="right-wrapper-config-left-weg">
                    <!-- start of content -->
                    <form name="formvalues" id="formvalues" method="POST">

                        <div class="frame-4-top">
                            <span class="text-15"><?php echo strIdx( 740 );?></span>
                        </div>
                        <div class="frame-4-bot">

                            <div class="float-left pad-17" >
                                <div id="stats-table"></div>
                            </div>
                        <p></p>
                        <div class="float-left" title="<?php echo strIdx( 738 );?>">
                            <button class="input-2 but-4 cursor-pointer" id="add_record_button">
                                <i class="color-menu fa-3x fas fa-plus"></i><br>
                            </button>
                        </div>
                </div>

                    <!-- placeholder variables for session termination -->
                    <input type="hidden" name="logout"  id="logout" value="">
                    <input type="hidden" name="records" id="records" value="">
                </form>
            </div>
        </div>
    </div> 

    <div id="processingdata">
        <i class="fas fa-spinner fa-pulse fa-1x"></i>
        <span>&nbsp;<?php echo strIdx( 741 );?></span>
    </div>

    <?php echo autoLogout(); ?>

</body>
</html>