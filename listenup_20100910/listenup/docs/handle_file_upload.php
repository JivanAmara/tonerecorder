<?php
// Print information from HTML upload file form.
// (C) Phil Burk, http://www.softsynth.com

// These must come before anything else is printed so that they get in the header.
    header("Cache-control: private");
    header("Content-Type: text/plain");

    echo "Information from POSTed File\n";
    echo "This particular page must be on a web server running PHP.\n";
    echo "You can use any server language you wish with ListenUp\n";
    echo "if you write your own server scripts.\n";
    echo "\n";

// Get posted variables. Assume register_globals is off.
    $userComment = strip_tags($_POST['userComment']);
    $duration = strip_tags($_POST['duration']);
	
// Extract information provided by PHP POST processor.
    $upfile_size = $_FILES['userfile']['size'];
    $raw_name = $_FILES['userfile']['name'];

// Strip path info to prevent uploads outside target directory.
    $upfile_name = basename($raw_name);

// Print relevent file information provided by PHP POST processor for debugging.
    echo "name        = " . $upfile_name . "\n";
    echo "type        = " . $_FILES['userfile']['type'] . "\n";
    echo "size        = $upfile_size\n";
    echo "userComment = $userComment\n";
    echo "duration    = $duration\n";

// A status message is required. Return either SUCCESS, WARNING or ERROR
    echo "\nSUCCESS - test complete.\n\n";
    
    echo "Hit BACK Button to continue with tutorial.\n";
    
?>
