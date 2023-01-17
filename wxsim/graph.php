<head>
<link href="https://fonts.googleapis.com/css?family=Ubuntu+Condensed|Ubuntu:300" rel="stylesheet" type="text/css">
<link href="//maxcdn.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.min.css" rel="stylesheet"/>
<link rel="stylesheet" href="css/wxsim_2017.css" />
<link rel="stylesheet" href="css/weather-icons.min.css" />
<style>
#hourgraph td{color: #fff;font-family: "Ubuntu","Lucida Grande",Verdana,Helvetica,sans-serif;font-size: 13px;font-weight:300;line-height:1.25em;margin:0}
#hourgraph .highcharts-tooltip span {width:180px;}
</style>
<script src="https://static.nordicweather.net/jq/jquery-1.10.2.min.js"></script>
<script src="https://static.nordicweather.net/jq/jq_plugins2.min.js"></script>
<script src="//static.nordicweather.net/jq/highcharts-custom-4.2.0.js"></script>
</head>

<body>
<?php
$gdays=5;
$lang="en";         // Remove if your site has it defined allready
$gpath="/test/wxsim/wxsim";  # Path from root to data.php
include __DIR__.'/wxsim/config.php';
date_default_timezone_set("Europe/Helsinki");
foreach ($days as $key => $value) {
  $da[]=utf8_encode(html2utf8($value));
}
$day_array = json_encode($da);
foreach ($months as $key => $value) {
  $mo[]=utf8_encode($value);
}
$mo_array = json_encode($mo);

echo '<script>
var lang="'.$lang.'",gdays='.$gdays.',ewnpath="'.$gpath.'";
var days = '.$day_array.',months = '.$mo_array.';
 var temptxt="'.TEMP.'",barotxt="'.BARO.'",prectxt="'.PRECIP.'",windtxt="'.WIND.'",dewtxt="'.DEWP.'",snowtxt="'.SNOB.'",feeltxt="'.FEELS.'",tstxt="'.TSPROB.'",humtxt="'.HUMIDITY.'",gusttxt="'.GUST.'",rratetxt="'.RRATE.'",noclosetxt="'.NOCLOSE.'",txtgust="'.GUST.'",txtmidnightsun="'.MIDNIGHTSUN.'",txtpolarnight="'.POLARNIGHT.'";
</script>';

function html2utf8($name) {
  if(mb_detect_encoding($name, 'UTF-8', true)){$name=utf8_decode($name);}
  $n=str_replace("&auml;","ä",$name);
  $n=str_replace("&aring;","å",$n);
  $n=str_replace("&aelig;","æ",$n);
  $n=str_replace("&ouml;","ö",$n);
  $n=str_replace("&oslash;","ø",$n);
  return $n;
}
?>
<script src="js/wxsim_graphfrc_2017.js"></script>
<div id="hourgraph" style="min-width: 200px;margin:0 auto;position:relative;height:430px"></div>
</body>