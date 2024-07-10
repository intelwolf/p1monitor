<?php

/***********************************************************
 *             Settings voor jaarrekening.php              *
 ***********************************************************/
// IP ADRES van de P1mon Raspberry Pi:
// $p1monIP = '192.168.1.22'; <-- voorbeeld 
// Als het script op hetzelfde device draait als P1mon gebruikt je: 
$p1monIP='127.0.0.1'; 

// FORMAAT DATUM IN TITELS: 
// 1: jaar-maand-dag
// 2: dag-maand-jaar 
// 3: dag maandnaam jaar
$datumlayout = 3;

// GAS WEERGEVEN: 
// 0 : nee 
// 1 : ja 
$gasweergeven = 1;

// NAMEN HOOG/LAAG PIEK/DAL DAG/NACHT TARIEF
//$hoog = 'Dag';
//$laag = 'Nacht';
$hoog = 'Piek';
$laag = 'Dal';

// CHECK VOOR UPDATE
// internettoegang vereist
$checklaatsteversie = 1;
