<?php 

// sets the Highcharts.setOptions lang: attribute
function hc_cost_tooltip() {

    echo "
    tooltip: {
        useHTML: false,
        style: {
            padding: 0,
            color: '#6E797C',
        },
        formatter: function() {
    
            // HC_local_timestamp must be set in the calling javascript source
            var s = '<b>'+ Highcharts.dateFormat( HC_local_timestamp, this.x) +'</b>';
            
            var d = this.points;
            var piekVerbruikt=dalVerbruikt=piekGeleverd=dalGeleverd=gasVerbruikt=waterVerbruikt=0;

            for (var i=0,  tot=d.length; i < tot; i++) {
                //console.log (d[i].series.userOptions.id);

                if  ( d[i].series.userOptions.id === 'piek_ver') {
                    piekVerbruikt = d[i].y;
                }
                if  ( d[i].series.userOptions.id === 'dal_ver') {
                    dalVerbruikt = d[i].y;
                }
                if  ( d[i].series.userOptions.id === 'piek_gel') {
                    piekGeleverd = d[i].y;
                }
                if  ( d[i].series.userOptions.id === 'dal_gel') {
                    dalGeleverd = d[i].y;
                }
                if  ( d[i].series.userOptions.id === 'gas_ver') {
                    gasVerbruikt = d[i].y;
                }
                if  ( d[i].series.userOptions.id === 'water_ver') {
                    waterVerbruikt = d[i].y;
                }
            }

            var index = null;
            for (var i=0,  tot=GpiekDataVerbr.length; i < tot; i++) {
                if ( GpiekDataVerbr[i][0] === d[0].key ) {
                        index = i;
                        //console.log('index='+i);
                        break;
                    }
            }

            var KWhVerbruikt     = text_unknown;
            var kWhLevering      = text_unknown;
            var GasM3Verbruikt   = text_unknown;
            var WaterM3Verbruikt = text_unknown;

            if ( GExtraData[index][2] !== -1 ) { KWhVerbruikt     = GExtraData[index][2].toFixed(2); }
            if ( GExtraData[index][3] !== -1 ) { kWhLevering      = GExtraData[index][3].toFixed(2); }
            if ( GExtraData[index][4] !== -1 ) { GasM3Verbruikt   = GExtraData[index][4].toFixed(3); }
            if ( GExtraData[index][5] !== -1 ) { WaterM3Verbruikt = (GExtraData[index][5] / 1000 ).toFixed(3); }

            var pv1=pv2=dv1=dv2=pg1=pg2=dg1=dg2=pt1=pt2=dt1=dt2=gas1=gas2=net1=net2=gasm21=gasm22=verbrkwh1=verbrkwh2=levrkwh1=levrkwh2=water1=water2=water21=water22='';
            var totVerbruikt = 0;
            var totGeleverd  = 0;

            totVerbruikt = parseFloat( piekVerbruikt )+ parseFloat( dalVerbruikt ) + parseFloat( gasVerbruikt ) + parseFloat( waterVerbruikt );
            totGeleverd  = parseFloat( piekGeleverd ) + parseFloat( dalGeleverd );
            totaalNetto  = parseFloat( totVerbruikt ) + parseFloat( totGeleverd );

            if ( $('#CostChartVerbr').highcharts().series[0].visible === true ) { 
                pv1 = '<br><span style=\"color: #FFC311;\">'+text_peak_consumption_tariff+': </span>';
                pv2 = '&nbsp;&euro;&nbsp;'+piekVerbruikt.toFixed(2);
            }
            if ( $('#CostChartVerbr').highcharts().series[1].visible === true ) {
                dv1 = '<br><span style=\"color: #CEA731;\">'+text_low_consumption_tariff+':</span>';
                dv2 = '&nbsp;&euro;&nbsp;'+dalVerbruikt.toFixed(2);
            }

            if ( $('#CostChartVerbr').highcharts().series[4].visible === true ) {
                gas1 = '<br><span style=\"color: #507ABF;\">'+text_gas_cost_consumption+' :</span>';
                if ( GasM3Verbruikt !== text_unknown ) {
                    gas2 = '&nbsp;&euro;&nbsp;'+gasVerbruikt.toFixed(2) + '&nbsp;(' + GasM3Verbruikt + ' m&#179;)';
                } else {
                    gas2 = '&nbsp;&euro;&nbsp;'+gasVerbruikt.toFixed(2) + '&nbsp;(' + GasM3Verbruikt + ' )';
                }
            }

            if ( $('#CostChartVerbr').highcharts().series[5].visible === true ) {
                water1  = '<br><span style=\"color: #6699ff;\">'+text_water_cost_consumption+' :</span>';
                if ( WaterM3Verbruikt !== text_unknown ) {
                    water2  = '&nbsp;&euro;&nbsp;' + waterVerbruikt.toFixed(2) + '&nbsp;(' + WaterM3Verbruikt + ' m&#179;)';
                } else {
                    water2  = '&nbsp;&euro;&nbsp;' + waterVerbruikt.toFixed(2) + '&nbsp;(' + WaterM3Verbruikt + ' )';
                }
            }

            if ( $('#CostChartVerbr').highcharts().series[2].visible === true ) {
                pg1 = '<br><span style=\"color: #98D023;\">'+text_high_tariff_production+' :</span>';
                pg2 = '&nbsp;&euro;&nbsp;'+piekGeleverd.toFixed(2);
            }
            if ( $('#CostChartVerbr').highcharts().series[3].visible === true ) {
                dg1 = '<br><span style=\"color: #7FAD1D;\">'+text_low_tariff_production+' :</span>';
                dg2 = '&nbsp;&euro;&nbsp;'+dalGeleverd.toFixed(2);
            }

            if ( $('#CostChartVerbr').highcharts().series[0].visible === true && $('#CostChartVerbr').highcharts().series[1].visible === true) {
                pt1 = '<br><span style=\"color: #6E797C;\"><b>'+text_total_consumed+' :</b></span>';
                pt2 = '&nbsp;&euro;&nbsp;' + totVerbruikt.toFixed(2) + \"<br>\";
                verbrkwh1 = '<br/>kWh '+ text_consumption+':'
                if ( KWhVerbruikt !== text_unknown ) {
                    verbrkwh2 = KWhVerbruikt +' kWh'
                } else {
                    verbrkwh2 = KWhVerbruikt
                }
            }

            if ( $('#CostChartVerbr').highcharts().series[2].visible === true && $('#CostChartVerbr').highcharts().series[3].visible === true ) {
                dt1= '<br><span style=\"color: #6E797C;\"><b>'+text_total_produced+' :</b></span>';
                dt2= '&nbsp;&euro;&nbsp;'+totGeleverd.toFixed(2) + \"<br>\";
                levrkwh1 = '<br/>kWh '+text_production+':';
                if ( KWhVerbruikt !== text_unknown ) {
                    levrkwh2 = kWhLevering +' kWh';
                } else {
                    levrkwh2 = kWhLevering
                }
            }

            if ( $('#CostChartVerbr').highcharts().series[7].visible === true ) {
                // adjust text if we we have to pay or get money back
                if (totaalNetto >= 0) {
                    net1 = '<br><span style=\"color: #6E797C;\"><b>'+text_net_cost+' :</b></span>';
                } else {
                    totaalNetto = Math.abs(totaalNetto) // no minus numbers
                    net1 = '<br><span style=\"color: #6E797C;\"><b>'+text_net_revenue+' :</b></span>';
                }
                net2 = '&nbsp;&euro;&nbsp;'+totaalNetto.toFixed(2) + \"<br>\";
            }

            s += pv1        + pv2;
            s += dv1        + dv2;
            s += gas1       + gas2;
            s += water1     + water2;
            s += pt1        + pt2;
            s += dg1        + dg2;
            s += pg1        + pg2;
            s += dt1        + dt2;
            s += net1       + net2;
            s += verbrkwh1  + verbrkwh2;
            s += levrkwh1   + levrkwh2;
            return s;
        },
        backgroundColor: '#F5F5F5',
        borderColor: '#DCE1E3',
        crosshairs: [true, true],
        borderWidth: 1
    }
    ";
}
?>