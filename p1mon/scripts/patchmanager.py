from logging import raiseExceptions
import subprocess
import crypto_lib
import os
import sys
import time
import quote_lib
import util
import subprocess
import patch_lib

import os.path
from simple_term_menu import TerminalMenu
from colorama import Fore, Back, Style, init
init() # part of colorama

TMP_BASE                = "/tmp/"
PRG_NAME                = "Patch manager V1.0"

HELP_TEXT = \
"\
Met P1Patchmanger kun je een folder omzetten in een zip bestand dat al dan niet\n\
van een digitale handteking is voorzien. De P1 monitor leest die in en voert het\n\
script (start.p1monpatch) uit. Het is primair bedoeld voor patches en kleine upgrades.\n\
Een signed patch bestand zorgt ervoor dat een gebruiker zeker weet dan het van de\n\
P1 monitor ontwikkelaar komt. Je kunt als derde geen signed patch bestand maken.\n\
Daarvoor heb je de geheime signing key nodig. Echter in de UI van de P1 monitor\n\
kun je aangeven dat je unsigned patch bestanden accepteert.\
"

patch_source_folder     = ""
patch_unsigned_filepath = ""
patch_signed_filepath   = ""
signing_key             = ""
verify_key              = ""
keys_filepath           = ""

menu_style_1        = ( "bg_blue",  "fg_yellow" )
menu_style_2        = ( "bg_black", "fg_yellow" )
menu_cursor_1       = "* "
menu_cursor_style_1 = ("fg_red", "bold")

main_menu_title = "  " + PRG_NAME + "\n  Hoofd menu\n"


main_menu_items = [
"[1] Digitale handtekening sleutels aanmaken.",
"[2] Maak een signed of unsigned patch bestand.",
"[3] Help",
"[0] Stop Patch manager"
]

patch_file_menu_items = [
"[1] Voer folder met de patch bestanden in",
"[2] Voer file in voor het creëren patch bestand",
"[3] Voer de signing key in (optioneel)",
"[4] Voer de verify key in (optioneel)",
"[5] Start patch creatie",
"[0] Terug naar het hoofdmenu"
]


def main():
    global patch_file_menu_items

    while( True ):
        #print_header()
        #print_menu_header()
       
        terminal_menu = TerminalMenu( 
            menu_entries=main_menu_items,
            title=main_menu_title,
            menu_cursor=menu_cursor_1,
            menu_cursor_style=menu_cursor_style_1,
            menu_highlight_style=menu_style_1,
            cycle_cursor=True,
            clear_screen=True,
            shortcut_key_highlight_style=menu_style_2
         )
        menu_entry_index = terminal_menu.show()
        #print ( menu_entry_index )

        if menu_entry_index == 3:
            os.system( 'clear' )
            print_msg ( quote_lib.get_quote(), colorama_color=Fore.GREEN )
            print( "\nTot ziens!\n" )
            sys.exit(0)
        elif menu_entry_index+1 == 1:
            menu_make_keys()
        elif menu_entry_index+1 == 2:
            menu_make_patch_file()
        elif menu_entry_index+1 == 3:
            print_help()
            
def menu_make_patch_file():
    global patch_source_folder, patch_unsigned_filepath, patch_signed_filepath, signing_key, verify_key

    while( True ):

        os.system( 'clear' )

        patch_file_menu_title = "  " + PRG_NAME + "\n\
  Patch creatie menu\n\
  -----------------------------------------\n\
  Folder met de patch bestanden: " + str( patch_source_folder ) + "\n\
  Patch bestand: " + str( patch_unsigned_filepath ) + " en " + str(patch_signed_filepath) + "\n\
  Signing key: " + str( signing_key ) + "\n\
  Verify bestand: " + str( verify_key ) + "\n\
"

        terminal_menu = TerminalMenu(
            menu_entries=patch_file_menu_items,
            title=patch_file_menu_title,
            menu_cursor=menu_cursor_1,
            menu_cursor_style=menu_cursor_style_1,
            menu_highlight_style=menu_style_1,
            cycle_cursor=True,
            clear_screen=True,
            shortcut_key_highlight_style=menu_style_2
        )
        menu_entry_index = terminal_menu.show()


        if menu_entry_index+1 == 6:
            return

        if menu_entry_index+1 == 1:
            if len( patch_source_folder ) != 0:
                value = input( Fore.YELLOW + "Voer de folder met path met de patch bestanden in, huidiger locatie is " + str( patch_source_folder ) + " > " + Style.RESET_ALL)
            else:
                value = input( Fore.YELLOW + "Voer de folder met path met de patch bestanden in > " + Style.RESET_ALL )
            patch_source_folder = str( value )
            
            if not patch_source_folder.endswith( os.path.sep ):
                patch_source_folder += os.path.sep # make sure we have a slash on the end of the path 

            if os.path.isdir( patch_source_folder ) == False and len( patch_source_folder ) != 0:
                print_msg ("folder " + patch_source_folder  + " bestaat niet.", colorama_color=Fore.RED )
                enter_to_continue()
                continue
            if os.path.isfile( patch_source_folder + patch_lib.PATCH_START_SCRIPT_NAME ) == False:
                print_msg ("start bestand " + patch_source_folder + patch_lib.PATCH_START_SCRIPT_NAME + " niet gevonden", colorama_color=Fore.RED )
                enter_to_continue()

        if menu_entry_index+1 == 2:
            value = input( Fore.YELLOW + "Voer de naam in van het patch bestand zonder path (VnnnPnnn is gebruikelijk )" + str( patch_unsigned_filepath ) + " > " + Style.RESET_ALL)
            if len( value ) != 0:
                patch_unsigned_filepath = TMP_BASE + value + patch_lib.UNSIGNED_ZIP_EXTENTION
                patch_signed_filepath   = TMP_BASE + value + patch_lib.SIGNED_ZIP_EXTENTION

            print(f'Bestand { patch_unsigned_filepath } wordt gebruikt.\n')
            enter_to_continue()

        if menu_entry_index+1 == 3:
            value = input( Fore.YELLOW + "Voer de signing key in : " + str( signing_key ) + " > " + Style.RESET_ALL)
            if len( value ) != 0:
                signing_key = value
            
            print( f'signing_key  { signing_key } wordt gebruikt.\n' )
            enter_to_continue()

        if menu_entry_index+1 == 4:
            value = input( Fore.YELLOW + "Voer de verify key in : " + str( verify_key ) + " > " + Style.RESET_ALL)
            if len( value ) != 0:
                verify_key = value
            print( f'signing_key  {  verify_key } wordt gebruikt.\n' )
            enter_to_continue()
        
        if menu_entry_index+1 == 5:

            # check if PATCH_START_SCRIPT_NAME is in the root of the patch_source_folder
            if os.path.isfile( patch_source_folder + patch_lib.PATCH_START_SCRIPT_NAME ) == True:
                print_line_mgs( status ="OK", msg="patch start bestand " + patch_source_folder + patch_lib.PATCH_START_SCRIPT_NAME + " bestaat", colorama_color=Fore.GREEN )
            else:
                print_line_mgs(status ="FAIL", msg="fataal startbestand " + patch_source_folder + patch_lib.PATCH_START_SCRIPT_NAME + " ontbreekt", colorama_color=Fore.RED )
                enter_to_continue()
                continue # back to top 

            print_line_mgs( status ="OK", msg="zip bestand " + patch_unsigned_filepath + " wordt aangemaakt.", colorama_color=Fore.GREEN )

            # do this trick with cd so we don't include the complete path. 
            cmd = "cd /tmp; zip -r -9 " + patch_unsigned_filepath  + " ./" + patch_source_folder.replace(TMP_BASE,"" ).strip("/")
            print_line_mgs( status ="OK", msg="commando: " + cmd + " gestart.", colorama_color=Fore.GREEN )

            proc = subprocess.Popen( [cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            try:
               
                stdout, _stderr  = proc.communicate()
                returncode = int( proc.wait(timeout=60) )
                #raise Exception( "TEST" )
                if returncode != 0:
                    raise Exception( "zip uitvoering onverwacht gefaald." )
            except Exception as e:
                print_line_mgs( status ="FAIL", msg=str(e.args[0]) , colorama_color=Fore.RED )
                enter_to_continue()
                continue # back to top 

            for line in stdout.splitlines():
                print_line_mgs( status ="INFO", msg=line.decode("utf-8").lstrip(), colorama_color=Fore.LIGHTWHITE_EX )

            if len( signing_key ) != 0:
                print_line_mgs( status ="OK", msg="signed zip bestand " + patch_signed_filepath + " aanmaken." , colorama_color=Fore.GREEN )
                #patch_filepath_signed =  unsigned_zip_file.replace( UNSIGNED_ZIP_EXTENTION,'') + SIGNED_ZIP_EXTENTION
                try:
                    ds=crypto_lib.DigitalSignature( debug=False )

                    ds.sign_write_file( source_filepath=patch_unsigned_filepath, destination_filepath=patch_signed_filepath, signing_key_b64=signing_key )

                except Exception as e:
                    print_line_mgs(status ="FAIL", msg=str(e.args[0]) , colorama_color=Fore.RED )
                    enter_to_continue()
                    continue # back to top 

                print_line_mgs( status ="OK", msg="signed zip bestand " + patch_signed_filepath + " gereed." , colorama_color=Fore.GREEN )

                if len( verify_key ) != 0:
                    try:
                        print_line_mgs( status ="OK", msg="signed zip bestand " + patch_signed_filepath + " controleren met verify key." , colorama_color=Fore.GREEN )
                        ds.verify_write_file( source_filepath=patch_signed_filepath, destination_filepath=patch_unsigned_filepath, verify_key_b64=verify_key )
                        print_line_mgs( status ="OK", msg="signed zip bestand " + patch_signed_filepath + " verificatie geslaagd." , colorama_color=Fore.GREEN )
                    except Exception as e:
                        print_line_mgs(status ="FAIL", msg="verificatie gefaald " + str(e.args[0]) , colorama_color=Fore.RED )
                        enter_to_continue()
                        continue # back to top
            
            else:
                print_msg (patch_unsigned_filepath + " gemaakt.", colorama_color=Fore.GREEN )

            enter_to_continue()


def print_help():
    print ( HELP_TEXT )
    enter_to_continue()


def menu_make_keys():
    global keys_filepath
    os.system( 'clear' )

    value = input( Fore.YELLOW + "Voer een bestandsnaam naam zonder path in of Enter voor de default : " + " > " + Style.RESET_ALL )
    if len( value ) != 0:
        keys_filepath = TMP_BASE + str( value )
    else:
        t=time.localtime()
        keys_filepath = TMP_BASE + "keypair" + "%04d%02d%02d%02d%02d%02d"%(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec) + ".p1mon"

    print(f'Bestand { keys_filepath } wordt gebruikt.\n')
        
    try:
        ds=crypto_lib.DigitalSignature( debug=False )
        str_signing_key_b64, str_verify_key_b64 = ds.create_key_pairs()
        str_buffer = generate_header_string()
        str_buffer +=  "str_signing_key_b64" + " : " + str_signing_key_b64 + "\n"
        str_buffer +=  "str_verify_key_b64"  + " : " + str_verify_key_b64  + "\n"
    except Exception as e:
        print_msg ( "sleutel creatie probleem " + str(e.args[0]), colorama_color=Fore.RED )
        enter_to_continue()
        return

    try:
        f = open( keys_filepath, 'w')
        f.write( str_buffer )
        f.close()
    except Exception as e:
        print_msg ( "bestand probleem " + keys_filepath + " " + str(e.args[0]), colorama_color=Fore.RED )
        enter_to_continue()
        return

    print( str_buffer )
    enter_to_continue()


def enter_to_continue():
    input( Fore.GREEN + "Enter om door te gaan." + Style.RESET_ALL )

def print_line_mgs( status="OK", msg=None, colorama_color=Fore.WHITE ):
    print( Fore.CYAN + "[" + status + "] " + colorama_color + msg + Style.RESET_ALL)

def print_msg(  msg=None, colorama_color=Fore.WHITE ):
    msg = '# ' + msg + ' #'
    l = len( msg )
    print(colorama_color + '#' * l )
    print( msg )
    print(colorama_color + '#' * l + Style.RESET_ALL )

########################################################
# header timestamp string                              #
########################################################
def generate_header_string():
    str = \
'###################################\n\
# Gegenereerd door P1PatchManager.#\n\
# op '+ util.mkLocalTimeString() + '          #\n'+\
'###################################\n\n' +\
'WAARSCHUWING! Verwijder de signing key van de Rpi.\n\n'
    return str


if __name__ == "__main__":
    main()