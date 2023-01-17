<?php
############################################################################
# WXSIM Forecast EWN-style v. 2017.2 (February 2017)
############################################################################
#
# Author:	Henkka <nordicweather@gmail.com.net>
#
# Copyright:	(c) 2017 Copyright nordicweather.net.
#
############################################################################
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
############################################################################
#
# This work is licensed under the 
# Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported License. 
# To view a copy of this license, visit 
# http://creativecommons.org/licenses/by-nc-nd/3.0/.
#
############################################################################

// Next update by Labbs
$thishr = date('i') < $uploadupdate ? date('G') : date('G') + 1;
$nextupdate = $updatehrs[0];
for ($i = 0 ; $i < count($updatehrs) ; $i++) {
	if ($updatehrs[$i] >= $thishr) {
		$nextupdate = $updatehrs[$i];
		break;
  }else if ($i+1 == count($updatehrs)){
    $nextupdate = "+1 day " . $nextupdate;
  }
}
$wxallnext = date($timeFormat,strtotime($nextupdate.':'.$updateminute));


$query=$_SERVER["QUERY_STRING"];
$q=explode("|",$query);
$initload="true";
if(preg_match("|\||",$query)){
  $lang=$q[0];
}else{
  if(isset($_GET[lang])){$lang = $_GET[lang];}
}

foreach ($days as $key => $value) {
  $da[]=utf8_encode(html2utf8($value));
}
$day_array = json_encode($da);
foreach ($months as $key => $value) {
  $mo[]=utf8_encode($value);
}
$mo_array = json_encode($mo);

$wunit="ms";
if($_COOKIE[ewnwunit]){
  $wunit=$_COOKIE[ewnwunit];
}

###########################################################

$ewnhead='
<link href="//maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet"/>
<link href="//static.nordicweather.net/css/leaflet-0.7.3.min.css" rel="stylesheet"/>
<link href="//static.nordicweather.net/css/bootstrap_ewn.css?'.$wxsimversion .'" rel="stylesheet"/>
<link rel="stylesheet" href="'.$path_to_css.'wxsim_2017.css?'.$wxsimversion .'" />
<link rel="stylesheet" href="'.$path_to_css.'weather-icons.min.css?'.$wxsimversion .'" />';

###########################################################

if($jqueryload ){
  $ewnfooter.='
  <script src="//static.nordicweather.net/jq/jquery-1.10.2.min.js"></script>';
}
$ewnfooter.='
  <script src="//static.nordicweather.net/jq/jq_plugins2.min.js?'.$wxsimversion .'"></script>';
if($bootstrapload ){
  $ewnfooter.='
  <script src="//static.nordicweather.net/jq/bootstrap-3.3.5.min.js"></script>';
}
$ewnfooter.='
  <script src="//static.nordicweather.net/jq/bootstrap_plugins.min.js?'.$wxsimversion .'"></script>
  <script src="//static.nordicweather.net/jq/highcharts-custom-4.2.0.js"></script>
<script>
';

$ewnfooter.='
  name="'.$wxsimlocation.'",lang="'.$lang.'",tzabb = "'.$tzabb.'",version='.$wxsimversion.',ewnpath="'.$path_to_dataphp.'",latitude='.$latitude.';
  var days = '.$day_array.',months = '.$mo_array.';
  var temptxt="'.TEMP.'",barotxt="'.BARO.'",prectxt="'.PRECIP.'",windtxt="'.WIND.'",dewtxt="'.DEWP.'",snowtxt="'.SNOB.'",feeltxt="'.FEELS.'",tstxt="'.TSPROB.'",humtxt="'.HUMIDITY.'",gusttxt="'.GUST.'",rratetxt="'.RRATE.'",txtgust="'.GUST.'",txtmidnightsun="'.MIDNIGHTSUN.'",txtpolarnight="'.POLARNIGHT.'";
  var snowset="'.strtolower($uoms[4]).'",baroset="'.$uoms[3].'",wiset="'.str_replace("/","",$uoms[2]).'",piset="'.strtolower($uoms[1]).'",tiset="'.strtolower($uoms[0]).'";
</script>
<script src="'.$path_to_js.'wxsim_frc_2017.js?'.$wxsimversion .'"></script>
';

###########################################################
# PUT TOGETHER BODY

if($alt>0){$alt=', '.$alt.' '.MASL;}else{$alt='';}
$nfrcbody='
<div id="favobar">
  <span id="wunitlink">
    '.SELECTWUNIT.'&nbsp;&nbsp;<i class="fa fa-gear"></i>
  </span>
  &nbsp;
</div>

<div id="frctop">
  <span id="wunitbar">
    <input type="radio" class="wunitbox" name="wunit" id="ms"/>&nbsp;<label for="ms">m/s</label>&nbsp;&nbsp;
    <input type="radio" class="wunitbox" name="wunit" id="kmh"/>&nbsp;<label for="kmh">km/h</label>&nbsp;&nbsp;
    <input type="radio" class="wunitbox" name="wunit" id="mph"/>&nbsp;<label for="mph">mph</label>&nbsp;&nbsp;
    <input type="radio" class="wunitbox" name="wunit" id="kts"/>&nbsp;<label for="kts">kts</label><br/>
    <input type="radio" class="punitbox" name="punit" id="mm"/>&nbsp;<label for="mm">mm</label>&nbsp;&nbsp;
    <input type="radio" class="punitbox" name="punit" id="in"/>&nbsp;<label for="in">in</label><br/>
    <input type="radio" class="tunitbox" name="tunit" id="tc"/>&nbsp;<label for="c">&deg;C</label>&nbsp;&nbsp;
    <input type="radio" class="tunitbox" name="tunit" id="tf"/>&nbsp;<label for="f">&deg;F</label>
  </span>
  <div class="frctop_half" style="padding:20px;display: flex;-webkit-flex: 1;-ms-flex: 1;flex-direction:column;">
    <div style="position: relative;color: #fff;font-size: 14px;height: 150px;line-height: 22px;">
      <h1 id="frctopname" style="margin-bottom: 10px;margin-top: 0px;">'.WSXFRC.' '.$wxsimlocation.'</h1>
      '.UPDATED.': '.date($timeFormat,filemtime($path_to_lastret)).'<br/>
      '.NXTUPDATE.': '.$wxallnext.'
    </div>
  </div>

  <div class="frctop_half_last">
    <div id="loading">
      <i class="fa fa-circle-o-notch fa-spin fa-3x fa-fw"></i>
    </div>
    <div id="frcinfotop" style="display:none">
      <div id="frctopclock"><i class="fa fa-clock-o" style="font-size:22px"></i><span></span></div>
      <div id="frctopbox">
        <div id="frctopicon"></div>
        <div id="frctoptemp"><span></span></div>
      </div>
      <div id="frctoprest">
        <i class="wi wi-raindrops" style="color:#4F94CD;font-size:30px;top:3px;left:0px"></i><span id="toprain"></span>
        <i class="wi wi-umbrella" style="font-size:20px;top:-4px;"></i><span id="toppop"></span>
        <span id="frctoplight" style="top:0px">
          <i class="wi wi-lightning" style="color:#FFA500;font-size:20px;top:-4px;"></i><span id="topts"></span>
        </span>
        <span id="frctopsnow" style="top:0px">
          <i class="fa fa-snowflake-o" style="color:#ffffff;font-size:20px;top:-4px;left:6px"></i>
          <span id="topsnow"></span>
        </span>
        <span id="frctopwind"></span>
      </div>
    </div>
  </div>
  <div style="clear:both"></div>
</div>
<div id="frcMAlarm"></div>

<div id="dailyCarousel" class="touchcarousel">     
    <ul class="touchcarousel-container"></ul>
</div>

<div id="frcnavouter">
  <div id="frcnav">
    <div class="frcnavs selected" data-id="plain">'.OVERVIEW.'</div>
    <div class="frcnavs" data-id="table">'.TABLE.'</div>
    <div class="frcnavs" data-id="graph">'.GRAPH.'</div>
  </div>
</div>

<div id="frccontent">

    <div id="plaintable">
    <div id="plaintblhead">
      <div class="frctblheadrow datehead" style="flex: 2;"></div>
      <div class="frctblheadrow" style="flex: 1;" data-toggle="tooltip" data-placement="top" title="'.TEMP.'">
        <i class="wi wi-thermometer" style="font-size: 22px;top: 4px;position: relative;"></i>
      </div>
      <div class="frctblheadrow" style="flex: 1;" data-toggle="tooltip" data-placement="top" title="'.WIND.'">
      <i class="wi wi-strong-wind" style="font-size: 22px;top: 4px;position: relative;"></i>
      </div>
      <div class="frctblheadrow" style="flex: 1;" data-toggle="tooltip" data-placement="top" title="'.PRECIP.'">
        <i class="wi wi-raindrops" style="color:#4F94CD;font-size:34px;top:10px;position: relative;"></i>
      </div>
      <div class="frctblheadrow ppophead" style="flex: 1;" data-toggle="tooltip" data-placement="top" title="'.POP.'">
        <i class="wi wi-umbrella" style="font-size:20px;top:2px;position: relative;margin:0 10px 0 0;"></i>
      </div>
      <div class="frctblheadrow puvihead" style="flex: 1;" data-toggle="tooltip" data-placement="top" title="UV">
        <i class="wi wi-day-sunny" style="color: rgb(255, 204, 0);font-size:20px;top:2px;position: relative;margin:0 10px 0 0;"></i>
      </div>
      <div class="frctblheadrow" style="flex: 3;" data-toggle="tooltip" data-placement="top" title="'.DESCRIPTION.'">
        <i class="fa fa-info" style="font-size: 22px;top: 4px;position: relative;"></i>
      </div>
    </div>
    <div id="plaintbl"></div>
  </div>

  <div id="frctable" style="display:none">
    <div id="frctblhead">
      <div class="frctblheadrow datehead" style="flex: 2;"></div>
      <div class="frctblheadrow" style="flex: 1;" data-toggle="tooltip" data-placement="top" title="'.TEMP.'">
        <i class="wi wi-thermometer" style="font-size: 22px;top: 4px;position: relative;"></i>
      </div>
      <div class="frctblheadrow" style="flex: 1;" data-toggle="tooltip" data-placement="top" title="'.FEELS.'">
        <i class="fa fa-user" style="font-size: 26px;top: 3px;position: relative;"></i>
      </div>
      <div class="frctblheadrow" style="flex: 1;" data-toggle="tooltip" data-placement="top" title="'.WIND.'">
      <i class="wi wi-strong-wind" style="font-size: 22px;top: 4px;position: relative;"></i>
      </div>
      <div class="frctblheadrow" style="flex: 1;" data-toggle="tooltip" data-placement="top" title="'.HUMIDITY.'">
        <i class="wi wi-humidity" style="font-size: 22px;top: 4px;position: relative;"></i>
      </div>
      <div class="frctblheadrow" style="flex: 1;" data-toggle="tooltip" data-placement="top" title="'.PRECIP.'">
        <i class="wi wi-raindrops" style="color:#4F94CD;font-size:34px;top:10px;position: relative;"></i>
      </div>
      <div class="frctblheadrow pophead" style="flex: 1;" data-toggle="tooltip" data-placement="top" title="'.POP.'">
        <i class="wi wi-umbrella" style="font-size:20px;top:2px;position: relative;margin:0 10px 0 0;"></i>
      </div>
      <div class="frctblheadrow snowhead" style="flex: 1;" data-toggle="tooltip" data-placement="top" title="'.SNOW.'">
        <i class="fa fa-snowflake-o" style="color:#ffffff;font-size:20px;top:-4px;left:6px"></i>
      </div>
      <div class="frctblheadrow tshead" style="flex: 1;" data-toggle="tooltip" data-placement="top" title="'.TSPROB.'">
        <i class="wi wi-lightning" style="color:#FFA500;font-size:24px;top:4px;position: relative;margin:0 10px;"></i>
      </div>
      <div class="frctblheadrow uvihead" style="flex: 1;" data-toggle="tooltip" data-placement="top" title="UV">
        <i class="wi wi-day-sunny" style="color: rgb(255, 204, 0);font-size:20px;top:2px;position: relative;margin:0;"></i>
      </div>
      <div class="frctblheadrow barohead" style="flex: 1;" data-toggle="tooltip" data-placement="top" title="'.BARO.'">
        <i class="wi wi-barometer" style="font-size: 22px;top: 4px;position: relative;"></i>
      </div>
    </div>
    <div id="frctbl"></div>
    <div id="sunmoon"></div>
  </div>
  
  <div id="graphtable" style="display:none">
    <div id="hourgraph" style="min-width: 200px;margin:0 auto;position:relative;height:430px"></div>
    <div id="graphbuttons" class="buttons">
      <div style="flex:1"><div class="active" data-id="frc">'.FRCGRAPH.'</div></div>
      <!--div style="flex:1"><div data-id="comp">'.COMPAREDESC.'</div></div-->
      <div style="flex:1"><div data-id="fullgraph">'.FULLGRAPH.'</div></div>
    </div>
  </div>
  
</div>
';

###########################################################

function fix_wxsi($a,$wxsi,$b){
  if($wxsi){return $a.$b;}
}

function html2utf8($name) {
  if(mb_detect_encoding($name, 'UTF-8', true)){$name=utf8_decode($name);}
  $n=str_replace("&auml;","ä",$name);
  $n=str_replace("&aring;","å",$n);
  $n=str_replace("&aelig;","æ",$n);
  $n=str_replace("&ouml;","ö",$n);
  $n=str_replace("&oslash;","ø",$n);
  return $n;
}

function fixwsp($num,$ext,$round){
  global $wunit;
  if($wunit=="kmh"){$num = sprintf("%01.1f",$num*3.6);$wu="km/h";}
  elseif($wunit=="mph"){$num = sprintf("%01.1f",$num*2.23693629);$wu="mph";}
  elseif($wunit=="kts"){$num = sprintf("%01.1f",$num*1.94384449);$wu="kts";}
  else{$wu="m/s";}
  if($round){$num=round($num);}
  if($ext){return $num.' '.$wu;}
  else{return $num;}
}

function get_flags(){
$countrys = array(
"AL" => defcountries("Albania"),
"AD" => defcountries("Andorra"),
"AT" => defcountries("Austria"),
"AX" => defcountries("&Aring;land"),
"BY" => defcountries("Belarus"),
"BE" => defcountries("Belgium"),
"BA" => defcountries("Bosnia"),
"BG" => defcountries("Bulgaria"),
"HR" => defcountries("Croatia"),
"CY" => defcountries("Cyprus"),
"CZ" => defcountries("Czech"),
"DK" => defcountries("Denmark"),
"EE" => defcountries("Estonia"),
"FO" => defcountries("Faroe"),
"FI" => defcountries("Finland"),
"FR" => defcountries("France"),
"DE" => defcountries("Germany"),
"GI" => defcountries("Gibraltar"),
"GR" => defcountries("Greece"),
"GL" => defcountries("Greenland"),
"HU" => defcountries("Hungary"),
"IS" => defcountries("Iceland"),
"IE" => defcountries("Ireland"),
"IT" => defcountries("Italy"),
"RS" => defcountries("Kosovo"), 
"LV" => defcountries("Latvia"),
"LI" => defcountries("Liechtenstein"),
"LT" => defcountries("Lithuania"),
"LU" => defcountries("Luxembourg"),
"MK" => defcountries("Macedonia"),
"MT" => defcountries("Malta"),
"MD" => defcountries("Moldova"),
"MC" => defcountries("Monaco"),
"ME" => defcountries("Montenegro"),
"NL" => defcountries("Netherlands"),
"NO" => defcountries("Norway"),
"PL" => defcountries("Poland"),
"PT" => defcountries("Portugal"),
"RO" => defcountries("Romania"),
"RU" => defcountries("Russia"),
"SM" => defcountries("San Marino"),
"RS" => defcountries("Serbia"),
"SK" => defcountries("Slovakia"),
"SI" => defcountries("Slovenia"),
"ES" => defcountries("Spain"),
"SE" => defcountries("Sweden"),
"CH" => defcountries("Switzerland"),
"TR" => defcountries("Turkey"),
"UA" => defcountries("Ukraine"),
"GB" => defcountries("UK"),
"VA" => defcountries("Vatican")
);
$flags='<table style=\'width:450px;position: relative;top: -10px;\'><tr><td style=\'width:33%\'>';
foreach ($countrys as $key => $value) {
  $flags.='<div class=\'popoverflags\' data-country=\''.strtolower($key).'\'><span class=\'knob knob-'.$key.' popoverflag\'></span>'.$value.'</div>';
  $i++;
  if($i==17||$i==34){$flags.='</td><td>';}
}
$flags.='</td></tr></table>';
  return $flags;
}
?>