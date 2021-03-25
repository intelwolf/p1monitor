<?php
function config_buttons($mode){
    
$save = '<button id="buttonSaved" name="buttonSaved" class="input-4 pos-31 cursor-pointer" type="submit" value="save">
            <i class="color-settings far fa-save"></i>&nbsp;<span class="color-menu">opslaan</span>
        </button>';
$revert = '<button id="buttonRevert" name="buttonRevert" class="input-4 pos-31 cursor-pointer" type="submit" value="revert">
            <i class="color-warning fas fa-undo"></i>&nbsp;<span class="color-menu">herstel</span>
        </button>';        
$logout = '<button id="buttonLogout" name="buttonLogout" class="input-4 pos-31 cursor-pointer" type="submit" value="logout">
            <i class="color-ok fas fa-sign-out-alt"></i>&nbsp;<span class="color-menu">loguit</span>
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