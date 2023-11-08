<?php
session_start(); 
include_once '/p1mon/www/util/config_read.php';
include_once '/p1mon/www/util/p1mon-util.php';
include_once '/p1mon/www/util/p1mon-password.php';
include_once '/p1mon/www/util/textlib.php';

#print_r($_post);

#echo "session=".getPasswordSession()."<br>";
#passwordSessionExpiredCheck();
#echo "session=".getPasswordSession()."<br>";
#echo 'Orgin page=' . getPasswordHttpReferer(). "length=".strlen(getPasswordHttpReferer()).'<BR>';

$noInetCheck = isInternetIPAllowed();
$localip     = validLocalIpAdress(getClientIP());
//$localip        = False;
//$noInetCheck    = False;
if( $localip == False ){ 
    if( $noInetCheck == False ) {
        die();
    }
}

?>
<!doctype html>
<html lang="<?php echo strIdx( 531 )?>">
<head>
<meta name="robots" content="noindex">
<title>P1-monitor login</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
<link type="text/css" rel="stylesheet" href="./css/p1mon.css" />
<link type="text/css" rel="stylesheet" href="./font/roboto/roboto.css"/>

<script defer src="./font/awsome/js/all.js"></script>
<script src="./js/jquery.min.js"></script>
<script src="./js/p1mon-util.js"></script>
</head>
<body>
<script>

    $(document).ready(function () {
        centerPosition('#dialog_setpw');
        centerPosition('#dialog_checkpw');
        hideStuff('button_id_set_pw');        
        
    <?php 
    if (passwordFileIsSet()) {
        echo "        hideStuff('dialog_setpw');"."\n";
        echo "        showStuff('dialog_checkpw');"."\n"; 
    } else {
        echo "    showStuff('dialog_setpw');"."\n";
        echo "        hideStuff('dialog_checkpw');"."\n"; 
    }
    ?>
    });
    
    <?php
    if ( isset($_POST["go_home_button"])) {
        if ($_POST["go_home_button"] == "go_home") {
            header('Location: home.php');
            die;
        }
    }


    if ( isset($_POST["set_password"]) && isset($_POST["password_text"]) && passwordFileIsSet() === false) { 
        setPasswordSession();
        writePwFile(passwdHashValue($_POST['password_text']));
        if ( strlen(getPasswordHttpReferer()) == 0 ){ 
            header('Location: ' .'/config-tarief.php');
        } else {
            header('Location: ' . getPasswordHttpReferer());
        }
    }
    
    if ( isset($_POST["password"]) ) { 
        
        //error_log('ref=*password check*', 0);
        //error_log('ref=*readPasswordFile()=*'.readPasswordFile(), 0);
        //error_log('ref=*passwdHashValue   =*'.passwdHashValue($_POST['password']), 0);
        
        if (readPasswordFile() == passwdHashValue($_POST['password']) ) {
                //error_log('ref=*password is ok*', 0);
                setPasswordSession();
                if ( strlen(getPasswordHttpReferer()) == 0 ){ 
                    header('Location: ' .'/config-tarief.php');
                } else {
                    header('Location: ' . getPasswordHttpReferer());
                }
                //header('Location: ' .'/config-tarief.php');
        } 
        /*
        else {
            error_log('ref=*password is fout*', 0);
        }
        */
    }
    ?>

    $(function () {

        $("#password_text").bind("keyup", function () {
            //TextBox left blank.
            if ($(this).val().length == 0) {
                $("#password_strength").html("voer wachtwoord in");
                $("#password_strength").css("color", '#6E797C');
                hideStuff('button_id_set_pw');
                return;
            } else {
                showStuff('button_id_set_pw');
            }
 
            //Regular Expressions.
            var regex = new Array();
            regex.push("[A-Z]"); //Uppercase Alphabet.
            regex.push("[a-z]"); //Lowercase Alphabet.
            regex.push("[0-9]"); //Digit.
            regex.push("[$@$!%*#?&]"); //Special Character.
 
            var passed = 0;
 
            //Validate for each Regular Expression.
            for (var i = 0; i < regex.length; i++) {
                if (new RegExp(regex[i]).test($(this).val())) {
                    passed++;
                }
            }

            //Validate for length of Password.
            if (passed > 2 && $(this).val().length > 8) {
                passed++;
            }

            //Display status.
            var color = "";
            var strength = "";
            switch (passed) {
                case 0:
                case 1:
                    strength = "<?php echo strIdx( 609 )?>";
                    color = "red";
                    break;
                case 2:
                    strength = "<?php echo strIdx( 570 )?>";
                    color = "darkorange";
                    break;
                case 3:
                case 4:
                    strength = "<?php echo strIdx( 571 )?>";
                    color = "green";
                    break;
                case 5:
                    strength = "<?php echo strIdx( 610 )?>";
                    color = "darkgreen";
                    break;
            }
            $("#password_strength").html(strength);
            $("#password_strength").css("color", color);
        });
        document.getElementById("loginpasswd").focus();
    });

</script>

<div>
   <!-- wachtwoord instellen -->
    <div id="dialog_setpw">
    <h2><?php echo strIdx( 611 )?></h2>
    <form name="login_set" method="post" action="<?php echo $_SERVER['PHP_SELF'] ?>">
        <input id="password_text" type="password" name="password_text"><br><br>
        <span class="text-4"><?php echo strIdx( 613 )?>:&nbsp;&nbsp;</span><span class="text-4" id="password_strength"><?php echo strIdx( 614 )?></span>
        <p></p>
        <div id='button_id_set_pw'>
            <button id="login_set_pw_button" class="input-2 but-3" name="set_password" type="submit" value="set_password">
                <i class="color-menu fa fa-3x fa-database"></i>
                <span class="color-menu text-7"><?php echo strIdx( 117 )?></span>
            </button>
        </div>
    </form>
    </div>
    <!-- wachtwoord invoeren -->
    <div id="dialog_checkpw">
    <h2 class="color-ok-2"><?php echo strIdx( 612 )?></h2>
    <form name="login" method="post" action="<?php echo $_SERVER['PHP_SELF'] ?>">
        <div class="content-wrapper pad-2">
            <input class="input-8" id="loginpasswd" type="password" name="password" autocomplete="off">
            <span class="pad-13" onclick="toggelPasswordVisibility('loginpasswd')"><i class="color-menu fas fa-eye fa-lg"></i></span>
        </div>

        <div class='content-wrapper pos-12'>
            <button class="input-2 but-1 float-left" name="check_password_button" type="submit" value="check_password_button">
                <i class="color-menu fas fa-sign-in-alt fa-3x"></i>
                <span class="color-menu text-7">login</span>
            </button>
            <button class="input-2 but-1 float-right" name="go_home_button" type="submit" value="go_home">
                <i class="color-settings fas fa-sign-out-alt fa-3x"></i>
                <span class="color-settings text-7"><?php echo strIdx( 615 )?></span>
            </button>
        </div>
    </form>
    </div>
</div>

</body>
</html>
