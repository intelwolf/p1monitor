<?php

/* Getting file name */
$filename = $_FILES['file']['name'];

/* Location */
$location = "/tmp/".$filename;
$uploadOk = 1;

if( $uploadOk == 0 ){
    echo 0;
} else {
/* Upload file */
if(move_uploaded_file($_FILES['file']['tmp_name'], $location)){
    echo $location;
}else{
    echo 0;
}
}


/*

$filename = $_FILES['file']['name'];

$location = "/tmp/".$filename;

if ( move_uploaded_file($_FILES['file']['tmp_name'], $location) ) {
  echo '{ 
    Success:1 
    }';
} else {
  echo '{
    Failure:0
    }';
}

echo "<br>";
print_r( $_POST );
print_r( $_FILES );
?>
