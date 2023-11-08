
function setFaseHorizontalOrVertical() {
    var current_page = localStorage.getItem("phase-actual-orientation");
    console.log("clicked = " + current_page )
    if ( current_page == '/fase-a-v.php') {
        window.location.replace('/fase-a-h.php');
    } else {
        window.location.replace('/fase-a-v.php');
    }
}


// check if the url/file exists
function doesFileExistOnWebServer( urlToFile ) {
    var xhr = new XMLHttpRequest();
    xhr.open('HEAD', urlToFile, false);
    xhr.send();
     
    if ( xhr.status == "404" ) {
        return false;
    } else {
        return true;
    }
}


// set HighChart Button text
function setHCButtonText( HCbutton, textarray , boolval ){
    if ( boolval == true ) {
        HCbutton.attr({ text: textarray[0] }); 
    } else {
        HCbutton.attr({ text: textarray[1]});
    }
}


// read CSS selector and style from loaded pages
function getStyleRuleValue( selector, style ) {
    for (var i = 0; i < document.styleSheets.length; i++) {
        var mysheet = document.styleSheets[i];
        var myrules = mysheet.cssRules ? mysheet.cssRules : mysheet.rules;
        for (var j = 0; j < myrules.length; j++) {
            if (myrules[j].selectorText && myrules[j].selectorText.toLowerCase() === selector) {
                return myrules[j].style[style];
            }
        }
    }
};


// set the highchart language options.
function setHighChartLanguageOptions( idx ) {
    
    if ( idx == 0 ) {  // Nederlands
        Highcharts.setOptions({
            lang: {
                months: [
                    'januari', 'februari', 'maart', 'april',
                    'mei', 'juni', 'juli', 'augustus',
                    'september', 'oktober', 'november', 'december'
                ],
                weekdays: [
                    'zondag', 'maandag', 'dinsdag', 'woensdag',
                    'donderdag', 'vrijdag', 'zaterdag'
                ]
            }
        });
    } else if ( idx == 1 ) { // English
        
        Highcharts.setOptions({
            lang: {
                months: [
                    'January', 'February', 'March', 'April',
                    'May', 'June', 'July', 'August',
                    'September', 'October', 'November', 'December'
                ],
                weekdays: [
                    'Sunday', 'Monday', 'Tuesday', 'Wednesday',
                    'Thursday', 'Friday', 'Saturday'
                ]
            }
            });

    } else if ( idx == 2 ) { // French

        Highcharts.setOptions({
            lang: {
                months: [
                    'Janvier', 'Février', 'Mars', 'Avril',
                    'Mai', 'Juin', 'Juillet', 'Août',
                    'Septembre', 'Octobre', 'Novembre', 'Décembre'
                ],
                weekdays: [
                    'Dimanche', 'Lundi', 'Mardi', 'Mercredi',
                    'Jeudi', 'Vendredi', 'Samedi'
                ]
            }
            });
    }

}


// copy to clipboard
// usage: <button onclick="copyClipboard('slimmemeter')">Copy to clipboard</button>
function copyClipboard( element ) {
    var elm = document.getElementById( element );
    var alertText = "Naar clipboard gekopieerd."
    // for Internet Explorer
  
    if( document.body.createTextRange ) {
      var range = document.body.createTextRange();
      range.moveToElementText(elm);
      range.select();
      document.execCommand("Copy");
      alert( alertText );
    }
    else if( window.getSelection ) {
      // other browsers
      var selection = window.getSelection();
      var range = document.createRange();
      range.selectNodeContents(elm);
      selection.removeAllRanges();
      selection.addRange(range);
      document.execCommand("Copy");
      alert( alertText );
    }
  }

// screensaver 
function screenSaver(timeout) {
    var screenSaverTimeout = parseInt(timeout);
    //console.log("screenSaverTimeout=" + timeout);
    var screensaverUrl = location.protocol + "//" + location.host + "/screensaver.php";

    if (screenSaverTimeout == 0) { // do noting
        //console.log("screensaver staat uit, timeout=" + screenSaverTimeout);
        return;
    }

    //console.log("screenSaver.screenSaverTimeout=" + screenSaverTimeout);
    var timeout_var = 0;
    setScreenSaverTimer();

    document.addEventListener('mouseover', function() {
        //console.log("screenSaverTimeout reset (mouseover).")
        setScreenSaverTimer();
    });
    document.addEventListener('click', function() {
        //console.log("screenSaverTimeout reset (click).")
        setScreenSaverTimer();
    });
    document.addEventListener('scroll', function() {
        //console.log("screenSaverTimeout reset (scroll).")
        setScreenSaverTimer();
    });

    function setScreenSaverTimer() {
        //console.log("screenSaverTimeout set met een timeout van " + screenSaverTimeout + " seconden.");
        toLocalStorage('screensaver-href', location.href);
        clearTimeout(timeout_var);
        timeout_var = setTimeout(function() { window.location.assign(screensaverUrl); }, (screenSaverTimeout * 1000 ) );
        //console.log("screenSaverTimeout set done");
    }

}

// days in the current month.
function daysInThisMonth() {
    var now = new Date();
    return new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
}

// toggel type attr. between text and passwd
function toggelPasswordVisibility(id) {
    var x = document.getElementById(id);
    if (x.type === "password") {
        x.type = "text";
    } else {
        x.type = "password";
    }
}

// random number between to values
function randomIntFromInterval(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min);
}

// ascii test html conversion.
function text2Json(myString) {
    var regX = / /g;
    s = new String(myString);
    s = s.replace(regX, "&nbsp;");
    var regX = /\n/gi;
    s = s.replace(regX, "<br /> \n");
    return s;
}

// yy-mm-dd hh:mm:ss to epoch
function getEpochMillis(dateStr) {
    var r = /^\s*(\d{4})-(\d\d)-(\d\d)\s+(\d\d):(\d\d):(\d\d)\s*$/,
        m = ("" + dateStr).match(r);
    return (m) ? Date.UTC(m[1], m[2] - 1, m[3], m[4], m[5], m[6]) : undefined;
};

function showStuff(boxid) { document.getElementById(boxid).style.display = "block"; }

function hideStuff(boxid) { document.getElementById(boxid).style.display = "none"; }

function zeroPad(num, places) {
    var zero = places - num.toString().length + 1;
    return Array(+(zero > 0 && zero)).join("0") + num;
}

function padXX(value, pre, post) {
    var v = (parseFloat(value).toFixed(post));
    if (isNaN(v)) { return "??.???"; }
    var s = "00000000000000000" + v;
    return s.substr(s.length - (pre + post + 1));
}

function colorFader(id_label, color_in) {
    $(id_label).fadeOut("slow");
    $(id_label).css("color", color_in);
    $(id_label).fadeIn("slow");
}

function toLocalStorage(key, value) {
    if (!!window.localStorage && true) {
        try {
            window.localStorage.setItem(key, value);
        } catch (e) { return; }
    }
}

function getLocalStorage(key) {
    if (!!window.localStorage && true) {
        try {
            return window.localStorage.getItem(key);
        } catch (e) { return null; }
    }
}

function centerPosition(element_id) {
    $(window).resize(function() {
        $(element_id).css({
            position: 'absolute',
            left: ($(window).width() - $(element_id).outerWidth()) / 2,
            top: ($(window).height() - $(element_id).outerHeight()) / 3
        });
    });
    $(window).resize();
}

function getTimestamp() {
    const pad = (n,s=2) => (`${new Array(s).fill(0)}${n}`).slice(-s);
    const d = new Date();
    return `${pad(d.getFullYear(),4)}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

  function getRandomHex( size, offset ) {
    let result = [];
    let hexRef = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'];
    let currentTime = new Date();
    seed = currentTime.getTime() + offset
    for (let n = 0; n < size; n++) {
      result.push(hexRef[Math.floor( Math.random( seed ) * 16)]);
    }
    return result.join('');
  }
  
