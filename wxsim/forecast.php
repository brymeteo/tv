<!DOCTYPE HTML>
<html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<?php
$wxsimtype="forecast";
include 'wxsim/config.php';
echo $ewnhead;
?>
<style>
body {background: #fff;color: #555555;font-family: "Ubuntu","Lucida Grande",Verdana,Helvetica,sans-serif;font-size: 13px;font-weight:300;line-height:1.25em;margin:0}
:focus {outline:0}
</style>
</head>
<body>
<?php
echo '<div class="ewn" style="max-width:1000px;margin:0 auto;">';
echo '<h1> WXSIM Forecast Demo</h1>';
echo $nfrcbody;
echo '</div>';
echo $ewnfooter;
?>
</body></html>