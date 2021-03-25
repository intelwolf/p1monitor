<?php
function pageclock(){

echo <<<"END"
		<!-- start page clock -->
				<div id="pageclock" class="pos-13 content-wrapper color-timer"><span class="pos-28"></span></div>
				<script>
				var pageclockTimer;
				 // klok met uren en minuten laten zien
				function clockLoop() {
					//console.log("clock");
					try {	
						var elt = document.getElementById("pageclock");
						if (elt == null ) { return; }
						var d = new Date();
						var time = "<span class='pos-28'>" + zeroPad(d.getHours(),2) + "<b id='PageClockTicks'>:</b>" + zeroPad(d.getMinutes(),2) + "</span>";
						elt.innerHTML = time;
						if( (d.getSeconds()%2) === 0 ) {
						colorFader("#PageClockTicks","#0C7DAD");
						}
						pageclockTimer = setTimeout(clockLoop, 1000); // Run again in 1 second
						} catch(err) {
							console.log(err);
						}
				}
				clockLoop();
				</script>
				 <!-- end page clock --> 	
END;
}
?>