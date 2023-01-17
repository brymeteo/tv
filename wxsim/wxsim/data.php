<?php
ini_set('display_errors', '1');
include 'config.php';

# Unit-specific limits & traceamount
// rain
if (preg_match("|mm|",$uoms[1])) {$traceam3 = 0.3;$traceam1 = 0.2;} 
else {$traceam3 = 0.009;$traceam1 = 0.007;} 
// temp
if (preg_match("|C|",$uoms[0])) {$tempuom="C";$frzpoint = 0;}
else {$tempuom="F";$frzpoint = 32;$useustemp=true;} 
// wind
if (preg_match("|ms|",$uoms[2])) {} 
else if (preg_match("|mph|",$uoms[2])) {} 
else if (preg_match("|km|",$uoms[2])) {}
// snow
if (preg_match("|cm|",$uoms[1])) {$useussnow=false;} 
else {$useussnow=true;} 

include 'sunmoon.php';
include 'plaintext.php';
$wxd = file_get_contents($path_to_lastret);

$prec6h=0;
$prec3h=0;
$debug.="Parsing WXSIM...<br/>";
$csv = explode("\n", $wxd);
$howmany = count($csv);
$csv = preg_replace( '/\s+/', ' ', $csv ); 
$csv = preg_replace( '/\,/', '.', $csv );
$stuff = $csv[6];
$line = explode(' ', $stuff);
$namedata = array_reverse($line);
for($r=0;$r<count($namedata);$r++){
  if($namedata[$r] == "AIR"){$tempwp = $r;}
  if($namedata[$r] == "DEW"){$dewwp = $r;}
  if($namedata[$r] == "WCF"){$chillwp = $r;}
  if($namedata[$r] == "HT.I"){$heatwp = $r;}
  if($namedata[$r] == "W.DIR"){$dirwp = $r;}
  if($namedata[$r] == "W.SP"){$windwp = $r;}
  if($namedata[$r] == "G10M"){$windgstwp = $r;}
  if($namedata[$r] == "G1HR"){$windgstwp = $r;}
  if($namedata[$r] == "%RH"){$humwp = $r;}
  if($namedata[$r] == "SLP"){$barowp = $r;}
  if($namedata[$r] == "PTOT"){$precwp = $r;}
  if($namedata[$r] == "POP"){$popwp = $r;}
  if($namedata[$r] == "UVI"){$uviwp = $r;}
  if($namedata[$r] == "SN.C"){$snowwp = $r;}
  if($namedata[$r] == "TSMO"){$showerwp = $r;}
  if($namedata[$r] == "SWXO"){$severewp = $r;}
  if($namedata[$r] == "TSCD"){$tscdwp = $r;}
  if($namedata[$r] == "L.CD"){$covvwp = $r;}
  if($namedata[$r] == "SKY"){$covvwp = $r;}
  if($namedata[$r] == "TMAX"){$tmaxwp = $r;}
  if($namedata[$r] == "TMIN"){$tminwp = $r;}
  if($namedata[$r] == "LVL1"){$levelwp = $r;}
  if($namedata[$r] == "850T"){$t850wp = $r;}
  if($namedata[$r] == "DATE/TIME"){$timewp = $r;}
}
$condwp1 = $tempwp+1;
$condwp2 = $tempwp+2;
$condwp3 = $tempwp+3;

$a=0;
$day=0;
for($i=3;$i<$howmany;$i++) {
  $stuff = $csv[$i];
  if(is_substr($stuff,'Nighttime lows and daytime highs')) { break;}
  $lines = explode(' ', $stuff);
  $revdata = array_reverse($lines);
  if(is_numeric($revdata[2])){
    $t=str_replace("_"," ",$revdata[$timewp]);
    $t=str_replace(" UTC",":00 UTC",$t);
    date_default_timezone_set("UTC");
    $tt=strtotime($t);
    date_default_timezone_set($tzabb);
    $utcdiff=date("Z",$tt);
    $hh=date("H", $tt);
    $dn = wxsimsunstuff($tt);
    if((is_substr($t,':00:00')||is_substr($t,':55:00'))&&$tt>time()) {
      if((date("Hi",$tt)==0000||date("Hi",$tt)==2355)&&count($clouds)>=1) {getdaily();}
      $data[$a][timestamp] = $tt+$utcdiff;
      $data[$a][time] = date("H:i",$tt);
      $data[$a][day] = $day;
      $data[$a][temp]= fixtemp($revdata[$tempwp]);
      $data[$a][tempRoundedColor]= getcsscolor(round(fixtemp($revdata[$tempwp])));
      $data[$a][dewp] = fixtemp($revdata[$dewwp]);
      $data[$a][chill] = fixtemp($revdata[$chillwp]);
      if(fixtemp($revdata[$tempwp])<15){
        $data[$a][feels] = fixtemp($revdata[$chillwp]);
      }else{
        $data[$a][feels] = fixtemp($revdata[$heatwp]);
      }
      $data[$a][heat] = fixtemp($revdata[$heatwp]);
      $data[$a][rh] = $revdata[$humwp];
      $data[$a][wspd] = fixwind($revdata[$windwp]);
      $data[$a][wgst] = fixwind($revdata[$windgstwp]);
      $data[$a][wdir] = $revdata[$dirwp];
      $data[$a][bft] = get_bft($data[$a][wspd]);
      $data[$a][prmsl] = fixbaro($revdata[$barowp]);
      $data[$a][tcdc] = $revdata[$covvwp];
      $data[$a][snowd] = $revdata[$snowwp];
      $data[$a][uvi] = floor($revdata[$uviwp]);
      if($data[$a][uvi]<10){$data[$a][uvi]='0'.$data[$a][uvi];}
      $data[$a][prec] = fixprec($revdata[$precwp])-$pre;
      $data[$a][snowfall] = get_snowfall($data[$a][prec],$data[$a][temp]);
      if($revdata[$kiwp]<0){$data[$a][ki]=0;}
      $data[$a][lev] = fixtemp($revdata[$levelwp]);
      $data[$a][t850] = fixtemp($revdata[$t850wp]);
      $data[$a][shower] = $revdata[$showerwp];
      $data[$a][severe] = $revdata[$severewp];
      $data[$a][pop] = fixpop($revdata[$popwp]);
      if($revdata[$popwp]==''){$data[$a][pop]=-1;}
      $tsrisks[] = $revdata[$severewp];
      if(count($tsrisks)>1){$data[$a][tsrisk] = thunder(floor(max($tsrisks)));}else{$data[$a][tsrisk] = thunder(floor($tsrisks));}
      $tsdescs[] = $revdata[$tscdwp];
      $data[$a][rawcond]= $revdata[$condwp3].$revdata[$condwp2].$revdata[$condwp1];
      $pre=fixprec($revdata[$precwp]);
      $icons = explode('|',wanewicon($data[$a],$tempuom));
      if($dn<> "day") {$data[$a][icon] = $icons[1];} 
      else {$data[$a][icon] = $icons[0];}
      $tsdescs=array();
      $tsrisks=array();
      
      # Collect for daily
      $temps[]=$data[$a][temp];
      $temps[]=fixtemp($revdata[$tmaxwp]);
      $temps[]=fixtemp($revdata[$tminwp]);
      $wspds[]=$data[$a][wspd];
      $wdirs[]=$data[$a][wdir];
      $clouds[]=$data[$a][cloud];
      $pops[]=-1;
      $precs+=$data[$a][prec];
      $a++;
    }elseif(is_substr($t,':00:00')) {
      $pre=fixprec($revdata[$precwp]);
      $tsdescs=array();
      $tsrisks=array();
    }else{
      $tsdescs[]= $revdata[$tscdwp];
      $tsrisks[] = $revdata[$severewp];
    }
  }
}
//print_r($data);
getdaily();

$out=array(
  "plaintext"=>$pldata,
  "data"=>$data,
  "daily"=>$ddata
);

if($_GET[deb]){
  print_r($out);
}else{
  header('Access-Control-Allow-Origin: *');  
  header('Content-type: application/json');
  echo json_encode($out);
}


###################################################################

function getdaily(){
  global $tzabb,$t,$ddata,$utcdiff,$temps,$precs,$clouds,$wspds,$wdirs,$pops,$tsrisks,$icno12h,$ics12h,$icno12hna,$ics12hna,$latitude,$longitude,$day,$debug;
  if(count($clouds)==1){
    $temps=$clouds=$wspds=$wdirs=$pops=$tsrisks=$ics12h=$icno12h=$ics12hna=$icno12hna=array();
    return;
  }
  date_default_timezone_set($tzabb);
  $da=date("Y-m-d", strtotime($t)-(1*3600));
  $daystr=strtotime($t)-(1*3600);
  $ddata[$da]["day"] = checkday($daystr);
  date_default_timezone_set("UTC");
  $ddata[$da]["maxTemp"] = max($temps);
  $ddata[$da]["minTemp"] = min($temps);
  $ddata[$da]["maxTempRoundedColor"] = getcsscolor(round(max($temps)));
  $ddata[$da]["minTempRoundedColor"] = getcsscolor(round(min($temps)));
  $ddata[$da]["prec"] = $precs;
  $ddata[$da]["tcdc"] = round(array_sum($clouds)/count($clouds),0);
  $ddata[$da]["wspd"] = round(array_sum($wspds)/count($wspds),1);
  $ddata[$da]["wdir"] = round(array_sum($wdirs)/count($wdirs),0);
  $ddata[$da]["pop"] = round(array_sum($pops)/count($pops),0);
  $ddata[$da]["tsrisk"] = round(max($tsrisks),0);
  if(count($icno12h)>1){
    $maxs = array_search(max($icno12h),$icno12h);
    $icg=$ics12h[$maxs];
    $ddata[$da]["icon"] = $icg;
  }elseif(count($icno12h)==1){
    $ddata[$da]["icon"] = $ics12h[0];
  }else{
    $maxs = array_search(max($icno12hna),$icno12hna);
    $icg=$ics12hna[$maxs];
    $ddata[$da]["icon"] = $icg;
  }
  
  date_default_timezone_set($tzabb);
  $datetime = new DateTime();
  $datetime->setTimestamp($daystr);
  $sunmoon = new SunCalc($datetime, $latitude, $longitude);
  
  $m = date('m');
  $ddata[$da]["sunrise"]=$ddata[$da]["sunset"]="--:--";
  $suntimes = $sunmoon->getSunTimes();
  if(!empty($suntimes["sunrise"])){
    $ddata[$da]["sunrise"] = $suntimes["sunrise"]->format('H:i');
    $ddata[$da]["sunset"] = $suntimes["sunset"]->format('H:i');
  }else{
    if(($m > 4 && $m < 9) && ($ddata[$da]["sunrise"] == '')) {$ddata[$da]["sunrise"] = 'midnightsun'; }
    if(($m > 9 && $m < 4) && ($ddata[$da]["sunrise"] == '')) {$ddata[$da]["sunrise"] = 'polarnight'; }
  }
  
  $ddata[$da]["moonrise"]=$ddata[$da]["moonset"]="--:--";
  $moontimes = $sunmoon->getMoonTimes();
  if(!empty($moontimes["moonrise"])){$ddata[$da]["moonrise"] = $moontimes["moonrise"]->format('H:i');}
  if(!empty($moontimes["moonset"])){$ddata[$da]["moonset"] = $moontimes["moonset"]->format('H:i');}
  
  $moonphase = $sunmoon->getMoonIllumination();
  if($latitude>0){
    $ma=round($moonphase[phase]*28)-1;
  }else{
    $ma=round($moonphase[phase]*28)+1;
  }
  if($ma==28){$ma=27;}
  $ddata[$da]["moonage"] = $ma;

  date_default_timezone_set("UTC");

  $temps=$clouds=$wspds=$wdirs=$pops=$tsrisks=$ics12h=$icno12h=$ics12hna=$icno12hna=array();
  $precs=0;
  date_default_timezone_set($tzabb);
  $day++;
}

###################################################################

function fixwind($val){
  # the script use m/s as raw value
  global $uoms;
  if (preg_match("|m/s|",$uoms[2])) {return $val;} 
  else if (preg_match("|mph|",$uoms[2])) {return round($val*0.44704,2);} 
  else if (preg_match("|km|",$uoms[2])) {return round($val*0.277777,2);}
}

function fixbaro($val){
  # the script use hpa as raw value
  global $uoms;
  if (preg_match("|in|",$uoms[3])) {return round($val*33.8638866,2);} 
  else {return $val;} 
}

function fixtemp($val){
  # the script use C as raw value
  global $uoms;
  if (preg_match("|C|",$uoms[0])) {return $val;} 
  else if (preg_match("|F|",$uoms[0])) {return round((($val-32)/1.8),2);} 
}

function fixprec($val){
  # the script use mm as raw value
  global $uoms;
  if (preg_match("|mm|",$uoms[1])) {return $val;} 
  else if (preg_match("|in|",$uoms[1])) {return round($val*25.4,2);} 
}

function fixpop($val){
  global $popmulti;
  $pop = $val*$popmulti; 
  if($pop>100) {return 100;} 
  else {return $pop;}
}

function get_snowfall($val,$tmp){
  $out=0;
  if($tmp>1&&$tmp<=1.8){$out=$val*4;}
  if($tmp>-0.2&&$tmp<=1){$out=$val*7;}
  if($tmp>-3&&$tmp<=-0.2){$out=$val*10;}
  if($tmp>-7&&$tmp<=-3){$out=$val*15;}
  if($tmp>-10&&$tmp<=-7){$out=$val*20;}
  if($tmp>-13&&$tmp<=-10){$out=$val*25;}
  if($tmp>-18&&$tmp<=-13){$out=$val*30;}
  if($tmp<=-18){$out=$val*35;}
  return sprintf("%01.1f",($out/10)); # output as cm
}

function get_bft($w) {
 	if($w<0.3){$b=0;}
 	if($w>=0.3&&$w<1.5){$b=1;}
  if($w>=1.5&&$w<3.3){$b=2;}
  if($w>=3.3&&$w<5.5){$b=3;}
  if($w>=5.5&&$w<8){$b=4;}
  if($w>=8&&$w<10.8){$b=5;}
  if($w>=10.8&&$w<13.9){$b=6;}
  if($w>=13.9&&$w<17.2){$b=7;}
  if($w>=17.2&&$w<20.7){$b=8;}
  if($w>=20.7&&$w<24.5){$b=9;}
  if($w>=24.5&&$w<28.4){$b=10;}
  if($w>=28.4&&$w<32.6){$b=11;}
  if($w>=32.6){$b=12;}
  return $b;
}

function thunder($raw){
  switch (TRUE) {
    case ($raw <= 0): return 0; break;
    case ($raw == 1): return 10; break;
    case ($raw == 2): return 20; break;
    case ($raw == 3): return 40; break;
    case ($raw == 4): return 60; break;
    case ($raw == 5): return 80; break;
    case ($raw == 6): return 90; break;
  }
}

############################################################################
# ICONSELECTOR
function wanewicon($data,$unit) {
global $dn,$icno12hna,$ics12hna,$icno12h,$ics12h,$hh,$tsdescs,$tt,$uoms;

  foreach($data as $key => $value) {$$key = $value;}
  # Clouds
  switch (TRUE) {
    case($tcdc<12.5):$clouds="skc";break;
    case($tcdc>12.5&&$tcdc<37.5):$clouds="few";break;
    case($tcdc>=37.5&&$tcdc<62.5):$clouds="sct";break;
    case($tcdc>=62.5&&$tcdc<95):$clouds="bkn";break;
    case($tcdc>=95):$clouds="ovc";break;
  }
  # Fog
  switch (TRUE) {
    case (preg_match("|HEAVYFOG|",$rawcond)): $fog = 'fog'; break;
    case (preg_match("|MOD.FOG|",$rawcond)): $fog = 'fog'; break;
    case (preg_match("|LIGHTFOG|",$rawcond)): $fog = 'fog'; break;
  }
  
  # Rates from UK Metoffice/SMHI
  $hard=false;
  $pr=false;
  $shower=false;
  $trace=0.1;
  $a1=2;$a2=10;$b1=1;$b2=5;
  if($tcdc <= 95) { 
    $shower = ' showers';  
    switch (TRUE) {
      case($prec>=$trace&&$prec<$a1):$hard="light";break;
      case($prec>=$a1&&$prec<$a2):$hard="moderate";break;
      case($prec>=$a2):$hard="heavy";break;
    }
  }else{
    switch (TRUE) {
      case($prec>=$trace&&$prec<$b1):$hard="light";break;
      case($prec>=$b1&&$prec<$b2):$hard="moderate";break;
      case($prec>=$b2):$hard="heavy";break;
    }
  }
  # Type
  switch (TRUE) {
    case (($lev > 3 || $t850 > 3) && $temp < 0): $pr = 'freezingrain'; break;
    case ($dewp <= 0 && $temp < 0): $pr = 'snow'; break;
    case ($dewp > 0 && $dewp <= 0.8): $pr = 'sleet'; break;
    case ($dewp > 0.8): $pr = 'rain'; break;
    case ($temp < 0): $pr = 'snow'; break;
    case ($temp >= 0 && $temp<= 1.8): $pr = 'sleet'; break;
    case ($temp > 1.8): $pr = 'rain'; break;
    default: $pr = 'rain';
  }
  if($prec<0.1||($pop<>-1&&$pop<30)){$pr=false;$shower=false;}
  $prcond = $clouds.$hard.$pr.$shower.$fog;
  $prcond = str_replace(' ','',$prcond);
  if(count($tsdescs)>0){$tsdesc=max($tsdescs);}else{$tsdesc=$tsdescs;}

  $arr=array(302,303,402,403,404,501,503,504,505,506);
  switch (TRUE) {

    case($tsdesc==302&&$tcdc>85&&$prec>0):$newicon = "rainthunder|rainthunder";$icn=60;break;
    case($tsdesc==303&&$tcdc>85&&$prec>0):$newicon = "rainthunder|rainthunder";$icn=61;break;
    case($tsdesc==402&&$tcdc>85&&$prec>0):$newicon = "rainthunder|rainthunder";$icn=62;break;
    case($tsdesc==403&&$tcdc>85&&$prec>0):$newicon = "rainthunder|rainthunder";$icn=63;break;
    case($tsdesc==404&&$tcdc>85&&$prec>0):$newicon = "heavy_thunder|heavy_thunder";$icn=70;break;
    case($tsdesc==501&&$tcdc>85&&$prec>0):$newicon = "rainthunder|rainthunder";$icn=64;break;
    case($tsdesc==503&&$tcdc>85&&$prec>0):$newicon = "heavy_thunder|heavy_thunder";$icn=71;break;
    case($tsdesc==504&&$tcdc>85&&$prec>0):$newicon = "heavy_thunder|heavy_thunder";$icn=72;break;
    case($tsdesc==505&&$tcdc>85&&$prec>0):$newicon = "heavy_thunder|heavy_thunder";$icn=73;break;
    case($tsdesc==506&&$tcdc>85&&$prec>0):$newicon = "heavy_thunder|heavy_thunder";$icn=74;break;
    // If bkn
    case(in_array($tsdesc,$arr)&&$tcdc>35&&$prec>0):$newicon = "rainthundershower|nt_rainthundershower";$icn=50;break;

    # Freezing rain
    case (preg_match("|freezingrain|",$prcond)): $newicon = "freezingrain|freezingrain";$icn=40; break;
    # Snow
    case (preg_match("|ovcheavysnow|",$prcond)): $newicon = "snow3|snow3";$icn=38; break;
    case (preg_match("|ovcmoderatesnow|",$prcond)): $newicon = "snow2|snow2";$icn=37; break;
    case (preg_match("|ovclightsnow|",$prcond)): $newicon = "snow1|snow1";$icn=36; break;
    case (preg_match("|bknheavysnow|is",$prcond)): $newicon = "heavysnowshowers|nt_heavysnowshowers";$icn=35; break;
    case (preg_match("|bknmoderatesnow|is",$prcond)): $newicon = "moderatesnowshowers|nt_moderatesnowshowers";$icn=34; break;
    case (preg_match("|bknlightsnow|is",$prcond)): $newicon = "snowshowers|nt_snowshowers";$icn=33; break;
    case (preg_match("![sct|few]heavysnow!is",$prcond)): $newicon = "heavysnowshowers|nt_heavysnowshowers";$icn=32; break;
    case (preg_match("![sct|few]moderatesnow!is",$prcond)): $newicon = "moderatesnowshowers|nt_moderatesnowshowers";$icn=31; break;
    case (preg_match("![sct|few]lightsnow!is",$prcond)): $newicon = "snowshowers|nt_snowshowers";$icn=30; break;
    # Sleet
    case (preg_match("|ovcheavysleet|",$prcond)): $newicon = "heavysleet|heavysleet";$icn=28; break;
    case (preg_match("|ovcmoderatesleet|",$prcond)): $newicon = "sleet|sleet";$icn=27; break;
    case (preg_match("|ovclightsleet|",$prcond)): $newicon = "sleet|sleet";$icn=26; break;
    case (preg_match("|bknheavysleet|is",$prcond)): $newicon = "heavysleetshowers|nt_heavysleetshowers";$icn=25; break;
    case (preg_match("|bknmoderatesleet|is",$prcond)): $newicon = "sleetshowers|nt_sleetshowers";$icn=24; break;
    case (preg_match("|bknlightsleet|is",$prcond)): $newicon = "sleetshowers|nt_sleetshowers";$icn=23; break;
    case (preg_match("![sct|few]heavysleet!is",$prcond)): $newicon = "heavysleetshowers|nt_heavysleetshowers";$icn=22; break;
    case (preg_match("![sct|few]moderatesleet!is",$prcond)): $newicon = "sleetshowers|nt_sleetshowers";$icn=21; break;
    case (preg_match("![sct|few]lightsleet!is",$prcond)): $newicon = "sleetshowers|nt_sleetshowers";$icn=20; break;
    # Rain
    case (preg_match("!ovcheavy[rain|showers]!is",$prcond)): $newicon = "rain3|rain3";$icn=18; break;
    case (preg_match("!ovcmoderate[rain|showers]!is",$prcond)): $newicon = "rain2|rain2";$icn=17; break;
    case (preg_match("!ovclight[rain|showers]!is",$prcond)): $newicon = "rain1|rain1";$icn=16; break;
    case (preg_match("!bknheavy[rain|showers]!is",$prcond)): $newicon = "heavyrainshowers|nt_heavyrainshowers";$icn=15; break;
    case (preg_match("!bknmoderate[rain|showers]!is",$prcond)): $newicon = "moderaterainshowers|nt_moderaterainshowers";$icn=14; break;
    case (preg_match("!bknlight[rain|showers]!is",$prcond)): $newicon = "rainshowers|nt_rainshowers";$icn=13; break;
    case (preg_match("![sct|few]heavy[rain|showers]!is",$prcond)): $newicon = "heavyrainshowers|nt_heavyrainshowers";$icn=12; break;
    case (preg_match("![sct|few]moderate[rain|showers]!is",$prcond)): $newicon = "moderaterainshowers|nt_moderaterainshowers";$icn=11; break;
    case (preg_match("![sct|few]light[rain|showers]!is",$prcond)): $newicon = "rainshowers|nt_rainshowers";$icn=10; break;
    # Fog
    case (preg_match("|fog|",$prcond)): $newicon = "fog|nt_fog";$icn=6; break;
    # Other
    case (preg_match("|ovc|",$prcond)): $newicon = "cloudy|cloudy";$icn=5; break;
    case (preg_match("|bkn|",$prcond)): $newicon = "mostlycloudy|nt_mostlycloudy";$icn=4; break;
    case (preg_match("|sct|",$prcond)): $newicon = "partlycloudy|nt_partlycloudy";$icn=3; break;  
    case (preg_match("|few|",$prcond)): $newicon = "mostlyclear|nt_mostlyclear";$icn=2; break;
    case (preg_match("|skc|",$prcond)): $newicon = "clear|nt_clear";$icn=1; break;
  }
  $newsicon = explode("|",$newicon);
  if($tt>time()){
    if($dn<>"day") {
      $icno12hna[]=$icn;
      $ics12hna[]=$newsicon[1];
    } else {
      $icno12h[]=$icn;
      $ics12h[]=$newsicon[0];
    }
  }
return $newicon;
}

function getcsscolor($raw){
 $raw = round($raw);
  switch (TRUE) {
    case($raw>=38):return"rgb(223,6,84)";break;
    case($raw==37):return"rgb(219, 9, 73)";break;
    case($raw==36):return"rgb(215, 12, 62)";break;
    case($raw==35):return"rgb(211, 15, 51)";break;
    case($raw==34):return"rgb(207, 18, 40)";break;
    case($raw==33):return"rgb(203, 21, 29)";break;
    case($raw==32):return"rgb(199, 24, 18)";break;
    case($raw==31):return"rgb(195, 28, 7)";break;
    case($raw==30):return"rgb(207, 32, 7)";break;
    case($raw==29):return"rgb(211, 42, 8)";break;
    case($raw==28):return"rgb(215,52,8)";break;
    case($raw==27):return"rgb(219, 62, 9)";break;
    case($raw==26):return"rgb(223, 72, 9)";break;
    case($raw==25):return"rgb(227,82,9)";break;
    case($raw==24):return"rgb(232, 92, 10)";break;
    case($raw==23):return"rgb(236, 102, 10)";break;
    case($raw==22):return"rgb(240, 112, 11)";break;
    case($raw==21):return"rgb(244, 122, 11)";break;
    case($raw==20):return"rgb(244, 144, 11)";break;
    case($raw==19):return"rgb(244, 152, 11)";break;
    case($raw==18):return"rgb(244, 160, 11)";break;
    case($raw==17):return"rgb(244, 168, 11)";break;
    case($raw==16):return"rgb(244, 176, 11)";break;
    case($raw==15):return"rgb(244, 184, 11)";break;
    case($raw==14):return"rgb(244, 192, 11)";break;
    case($raw==13):return"rgb(244, 200, 11)";break;
    case($raw==12):return"rgb(244, 208, 11)";break;  
    case($raw==11):return"rgb(244, 208, 11)";break;
    case($raw==10):return"rgb(233, 211, 17)";break;
    case($raw==9):return"rgb(222, 214, 22)";break;
    case($raw==8):return"rgb(211, 218, 28)";break;
    case($raw==7):return"rgb(200, 221, 33)";break;
    case($raw==6):return"rgb(189, 225, 39)";break;
    case($raw==5):return"rgb(178, 229, 44)";break;
    case($raw==4):return"rgb(167, 233, 50)";break;
    case($raw==3):return"rgb(156, 237, 55)";break;
    case($raw==2):return"rgb(145, 241, 61)";break;
    case($raw==1):return"#82F543";break; // 130, 245, 67
    case($raw==0):return"#91ccff";break;
    case($raw==-1):return"#91ccff";break;
    case($raw==-2):return"#91ccff";break;
    case($raw==-3):return"#7fc4ff";break;
    case($raw==-4):return"#7fc4ff";break;
    case($raw==-5):return"#6dbcff";break;
    case($raw==-6):return"#6dbcff";break;
    case($raw==-7):return"#5bb4ff";break;
    case($raw==-8):return"#49acff";break;
    case($raw==-9):return"#259aff";break;
    case($raw<=-10):return"#1392ff";break;
    /*case($raw==-11):return"#0082ef";break;
    case($raw==-12):return"#0072cf";break;
    case($raw==-13):return"#0062af";break;
    case($raw==-14):return"#00528f";break;
    case($raw==-15):return"#00467f";break;
    case($raw==-16):return"#003c7f";break;
    case($raw==-17):return"#00327f";break;
    case($raw==-18):return"#00287f";break;
    case($raw==-19):return"#001e7f";break;
    case($raw==-20):return"#00187f";break;
    case($raw==-21):return"#00007f";break;
    case($raw==-22):return"#0c007f";break;
    case($raw==-23):return"#19007f";break;
    case($raw==-24):return"#25007f";break;
    case($raw==-25):return"#32007f";break;
    case($raw==-26):return"#3e007f";break;
    case($raw==-27):return"#4b007f";break;
    case($raw==-28):return"#57007f";break;
    case($raw==-29):return"#64007f";break;
    case($raw==-30):return"#78048d";break;
    case($raw==-31):return"#870898";break;
    case($raw==-32):return"#960ca3";break;
    case($raw==-33):return"#a510ae";break;
    case($raw==-34):return"rgb(180,20,185)";break;
    case($raw==-35):return"rgb(182,18,160)";break;
    case($raw==-36):return"rgb(185,16,150)";break;
    case($raw==-37):return"rgb(188,14,140)";break;
    case($raw==-38):return"rgb(191,13,130)";break;
    case($raw<=-39):return"rgb(194,12,120)";break;*/
   }
}

function checkday($val){
  global $days,$months,$lastday,$debug,$ptz;
  $curr = date('z', time());
  $va  = date('z', $val);
  $vv  = date('w', $val);
  $mm  = date('n', $val);
  $cday = date('dm', time());
  $fday = date('dm', $val);

  $day = '';
  if($curr == $va) {
    $day = TODAY;
  } else if(($va-$curr) == 1 || ($cday == "3112" && $fday == "0101")) {
    $day = TOMORROW;
  } else {
    $day = $days[$vv].' '.date("d.m",$val);
  }
  return $day;
}

function wxsimsunstuff($time){
global $latitude,$longitude;
$offset = date('Z')/3600;
$zenith=90+40/60;
$sunrise_epoch = date_sunrise($time, SUNFUNCS_RET_TIMESTAMP, $latitude,$longitude, $zenith, $offset);
$sunset_epoch  = date_sunset($time, SUNFUNCS_RET_TIMESTAMP, $latitude,$longitude, $zenith, $offset);

if ($time >= $sunset_epoch or $time <= $sunrise_epoch) {
$dayornight = 'night';
} else {
$dayornight = 'day';
}

return $dayornight;
}

function is_substr($haystack, $needle){
$pos = strpos($haystack, $needle);
   if ($pos === false) {
   return false;
   } else {
   return true;
   }
}