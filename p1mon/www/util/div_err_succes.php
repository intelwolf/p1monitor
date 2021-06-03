<?php 
function div_err_succes(){
    global $err_cnt;
    $msg = '';
    
    if ( $err_cnt == 0 ) {
         $msg = "showStuff('succes_msg');"."\n"."setTimeout( function() { hideStuff('succes_msg');},5000);";
    }
    if ( $err_cnt > 0 ) {
         $msg = "showStuff('err_msg');"."setTimeout( function() { hideStuff('err_msg');},5000);";
    }

echo <<<"END"
<div id="succes_msg"><i class="fas fa-fw fa-1x fa-check-square">&nbsp;&nbsp;</i><span id="succes_msg_text">Gegevens succesvol weggeschreven.</span></div>
<div id="err_msg"><i class="fas    fa-fw fa-1x fa-exclamation-triangle">&nbsp;&nbsp;</i><span id="err_msg_text">Gegevens wegschrijven mislukt.</span></div>
<script>
    centerPosition('#err_msg');
    centerPosition('#succes_msg');
    $msg;
</script>
END;
}
?>