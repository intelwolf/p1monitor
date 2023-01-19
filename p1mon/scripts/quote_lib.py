import random

def get_quote( ):
   #print ( len(quoteStrings) )
   try:
        return quoteStrings[ random.randrange( 0, len(quoteStrings)-1, 1 )]
   except:
       #return default when things go wrong.
       return quoteStrings[0]

# list of quotes.
quoteStrings = [
    'Wie ooit gezegd heeft dat technologie papier zal vervangen, heeft vast en zeker nooit zijn billen afgeveegd met een iPad',
    'Als het eten van chocolade een sport zou zijn, was ik een atleet',
    'Een optimist heeft het vliegtuig uitgevonden, een pessimist de parachute',
    'Vannacht om half 3 belde mijn buurman aan de deur! Hoe gek is dat, hij had geluk dat ik nog aan het drummen was.',
    'Ik heb geen wespentaille, ik heb hommelheupen',
    'Ik weet dat ik gewicht moet verliezen, maar ik kan alleen niet zo goed tegen mijn verlies',
    'Een waterlelie is een levensgevaarlijke plant, want als je er langer dan vijf minuten onder zit, ben je dood.', 
    'Wie zwijgt stemt niet altijd toe, want soms hebben ze geen zin om met idioten te discussiëren.', 
    'Je waardeert pas wat je hebt, tot je het mist, zoals toiletpapier.',
    'Als je niet blij bent met wat je hebt, wees dan blij met wat je allemaal gelukkig niet hebt.',
    'Ik ben niet lui, ik bespaar gewoon energie.',
    'Wees jezelf want een origineel is altijd meer waard dan een kopie.',
    'Een pessimist is een optimist met ervaring.',
    'Geen pech hebben, is al mazzel genoeg.',
    'Wacht niet op een goede dag, maak er een.',
    'Ik ben niet klein, ze hadden gewoon minder nodig om mij fantastisch te maken.',
    'Een dwaas doet wat hij niet laten kan, een wijze laat wat hij niet kan doen.',
    'Doe liever weinig goed, dan veel fout.',
    'Er zijn 3 soorten mensen in de wereld: diegenen die er voor zorgen dat er iets gebeurd, diegenen die kijken naar hoe dingen gebeuren en diegenen die zich afvragen wat er gebeurd is.',
    'Ik ben niet onhandelbaar, ik ben gewoon een uitdaging.',
    'Ik ben niet eigenwijs, mijn manier is gewoon beter.',
    'Aanvaard wat je niet veranderen kan, maar verander dat wat je niet aanvaarden kan.',
    'Soms merken mensen de dingen die we voor hen doen niet op, tot we er mee stoppen.',
    'Mensen zijn niet lastig, mensen zijn verschillend, dat is best lastig.',
    'Niemand is perfect, maar sommigen laten het wel heel erg merken.',
    'Wees altijd een eersteklas versie van jezelf, in plaats van een tweederangs versie van iemand anders.',
    'Je bent niet verantwoordelijk voor het hoofd dat je gekregen hebt, maar wel voor het gezicht dat je trekt.',
    'Wie geen fouten maakt, maakt meestal niets',
    'Een negatieve houding is als een lekke band; je komt er nergens mee tenzij je hem vervangt.',
    'Je zult nooit tijd vinden, je zult tijd moeten maken.',
    'Zij die achter mijn rug om spreken, staan op de juiste plek om mijn kont te kussen.',
    'Doe wat je zegt en zeg wat je doet.',
    'Als je tot je nek in de shit zit, laat dan je hoofd niet hangen.',
    'Vroeger was ik een twijfelaar, ik ben daar nu niet meer zo zeker van.',
    'Er zijn 3 dingen die ik altijd vergeet, namen, gezichten en nog iets...',
    'Godzijdank ben ik atheïst',
    'Als je voet slaapt, kun je geen herrie schoppen.',
    'Een hypnotiseur is iemand die net zolang zeurt, tot je in slaap valt.',
    'Ik heb ze nog steeds alle 5 op een rij, ze werken alleen in ploegendiensten.',
    'Hersens zijn geweldig, ik wou dat iedereen er had.',
    'Een verhaal heeft altijd 3 kanten, mijn kant, jouw kant en de waarheid.',
    'Ik zou meer van de ochtend houden als die later zou beginnen',
    'Geduld is een schone zaak, maar je moet er wel de tijd voor hebben.',
    'Het leven is duurder geworden, maar heb je gemerkt hoe populair het nog steeds is?',
    'Het leven kan alleen achterwaarts begrepen worden, maar het moet voorwaarts worden geleefd.',
    'De beste manier om de toekomst te voorspellen is haar zelf te creëren.',
    'Tijdreizen doen wel al, het is alleen eenrichtingsverkeer.',
    'Een koude wc bril is balen, maar een warme wc bril is gewoon eng.',
    'Niemand is volstrekt waardeloos, hij/zij kan altijd nog als slecht voorbeeld dienen.',
    'Ik heb alles wel op een rijtje, maar niet in de goede volgorde.',
    'Hoe lang een minuut duurt, hangt er van af aan welke kant van de wc-deur je je bevindt.',
    'Spoed komt meestal door voorafgaande traagheid.',
    'Als je ontbijt op bed wil, slaap je maar in de keuken.',
    'Wat is het verschil tussen onwetendheid en onverschilligheid? Ik weet het niet en het kan me ook niet schelen.',
    'Een verrekijker vergroot 8 maal, maar toen ik hem de 9e keer gebruikte, deed hij het gewoon.',
    'Je moet de mening van een meerderheid niet verwarren met de waarheid.',
    'Wees lief tegen je kinderen zij kiezen later je tehuis uit.',
    'Als je minder wil dan heb je meer',
    'Een goed beschreven probleem is voor de helft opgelost.',
    'Echte domheid verslaat kunstmatige intelligentie elke keer.'
]