import crypto_lib


signing_key_b64 = '5WGVeeOQ2hJ/x0etrc/XJBJp5/LRYKt2F14XiFv8YOA='
verify_key_b64  = 'Eo0eNTVykaF0esMwe37GDKqCHpaNxe3HnzYhYosGNXY='

ds=crypto_lib.DigitalSignature( debug=False )

#ds.sign_file( source_filepath="/tmp/V200P001.zip" )
#ds.sign_write_file( source_filepath="/tmp/wil.txt", destination_filepath="/tmp/wil.signed.txt" ,signing_key_b64=signing_key_b64, verify_key_b64=verify_key_b64 )
#ds.verify_write_file( source_filepath="/tmp/wil.signed.txt", destination_filepath="/tmp/wil.nosigned.txt", verify_key_b64=verify_key_b64 )

ds.sign_write_file( source_filepath="/tmp/V200P001.zip", destination_filepath="/tmp/V200P001.signed.zip" ,signing_key_b64=signing_key_b64, verify_key_b64=verify_key_b64 )
ds.verify_write_file( source_filepath="/tmp/V200P001.signed.zip", destination_filepath="/tmp/V200P001.nosigned.zip", verify_key_b64=verify_key_b64 )
print ( ds.print_key_pairs() )