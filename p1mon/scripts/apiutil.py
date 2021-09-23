import datetime
import falcon
import re
import time
import yaml

# functions 
def p1_serializer( req, resp, exception):
    representation = None

    #print (req)
    #print (resp )
    #print (exception)

    preferred = req.client_prefers(('application/x-yaml',
                                    'application/json'))
    if preferred is not None:
        if preferred == 'application/json':
            representation = exception.to_json()
        else:
            representation = yaml.dump(exception.to_dict(),
                                       encoding=None)
        #resp.body = representation
        resp.text = representation
        resp.content_type = preferred

    resp.append_header('Vary', 'Accept')

#TODO overall vervangen voor validate_timestamp_by_length
def validate_timestamp( timestamp_str ):
    try:
        if timestamp_str != datetime.datetime.strptime( timestamp_str, '%Y-%m-%d %H:%M:%S' ).strftime('%Y-%m-%d %H:%M:%S'):
            raise ValueError
        return True
    except ValueError:
        return False

def validate_timestamp_by_length( timestamp_str ):
    format_padding = '2000-01-01 00:00:00'
    try:
        #print ( "## " + timestamp_str )
        #print ( "## " + timestamp_str + format_padding[len(timestamp_str):len(format_padding)])
        adjusted_timestring = timestamp_str + format_padding[len(timestamp_str):len(format_padding)]
        if adjusted_timestring != datetime.datetime.strptime( adjusted_timestring, '%Y-%m-%d %H:%M:%S' ).strftime('%Y-%m-%d %H:%M:%S'):
            raise ValueError
        #print ("## ok")
        return True
    except ValueError:
        #print ("## not ok")
        return False

def clean_timestamp_str( str_in ):
    str_out = re.sub(r'[^-:0-9 ]', '', str_in)
    return str_out

def list_filter_to_str( in_value ):
    if type(in_value) is list:
        return str( in_value[0] )
    return str( in_value )

####################################
# tries to santize html so no bad  #
# scripting will be excuted        #
####################################
def santize_html( str_in ):

    html_escape_table = {
       "&": "&amp;",
        '"': "&quot;",
       "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
    }
    return "".join( html_escape_table.get(c,c) for c in str_in )

