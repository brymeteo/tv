<head>
<link href="https://fonts.googleapis.com/css?family=Ubuntu+Condensed|Ubuntu:300" rel="stylesheet" type="text/css">
<link href="//maxcdn.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.min.css" rel="stylesheet"/>
<link rel="stylesheet" href="css/wxsim_2017.css" />
<link rel="stylesheet" href="css/weather-icons.min.css" />
<style>
#dailyCarousel{color: #fff;font-family: "Ubuntu","Lucida Grande",Verdana,Helvetica,sans-serif;font-size: 13px;font-weight:300;line-height:1.25em;margin:0}
:focus {outline:0}
</style>
<script src="https://static.nordicweather.net/jq/jquery-1.10.2.min.js"></script>
<script src="https://static.nordicweather.net/jq/jq_plugins2.min.js"></script>
</head>

<body>
<?php
date_default_timezone_set("Europe/Helsinki");
$windunit="ms";
$lang="en";         // Remove if your site has it defined allready

echo '<script>var lang="'.$lang.'",wiset="'.$windunit.'",ewnpath="/test/wxsim/wxsim";</script>';
?>
<script src="js/wxsim_shortfrc_2017.js"></script>
<div id="dailyCarousel" class="touchcarousel">
  <ul class="touchcarousel-container"></ul>
</div>
</body>