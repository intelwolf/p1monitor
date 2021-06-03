<?php
include_once '/p1mon/www/util/textlib.php';

function config_buttons($mode){

$save_text   = strIdx(117);
$revert_text = strIdx(118);
$logout_text = strIdx(119);

$save = '<button id="buttonSaved" name="buttonSaved" class="input-4 pos-31 cursor-pointer" type="submit" value="save">
            <i class="color-settings far fa-save"></i>&nbsp;<span class="color-menu">'.$save_text.'</span>
        </button>';
$revert = '<button id="buttonRevert" name="buttonRevert" class="input-4 pos-31 cursor-pointer" type="submit" value="revert">
            <i class="color-warning fas fa-undo"></i>&nbsp;<span class="color-menu">'.$revert_text.'</span>
        </button>';        
$logout = '<button id="buttonLogout" name="buttonLogout" class="input-4 pos-31 cursor-pointer" type="submit" value="logout">
            <i class="color-ok fas fa-sign-out-alt"></i>&nbsp;<span class="color-menu">'.$logout_text.'</span>
        </button>';
        
switch ($mode) {
    case 0: /* default all options */
        break;
    case 1: /* only logout */
            $save= '';
        $revert= '';
        break;
}                
echo <<<"END"
<div class="pos-30" id="formbuttons">    
        $save
        $revert
        $logout
        </div>    
        
        <script>
        $(function() {
        
            $('#buttonSaved').click(function(){
            $('#formvalues').submit();
            $('#busy_indicator').removeClass('display-none');
            });

            $('#buttonRevert').click(function(){
            location.reload(false);
            });
    
            $('#buttonLogout').click(function(){
            document.formvalues.logout.value = 'true';
            $('#formvalues').submit();
            });
        });
        </script>
        
END;
}
?>