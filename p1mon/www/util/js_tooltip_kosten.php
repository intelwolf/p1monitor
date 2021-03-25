<?php
function tooltip_kosten(){
echo <<<'END'
tooltip: {
	        	useHTML: true,
	        	style: {
         			padding: 3,
         			color: '#6E797C'
     			},
	        	formatter: function() {
					var s = '<b>'+ Highcharts.dateFormat('%A, %Y-%m-%d', this.x) +'</b>';
					var d = this.points;
					var index = 0;
					for (var i=0,  tot=GpiekDataVerbr.length; i < tot; i++) {
						  if ( GpiekDataVerbr[i][0] === d[0].key ) {
						  	index = i;
						  	break;
						}
					}

					var pv1=pv2=dv1=dv2=pg1=pg2=dg1=dg2=pt1=pt2=dt1=dt2=gas1=gas2=net1=net2='';
					var totVerbruikt=0;
					var totGeleverd=0;

					piekVerbruikt	= GpiekDataVerbr[index][1].toFixed(2);
					dalVerbruikt	= GdalDataVerbr[index][1].toFixed(2);
					piekGeleverd	= Math.abs(GpiekDataGelvr[index][1]).toFixed(2);
					dalGeleverd		= Math.abs(GdalDataGelvr[index][1]).toFixed(2);
					gasVerbruikt	= GGasDataGelvr[index][1].toFixed(2);
					totVerbruikt 	= (parseFloat(piekVerbruikt)+parseFloat(dalVerbruikt)+parseFloat(gasVerbruikt)).toFixed(2);
					totGeleverd 	= (parseFloat(piekGeleverd)+parseFloat(dalGeleverd)).toFixed(2);
					totaalNetto		= (parseFloat(totVerbruikt) - parseFloat(totGeleverd)).toFixed(2);

					//console.log("totaalNetto = "+totaalNetto	);
					
					if ( $('#CostChartVerbr').highcharts().series[0].visible === true ) {	
						pv1 = '<span style="color: #CEA731;">Piek kosten verbruik(x):</span><br/>';
						pv2 = '&nbsp;&euro;&nbsp;'+piekVerbruikt+'<br/>';
					}
					if ( $('#CostChartVerbr').highcharts().series[1].visible === true ) {
						dv1 = '<span style="color: #FFC311;">Dal kosten verbruik:</span><br/>';
						dv2 = '&nbsp;&euro;&nbsp;'+dalVerbruikt+'<br/>';
					}

					if ( $('#CostChartVerbr').highcharts().series[4].visible === true ) {
						gas1 = '<span style="color: #507ABF;">Gas kosten verbruik:</span><br/>';
						gas2 = '&nbsp;&euro;&nbsp;'+gasVerbruikt+'<br/>';
					}
					
					if ( $('#CostChartVerbr').highcharts().series[2].visible === true ) {
						pg1 = '<span style="color: #7FAD1D;">Piek kosten geleverd:</span><br/>';
						pg2 = '&nbsp;&euro;&nbsp;'+piekGeleverd+'<br/>';
					}
					if ( $('#CostChartVerbr').highcharts().series[3].visible === true ) {
						dg1 = '<span style="color: #98D023;">Dal kosten geleverd:</span><br/>';
						dg2 = '&nbsp;&euro;&nbsp;'+dalGeleverd+'<br/>';
					}
					if ( $('#CostChartVerbr').highcharts().series[0].visible === true  && $('#CostChartVerbr').highcharts().series[1].visible === true ) {
						pt1= '<span style="color: #6E797C;"><b>Totaal verbruikt:</b></span><br/>';
						pt2= '&nbsp;&euro;&nbsp;'+totVerbruikt+'<br/>';
		
					}
					if ( $('#CostChartVerbr').highcharts().series[2].visible === true && $('#CostChartVerbr').highcharts().series[3].visible === true ) {
						dt1= '<span style="color: #6E797C;"><b>Totaal geleverd:</b></span><br/>';
						dt2= '&nbsp;&euro;&nbsp;'+totGeleverd +'<br/>';
					}

					// adjust text if we we have to pay or get money back
					if (totaalNetto >= 0) {
						net1 = '<span style="color: #6E797C;"><b>Netto kosten:</b></span><br/>';
					} else {
						totaalNetto = Math.abs(totaalNetto) // now minus numbers
						net1 = '<span style="color: #6E797C;"><b>Netto opbrengsten:</b></span><br/>';
					}
					net2 = '&nbsp;&euro;&nbsp;'+totaalNetto+'<br/>';

 					s += '<div style="width: 220px;">'; 
 					s += '<div class="float-left">';		
 					s += pv1;
 					s += dv1;
 					s += gas1;
 					s += pt1;
 					s += '<br>';		
 					s += dg1;
 					s += pg1;
 					s += dt1;
 					s += '<br>';
 					s += net1;				
 					s += '</div>';
 					s += '<div class="float-right">';
 					s += pv2;
 					s += dv2;
 					s += gas2;
 					s += pt2;
 					s += '<br>';
 					s += dg2;
 					s += pg2;
 					s += dt2;
 					s += '<br>';
 					s += net2;
 					s += '</div>';
 					s += '</div>';
					
					return s;
				},			      	
		    	backgroundColor: '#F5F5F5',
		    	borderColor: '#DCE1E3',
		    	crosshairs: [true, true],
		    	borderWidth: 1
		    },

END;
}
?>