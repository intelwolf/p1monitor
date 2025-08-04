
// array starts at 0
const selectorLanguageArr = [

/* 0   */ ["gemiddelde", "average", "moyenne"],
/* 1   */ ["maximum", "maximum", "maximum"],
/* 2   */ ["minimum", "minimum", "minimum"],
/* 3   */ ["som", "sum", "somme"],
/* 4   */ ["kWh min. verbruik", "kWh min. consumption", "kWh min. consommation"],
/* 5   */ ["kWh uur verbruik", "kWh hour consumption", "consommation horaire en kWh"],
/* 6   */ ["kWh dag verbruik", "kWh day consumption", "consommation quotidienne en kWh"],
/* 7   */ ["kWh maand verbruik", "kWh month consumption", "consommation mensuelle en kWh"],
/* 8   */ ["kWh jaar verbruik", "kWh annual consumption", "consommation annuelle en kWh"],
/* 9   */ ["kWh min. levering", "kWh min. production", "kWh production min."],
/* 10  */ ["kWh uur levering", "kWh hour production", "kWh de production horaire"],
/* 11  */ ["kWh dag levering", "kWh day production", "kWh de production journalière"],
/* 12  */ ["kWh maand levering", "kWh month production", "kWh de production mensuelle"],
/* 13  */ ["kWh jaar levering", "kWh annual production", "kWh de production annuelle"],
/* 14  */ ["gas uur", "gas hour", "heure de gaz"],
/* 15  */ ["gas dag", "gas day", "journée du gaz"],
/* 16  */ ["gas maand", "gas month", "mois du gaz"],
/* 17  */ ["gas jaar", "gas year", "gaz annuel"],
/* 18  */ ["water minuut", "water minute", "minute d'eau"],
/* 19  */ ["water uur", "water hour", "heure de l'eau"],
/* 20  */ ["water dag", "water day", "journée de l'eau"],
/* 21  */ ["water maand", "water month", "mois de l'eau"],
/* 22  */ ["water jaar", "water year", "water annuel"],

];


function getString( arr, index, languageIndex ) {

    //console.log("languageIndex = ", languageIndex, " index = ", index );
    if ( languageIndex > 2 ) {
        return "error 1";
    }
    if ( index > ( arr.length -1) || index < 0 ) {
        return "error 2";
    }
    str = arr[index][languageIndex];
    return str;
}


function selectorTextToMode( text, languageIndex=0 ) {

        switch( text ) {
            case getString( selectorLanguageArr, 0, languageIndex):
                return 1;
                break;
            case getString( selectorLanguageArr, 1, languageIndex):
                return 2
                break;
            case getString( selectorLanguageArr, 2, languageIndex):
                return 3
                break;
            case getString( selectorLanguageArr, 3, languageIndex):
                return 4
                break;
            default:
                return 0
        }
}

function selectorModeToText( mode=0, languageIndex=0 ) {

    switch( mode ) {
        case 1:
            return getString( selectorLanguageArr, 0, languageIndex);
        case 2:
            return getString( selectorLanguageArr, 1, languageIndex);
        case 3:
            return getString( selectorLanguageArr, 2, languageIndex);
        case 4:
            return getString( selectorLanguageArr, 3, languageIndex);
        default:
            return "???"
    }

}

function selectorTypeToText( type=0 , languageIndex=0) {

    switch( type ) {
        case 1:
            //return "kWh min. verbruik";
            return getString( selectorLanguageArr, 4, languageIndex);
        case 2:
            //return "kWh uur verbruik";
            return getString( selectorLanguageArr, 5, languageIndex);
        case 3:
            // return "kWh dag verbruik";
            return getString( selectorLanguageArr, 6, languageIndex);
        case 4:
            //return "kWh maand verbruik";
            return getString( selectorLanguageArr, 7, languageIndex);
        case 5:
            //return "kWh jaar verbruik";
            return getString( selectorLanguageArr, 8, languageIndex);
        case 6:
            //return "kWh min. levering";
            return getString( selectorLanguageArr, 9, languageIndex);
        case 7:
            //return "kWh uur levering";
            return getString( selectorLanguageArr, 10, languageIndex);
        case 8:
            //return "kWh dag levering";
            return getString( selectorLanguageArr, 11, languageIndex);
        case 9:
           //return "kWh maand levering";
            return getString( selectorLanguageArr, 12, languageIndex);
        case 10:
            //return "kWh jaar levering";
            return getString( selectorLanguageArr, 13, languageIndex);
        case 11:
            //return "gas uur";
            return getString( selectorLanguageArr, 14, languageIndex);
        case 12:
            //return "gas dag";
            return getString( selectorLanguageArr, 15, languageIndex);
        case 13:
            //return "gas maand";
            return getString( selectorLanguageArr, 16, languageIndex);
        case 14:
            //return "gas jaar";
            return getString( selectorLanguageArr, 17, languageIndex);
        case 15:
            //return "water minuut";
            return getString( selectorLanguageArr, 18, languageIndex);
        case 16:
            //return "water uur";
            return getString( selectorLanguageArr, 19, languageIndex);
        case 17:
            //return "water dag";
            return getString( selectorLanguageArr, 20, languageIndex);
        case 18:
           //return "water maand";
            return getString( selectorLanguageArr, 21, languageIndex);
        case 19:
           // return "water jaar";
            return getString( selectorLanguageArr, 22, languageIndex);
        default:
            console.log("error = ", type );
            return "???"
    }

}


function selectorTextToType( text, languageIndex=0 ) {

    switch( text ) {
        case getString( selectorLanguageArr, 4, languageIndex):
            return 1
        case getString( selectorLanguageArr, 5, languageIndex):
            return 2;
        case getString( selectorLanguageArr, 6, languageIndex):
            return 3
        case getString( selectorLanguageArr, 7, languageIndex):
            return 4;
        case getString( selectorLanguageArr, 8, languageIndex):
            return 5;
        case getString( selectorLanguageArr, 9, languageIndex):
            return 6;
        case getString( selectorLanguageArr, 10, languageIndex):
            return 7;
        case getString( selectorLanguageArr, 11, languageIndex):
            return 8;
        case getString( selectorLanguageArr, 12, languageIndex):
            return 9;
        case getString( selectorLanguageArr, 13, languageIndex):
            return 10;
        case getString( selectorLanguageArr, 14, languageIndex):
            return 11;
        case getString( selectorLanguageArr, 15, languageIndex):
            return 12;
        case getString( selectorLanguageArr, 16, languageIndex):
            return 13;
        case getString( selectorLanguageArr, 17, languageIndex):
            return 14;
        case getString( selectorLanguageArr, 18, languageIndex):
            return 15;
        case getString( selectorLanguageArr, 19, languageIndex):
            return 16;
        case getString( selectorLanguageArr, 20, languageIndex):
            return 17;
        case getString( selectorLanguageArr, 21, languageIndex):
            return 18;
        case getString( selectorLanguageArr, 22, languageIndex):
            return 19;
        default:
            return 0
    }

}