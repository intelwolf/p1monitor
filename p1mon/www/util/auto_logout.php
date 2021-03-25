<?php
function autoLogout() {
echo <<<"END"
<script>
$(function () {
	setInterval(function(){readPHPsessionStatus();}, 5000);
	function readPHPsessionStatus(){ 
		$.getScript( "./json/session-check.php", function( data, textStatus, jqxhr ) {
			try {
				var d = JSON.parse(data);
				//console.log(d[0]['SESSION_STATUS']);
				if (d[0]['SESSION_STATUS'] != 2) {
					location.reload();
				}
			} catch(err) {
				return null;
			}
		});	
	}
});	
</script>
END;
}
?>