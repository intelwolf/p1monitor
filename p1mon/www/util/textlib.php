<?php
function strIdx($_index) {

// support for Nederlands, English, French.

$arr = array (
/* 000 */   array(
    '0 index voor test.','0 index for testing.','0 index pour les tests.'
    ),
/* 001 */   array(
    'De P1 poort op de slimme meter is een seriële interface die afhankelijk van de het type slimme meter anders ingesteld moet worden.<br><br>In Nederland is het DSMR 3 protocol 9600 7E1 (7 databits, even parity, 1 stop bit) of DSMR 4 protocol 115200 8N1 (8 databits, geen parity, 1 stop bit) gebruikelijk.<br><br>',
    'The P1 port on the smart meter is a serial interface that must be set differently depending on the type of smart meter.<br><br>In the Netherlands, the DSMR 3 protocol is 9600 7E1 (7 data bits, even parity, 1 stop bit) or DSMR 4 protocol 115200 8N1 (8 data bits, no parity, 1 stop bit) are common.<br><br>',
    'Le port P1 du compteur intelligent est une interface série qui doit être réglée différemment selon le type de compteur intelligent. <br> <br> Aux Pays-Bas, le protocole DSMR 3 est 9600 7E1 (7 bits de données, parité paire, 1 bit d&apos;arrêt) ou le protocole DSMR 4 115200 8N1 (8 bits de données, pas de parité, 1 bit d&apos;arrêt) sont communs.<br><br>'
    ),
/* 002 */   array(
    'het kan tussen de 30 tot 60 seconden duren voordat de status correct wordt weergegeven.',
    'it may take anywhere from 30 to 60 seconds for the status to display correctly.',
    'cela peut prendre de 30 à 60 secondes pour que l&apos;état s&apos;affiche correctement.'
    ),
/* 003 */   array(
    'Het overzicht van de wifi access points (essid’s) wordt elke 60 seconden aangepast.<br>Mocht de wifi naam er niet tussen staan wacht dat 1 minuut en ververs de pagina (bijvoorbeeld via herstel optie.)<br><br>Het wijzingen van de wifi instellingen kan enkele minuten duren.<br><br>Mocht de Wifi niet actief worden herstart de Raspberry Pi dan via het configuratie systeem menu.',
    'The overview of the wifi access points (essid&apos;s) is updated every 60 seconds.<br>If the wifi name is not show, wait 1 minute and refresh the page (for example via the recovery option.)<br><br>Changing the Wi-Fi settings can take a few minutes.<br><br>If the Wi-Fi is not actived, restart the Raspberry Pi via the configuration system menu.',
    'La vue d&apos;ensemble des points d&apos;accès wifi (ESSID) est mis à jour toutes les 60 secondes.<br> Si le nom wifi est montre pas, attendez 1 minute et actualisez la page (par exemple via l&apos;option de récupération.)<br><br>La modification des paramètres Wi-Fi peut prendre quelques minutes.<br><br> Si le Wi-Fi n&apos;est pas activé, redémarrez le Raspberry Pi via le menu du système de configuration.'
    ),
/* 004 */   array(
    'Tarieven in euro&apos;s per geleverde kWh, kubieke meter gas of water.<br><br>De vastrechtkosten worden opgeteld bij het kosten voor geleverde kWh, gas of water.',
    'Rates in euros per consumed kWh, cubic meter of gas or water.<br><br>The standing charges are added to the costs for consumed kWh, gas or water.',
    'Tarifs en euros par kWh consommé, mètre cube ou gaz ou eau.<br><br>Les charges permanentes s&apos;ajoutent aux coûts de consommation de kWh, de gaz ou d&apos;eau.'
    ),
/* 005 */   array(
    'Zet de de Rasberry Pi uit via deze opties om te voorkomen dat er data verloren gaat of corrupt raakt.<br><br>Na wissen van het wachtwoord wordt aanbevolen het wachtwoord opnieuw in te stellen.',
    'Turn off the Raspberry Pi using these options to avoid data loss or data corruption.<br><br>After clearing the password, it is recommended to reset the password',
    'Éteignez le Raspberry Pi à l&apos;aide de ces options pour éviter la perte de données ou la corruption des données.<br><br>Après avoir effacé le mot de passe, il est recommandé de réinitialiser le mot de passe'
    ),
/* 006 */   array(
    'Database is de optie voor het delen van data. De ontwikkeloptie geeft toegang tot alle bestanden en moet vermeden worden. Uit is de standaard optie.',
    'Database is the option for data sharing. The develop option gives access to all files and should be avoided. Off is the default option.',
    'La base de données est l&apos;option de partage de données. L&apos;option develop donne accès à tous les fichiers et doit être évitée. Off est l&apos;option par défaut.'
    ),
/* 007 */   array(
    'Met export worden alle gegevens uit de SQLite database naar SQL statements in een zip file weggeschreven. Het exporteren is bedoeld om de gegevens veilig te stellen als er een nieuwe versie van P1-monitor uitkomt of als back-up. Importeren is bedoeld voor het inlezen van eerder gemaakte export bestanden en werkt alleen met een P1-monitor exportfile.',
    'With export, all data from the SQLite database is saved to SQL statements in a zip file. The export is intended to secure the data when a new version of P1-monitor is released or as a backup. Import is intended for reading previously created export files and only works with a P1-monitor export file.',
    'Avec l&apos;exportation, toutes les données de la base de données SQLite sont enregistrées dans des instructions SQL dans un fichier zip. L&apos;exportation est destinée à sécuriser les données lorsqu &apos;une nouvelle version du moniteur P1 est publiée ou en tant que sauvegarde. L&apos;importation est destinée à la lecture de fichiers d&apos;exportation créés précédemment et ne fonctionne qu&apos; avec un fichier d&apos;exportation de moniteur P1.'
    ),
/* 008 */   array(
    'Klik op de link voor een voorbeeld van de data die gelezen kan worden via de API. De help extensie van de API geeft uitleg.',
    'Click on the link for an example of the data that can be read via the API. The help extension of the API provides an explanation.',
    'Cliquez sur le lien pour un exemple des données pouvant être lues via l&apos;API. L&apos;extension d&apos;aide de l&apos;API fournit une explication.'
    ),
/* 009 */   array(
    'Het de-activeren van schermen maakt het mogelijk bepaalde schermen uit de userinterface(UI)te verwijderen. <br><br>Waarden instellen UI elementen maakt het mogelijk om een subset van grenswaarden in te stellen.<br><br> Als je een eigen userinterface wil gebruiken als alternatief van de standaard interface selecteer dan de optie eigen userinterface.  Als deze ingeschakeld wordt dan wordt standaard als eerste pagina /www/custom/p1mon.php weergegeven. Maak alleen gebruik van de API calls en eigen javascript of andere bestanden. De bronnen uit de standaard interface kunnen per versie worden veranderd.',
    'Disabling screens allows you to remove certain screens from the user interface (UI). <br> <br> Setting values UI elements allows to set a subset of limit values. <br> <br> If you want to use your own user interface as an alternative to the standard interface then select the option own user interface. If this is enabled, the first page will be displayed as /www/custom/p1mon.php. Only use the API calls and your own javascript or other files. The sources from the standard interface can be changed per version.',
    'La désactivation des écrans vous permet de supprimer certains écrans de l&apos;interface utilisateur (UI). <br> <br> Définition des valeurs Les éléments de l&apos;interface utilisateur permettent de définir un sous-ensemble de valeurs limites.<br><br>Si vous souhaitez utiliser votre propre interface utilisateur comme alternative à l&apos;interface standard, sélectionnez l&apos;option propre interface utilisateur. Si cette option est activée, la première page sera affichée sous la forme /www/custom/p1mon.php. N&apos;utilisez que les appels d&apos;API et vos propres fichiers javascript ou autres. Les sources de l&apos;interface standard peuvent être modifiées par version.'
    ),
/* 010 */   array(
    'De weer informatie wordt verkregen via openweathermap.org website. Om deze website te kunnen gebruiken moet je een gratis account aanmaken op de website en een API key verkrijgen. Dit is erg eenvoudig zie de openweathermap.org website.<br><br>Voer de API key in en de stad. Voer bij de stad minimaal drie karakters in. Je kunt tevens een landcode opgeven in het formaat stad, landcode bijvoorbeeld amsterdam,nl vs amsterdam,us om te voorkomen de verkeerde locatie wordt ingesteld.<br><br> je kunt tevens de stad id invoeren als het niet lukt om via de naam van de stad de juiste locatie in te stellen. De stad id kun je achter halen via de site van openweathermap.org. Zoek een stad. Als de pagina verschijnt op de site achter de url de stad id. Voor Alkmaar is dit bijvoorbeeld https://openweathermap.org/city/2759899',
    'Weather information is obtained from openweathermap.org website. To use this website you need to create a free account on the website and obtain an API key. This is very simple see the openweathermap.org website. <br> <br> Enter the API key and the city. Enter at least three characters for the city. You can also enter a country code in the format city, country code for example amsterdam, nl vs amsterdam, us to avoid setting the wrong location.<br><br>you can also enter the city id if it is not possible to use the name of the city to set the correct location. You can find out the city id from the site of openweathermap.org. Search for a city. If the page appears on the site after the url the city id. For Alkmaar this is for example https://openweathermap.org/city/2759899',
    'Les informations météorologiques sont obtenues sur le site Web openweathermap.org. Pour utiliser ce site Web, vous devez créer un compte gratuit sur le site Web et obtenir une clé API. C&apos;est très simple, consultez le site Web openweathermap.org.<br><br>Entrez la clé API et la ville. Entrez au moins trois caractères pour la ville. Vous pouvez également entrer un code de pays au format ville, code de pays par exemple Amsterdam, nl vs Amsterdam, nous pour éviter de définir le mauvais emplacement. <br><br>vous pouvez également saisir l&apos;identifiant de la ville s&apos;il n&apos;est pas possible d&apos;utiliser le nom de la ville pour définir l&apos;emplacement correct. Vous pouvez trouver l&apos;identifiant de la ville sur le site openweathermap.org. Recherchez une ville. Si la page apparaît sur le site après l&apos;url, l&apos;identifiant de la ville. Pour Alkmaar, c&apos;est par exemple https://openweathermap.org/city/2759899'
    ),
/* 011 */   array(
    'De timer instellingen geven de mogelijkheid om het tijdstip van de back-up in te stellen. Het is gebaseerd op de crontab syntax. Voor meer details zie http://www.cronjob.nl/.<BR><BR>Beweeg je muis over de velden voor extra informatie.',
    'The timer settings allow you to set the time of the backup. It is based on the crontab syntax. For more details see <a href="https://www.geeksforgeeks.org/crontab-in-linux-with-examples">crontab-in-linux-with-examples</a>crontab-in-linux-with-examples/.<br><br>Move your mouse over the fields for extra information.',
    'Les paramètres du minuteur vous permettent de définir l&apos;heure de la sauvegarde. Il est basé sur la syntaxe crontab. Pour plus de détails, consultez <a href="https://www.geeksforgeeks.org/crontab-in-linux-with-examples">crontab-in-linux-with-examples</a><br><br>Déplacez votre souris sur les champs pour plus d&apos;informations.'
    ),
/* 012 */   array(
    'FTP is een niet versleutelde verbinding, FTPS is een versleutelde verbinding die de inlog gegevens beveiligd, alleen expliciet FTPS over poort 21 wordt ondersteund, impliciet over poort 990 niet. SFTP is een verbinding gebaseerd op SSH en is de meest veilige optie.',
    'FTP is a non-encrypted connection, FTPS is an encrypted connection that secures the login data, only explicit FTPS over port 21 is supported, implicitly over port 990 not. SFTP is a connection based on SSH and is the most secure option.',
    'FTP est une connexion non cryptée, FTPS est une connexion cryptée qui sécurise les données de connexion, seul le FTPS explicite sur le port 21 est pris en charge, implicitement sur le port 990 non. SFTP est une connexion basée sur SSH et est l&apos;option la plus sécurisée.'
    ),
/* 013 */   array(
    'Account de naam van ftp inlog naam (account) vaak is dit in het formaat naam@domein.xxx',
    'Account the name of ftp login name (account) is often in the format name@domain.xxx',
    'Compte le nom du nom de connexion ftp (compte) est souvent au format nom@domaine.xxx'
    ),
/* 014 */   array(
    'het wachtwoord van ftp / ftps / sftp account.','the password of ftp/ ftps / sftp account.','le mot de passe du compte ftp / ftps / sftp.'
    ),
/* 015 */   array(
    'folder van de back-up’s, het veld mag ook leeg zijn.','folder of the backups, the field may be empty.','dossier des sauvegardes, le champ peut être vide.'
    ),
/* 016 */   array(
    'IP adres of domeinnaam (ftp@mijndomein.nl o.i.d) van de ftp server.',
    'IP address or domain name (ftp@myserver.com or similar) of the ftp server.',
    'Adresse IP ou nom de domaine (ftp@mmonftp.be ou similaire) du serveur ftp.'
    ),
/* 017 */   array(
    'Dit is normaal poort 21 en hoeft niet aangepast te worden maar kan nodig zijn als je een niet standaard ftp server gebruikt. Deze poort instelling werkt alleen voor FTP!',
    'This is normally port 21 and does not need to be changed but may be necessary if you are using a non-standard ftp server. This port setting only works for FTP!',
    'Il s&apos;agit normalement du port 21 et n&apos;a pas besoin d&apos;être changé mais peut être nécessaire si vous utilisez un serveur ftp non standard. Ce paramètre de port ne fonctionne que pour FTP!'
    ),
/* 018 */   array(
    'Aantal versies die je wil bewaren, na het bereiken van dit aantal wordt de oudste back-up gewist.',
    'Number of versions you want to retain, after reaching this number the oldest backup will be deleted.',
    'Nombre de versions que vous souhaitez conserver, après avoir atteint ce nombre, la sauvegarde la plus ancienne sera supprimée.'
    ),
/* 019 */   array(
    'de laatste keer dat de timer een back-up heeft gestart.','the last time the timer started a backup.','la dernière fois que le minuteur a démarré une sauvegarde.'
    ),
/* 020 */   array(
    'de laatste keer dat de back-up succesvol is afgerond.','the last time the backup completed successfully.','la dernière fois que la sauvegarde terminée avec succès.'
),
/* 021 */   array(
    'Hier worden meldingen weergegeven die de back-up server rapporteert.',
    'Displays messages reported by the backup server.',
    'Affiche les messages signalés par le serveur de sauvegarde.'
),
/* 022 */   array(
    'test de back-up apart van de timer.','test the backup separately from the timer.','testez la sauvegarde séparément du minuteur.'
),
/* 023 */   array(
    'Dit is de 1.8.1 waarde ook wel laag/dal/nacht/tarief 1 genoemd (Nederland).',
    'This is the 1.8.1 value, also referred to as low / off-peak / night / rate 1 (Netherlands).',
    'Il s&apos;agit de la valeur 1.8.1, également appelée faible / heures creuses / nuit / tarif 1 (Pays-Bas).'
    ),
/* 024 */   array(
    'Dit is de 1.8.2 waarde ook wel hoog/piek/dag/tarief 2 genoemd (Nederland).',
    'This is the 1.8.2 value also referred to as high / peak / day / tariff 2 (Netherlands).',
    'Il s&apos;agit de la valeur 1.8.2 également appelée haut / pic / jour / tarif 2 (Pays-Bas).'
    ),
/* 025 */   array(
    'Dit is de 2.8.1 waarde ook wel laag,dal/nacht/tarief 1 genoemd (Nederland).',
    'This is the 2.8.1 value, also called low, off-peak / night / rate 1 (Netherlands).',
    'Il s&apos;agit de la valeur 2.8.1, également appelée faible, heures creuses / nuit / tarif 1 (Pays-Bas).'
    ),
/* 026 */   array(
    'Dit is de 2.8.2 waarde ook wel hoog/piek/dag/tarief 2 genoemd (Nederland).',
    'This is the 2.8.2 value also called high / peak / day / tariff 2 (Netherlands).',
    'Il s&apos;agit de la valeur 2.8.2 également appelée haute / pointe / jour / tarif 2 (Pays-Bas).'
    ),
/* 027 */   array(
    'Het gas telegramcodenummer is het nummer van de gasmeting, normaal is dit een gasmeting met het nummer 0-1 zoals bij de codes 0-1:24.2.1, 0-1:24.3.0 of 0-1:24.2.3. Deze optie stelt het nummer achter het streepje in. Bijvoorbeeld een 2 wordt dan 0-2:24.2.1',
    'The gas telegram code number is the number of the gas measurement, normally this is a gas measurement with the number 0-1 as with the codes 0-1: 24.2.1, 0-1: 24.3.0 or 0-1: 24.2.3. This option sets the number after the dash. For example a 2 becomes 0-2: 24.2.1',
    'Le numéro de code du télégramme de gaz est le numéro de la mesure de gaz, normalement il s&apos;agit d&apos;une mesure de gaz avec le numéro 0-1 comme avec les codes 0-1: 24.2.1, 0-1: 24.3.0 ou 0-1: 24.2 .3. Cette option définit le nombre après le tiret. Par exemple, un 2 devient 0-2: 24.2.1'
    ),
/* 028 */   array(
    'Grenswaarde kosten is het bedrag wat je per maand aan kosten maakt of wil maken. In de kostenoverzicht levert dit een grenslijn op die aangeeft of je over of onder je maandbedrag blijft.',
    'Limit cost is the amount that you incur or want to incur per month. In the cost overview, this produces a boundary line that indicates whether you stay over or under your monthly amount.',
    'Le coût limite est le montant que vous engagez ou que vous souhaitez engager par mois. Dans l&apos;aperçu des coûts, cela produit une ligne de démarcation qui indique si vous restez au-dessus ou en dessous de votre montant mensuel.'
    ),
/* 029 */   array(
    'Sommige slimme meters maakt gebruik van een controle methode(CRC) waarmee vastgesteld kan worden of de P1 data correct is verstuurd. Mocht je problemen ondervinden dan kan deze controle aan of uitgezet worden. Voor meters zonder CRC (geen vier karakters achter het einde telegram karakter !) uitzetten.',
    'Some smart meters use a control method (CRC) to determine whether the P1 data has been sent correctly. If you encounter problems, this check can be turned on or off. Turn off for meters without CRC (no four characters after the end of the telegram character!).',
    'Certains compteurs intelligents utilisent une méthode de contrôle (CRC) pour déterminer si les données P1 ont été envoyées correctement. Si vous rencontrez des problèmes, cette vérification peut être activée ou désactivée. Éteignez pour les compteurs sans CRC (pas de quatre caractères après la fin du caractère de télégramme!).'
    ),
/* 030 */   array(
    'Om Dropbox te kunnen gebruiken moet de P1-monitor beperkt toegang krijgen tot een Dropbox account. Er wordt alleen toegang gevraagd tot de /apps/p1monitor folder. Klik op het Dropbox icoon volg de instructies van Dropbox en knip en plak het autorisatie token.',
    'To use Dropbox, the P1-monitor must have limited access to a Dropbox account. Access is only requested to the / apps / p1monitor folder. Click on the Dropbox icon and follow the Dropbox instructions and cut and paste the authorization token.',
    'Pour utiliser Dropbox, le moniteur P1 doit avoir un accès limité à un compte Dropbox. L&apos;accès n&apos;est demandé qu&apos;au dossier / apps / p1monitor. Cliquez sur l&apos;icône Dropbox et suivez les instructions de Dropbox et coupez et collez le jeton d&apos;autorisation.'
    ),
/* 031 */   array(
    'De laatste keer dat er succesvol data naar Dropbox is gekopieerd.',
    'The last time data was successfully copied to Dropbox.',
    'La dernière fois que les données ont été copiées avec succès dans Dropbox.'
),
/* 032 */   array(
    'Dropbox statusmelding.','Dropbox status notification.','notification d&apos;état Dropbox.'
),
/* 033 */   array(
    'Met versie controle wordt automatisch periodiek gecontroleerd of er een nieuwe versie beschikbaar is. Deze optie staat om privacy reden standaard uit. Als de optie aan staat dan word je publieke IP-adres gedeeld met ztatz.nl. We doen niets met het IP-adres en wissen deze periodiek.',
    'Version check automatically checks periodically whether a new version is available. This option is disabled by default for privacy reasons. If the option is on, your public IP address will be shared with ztatz.nl. We do nothing with the IP address and we delete it periodically.',
    'Le contrôle de version vérifie automatiquement périodiquement si une nouvelle version est disponible. Cette option est désactivée par défaut pour des raisons de confidentialité. Si l&apos;option est activée, votre adresse IP publique sera partagée avec ztatz.nl. Nous ne faisons rien avec l&apos;adresse IP et nous la supprimons périodiquement.'
    ),
/* 034 */   array(
    'De UDP broadcast verstuurt ongeveer elke 10 seconden een JSON netwerkbericht (UDP broadcast op poort 40721).',
    'The UDP broadcast sends a network JSON message (UDP broadcast on port 40721) approximately every 10 seconds.',
    'La diffusion UDP envoie un message JSON réseau (diffusion UDP sur le port 40721) environ toutes les 10 secondes.'
    ),
/* 035 */   array(
    'Systeem ID is een unieke code van de P1-monitor. Deze code wordt gebruik om onderscheid te maken tussen verschillende P1-monitor systemen. De code wordt bijvoorbeeld gebruik in back-up en in Dropbox data bestanden.',
    'System ID is a unique code of the P1-monitor. This code is used to distinguish between different P1-monitor systems. The code is used, for example, in backup and in Dropbox data files.',
    'L&apos;ID système est un code unique du moniteur P1. Ce code est utilisé pour distinguer les différents systèmes de surveillance P1. Le code est utilisé, par exemple, dans la sauvegarde et dans les fichiers de données Dropbox.'
    ),
/* 036 */   array(
    '"Voorspelling aan in de UI" probeert in die gevallen waar de data nog niet van is gemeten een voorspelling te doen. Dit is een inschatting geen absolute waarde en beperkt betrouwbaar.',
    '"Prediction on in the UI" tries to make a prediction in those cases where the data has not yet been measured. This estimate is not an absolute value and is of limited reliability.',
    '"Prédiction activée dans l&apos;interface utilisateur" tente de faire une prédiction dans les cas où les données n&apos;ont pas encore été mesurées. Cette estimation n&apos;est pas une valeur absolue et est d&apos;une fiabilité limitée.'
),
/* 037 */   array(
    'De upgrade assistent helpt bij het migreren/upgrade naar een nieuwere versie. Om de upgrade assistent te kunnen gebruiken heb je een USB-stick nodig die met FAT of FAT32 is geformatteerd. NFTS , exFat of andere filesystems worden niet ondersteund. In principe kan elke USB-drive worden gebruikt tussen de 1Gb en 32 Gb. De daadwerkelijke ruimte die nodig is zeer beperkt en minder dan 100Mb. Bij het activeren van de Upgrade assistent wordt gezocht naar een geschikte USB-stick in een van de USB-poorten en de database en andere configuratie data gekopieerd naar de USB-stick. Bij de volgende keer dat de P1-monitor wordt gestart wordt de data van de USB-stick naar het SDHC-kaartje gekopieerd. Dit is een eenmalig actie waarbij de data van de USB-stick wordt verwijderd. Het is belangrijk te begrijpen dat het activeren van de Upgrade assistent waarbij de USB-stick in de Raspberry Rpi blijft de database overschreven wordt met de (oude) data van de USB-stick. De USB-stick is na een upgrade leeg en bevat geen data meer.  De upgrade wordt in twee fasen gedaan. In de eerste fase worden de basis configuratie gegeven overgezet en Rpi herstart. Na de herstart wordt op de achtergrond een import uitgevoerd die afhankelijk van de hoeveelheid data wel tot een 20 minuten in beslag kan nemen.<br><br><span style="color:red">Bij een upgrade mag de Pi dan ook de eerste 20 minuten niet herstart worden.</span><br><br>Mocht je USB-stick willen wissen dan kun je de folder p1monitor wissen.<br><br><span style="color:red">Het wordt aanbevolen een export te doen van de data als noodmaatregel, mocht er een probleem optreden met de upgrade assistent.</span><br><br>',
    'The upgrade assistant helps you migrate / upgrade to a newer version. To use the upgrade assistant you need a USB stick formatted with FAT or FAT32. NFTS, exFat or other filesystems are not supported. In principle, any USB drive can be used between 1Gb and 32Gb. The actual space required is very limited and less than 100Mb. When activating the Upgrade Assistant, a suitable USB stick is searched for in one of the USB ports and the database and other configuration data is copied to the USB stick. The next time the P1-monitor is started, the data will be copied from the USB stick to the SDHC card. This is a one-time action where the data is removed from the USB stick. It is important to understand that activating the Upgrade Assistant where the USB stick remains in the Raspberry Pi will overwrite the database with the (old) data from the USB stick. The USB stick is empty after an upgrade and no longer contains any data. The upgrade is done in two stages. In the first phase, the basic configuration data are transferred and the Rpi restarted. After the restart, an import is performed in the background, which, depending on the amount of data, can take up to 20 minutes. <br> <br> <span style = "color: red"> When upgrading, the Rpi may not be rebooted in the first 20 minutes </span> <br> <br> If you want to delete the USB stick data, you can delete the folder p1monitor.<br><br> <span style = "color: red"> The it is recommended to export the data as an emergency measure, should there be a problem with the upgrade assistant.</span><br><br>',
    'L&apos;assistant de mise à niveau vous aide à migrer / mettre à niveau vers une version plus récente. Pour utiliser l&apos;assistant de mise à niveau, vous avez besoin d&apos;une clé USB formatée avec FAT ou FAT32. Les systèmes de fichiers NFTS, exFat ou autres ne sont pas pris en charge. En principe, n&apos;importe quelle clé USB peut être utilisée entre 1 Go et 32 ​​Go. L&apos;espace réel requis est très limité et inférieur à 100 Mo. Lors de l&apos;activation de l&apos;assistant de mise à niveau, une clé USB appropriée est recherchée dans l&apos;un des ports USB et la base de données et les autres données de configuration sont copiées sur la clé USB. Au prochain démarrage du moniteur P1, les données seront copiées de la clé USB vers la carte SDHC. Il s&apos;agit d&apos;une action ponctuelle où les données sont supprimées de la clé USB. Il est important de comprendre que l&apos;activation de l&apos;assistant de mise à niveau où la clé USB reste dans le Raspberry Pi écrasera la base de données avec les (anciennes) données de la clé USB. La clé USB est vide après une mise à jour et ne contient plus de données. La mise à niveau se fait en deux étapes. Dans la première phase, les données de configuration de base sont transférées et le Rpi redémarré. Après le redémarrage, une importation est effectuée en arrière-plan, ce qui, selon la quantité de données, peut prendre jusqu&apos;à 20 minutes.<br><br><span style = "color: red"> Lors de la mise à niveau, le Rpi peut ne pas être redémarré dans les 20 premières minutes </span> <br> <br> Si vous souhaitez supprimer les données de la clé USB, vous pouvez supprimer le dossier p1monitor.<br><br><span style = "color: red"> Il est recommandé d&apos;exporter les données comme mesure d&apos;urgence, en cas de problème avec l&apos;assistant de mise à jour. </span><br><br>'
    ),
/* 038 */   array(
    'De gasmeter stand.','the gas meter reading.','la lecture du compteur de gaz.'
    ),
/* 039 */   array(
    'moment van hoogste verbruik.','moment of highest consumption.','moment de consommation la plus élevée.'
    ),
/* 040 */   array(
    'piek verbruikswaarde.','peak consumption value.','valeur de consommation de pointe.'
    ),
/* 041 */   array(
    'verbruik vandaag.','consumption today.','consommation aujourd&apos;hui.'
    ),
/* 042 */   array(
    'Kosten vandaag gas, elektriciteit en water.',
    'Today expenses for gas, electricity and water.',
    'Aujourd&apos;hui, les coûts du gaz, de l&apos;électricité et de l&apos;eau.'
    ),
/* 043 */   array(
    'moment van hoogste levering.','moment of highest production.','moment de la plus haute production.'
    ),
/* 044 */   array(
    'Piek leveringswaarde.','Peak production value.','Valeur de production maximale.'
    ),
/* 045 */   array(
    'Levering vandaag.','Production today.','Production aujourd&apos;hui.'
),
/* 046 */   array(
    'Opbrengsten vandaag.','Revenue today.','revenus aujourd&apos;hui.'
    ),
/* 047 */   array(
    'Kosten vandaag elektriciteit en water','Electricity and water costs today','Les coûts d&apos;électricité et d&apos;eau aujourd&apos;hui'
    ),
/* 048 */   array(
    'Kosten gas vandaag.','Cost of gas today.','Coût du gaz aujourd&apos;hui.'
    ),
/* 049 */   array(
    'Configuratie via het Internet staat toe dat een browser met een Internet IP-adres aanpassingen kan maken in de configuratie of bepaalde afgeschermde pagina’s toegankelijk zijn, deze zijn normaal alleen met een RFC1918 IP-adres te gebruiken. De optie is gemaakt omdat er situaties zijn waar internetadressen op het lokale LAN worden gebruikt.',
    'Configuration via the Internet allows a browser with an public Internet IP address to make adjustments to the configuration or to access certain protected pages, which can normally only be used with an RFC1918 IP address. The option was made because there are situations where public internet addresses are used on the local LAN.',
    'La configuration via Internet permet à un navigateur avec une adresse IP Internet publique de faire des ajustements à la configuration ou d&apos;accéder à certaines pages protégées, qui ne peuvent normalement être utilisées qu&apos;avec une adresse IP RFC1918. L&apos;option a été faite car il existe des situations où des adresses Internet publiques sont utilisées sur le LAN local.'
),
/* 050 */   array(
    'Naam van de email inlognaam (account) vaak is dit in het formaat naam@domein.nl',
    'Name of the email login name (account) is often in the format name@domain.nl',
    'Le nom du nom de connexion de l&apos;e-mail (compte) est souvent au format nom@domaine.nl'
    ),
/* 051 */   array(
    'Het wachtwoord van het email account.','The password of the email account.','Le mot de passe du compte e-mail.'
    ),
/* 052 */   array(
    'IP-adres of domeinnaam (smtp.gmail.com / mail.server.nl o.i.d.) van de mailserver.',
    'IP address or domain name (smtp.gmail.com / mail.server.nl for example) of the mail server.',
    'adresse IP ou le nom de domaine (smtp.gmail.com / mail.server.nl par exemple) du serveur de e-mail.'
    ),
/* 053 */   array(
    'Dit is de poort die je email provider gebruikt voor het versleuteld versturen van email. Je email provider bepaalt deze poort. Voor Gmail is dit 465.',
    'The port used by your email provider to send encrypted email. Your email provider determines this port. For Gmail, this is 465.',
    'Le port utilisé par votre fournisseur de e-mail pour envoyer des e-mails chiffrés. Votre fournisseur de e-mail détermine ce port. Pour Gmail, il s&apos;agit de 465.'
    ),
/* 054 */   array(
    'Dit is de poort die je email provider gebruikt voor het gedeeltelijk versleuteld versturen van email. Je email provider bepaalt deze poort. Voor Gmail is dit 587.',
    'The port that your email provider uses for partially encrypted email. Your email provider determines this port. For Gmail, this is 587.',
    'Le port que votre fournisseur de e-mail utilise pour les e-mails partiellement cryptés. Votre fournisseur de messagerie détermine ce port. Pour Gmail, c&apos;est 587.'
    ),
/* 055 */   array(
    'Dit is de normale poort voor email verkeer(onveilig). Normaal is dit poort 25.',
    'This is the standard port for email traffic (non secure). Normally this is port 25.',
    'Il s&apos;agit du port standard pour le trafic de e-mail (non sécurisé). Normalement, il s&apos;agit du port 25.'
    ),
/* 056 */   array(
    'Het onderwerp van de notificatie e-mails die het standaard onderwerp vervangt.',
    'The subject of the notification emails that replaces the default subject.',
    'L&apos;objet des e-mails de notification qui remplace l&apos;objet par défaut.'
    ),
/* 057 */   array(
    'Lijst van email adressen van de ontvangers gescheiden met een spatie.',
    'List of email addresses of the recipients separated by a space.',
    'Liste des adresses e-mail des destinataires séparées par un espace.'
    ),
/* 058 */   array(
    'Lijst van email kopie adressen (CC) van de ontvangers gescheiden met een spatie.',
    'List of email addresses copy (CC) of the recipients separated by a space.',
    'Copie de la liste des adresses e-mail (CC) des destinataires séparés par un espace.'
    ),
/* 059 */   array(
    'Lijst van email blinde kopie adressen (BCC) van de ontvangers gescheiden met een spatie.',
    'List of email addresses blind copy (BCC) of the recipients separated by a space.',
    'Liste des adresses e-mail en copie invisible (BCC) des destinataires séparés par un espace.'
    ),
/* 060 */   array(
    'De zender van de notificatie e-mails die de standaard tekst vervangt, houdt dit veld leeg voor de standaard tekst.',
    'The sender of the notification e-mails that replaces the default text will keep this field empty for the default text.',
    'L&apos;expéditeur des e-mails de notification qui remplace le texte par défaut gardera ce champ vide pour le texte par défaut.'
    ),
/* 061 */   array(
    'De tijd in de seconden dat er gewacht wordt op een antwoord van de email server.',
    'The time in seconds to wait for a response from the email server.',
    'Le temps en secondes pour attendre une réponse du serveur de e-mail.'
    ),
/* 062 */   array(
    'Vul hier de instellingen in van de email provider die je wilt gebruiken.<br><br>Mocht je gebruik willen maken van een Gmail account dan moet Multi-factor authenticatie uit staan en toegang tot minder veilige apps moet worden toegestaan. <br><br> <span style="color:red">Er zijn soms problemen met het gebruik van Gmail, dit wordt onderzocht maar daar is nog geen oplossing voor.</span>',
    'Enter the settings of the email provider you want to use here. <br> <br> If you want to use a Gmail account, Multi-factor authentication must be turned off and access to less secure apps must be allowed. <br> <br> <span style = "color: red"> There are sometimes problems using Gmail, this is being investigated but there is no solution yet.</span>',
    'Entrez ici les paramètres du fournisseur de messagerie que vous souhaitez utiliser. <br> <br> Si vous souhaitez utiliser un compte Gmail, l&apos;authentification multifacteur doit être désactivée et l&apos;accès à des applications moins sécurisées doit être autorisé. <br> <br> <span style = "color: red"> Il y a parfois des problèmes avec Gmail, ceci est en cours d&apos;investigation mais il n&apos;y a pas encore de solution.</span>'
    ),
/* 063 */   array(
    'Notificatie als er geen slimme meter data wordt ontvangen.',
    'Notification if no smart meter data is received.',
    'Notification si aucune donnée de compteur intelligent n&apos;est reçue.'
    ),
/* 064 */   array(
    'Dag/nacht mode laag en hoog tarief verwerking aanpassen tussen België en Nederland. Alleen aanpassen als de dag en nacht waarden verwisseld worden.',
    'Adjust day / night mode low and high rate processing between Belgium and the Netherlands. Only adjust if the day and night values are swapped.',
    'Régler mode jour / nuit basse et traitement de taux élevé entre la Belgique et les Pays-Bas. Ajustez uniquement si les valeurs de jour et de nuit sont permutées.'
    ),
/* 065 */   array(
    'Dit is de 1.8.1 waarde ook wel hoog/piek/dag/tarief 2 genoemd (België).',
    'This is the 1.8.1 value also called high / peak / day / tariff 2 (Belgium).',
    'Il s&apos;agit de la valeur 1.8.1 également appelée haute / pointe / jour / tarif 2 (Belgique).'
    ),
/* 066 */   array(
    'Dit is de 1.8.2 waarde ook wel laag/dal/nacht/tarief 1 genoemd (België).',
    'This is the 1.8.2 value also called low / off-peak / night / tariff 1 (Belgium).',
    'Il s&apos;agit de la valeur 1.8.2 également appelée low / crête / nuit / tarif 1 (Belgique).'
    ),
/* 067 */   array(
    'Dit is de 2.8.1 waarde ook wel hoog/piek/dag/tarief 2 genoemd (België)',
    'This is the 2.8.1 value also called high / peak / day / tariff 2 (Belgium)',
    'Il s&apos;agit de la valeur 2.8.1 également appelée haute / pointe / jour / tarif 2 (Belgique)'
    ),
/* 068 */   array(
    'Dit is de 2.8.2 waarde ook wel laag/dal/nacht/tarief 1 genoemd (België)',
    'This is the 2.8.2 value also called low / off-peak / night / tariff 1 (Belgium)',
    'Il s&apos;agit de la valeur 2.8.2 également appelée low / crête / nuit / tarif 1 (Belgique)'
    ),
/* 069 */   array(
    'Screensaver met de in en uitschakeltijden, als de muis bewogen wordt zal de screensaver stoppen. Uit wil zeggen niet inschakelen of automatische uitschakelen. De optie geldt niet voor de instellingsschermen.',
    'Screen saver with the switch-on and switch-off times, when the mouse is moved, the screen saver will stop. Off means no switching on or automatic switching off. The option does not apply to the setup screens.',
    'Économiseur d&apos;écran avec les heures d&apos;allumage et d&apos;extinction, lorsque la souris est déplacée, l&apos;économiseur d&apos;écran s&apos;arrête. Off signifie pas de mise en marche ni de désactivation automatique L&apos;option ne s&apos;applique pas aux écrans de configuration.'),
/* 070 */   array(
    'Met de terug leveringsschakelaar kan een instelbare GPIO-pin worden geactiveerd om zo een bijvoorbeeld een boiler in te schakelen als er een ingesteld vermogen wordt opgewekt. De volgende parameters zijn beschikbaar. Grenswaarden voor het in- of uitschakelen. De periode van de gemiddelde waarde voor de grenswaarden. Minimale tijd dat in of uitgeschakeld wordt. GPIO pin die wordt gebruikt. Het aan of uitzetten van de terug levering. Of de ingesteld GPIO-pin activeren voor test o.i.d. Voor het selecteren van de GPIO-pin gebruik de nummering GPIOnn GPIO18 is dan pin 12. Zie onderstaande afbeelding.',
    'With the feed-in power switch, an adjustable GPIO pin can be activated to switch on for example a boiler when a certain power level is reached. The following parameters are available. Power limits for switching on or off. The period of the mean value for the limits. Minimum time to turn the GPIO pin on or off. The GPIO pin used. Turning on or off this function. Activate the set GPIO pin for test or similar. To select the GPIO pin, use the numbering GPIOnn. GPIO18 is pin 12. See the image below.',
    'Avec l&apos;interrupteur d&apos;alimentation, une broche GPIO réglable peut être activée pour allumer par exemple une chaudière lorsqu&apos;un certain niveau de puissance est atteint. Les paramètres suivants sont disponibles. Limites de puissance pour l&apos;activation ou la désactivation. La période de la valeur moyenne des limites. Temps minimum pour activer ou désactiver la broche GPIO. La broche GPIO utilisée. Activer ou désactiver cette fonction. Activez la broche GPIO définie pour un test ou similaire. Pour sélectionner la broche GPIO, utilisez la numérotation GPIOnn. GPIO18 est la broche 12. Voir l&apos;image ci-dessous.'
    ),
/* 071 */   array(
    'Database wissen wist alle database data inclusief de configuratie alsof het een nieuwe installatie is. Na het wissen moet alles opnieuw ingesteld worden ook al lijkt het te werken. Let op dit kan enkele minuten duren, geduld aub.',
    'Delete database erases all database data including the configuration as if it were a new installation. After erasing everything has to be reset even if it seems to work. Note this can take a few minutes, please be patient',
    'Supprimer la base de données efface toutes les données de la base de données, y compris la configuration, comme s&apos;il s&apos;agissait d&apos;une nouvelle installation. Après avoir effacé, tout doit être réinitialisé même si cela semble fonctionner. Notez que cela peut prendre quelques minutes, soyez patient'
    ),
/* 072 */   array(
    'Met de tarief schakelaar kan via een ingesteld GPIO-pin tijdens de ingestelde periodes worden geschakeld tijdens het piek of dal tarief. De ingevoerde schakelperioden worden bij elkaar gevoegd.',
    'With the tariff switch, a set GPIO pin can be used to switch during the set periods during the peak or off-peak tariff. The entered switching periods are added together.',
    'Avec le commutateur de tarif, une broche GPIO définie peut être utilisée pour basculer pendant les périodes définies pendant les heures de pointe ou les heures creuses. Les périodes de commutation saisies sont additionnées.'
),
/* 073 */   array(
    'De watermeter stand','The water meter reading','Le montant du compteur d&apos;eau'
    ),
/* 074 */   array(
    'Stuur een test email met de ingestelde parameters.','Send a test email with the set parameters.','Envoyez un e-mail de test avec les paramètres définis.'
    ),
/* 075 */   array(
    'Wat is kilowattuur per minuut, hoe kan dit?  De energie meter geeft aan wat het verbruik is per kWh.  Volgends de definitie is dit 1 Watt (W) staat gelijk aan 1 Joule (J) per seconde (s): 1 W = 1 J/s.  1 kilowatt = 1.000 Watt.  1 kWh is wat een apparaat met een vermogen van 1.000 Watt (1 kW) in één uur verbruikt.  In de P1-monitor nemen we de waarde van kWh op tijdstip T1 en tijdstip T2 (dat is T1 + 1 minuut)  waarbij we de kWh waarde van T2 – T1 aftrekken. Stel T1 is 10kWh en T2 is 10.005 kWh dan is er tijdens die minuut dus 10.005 – 10kWh verbruikt is 0.005 kWh.  De “echte” kWh waarde wordt dan 0.005 * 60 minuten wat 0,3kWh over een uur.',
    'What is a value of kilowatt hours per minute, how is this possible? The energy meter measures the consumption per kWh. According to the definition this is 1 Watt (W) equals 1 Joule (J) per second (s): 1 W = 1 J / s. 1 kilowatt = 1,000 watts. 1 kWh is what a device with a power consumption of 1,000 watts (1 kW) consumes in one hour. In the P1-monitor we take the value of kWh at time T1 and time T2 (that is T1 + 1 minute), subtracting the kWh value from T2 - T1. Suppose T1 is 10kWh and T2 is 10.005 kWh, then during that minute 10.005 - 10kWh is consumed is 0.005 kWh. The “real” kWh value will then be 0.005 * 60 minutes, which is 0.3 kWh in an hour.',
    'Quelle est la valeur du kilowattheure par minute, comment est-ce possible? Le compteur d&apos;énergie mesure la consommation par kWh. Selon la définition, cela équivaut à 1 Watt (W) équivaut à 1 Joule (J) par seconde (s): 1 W = 1 J / s. 1 kilowatt = 1000 watts. 1 kWh, c&apos;est ce qu&apos;un appareil avec une consommation électrique de 1000 watts (1 kW) consomme en une heure. Dans le P1-monitor, nous prenons la valeur de kWh au temps T1 et au temps T2 (c&apos;est-à-dire T1 + 1 minute), en soustrayant la valeur du kWh de T2 - T1. Supposons que T1 est de 10 kWh et T2 de 10,005 kWh, puis pendant cette minute, 10,005 - 10 kWh sont consommés est de 0,005 kWh. La valeur «réelle» du kWh sera alors de 0,005 * 60 minutes, soit 0,3 kWh en une heure.'
    ),
/* 076 */   array(
    'MQTT (Message Queue Telemetry Transport) is een client met broker architectuur. De P1-monitor werkt als MQTT client en is geen MQTT broker. MQTT werkt met zogenaamde topics om de data bronnen aan te geven die naar de broker worden gestuurd. Het scherm “MQTT published topics” geeft welke topics ondersteund worden. Deze zijn aan te passen met de schakelaars.<br><br><b>client ID:</b> mag leeg zijn dan wordt er automatisch een client ID gemaakt.<br> <b>topic voorvoegsel:</b> mag leeg zijn dan wordt p1monitor gebruikt.<br> <b>broker servernaam / IP:</b> naam of IP adres van de MQTT broker.<br> <b>broker IP poort:</b> TCP/poort van de broker meestal 1883.<br> <b>broker keep alive tijd:</b> tijd in seconden dat gecontroleerd wordt of verbinding met de broker in orde is.<br> <b>broker gebruikers naam /  broker gebruikers wachtwoord:</b> Als een broker om een naam en wachtwoord nodig heeft anders kunnen de velden leeg blijven.<br> <b>QoS (Quality of Service)</b> en <b>protocol versie:</b> raadpleeg de MQTT specificatie.',
    'MQTT (Message Queue Telemetry Transport) is a client with broker architecture. The P1-monitor works as an MQTT client and is not an MQTT broker. MQTT works with so-called topics to indicate the data sources that are sent to the broker. The item “MQTT published topics” shows which topics are supported. These can be adjusted with the switches. <br> <br> <b> client ID: </b> can be empty, a client ID will be automatically created. <br> <b> topic prefix: </b> may be empty, p1monitor will be used. <br> <b> broker server name / IP: </b> name or IP address of the MQTT broker. <br> <b> broker IP port: </b> TCP / port of the broker usually 1883. <br> <b> broker keep alive time: </b> time in seconds to verify that the connection to the broker is ok. <br> <b> broker username / broker user password: < / b> If a broker requires a name and password otherwise the fields can be left empty. <br> <b> QoS (Quality of Service) </b> and <b> protocol version: </b> consult the MQTT specification.',
    'MQTT (Message Queue Telemetry Transport) est un client avec une architecture de broker. Le moniteur P1 fonctionne comme un client MQTT et n&apos;est pas un broker MQTT. MQTT fonctionne avec des topics dites pour indiquer les sources de données envoyées au broker. L&apos;élément «Topics publiés MQTT» indique les rubriques prises en charge. Ceux-ci peuvent être ajustés avec les commutateurs. <br> <br> <b> ID client: </b> peut être vide, un ID client sera automatiquement créé. <br> <b> préfixe de sujet: </b> peut être vide, p1monitor sera utilisé. <br> <b> nom / IP du serveur de broker: </b> nom ou adresse IP du courtier MQTT. <br> <b> port IP du courtier: </b> TCP / port du broker généralement 1883. <br> <b> temps de maintien du broker: </b> temps en secondes pour vérifier que la connexion au broker est d&apos;accord. <br> <b> nom d&apos;utilisateur du broker / mot de passe de l&apos;utilisateur du broker: </ b> Si un broker a besoin d&apos;un nom et d&apos;un mot de passe, les champs peuvent être laissés vides. <br> <b> QoS (Quality of Service) </b> et <b> version du protocole: </b> consultez la spécification MQTT.'
    ),
/* 077 */   array(
    'Niet alle slimme meters geven fase informatie door en sommige slimme meters een beperkte set van volt, ampère of vermogen (Watt) waarden.  Als deze informatie niet doorgegeven wordt dan zullen de meetwaarden als nul (0) worden weergegeven.',
    'Not all smart meters transmit phase information and some smart meters have a limited set of volts, amps or power (Watt) measurements. If this information is not available in the smart meter telegram on, the measured values will be displayed as zero (0).',
    'Tous les compteurs intelligents ne transmettent pas les informations de phase et certains compteurs intelligents ont un ensemble limité de mesures de tension, d&apos;ampères ou de puissance (Watt). Si ces informations ne sont pas disponibles dans le télégramme du compteur intelligent activé, les valeurs mesurées seront affichées sous forme de zéro (0).'
    ),
/* 078 */   array(
    'Verberg of laat een grafiek zien.','Hide or show a graph.','Masquer ou afficher un graphique.'
    ),
/* 079 */   array(
    'Datapunten (samples) terug in de tijd.','Data points (samples) back in time.','Points de données (échantillons) dans le temps.'
    ),
/* 080 */   array(
    'Datapunten (samples) vooruit in de tijd.',
    'Data points (samples) forward in time',
    'Points de données (échantillons) vers l&apos;avant dans le temps.'
),
/* 081 */   array(
    'Aantal datapunten instellen.','Set the number of data points.','Définissez le nombre de points de données.'
    ),
/* 082 */   array(
    'De historische fase data is relatief veel data. Als de historische data niet gebruikt wordt dan is het verstandig om deze optie uit te zetten om de belasting  op de database en de processor te verminderen. Belangrijk: niet alle slimme meters geven fase informatie door.  In het telegram moet minimaal een van de volgende codes voorkomen 1-0:21.7.0, 1-0:41.7.0, 1-0:61.7.0, 1-0:22.7.0, 1-0:42.7.0, 1-0:62.7.0, 1-0:32.7.0, 1-0:52.7.0, 1-0:72.7.0, 1-0:31.7.0, 1-0:51.7.0, 1-0:71.7.0.',
    'The historical phase data is relatively much data. If the historical data is not used then it is wise to turn this option off to reduce the load on the database and the processor. Important: not all smart meters transmit phase information. The telegram must contain at least one of the following codes: 1-0: 21.7.0, 1-0: 41.7.0, 1-0: 61.7.0, 1-0: 22.7.0, 1-0: 42.7.0 , 1-0: 62.7.0, 1-0: 32.7.0, 1-0: 52.7.0, 1-0: 72.7.0, 1-0: 31.7.0, 1-0: 51.7.0, 1 -0: 71.7.0.',
    'Les données de la phase historique sont relativement nombreuses. Si les données historiques ne sont pas utilisées, il est judicieux de désactiver cette option pour réduire la charge sur la base de données et le processeur. Important: tous les compteurs intelligents ne transmettent pas les informations de phase. Le télégramme doit contenir au moins l&apos;un des codes suivants: 1-0: 21.7.0, 1-0: 41.7.0, 1-0: 61.7.0, 1-0: 22.7.0, 1-0: 42.7. 0, 1-0: 62.7.0, 1-0: 32.7.0, 1-0: 52.7.0, 1-0: 72.7.0, 1-0: 31.7.0, 1-0: 51.7.0, 1-0: 71,7,0.'
    ),
/* 083 */   array(
    'Met de UI labels kan een andere tekst in schermen worden ingesteld. Zonder invoer wordt de standaard tekst gebruikt.',
    'With the UI labels a different text in screens can be set. The default text is used without input',
    'Avec les étiquettes de l&apos;interface utilisateur, un texte différent dans les écrans peut être défini. Le texte par défaut est utilisé sans saisie'
    ),
/* 084 */   array(
    'De hoeveelheid water in de elke puls vertegenwoordigd.  Normaal is dit 1 liter per puls.',
    'The amount of water each pulse represents. Normally this is 1 liter per pulse.',
    'La quantité d&apos;eau chaque impulsion représente. Normalement, cela est de 1 litre par impulsion.'
    ),
/* 085 */   array(
    'Het aantal kubieke meter water dat op watermeter staat bij de opgegeven watermeter timestamp.',
    'The number of cubic meters of water on the water meter at the specified water meter timestamp.',
    'Le nombre de mètres cubes d&apos;eau sur le compteur d&apos;eau à l&apos;horodatage du compteur d&apos;eau spécifié.'
    ),
/* 086 */   array(
    'De datum van de watermeterstand uit het verleden. Vanaf deze datum wordt de watermeterstand opgeteld bij de gemeten liters.',
    'The date of the water meter reading from the past. From this date, the water meter reading is added to the measured liters.',
    'La date du relevé du compteur d&apos;eau du passé. A partir de cette date, la lecture du compteur d&apos;eau est ajoutée aux litres mesurés.'
    ),
/* 087 */   array(
    'Zet deze schakelaar op aan om de watermeterstand te verwerken in de database. Vergeet niet op opslaan te drukken rechts boven aan de pagina.',
    'Set this switch to on to process the water meter reading in the database. Don&apos;t forget to click save at the top right of the page.',
    'Activez ce commutateur pour traiter la lecture du compteur d&apos;eau dans la base de données. N&apos;oubliez pas de cliquer sur Enregistrer en haut à droite de la page.'
    ),
/* 088 */   array(
    'Dit geeft status van de aanpassing in de database, terwijl de database wordt aangepast.',
    'This gives the status of the modification in the database while the database is being modified.',
    'Cela donne l&apos;état de la modification dans la base de données pendant que la base de données est en cours de modification.'
    ),
/* 089 */   array(
    'De totale watermeterstand na of voor werking van de watermeter reset.',
    'The total water meter reading after or before operation of the water meter reset.',
    'La lecture totale du compteur d&apos;eau après ou avant le fonctionnement de la réinitialisation du compteur d&apos;eau.'
    ),
/* 090 */   array(
    'De laatste keer dat een watermeter puls verwerkt is.',
    'The last time a water meter pulse was processed.',
    'La dernière fois qu&apos;une impulsion de compteur d&apos;eau a été traitée.'
    ),
/* 091 */   array(
    'Als er geen gegevens worden weergegeven dan kan het zijn dat de opslag van historische gegevens niet aangezet is of dat de slimme meter geen fasegegevens doorgeeft. In het configuratie menu kan op de pagina bestanden de optie worden geactiveerd.',
    'If no data is displayed, it may be that the storage of historical data is not enabled or that the smart meter is not transmitting phase data. The option can be activated on the files page in the configuration menu.',
    'Si aucune donnée n&apos;est affichée, il se peut que le stockage des données historiques ne soit pas activé ou que le compteur intelligent ne fournisse pas de données de phase. L&apos;option peut être activée sur la page des fichiers dans le menu de configuration.'
    ),
/* 092 */   array(
    'De kWh waarde in de elke puls vertegenwoordigd. Dit is afhankelijk van de specifieke meter. Raadpleeg de kWh meter handleiding.',
    'The kWh value represented by each pulse. This depends on the specific meter. Consult the kWh meter manual.',
    'La valeur en kWh représentée par chaque impulsion. Cela dépend du compteur spécifique. Consultez le manuel du compteur kWh.'
    ),
/* 093 */   array(
    'De kWh meterstand opgegeven bij de ingevoerd timestamp.',
    'The kWh meter reading specified with the entered timestamp.',
    'La lecture du compteur kWh spécifiée avec l&apos;horodatage entré.'
    ),
/* 094 */   array(
    'Zet deze schakelaar op aan om de kWh meterstand te verwerken in de database. Vergeet niet op opslaan te drukken rechts boven aan de pagina.',
    'Set this switch to on to process the kWh meter reading in the database. Don&apos;t forget to click save at the top right of the page.',
    'Activez ce commutateur pour traiter la lecture du compteur kWh dans la base de données. N&apos;oubliez pas de cliquer sur Enregistrer en haut à droite de la page.'
    ),
/* 095 */   array(
    'De laatste keer dat een kWh S0 puls verwerkt is.',
    'The last time a kWh S0 pulse was processed.',
    'La dernière fois qu&apos;une impulsion kWh S0 a été traitée.'
    ),
/* 096 */   array(
    'De datum van de kWh meterstand uit het verleden. Vanaf deze datum wordt de kWh meterstand opgeteld bij de gemeten kWh waarden.',
    'The date of the past kWh meter reading. From this date, the kWh meter reading will be added to the measured kWh values.',
    'La date de la dernière lecture du compteur kWh. A partir de cette date, la lecture kWh mètre sera ajouté aux valeurs mesurées kWh.'
    ),
/* 097 */   array(
    'De kWh stand na of voor werking van de kWh meter reset.',
    'The kWh setting after or before operation of the kWh meter is reset.',
    'Le réglage du kWh après ou avant le fonctionnement du compteur kWh est réinitialisé.'
    ),
/* 098 */   array(
    'Kopieert het P1 telegram naar het clipboard zodat het telegram in een ander document of voor bijvoorbeeld een ondersteuningsvraag kan worden gebruikt.',
    'Copies the P1 telegram to the clipboard so that the telegram can be used in another document, for example a support request.',
    'Copie le télégramme P1 dans le presse-papiers afin que le télégramme puisse être utilisé dans un autre document, par exemple une demande d&apos;assistance.'
    ),
/* 099 */   array(
    'Bruto terug levering is wat de zonnepanelen, windmolen en enz. opwekken exclusief je eigen verbruik. Netto terug levering is wat er daadwerkelijk aan het energienetwerk via de slimme meter wordt terug geleverd.',
    'Gross production is what the solar panels, windmill and etc. generate, excluding your own consumption. Net power return is what is actually returned to the energy grid via the smart meter.',
    'La production brute est ce que les panneaux solaires, l&apos;éolienne, etc. génèrent, à l&apos;exclusion de votre propre consommation. retour de puissance nette est ce qui est effectivement retourné au réseau d&apos;énergie via le compteur intelligent.'
    ), 
/* 100 */   array(
    'Dit overzicht geef de log bestanden weer die de P1-monitor aanmaakt. Kies uit het overzicht van <b>beschikbare log bestanden</b>. Klik op de regel en dan wordt onderaan de pagina voor het geselecteerde log bestand de inhoud weergegeven.<br><br>Met de knoppen <b>automatisch</b> vernieuwen worden de overzichten automatisch ververst.<br><br>Klik ergens in het overzichten en gebruik vervolgens de toetsencombinatie <b>ctrl + c</b> om de inhoud te kopiëren en ga vervolgens naar een spreadsheetprogramma zoals Excel om de inhoud daar in te plakken.<br><br>Met de download knoppen kan een kopie van het log bestand in verschillende formaten worden gemaakt.',
    'This overview shows the log files that the P1-monitor creates. Select from the list of <b> available log files </b>. Click on the line and the contents for the selected log file will be displayed at the bottom of the page. <br> <br> With the buttons <b> automatically </b> refresh the overviews automatically. <br> <br> Click anywhere in the overviews and then use the <b> ctrl + c </b> key combination to copy the content and then go to a spreadsheet program such as Excel to paste the content there. <br> <br> Using the download buttons a copy of the log file can be made in various formats.',
    'Cette vue d&apos;ensemble montre les fichiers journaux créés par le P1-monitor. Faites votre choix dans la liste des <b> fichiers journaux disponibles </b>. Cliquez sur la ligne et le contenu du fichier journal sélectionné sera affiché en bas de la page. <br> <br> Avec les boutons d&apos;actualisation <b> automatique </b>, les aperçus sont automatiquement actualisés.<br><br>Cliquez n&apos;importe où dans les aperçus, puis utilisez la combinaison de touches <b> ctrl + c </b> pour copier le contenu, puis accédez à un tableur tel qu&apos;Excel pour y coller le contenu.<br><br>Utilisation les boutons de téléchargement une copie du fichier journal peut être faite dans différents formats.'
),
/* 101 */   array(
    'Gegevens wel of niet naar de database kopieren voor de site ID.',
    'Whether or not to copy data to the database for the site ID.',
    'Que ce soit ou non pour copier des données à la base de données pour l&apos;ID du site.'
    ),
/* 102 */   array(
    'De datbase wissen voor de site ID','Erase the database for the site ID','Effacer la base de données pour l&apos;ID de site'
    ),
/* 103 */   array(
    'Hoofdscherm met overzicht van diverse gegevens.','Main screen with overview of various data.','Écran principal avec aperçu de diverses données.'
    ),
/* 104 */   array(
    'Actuele verbruik.','Current consumption.','Consommation de courant.'
    ),
/* 105 */   array(
    'kWh verbruik en levering per tijdsperiode.','kWh consumption and production per time period.','Consommation et production de kWh par période.'
    ),
/* 106 */   array(
    'kWh opgewekt en gemeten met een puls kWh (S0) meter.',
    'kWh generated and measured with a pulse kWh (S0) meter.',
    'kWh générée et mesurée avec un kWh d&apos;impulsions (S0) mètre.'
    ),
/* 107 */   array(
    'kWh opgewekt via de omvormer API.','kWh generated via the power inverter API.','kWh généré via l&apos;API de l&apos;onduleur de puissance.'
    ),
/* 108 */   array(
    'Aardgas verbruik per tijdsperiode.','Natural gas consumption per time period.','Consommation de gaz naturel par période.'
    ),
/* 109 */   array(
    'Drinkwater verbruik per tijdsperiode.','Drinking water consumption per time period.','Consommation d&apos;eau potable par période.'
    ),
/* 110 */   array(
    'Verwarmingstemperatuur per tijdsperiode.','Heating temperature per time period.','Température chauffage par période.'
    ),
/* 111 */   array(
    'Kosten per tijdsperiode.','Cost per time period.','Coût par période.'
    ),
/* 112 */   array(
    'Meterstanden per dag.','Meter readings per day.','Relevés de compteurs par jour.'
    ),
/* 113 */   array(
    'Fase gegevens.','Phase data.','Données de phase.'
    ),
/* 114 */   array(
    'Algemene systeem informatie.','General system information.','Informations générales sur le système'
    ),
/* 115 */   array(
    'Configuratie en instellingen.','Configuration and settings.','Configuration et paramètres.'
    ),
/* 116 */   array( // repeat 3 times the same because it is an explanation of the language settings.
    'De taal van gebruikersinterface is beperkt geïmplementeerd en wordt uitgebreid bij volgende versies. Dit is een grote en saaie hoeveelheid werk en kan enige tijd in beslag nemen. Mochten er fouten in de tekst zijn dan graag melden op www.ztatz.nl onder vermelding van de versie van de software.<br><br>The user interface language has a limited implementation and will be expanded in subsequent releases. This is a large and tedious amount of work and can take some time. If there are errors in the text, please report to www.ztatz.nl stating the version of the software. <br><br>La langue de l&apos;interface utilisateur a une implémentation limitée et sera développée dans les versions ultérieures. Il s&apos;agit d&apos;un travail important et fastidieux qui peut prendre un certain temps. S&apos;il y a des erreurs dans le texte, veuillez le signaler à www.ztatz.nl en indiquant la version du logiciel.',
    'De taal van gebruikersinterface is beperkt geïmplementeerd en wordt uitgebreid bij volgende versies. Dit is een grote en saaie hoeveelheid werk en kan enige tijd in beslag nemen. Mochten er fouten in de tekst zijn dan graag melden op www.ztatz.nl onder vermelding van de versie van de software.<br><br>The user interface language has a limited implementation and will be expanded in subsequent releases. This is a large and tedious amount of work and can take some time. If there are errors in the text, please report to www.ztatz.nl stating the version of the software. <br><br>La langue de l&apos;interface utilisateur a une implémentation limitée et sera développée dans les versions ultérieures. Il s&apos;agit d&apos;un travail important et fastidieux qui peut prendre un certain temps. S&apos;il y a des erreurs dans le texte, veuillez le signaler à www.ztatz.nl en indiquant la version du logiciel.',
    'De taal van gebruikersinterface is beperkt geïmplementeerd en wordt uitgebreid bij volgende versies. Dit is een grote en saaie hoeveelheid werk en kan enige tijd in beslag nemen. Mochten er fouten in de tekst zijn dan graag melden op www.ztatz.nl onder vermelding van de versie van de software.<br><br>The user interface language has a limited implementation and will be expanded in subsequent releases. This is a large and tedious amount of work and can take some time. If there are errors in the text, please report to www.ztatz.nl stating the version of the software. <br><br>La langue de l&apos;interface utilisateur a une implémentation limitée et sera développée dans les versions ultérieures. Il s&apos;agit d&apos;un travail important et fastidieux qui peut prendre un certain temps. S&apos;il y a des erreurs dans le texte, veuillez le signaler à www.ztatz.nl en indiquant la version du logiciel.'
    ),
/* 117 */   array(
    'opslaan','save','enregistrer'
    ),
/* 118 */   array(
    'herstel','revert','revenir'
    ),
/* 119 */   array(
    'loguit','logoff','logoff'
    ),
/* 120 */   array(
    'minuten','minutes','minutes'
    ),
/* 121 */   array(
    'uren', 'hours', 'heures'
    ),
/* 122 */   array('dagen','days', 'jours'
    ),
/* 123 */   array(
    'maanden', 'months','mois'
    ),
/* 124 */   array(
    'jaren','years','années'
    ),
/* 125 */ array(
    'opgewekte kWh minuten','kWh minutes produced','kWh produit minutes'
    ),
 /* 126 */ array(
    'kWh hoog tarief','kWh high tariff','kWh tarif élevé'
    ),
/* 127 */ array(
    'kWh laag tarief','kWh low tariff','kWh bas tarif'
    ),
/* 128 */ array(// minute abbr.
    'min','min','min'
    ),
/* 129 */ array(
    'uur','hour','heure'
    ),
/* 130 */ array(
    'dagen','days','jours'
    ),
/* 131 */ array(
    'maand','month','mois'
    ),
/* 132 */ array(
    'jaar','year','ans'
    ),
/* 133 */ array(
    'P1monitor historie minuten opgewekte kWh','P1monitor history minutes kWh produced','P1monitor historique minutes de produites de kWh'
    ),
/* 134 */ array(
    'P1monitor historie uren opgewekte kWh','P1monitor history of hours produced kWh','P1monitor historique des heures produites kWh'
    ),
/* 135 */ array(
    'dag','day','jour'
    ),
/* 136 */ array(
    'maximum temperatuur','maximum temperature','température maximale'
    ),
/* 137 */ array(
    'gemiddelde temperatuur','average temperature','température moyenne'
    ),
/* 138 */ array(
    'minimum temperatuur','minimum temperature','température minimale'
    ),
/* 139 */ array(
    'temperatuur','temperature','température'
    ),
/* 140 */ array(
    'totaal','total','total'
    ),
/* 141 */ array(
    'opgewekte kWh uren','kWh hours produced','kWh produit heures'
    ),
/* 142 */ array(
    'P1monitor historie dagen opgewekte kWh','P1monitor history of days produced kWh','P1monitor historique des jours produites kWh'
    ),
/* 143 */ array(
    'opgewekte kWh dagen','kWh days produced','kWh produit jours'
    ),
/* 144 */ array(
    'week','week','semaine'
    ),
/* 145 */ array(
    'opgewekte kWh maanden','kWh months produced','kWh produit mois'
    ),
/* 146 */ array(
    'opgewekte kWh jaren','kWh years produced','kWh produit ans'
    ),
/* 147 */ array(
    'P1monitor historie dagen opgewekte kWh','P1monitor history of days produced kWh','P1monitor historique des jours produites kWh'
    ),
/* 148 */ array(
        'Voor het gebruik van de gegevens is een API key nodig die bij SolarEdge aangevraagd kan worden.  Na het invoeren van de API key wordt alle beschikbare data van één of meerdere sites automatisch geladen. Dit kan wel een paar minuten duren afhankelijk van diverse factoren.<br><br>Als data volledig opnieuw via de API ingelezen moet worden dan kan dat met de herlaad optie. Ook geldt dat dit afhankelijk van het aantal sites en hoeveel data er verwerkt moet worden een paar tot 30 minuten duren. Als deze optie te vaak wordt gebruikt dan blokkeert de API wegens de beperking van maximaal 300 API verzoeken per dag.<br><br>De tabel geeft de site ID weer zoals SolarEdge die toewijst. De DB index wordt automatisch door de P1-monitor toegewezen en is voor normaal gebruik niet relevant. Deze is alleen nodig als de data via de P1-monitor API wil inlezen. Start en eind datum geven de tijdsduur waar de API data van heeft. Actief geeft de mogelijkheid voor een bepaalde site ID geen data meer op te halen. Wissen zal alle data in de P1-monitor database voor die site ID wissen.',
        'To use the data, an API key is required, which can be requested from SolarEdge. After entering the API key, all available data from one or more sites is automatically loaded. This can take up to a few minutes depending on various factors.<br><br>If data has to be reread in completely via the API, use the reload option. Depending on the number of sites and how much data has to be processed, this also takes a few to 30 minutes. If this option is used too often, the API may be blocked due to the limitation of a maximum of 300 API requests per day.<br><br>The table lists the site ID as assigned by SolarEdge. The DB index is automatically assigned by the P1-monitor and is not relevant for normal use. This is only necessary if you want to read in the data via the P1-monitor API.tart and end date indicate the length of time the API has data from. Active gives the option of no longer retrieving data for a specific site ID. Delete will delete all data in P1-monitor database for that site ID.',
        'Pour utiliser les données, une clé API est requise, qui peut être demandée à SolarEdge. Après avoir entré la clé API, toutes les données disponibles ds&apos;un ou plusieurs sites sont automatiquement chargées. Cela peut prendre jusqus&apos;à quelques minutes en fonction de divers facteurs.<br><br>Si les données doivent être entièrement lues via ls&apos;API, cela est possible avec ls&apos;option de rechargement. En fonction du nombre de sites et de la quantité de données à traiter, cela prend également de quelques à 30 minutes. Si cette option est utilisée trop souvent, bloquez ls&apos;API en raison de la limitation ds&apos;un maximum de 300 requêtes ds&apos;API par jour.<br><br>Le tableau répertorie ls&apos;ID de site attribué par SolarEdge. Ls&apos;index DB est automatiquement attribué par le moniteur P1 et ns&apos;est pas pertinent pour une utilisation normale. Cela ns&apos;est nécessaire que si vous souhaitez lire les données via ls&apos;API du moniteur P1. Les dates de début et de fin indiquent la durée pendant laquelle ls&apos;API dispose de données. Actif donne la possibilité de ne plus récupérer les données pour un ID de site spécifique. Supprimer supprimera toutes les données de la base de données du moniteur P1 pour cet ID de site.'
        ),
/* 149 */ array(
    'De SolarEdge API key','The SolarEdge API key','La clé API SolarEdge'
    ),
/* 150 */ array(
    'Gegevens wel of niet verwerken.  ',
    'Whether or not to process data.',
    'Traiter ou non les données.'
    ),
/* 151 */ array(
    'De optie haalt alleen data op in de periode van 06: 00 – 21:59 gegevens via de API op omdat in de meeste gevallen er geen energie wordt opgewekt. Dit beperkt het aantal  keren dat de SolarEdge API gebruikt wordt. De heeft geen gevolgen voor juistheid van de gegevens die worden bij eerst volgende keer dat de API wordt gebruikt aangevuld.',
    'The option only retrieves data in the period from 06:00 - 21:59 data via the API because in most cases no energy is generated. This limits the number of times the SolarEdge API is used. This has no effect on the correctness of the data that will be completed the next time the API is used.',
    'Ll&apos;option récupère uniquement les données de la période de 06h00 à 21h59 via ll&apos;API car dans la plupart des cas, aucune énergie nl&apos;est générée. Cela limite le nombre de fois où ll&apos;API SolarEdge est utilisée. Cela nl&apos;a aucun effet sur ll&apos;exactitude des données qui seront complétées la prochaine fois que ll&apos;API sera utilisée.'
    ),
/* 152 */ array(
    'Laad alle data die de API kan leveren opnieuw in. Dit overschrijft de database voor die tijdstippen die al in de database zijn opgeslagen.',
    'Reload all data that the API can provide. This will overwrite the database for those times that are already stored in the database.',
    'Rechargez toutes les données que ll&apos;API peut fournir. Cela écrasera la base de données pour les heures qui sont déjà stockées dans la base de données.'
    ),
/* 153 */ array(
    'Wis de configuratie gegevens (niet de database gegevens) en lees de configuratie opnieuw in.',
    'Delete the configuration data (not the database data) and read the configuration again.',
    'Supprimez les données de configuration (pas les données de la base de données) et relisez la configuration.'
    ),
/* 154 */ array(
    'De SolarEdge API heeft geen tarief informatie (hoog/laag/piek/dal). De P1-monitor gebruikt deze optie om historische gegevens zo goed als mogelijk het juiste tarief te geven.',
    'The SolarEdge API has no tariff information (high / low / peak / valley). The P1-monitor uses this option to give historical data the correct tariff as best as possible.',
    'L&apos;API SolarEdge ne contient aucune information tarifaire (haut / bas / pic / vallée). Le moniteur P1 utilise cette option pour donner aux données historiques le meilleur taux possible'
    ),
/* 155 */ array(
    'hulp','help','aider'
    ),
/* 156 */ array(
    'Laatste gefaalde API aanvraag:','Last failed API request:','Dernière demande API a échoué:'
    ),
/* 157 */ array(
    'Laatste succesvolle API verwerking:','Latest successful API call:','Dernier traitement d&apos;API réussi:'
    ),
/* 158 */ array(
    'Solar Edge API configuratie','Solar Edge API configuration','Configuration de l&apos;API Solar Edge'
    ),
/* 159 */ array(
    'API status','API status','État de l&apos;API'
    ),
/* 160 */ array(
    'Solar Edge verwerking actief','Solar Edge processing active','Traitement Solar Edge actif'
    ),
/* 161 */ array(
    'slimme API updates','smart API updates','intelligentes mises à jour de l&apos;API'
    ),
/* 162 */ array(
    'Herlaad alle data (API)','Reload all data (API))','Recharger toutes les données (API)'
    ),
/* 163 */ array(
    'Reset de site configuratie','Reset the site configuration','Réinitialiser la configuration du site'
    ),
/* 164 */ array(
    'Hoog/piek - laag/dal tarief','High - low tariff','Haut - bas tarif'
    ),
/* 165 */ array(
    'geen aanpassing','no adjustment','pas de réglage'
    ),
/* 166 */ array(
    'hoog tarief weekdagen 07:00 - 23:00','high tariff weekdays 07:00 - 23:00','taux élevé en semaine de 07:00 à 23:00'
    ),
/* 167 */ array(
    'hoog tarief weekdagen 07:00 - 21:00','high rate weekdays 07:00 - 21:00','taux élevé en semaine de 7:00 à 21:00'
    ),
/* 168 */ array(
    'site ID','site ID','ID du site'
    ),
/* 169 */ array(
    'DB index','DB index','index DB'
    ),
/* 170 */ array(
    'start','start','début'
    ),
/* 171 */ array(
    'eind','end','fin'
    ),
/* 172 */ array(
    'actief','active','actif'
    ),
/* 173 */ array(
    'wissen','delete','supprimez'
    ),
/* 174 */ array(
    'de-activeren van pagina&apos;s','deactivating pages','désactivation des pages'
    ),
/* 175 */ array(
    'waarden instellen UI elementen','set values of UI elements','définir les valeurs des éléments de l&apos;interface'
    ),
/* 176 */ array(
    'eigen user interface gebruiken','use your own user interface','utilisez votre propre interface utilisateur'
    ),
/* 177 */ array(
    'diversen','miscellaneous','divers'
    ),
/* 178 */ array(
    'screensaver','screensaver','économiseur d&apos;écran'
    ),
/* 179 */ array(
    'UI labels','UI labels','étiquettes UI'
    ),
/* 180 */ array(
    'inschakeltijd','switch-on time','heure de mise en marche'
    ),
/* 181 */ array(
    'uitschakeltijd','switch-off time','heure de coupure'
    ),
/* 182 */ array(
    'elektriciteit & gas levering / verbruik','electricity & gas production / consumption','prod. / consom. d&apos;électricité et de gaz'
    ),
/* 183 */ array(
    'elektriciteit historie','electricity history','historique de l&apos;électricité'
    ),
/* 184 */ array(
    'gas historie','gas history','histoire gaz'
    ),
/* 185 */ array(
    'financiële historie','financial history','histoire financière'
    ),
/* 186 */ array(
    'systeem informatie','system information','informations système'
    ),
/* 187 */ array(
    'verwarming','heating','chauffage'
    ),
/* 188 */ array(
    'meterstanden historie','meter reading history','historique des relevés de compteurs'
    ),
/* 189 */ array(
    'water meter','water meter','compteur d&apos;eau'
    ),
/* 190 */ array(
    'opwekking (levering) kWh (S0)','production (supply) kWh (S0)','production (fourniture) kWh (S0)'
    ),
/* 191 */ array(
    'opwekking (levering) kWh (Solar Edge)','production (supply) kWh (Solar Edge)','production (fourniture) kWh (Solar Edge)'
    ),
/* 192 */ array(
    'aan','on','marche'
    ),
/* 193 */ array(
    'uit','off','arrêt'
    ),
/* 194 */ array(
    'seconden','seconds','secondes'
    ),
/* 195 */ array(
    'max. waarde e-levering','max. value e-delivery','valeur max. e-livraison'
    ),
/* 196 */ array(
    'max. dagwaarde e-levering','max. daily value of e-production','max. valeur quotidienne de l&apos;e-production'
    ),
/* 197 */ array(
    'max. waarde e-verbruik','max. value e-consumption','e-consommation valeur max.'
    ),
/* 198 */ array(
    'max. dagwaarde e-verbruik','max. day value e-consumption','max. e-consommation valeur journalière'
    ),
/* 199 */ array(
    'max. waarde gas verbruik','max. value gas consumption','max. consom. de gaz de valeur.'
    ),
/* 200 */ array(
    'max. fase meters','max. phase meters','compteurs de phase max.'
    ),
/* 201 */ array(
    'verwarming IN alternatief','heating input alternative','chauffage en alternative'
    ),
/* 202 */ array(
    'verwarming uit alternatief','heating output alternative','alternatif de sortie de chauffage'
    ),
/* 203 */ array(
    'P1-monitor interface gebruiken (standaard)','Use P1-monitor interface (default)','Utiliser l&apos;interface de contrôle P1 (par défaut)'
    ),
/* 204 */ array(
    'eigen user interface gebruiken.','use your own user interface.','utilisez votre propre interface utilisateur.'
    ),
/* 205 */ array(
    'voorspelling aan in de UI','prediction active in the UI','prédiction active dans l&apos;interface utilisateur'
    ),
/* 206 */ array(
    'drie fasen informatie tonen','show three phases information','afficher des informations trois phases'
    ),
/* 207 */ array(
    'P1-monitor header verbergen','Hide P1-monitor page header','masquer l&apos;en-tête de la page du moniteur P1'
    ),
/* 208 */ array(
    'tarief','tariff','tarif'
    ),
/* 209 */ array(
    'systeem','system','système'
    ),
/* 210 */ array(
    'database','database','database'
    ),
/* 211 */ array(
    'in-export','in-export','en-export'
    ),
/* 212 */ array(
    'P1 poort','P1 port','port P1'
    ),
/* 213 */ array(
    'netwerk','network','réseau'
    ),
/* 214 */ array(
    'display','display','afficher'
    ),
/* 215 */ array(
    'back-up','backup','sauveg.'
    ),
/* 216 */ array(
    'security','security','sécurité'
    ),
/* 217 */ array(
    'weer','weather','temps'
    ),
/* 218 */ array(
    'notificatie','notification','notification'
    ),
/* 219 */ array(
    'in-output','in-output','in-output'
    ),
/* 220 */ array(
    'water','water','l&apos;eau'
    ),
/* 221 */ array(
    'exit','exit','fermer'
    ),
/* 222 */ array(
    'logging','logging','log'
    ),
/* 223 */ array(
    'Alles wissen (fabrieksinstelling)','Clear all (factory setting)','Effacer tout (réglage d&apos;usine)'
    ),
/* 224 */ array(
    'Alle configuratie en database gegevens wissen.',
    'Delete all configuration and database data.',
    'Effacez toutes les données de configuration et de base de données.'
    ),
/* 225 */ array(
    'Netwerk configuratie','Network configuration','Configuration réseau'
    ),
/* 226 */ array(
    'wachtwoord','password','mot de passe'
    ),
/* 227 */ array(
    'Internet bereikbaar','Internet accessible','Internet accessible'
    ),
/* 228 */ array(
    'Internet IP adres','Internet IP address','Adresse IP Internet'
    ),
/* 229 */ array(
    'Internet DNS naam','Internet DNS name','Nom DNS Internet'
    ),
/* 230 */ array(
    'Internet timestamp','Internet timestamp','Horodatage Internet'
    ),
/* 231 */ array(
    'LAN IP adres','LAN IP address','Adresse IP LAN'
    ),
/* 232 */ array(
    'LAN host naam','LAN host name','Nom d&apos;hôte LAN'
    ),
/* 233 */ array(
    'wifi IP adres','wifi  IP address','Adresse IP wifi'
    ),
/* 234 */ array(
    'netwerk status','network status','état du réseau'
    ),
/* 235 */ array(
    'publieke domein naam (DNS)','public domain name (DNS)','nom de domaine public (DNS)'
    ),
/* 236 */ array(
    'forceer update','force update','forcer la mise'
    ),
/* 237 */ array(
    'De publieke domein naam wordt gebruikt als DNS naam waarmee de P1-monitor gevonden kan worden op het Internet. De koppeling van de naam met het publieke IP adres kan manueel worden gedaan door de aanschaf van een domeinnaam of door gebruik  te maken van diensten zoals DuckDNS.',
    'The public domain name is used as the DNS name with which the P1-monitor can be found on the Internet. The linking of the name with the public IP address can be done manually by purchasing a domain name or by using  services such as DuckDNS.',
    'Le nom de domaine public est utilisé comme nom DNS avec lequel le moniteur P1 peut être trouvé sur Internet. La liaison du nom avec l&apos;adresse IP publique peut se faire manuellement en achetant un nom de domaine ou en utilisant les services suivants tels que DuckDNS.'
    ),
/* 238 */ array(
    'DuckDNS is een gratis dienst waarmee je een IP adres dat je van je ISP krijgt kan koppelen aan een domeinnaam. Je moet je aanmelden bij <a href=\'https://www.duckdns.org/\' target=\'_blank\'> www.duckdns.org </a> na het aanmaken van de DNS naam moet het token van de pagina in het veld token worden ingevoerd. Het IP adres wordt 1 maal per zes uur gecontroleerd.',
    'DuckDNS is a free service that allows you to link an IP address you get from your ISP to a domain name. You must log in to <a href=\'https://www.duckdns.org/\' target=\'_blank\'> www.duckdns.org </a> after creating the DNS name the token must be inserted into the token field. The IP address is checked once every six hours.',
    'DuckDNS est un service gratuit qui vous permet de lier une adresse IP que vous obtenez d&apos;un FAI à un nom de domaine. Vous devez vous connecter à <a href=\'https://www.duckdns.org/\' target=\'_blank\'> www.duckdns.org </a> après avoir créé le nom DNS auquel le jeton doit appartenir la page dans le champ du jeton. L&apos;adresse IP est vérifiée toutes les six heures.'
    ),
/* 239 */ array(
    'Dit is de domeinnaam waarmee de API via internet te bereiken is.',
    'This is the domain name with which the API can be reached via the Internet.',
    'Il s&apos;agit du nom de domaine avec lequel l&apos;API est accessible via Internet.'
    ),
/* 240 */ array(
    'Het DuckDNS authenticatie token, nodig om de DNS naam te koppelen aan het IP publieke IP adres. ',
    'The DuckDNS authentication token, needed to map the DNS name to the IP public IP address.',
    'Le jeton d&apos;authentification DuckDNS, nécessaire pour mapper le nom DNS à l&apos;adresse IP publique IP.'
    ),
/* 241 */ array(
    'automatische updates aan of uit.',
    'automatic updates on or off.',
    'mises à jour automatiques activées ou désactivées.'
    ),
/* 242 */ array(
    'Eenmalig geforceerd updaten.','Forced one-time update.','Mise à jour unique forcée.'
    ),
/* 243 */ array(
    'Met deze optie wordt zo snel als mogelijke P1 telegrammen verwerkt. Oude meters geven elke 10 seconde een telegram. Nieuwe meters kunnen elke seconde een telegram sturen. Het voordeel van het activeren van deze optie is dat er zo goed al direct gegevens worden weergegeven. Dit is echter ook een groter belasting voor de Rpi en voor de database opslag.  Indien er problemen optreden of er data wegvalt dan wordt aanbevolen deze optie niet te gebruiken.',
    'With this option, P1 telegrams are processed as quickly as possible. Old meters send a telegram every 10 seconds. New meters can send a telegram every second. The advantage of activating this option is that data is almost immediately displayed. However, this is also a greater load on the Rpi and on the database storage. If problems occur or data is lost, it is recommended not to use this option.',
    'Avec cette option, les télégrammes P1 sont traités le plus rapidement possible. Les anciens compteurs envoient un télégramme toutes les 10 secondes. Les nouveaux compteurs peuvent envoyer un télégramme toutes les secondes. L&apos;avantage d&apos;activer cette option est que les données sont presque immédiatement affichées. Cependant, cela représente également une charge plus importante sur le Rpi et sur le stockage de la base de données. En cas de problème ou de perte de données, il est recommandé de ne pas utiliser cette option.'
    ),
/* 244 */ array(
    'P1-poort configuratie','P1 port configuration','Configuration du port P1'
    ),
/* 245 */ array(
    'seriële instellingen','serial settings','paramètres série'
    ),
/* 246 */ array(
    'status','status','condition'
    ),
/* 247 */ array(
    'P1 telegram','P1 telegram','Télégramme P1'
    ),
/* 248 */ array(
    'Seriële device in gebruik:','Serial device in use:','Périphérique série utilisé :'
    ),
/* 249 */ array(
    'gas code nummer','gas code number','numéro de code gaz'
    ),
/* 250 */ array(
    'crc controle aan','crc control on','control crc activado'
    ),
/* 251 */ array(
    'dag/nacht mode','day/night mode','mode jour/nuit'
    ),
/* 252 */ array(
    'maximale verwerkingssnelheid','maximum processing speed','vitesse de traitement maximale'
    ),
/* 253 */ array(
    'moment van laagste verbruik.','moment of lowest consumption.','moment de plus faible consommation.'
    ),
/* 254 */ array(
    'moment van hoogste levering.','moment of highest production.','moment de la production la plus élevée.'
    ),
/* 255 */ array(
    'moment van laagste levering.','moment of lowest production.','moment de la plus faible production.'
    ),
/* 256 */ array(
    'verbergen van water gegevens.','hide water data.','cacher les données d&apos;eau.'
    ),
/* 257 */ array(
    'verbergen van gas gegevens.','hide gas data.','cacher les données de gaz.'
    ),
/* 258 */ array(
    'wis het token.','delete the token.','supprimer le token.'
    ),
/* 259 */ array(
    'API configuratie','API configuration','Paramétrage de l&apos;API'
    ),
/* 260 */ array(
    'API authenticatie tokens','API authentication tokens','Token d&apos;authentification API'
    ),
/* 261 */ array(
    'API lijst','API list','Liste des API'
    ),
/* 262 */ array(
    'voeg een nieuw token toe.','add a new token.','ajouter un nouveau token.'
    ),
/* 263 */ array(
    'API authenticatie tokens worden gebruikt voor toegang via het Internet. Tokens zijn alleen nodig indien de API wordt gebruikt voor internet toegang of in de toekomst voor de IOS app.',
    'API authentication tokens are used for access over the Internet. Tokens are only needed if the API is used for internet access or in the future for the IOS app',
    'Les Tokens d&apos;authentification API sont utilisés pour l&apos;accès sur Internet. Les jetons ne sont nécessaires que si l&apos;API est utilisée pour l&apos;accès à Internet ou à l&apos;avenir pour l&apos;application IOS.'
    ),
/* 264 */ array(
    'Meer dan 25 tokens wordt afgeraden om snelheid van de API niet te beperken. Toevoegen heeft verder geen consequenties.',
    'More than 25 tokens is not recommended in order not to limit the speed of the API. Adding has no further consequences.',
    'Plus de 25 tokens n&apos;est pas recommandé afin de ne pas limiter la vitesse de l&apos;API. L&apos;ajout n&apos;a pas d&apos;autres conséquences.'
    ),
/* 265 */ array(
    'API via het Internet actief','API operates through the Internet','API active sur Internet'
    ),
/* 266 */ array(
    'HTTPS certificaat','HTTPS certificate','Certificat HTTPS'
    ),
/* 267 */ array(
    'Automatisch vernieuwen certificaat','Automatically renew certificate','Renouveler automatiquement le certificat'
    ),
/* 268 */ array(
    'Webserver configuratie','Webserver configuration','Configuration du serveur Web'
    ),
/* 269 */ array(
    'onbekend','unknown','inconnu'
    ),
/* 270 */ array(
    'e-mail voor de certificate authority','email for the certificate authority','email pour l&apos;autorité de certification'
    ),
/* 271 */ array(
    'Tijdstip laatste succesvolle certificaat vernieuwing',
    'Time of last successful certificate renewal',
    'Heure du dernier renouvellement de certificat réussi'
    ),
/* 272 */ array(
    'Certificaat geldig tot','Certificate valid until','Certificat valable jusqu&apos;au'
    ),
/* 273 */ array(
    'Het IP adres van de ethernet (kabel) aansluiting van de Rpi. Een leeg veld verwijderd het vaste IP adres.',
    'The IP address of the Ethernet (cable) connection of the Rpi. An empty field removes the fixed IP address.',
    'L&apos;adresse IP de la connexion Ethernet (câble) du Rpi. Un champ vide supprime l&apos;adresse IP fixe.'
    ),
/* 274 */ array(
    'Het IP adres van de WiFi aansluiting van de Rpi. Een leeg veld verwijderd het vaste IP adres.',
    'The IP address of the WiFi connection of the Rpi. An empty field removes the fixed IP address.',
    'L&apos;adresse IP de la connexion WiFi du Rpi. Un champ vide supprime l&apos;adresse IP fixe.'
    ),
/* 275 */ array(
    'Het IP adres van de router of meer formeel de “default gateway”.',
    'The IP address of the router or more formally the “default gateway”.',
    'L&apos;adresse IP du routeur ou plus formellement la “default gateway”.'
    ),
/* 276 */ array(
    'Het IP adres van de DNS server, dit is meestal gelijk aan het IP adres van router',
    'The IP address of the DNS server, which is usually the same as the IP address of the router.',
    'L&apos;adresse IP du serveur DNS, qui est généralement la même que l&apos;adresse IP du routeur.'
    ),
/* 277 */ array(
    'IP adres eth0','IP address eth0','Adresse IP eth0'
    ),
/* 278 */ array(
    'IP adres wlan0','IP address wlan0','Adresse IP wlan0'
    ),
/* 279 */ array(
    'IP adres router','IP address router','Routeur IP address'
    ),
/* 280 */ array(
    'IP adres DNS server','IP address DNS router','Adresse IP routeur DNS'
    ),
/* 281 */ array(
    'Vast IP adres','Fixed IP address','Adresse IP fixe'
    ),
/* 282 */ array(
    'Vast IP adres: <span style = "color: red">Waarschuwing! </span> de voorkeur methode is static binding via de DHCP server van je router. Niet deze optie. Als je een fout maakt met de IP adressen dan kun effectief je zelf buiten sluiten omdat de Rpi niet meer bereikbaar is. Controleer de adressen dus extra voordat je deze opslaat.',
    'Fixed IP address: <span style = "color: red">Warning! </span> the preferred method is static binding via your router&apos;s DHCP server, not this option. If you make a mistake with the IP addresses you can effectively exclude you because Rpi is inaccessible. So check the addresses extra before you save them.',
    'Adresse IP fixe: <span style = "color: red">Attention!</span> la méthode préférée est la liaison statique via le serveur DHCP de votre routeur, pas cette option. Si vous faites une erreur avec les adresses IP, vous pouvez effectivement vous exclure car Rpi est inaccessible. Vérifiez donc les adresses avant de les enregistrer.'
    ),
/* 283 */ array(
    'extra informatie','additional information','informations supplémentaires'
    ),
/* 284 */ array(
    'laat de QR code zien voor het instellen van de API in de app.',
    'show the QR code for setting the API in the app.',
    'afficher le code QR pour configurer l&apos;API dans l&apos;app.'
    ),
/* 285 */ array(
    'klik om te sluiten','click to close','cliquez pour fermer'
    ),
/* 286 */ array(
    '','',''
    ),




);




    $language_index = languageIndex();

    if(!isset($arr[ $_index  ][ $language_index ] ) ) {
        return '<span style = "color: red">tekst voor index '. $_index . ' niet gevonden! Meld dit op www.ztatz.nl.</span>';
    } else {
        return $arr[ $_index ][ $language_index ];
    }

}

function languageIndex() {

    $language_index = config_read(148 );
     
    if(!isset($language_index) ) {
        $language_index = 0; // FAILSAVE does the job for index numbers to high
    }
    return $language_index;
}

?>