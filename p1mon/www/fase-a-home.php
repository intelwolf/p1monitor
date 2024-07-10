<script>
// redirect to the vertical or horizontal fase actual page. 
 var current_page = localStorage.getItem("phase-actual-orientation");
    if ( current_page == '/fase-a-v.php') {
        window.location.replace('/fase-a-v.php');
    } else {
        window.location.replace('/fase-a-h.php');
    }
</script>
