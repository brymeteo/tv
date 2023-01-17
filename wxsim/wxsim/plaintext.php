<?php

ini_set('display_errors', '0');
#########################################################
# Translations, borrowed from Ken's plaintext-parser ;)

// load the config file
$pathtodata=str_replace("lastret.txt","",$path_to_lastret);
$config = file("plaintext-parser-data.txt");  // 
if ($lang <> 'en' and file_exists("plaintext-parser-lang-$lang.txt") ) {
  $doTranslate = true;
  $lfile = file("plaintext-parser-lang-$lang.txt");
  foreach ($lfile as $val) {
    array_push($config,$val);
  }
  $Status .= "<!-- translation file for '$lang' loaded -->\n";
  if (strpos($UTFLang,$lang) > 0) {$useCharSet = 'UTF-8'; $Status .= "<!-- using UTF-8 -->\n";}
} else {
  $doTranslate = false;
  if($lang <> 'en') {
    $Status .= "<!-- translation file for '$lang' not found -->\n";
    $lang = 'en';
  }
}
$LanguageLookup = array();
$WindLookup = array( 
'north' => 'N',
'north-northeast' => 'NNE',
'northeast' => 'NE',
'east-northeast' => 'ENE',
'east' => 'E',
'east-southeast' => 'ESE',
'southeast' => 'SE',
'south-southeast' => 'SSE',
'south' => 'S',
'south-southwest' => 'SSW',
'southwest' => 'SW',
'west-southwest' => 'WSW',
'west' => 'W',
'west-northwest' => 'WNW',
'northwest' => 'NW',
'north-northwest' => 'NNW'
);

$BeaufortText = array('Calm', 'Light air', 'Light breeze','Gentle breeze', 'Moderate breeze', 'Fresh breeze', 'Strong breeze', 'Near gale', 'Gale', 'Strong gale', 'Storm', 'Violent storm', 'Hurricane' );
$BeaufortKTS = array(1,4,7,11,17,22,28,34,41,48,56,64,64);
$BeaufortMPH = array(1,4,8,13,19,25,32,39,47,55,64,73,73);
$BeaufortKPH = array(1,6,12,20,30,40,51,63,76,88,103,118,118);
$BeaufortMS  = array(0.2,1.6,3.4,5.5,8.0,10.8,13.9,17.2,20.8,24.5,28.5,32.7,32.7);

reset($config);
foreach ($config as $key => $rec) { 
  $recin = trim($rec);
  if ($recin and substr($recin,0,1) <> '#') { // got a non comment record
    list($type,$keyword,$dayicon,$nighticon,$condition) = explode('|',$recin . '|||||');
    if (isset($type) and strtolower($type) == 'cond' and isset($condition)) {
      $Conditions["$keyword"] = "$dayicon\t$nighticon\t$condition";
    }
    if (isset($type) and strtolower($type) == 'precip' and isset($nighticon)) {
      $Precip["$keyword"] = "$dayicon\t$nighticon";
    }
    if (isset($type) and strtolower($type) == 'snow' and isset($nighticon)) {
      $Snow["$keyword"] = "$dayicon\t$nighticon";
    }
    if (isset($type) and strtolower($type) == 'lang' and isset($dayicon)) {
      $Language["$keyword"] = "$dayicon";
    } 
    if (isset($type) and strtolower($type) == 'langlookup' and isset($dayicon)) {
      $LanguageLookup["$keyword"] = "$dayicon";
    } 
    if (isset($type) and strtolower($type) == 'charset' and isset($keyword)) {
      $useCharSet = trim($keyword);
      $Status .= "<!-- using charset '$useCharSet' -->\n";
    } 
    if (isset($type) and strtolower($type) == 'notavail' and isset($keyword)) {
      $notAvail = trim($keyword);
    } 
  } // end if not comment or blank
} // end loading of $Conditions and $Precip

if (count($LanguageLookup) < 1) {$doTranslate = false; }

############################################################
# plaintext.txt, snippets borrowed from Ken's plaintext-parser

$pt = file($pathtodata."plaintext.txt");
// fix missing space at start of line if need be
foreach ($pt as $i => $line) {
	if(substr($line,0,1) != ' ') {$pt[$i] = ' ' . $line;}
}
$plaintext = implode('',$pt);   // get the plaintext file.
$plaintext = preg_replace('![\n][\r|\n]+!s',"\n \n",$plaintext);
$plaintext = preg_replace('![\r|\n]+ [\r|\n]+!s',"\t\t",$plaintext); 
$plaintext .= "\t\t";  // make sure a delimiter is at the end too.
$plaintext = preg_replace('|_|is','',$plaintext); // remove dashed line in front

// The loop
$pldata=array();
preg_match_all('!\t\s(.*):\s(.*)\t!Us',$plaintext,$matches); // split up the forecast
$howmany = count($matches[1]);
for ($i=0;$i<$howmany;$i++) {

  $wxallday = trim($matches[1][$i]);
  
  $wxalltext =  preg_replace('![\r|\n]+!is','',trim($matches[2][$i])); // remove CR and LF chars.
  $rawtext = $wxalltext;

  #################################################################
  # Temp
  if(preg_match('!(High|Low) ([-|\d]+)(.*)[\.|,]!i',$wxalltext,$mtemp)) {
    $temp = fixtemp($mtemp[2]);
  }
  
  ##################################################################
  # Precip & POP
  $wxallpop = 0;
  if (preg_match('!Chance of precipitation (.*) percent!i',$wxalltext,$mtemp)) {
    $wxallpop = $mtemp[1];
    $wxallpop = preg_replace('|less than |i','<',$wxallpop);
    if ($wxallpop == '<20') {$wxallpop[$i] = 10;}
    if ($wxallpop == 'near 100') { $wxallpop = 100; }
  }

  reset($Precip);  // Do search in load order
  $wxallprec = 0;
  foreach ($Precip as $pamt => $prec) { // look for matching precipitation amounts  
    if(preg_match("!$pamt!is",$wxalltext,$mtemp)) {
      list($amount,$units) = explode("\t",$prec);
      $wxallprec = $amount;
      break;
    }
  } // end of precipitation amount search

  $wxallprec = str_replace("&lt;","",$wxallprec);
  
  ####################################################
  # Icon
  // now look for harshest conditions first.. (in order in -data file
  reset($Conditions);  // Do search in load order
  foreach ($Conditions as $cond => $condrec) { // look for matching condition  
    if(preg_match("!$cond!i",$wxalltext,$mtemp)) {
      list($dayicon,$nighticon,$condition) = explode("\t",$condrec);
    if (preg_match('!chance!i',$condition) and $wxallpop < $minPoP) {
      continue; // skip this one
    }
    if (preg_match("|$cond level|i",$wxalltext) ) {
      continue; // skip 'snow level' and 'freezing level' entries
    }
    $wxallcond = get_lang($condition);
    if (preg_match('|night|i',$wxallday)) {
      $wxallicon = $nighticon;
    } else {
      $wxallicon = $dayicon;
    }
    break;
    }
  } // end of conditions search
  //  now fix up the full icon name and PoP if available
  $curicon = $wxallicon  . '.jpg';
  if ($wxallpop > 0) {
      $testicon = preg_replace("|\.jpg|","$wxallpop.jpg",$curicon);
    if (file_exists($iconDir . $testicon)) {
      $wxallicon = $testicon;
    } else {
      $wxallicon = $curicon;
    }
  } else {
    $wxallicon = $curicon;
  }
 
  $iconcheck = plaintexticon($wxallicon,$wxallprec,$temp,$wxallpop,$wxalltext,$tempuom);
  $icons = explode('|',$iconcheck);
  if (preg_match("|night|",$wxallday)) {
    $newicon = $icons[1];
    $wxalltime = get_lang($wxallday).' 18-06';
  }else {
    $newicon = $icons[0];
    $wxalltime = get_lang($wxallday).' 06-18';
  }

  $wxallbic = $newicon;
  
  #############################################################
  # UV
  // extract UV index value
  $wxalluv=0;
  if (preg_match('|UV index up to (\d+)\.|i',$wxalltext,$mtemp) ) {
    $wxalluv = $mtemp[1];
  }
  $uvic = $wxalluv;
  if($uvic<10){$uvic = '0'.$uvic;}
  
    #####################################################
  # Wind
  $wr = array ("N" => 0,"NNE" => 22,"NE" => 45, "ENE" => 67,"E" => 90, "ESE" => 112, "SE" => 135, 
  "SSE" => 157, "S" => 180,"SSW" => 202,"SW" => 225, "WSW" => 247, "W" => 270, "WNW" => 292, "NW" => 315, "NNW" => 337);
  $testwind = str_replace('Wind chill','Wind-chill',$rawtext);
  if (preg_match('|Wind (.*)\.|Ui',$testwind,$mtemp) ) {
    $wtemp = preg_replace('! around| near| in the| morning| evening| afternoon| midnight| tonight| to| after!Uis','',$mtemp[1]);
    $wtemp = explode(', ',$wtemp);
    $wparts = explode(' ',$wtemp[0]); // break it by spaces.
    for ($k =0;$k<count($wtemp);$k++) {
      $wparts = explode(' ',$wtemp[$k]);	
      if(isset($WindLookup[$wparts[0]]) ) { // got <dir> [speed] [units] format
        $wxallwdir = $WindLookup[$wparts[0]];  // get abbreviation for direction
        $wxallwind = $wparts[1];  // get speed
      }
    }
  }

  if(crop($wxallwind)=="calm"){
    $wspd=0;
  }else{
    $wspd=fixwind(round(crop($wxallwind)));
  }
  $wdir=$wr[crop($wxallwdir)];
  
  #############################################################
  # Text-section

  // extract temperature High/Low values
  $tempDegrees = "&deg;";
  if (preg_match('!(high|low) ([-|\d]+)[\.|,]!i',$wxalltext,$mtemp)) {
    $wxalltemp = get_lang($mtemp[1] .':') . ' ' . $mtemp[2] . $tempDegrees;
    if ($tempDegrees) {  // fix up degrees in the text
      $wxalltext = preg_replace('|' . $mtemp[1] . ' ' . $mtemp[2] .'|',$mtemp[1] . ' ' . $mtemp[2] . $tempDegrees,$wxalltext);
      $wxalltext = preg_replace('/Wind chill down to ([-|\d]+)/i',"Wind chill down to $1$tempDegrees",$wxalltext);
      $wxalltext = preg_replace('/Heat index up to ([-|\d]+)/i',"Heat index up to $1$tempDegrees",$wxalltext);
    }
  }

  $fixedtxt = $wxalltext;
  # Snow & ice
  // Freezinglevel
  $frzltxt = '';
  if(preg_match('|Maximum freezing level(.*)above sea level.|',$fixedtxt,$snowstr)) {
    if($snowlcolor == true) {
      $frzltxt = str_replace($snowstr[0],'. <span style="color:#3399CC"><b>'.$snowstr[0].'</b></span>',$snowstr[0]);
    } else {
      $frzltxt = ' '.$snowstr[0];
    }
    $fixedtxt = str_replace($snowstr[0],'',$fixedtxt);
  } else if(preg_match('|Minimum freezing level(.*)above sea level.|',$fixedtxt,$snowstr)) {
    if($snowlcolor == true) {
      $frzltxt = str_replace($snowstr[0],'. <span style="color:#3399CC"><b>'.$snowstr[0].'</b></span>',$snowstr[0]);
    } else {
      $frzltxt = ' '.$snowstr[0];
    }
    $fixedtxt = str_replace($snowstr[0],'',$fixedtxt);
  }
  // Snowlevel
  $snowltxt = '';
  if(preg_match('|Maximum snow level(.*)above sea level.|',$fixedtxt,$snowstr)) {
    if($snowlcolor == true) {
      $snowltxt = str_replace($snowstr[0],'. <span style="color:#3399CC"><b>'.$snowstr[0].'</b></span>',$snowstr[0]);
    } else {
      $snowltxt = ' '.$snowstr[0];
    }
    $fixedtxt = str_replace($snowstr[0],'',$fixedtxt);
  } else if(preg_match('|Minimum snow level(.*)above sea level.|',$fixedtxt,$snowstr)) {
    if($snowlcolor == true) {
      $snowltxt = str_replace($snowstr[0],'. <span style="color:#3399CC"><b>'.$snowstr[0].'</b></span>',$snowstr[0]);
    } else {
      $snowltxt = ' '.$snowstr[0];
    }
    $fixedtxt = str_replace($snowstr[0],'',$fixedtxt);
  }
  // Freezing rain
  $snowtxt = '';
  $frztxt = '';
  if(preg_match('|Little if any freezing rain accumulation(.*).|Ui',$fixedtxt,$frestr)) {
    $frztxt = str_replace($frestr[0],'. <span style="color:#EE7621"><b>'.$frestr[0].'</b></span>',$frestr[0]);
    $fixedtxt = str_replace($frestr[0],'',$fixedtxt);
  } else if(preg_match('|Above-ground freezing rain accumulation up(.*).|Ui',$fixedtxt,$frestr)) {
    $fixedtxt = str_replace($frestr[0],'',$fixedtxt);
  } else if(preg_match('|Freezing rain accumulation up(.*).|Ui',$fixedtxt,$frestr)) {
    $fixedtxt = str_replace($frestr[0],'',$fixedtxt);
  } else if(preg_match('|Freezing rain accumulation(.*).|Ui',$fixedtxt,$frestr)) {
    $frztxt = str_replace($frestr[0],'. <span style="color:#EE7621"><b>'.$frestr[0].'</b></span>',$frestr[0]);
    $fixedtxt = str_replace($frestr[0],'',$fixedtxt);
  }
  // Snow
  if(preg_match('|Little or no snow(.*)expected.|',$fixedtxt,$snowstr)) {
    $snowtxt = str_replace($snowstr[0],'. <span style="color:#3399CC"><b>'.$snowstr[0].'</b></span>',$snowstr[0]);
    $fixedtxt = str_replace($snowstr[0],'',$fixedtxt);
  } else if(preg_match('|Little if any snow(.*)expected.|',$fixedtxt,$snowstr)) {
    $snowtxt = str_replace($snowstr[0],'. <span style="color:#3399CC"><b>'.$snowstr[0].'</b></span>',$snowstr[0]);
    $fixedtxt = str_replace($snowstr[0],'',$fixedtxt);
  }else if(preg_match('|No (.*)\.|Ui',$fixedtxt,$snowstr)) {
    $snowtxt = ' '.$snowstr[0];
    $fixedtxt = str_replace($snowstr[0],'',$fixedtxt);
  }else if(preg_match('!Snow or ice(.*).!i',$fixedtxt,$snowstr)) {
    $snowtxt = str_replace($snowstr[0],'. <span style="color:#3399CC"><b>'.$snowstr[0].'</b></span>',$snowstr[0]);
    $fixedtxt = str_replace($snowstr[0],'',$fixedtxt);
  }else if(preg_match('!snow accumulation(.*).!i',$fixedtxt,$snowstr)) {
    $snowtxt = str_replace($snowstr[0],'. <span style="color:#3399CC"><b>'.$snowstr[0].'</b></span>',$snowstr[0]);
    $fixedtxt = str_replace($snowstr[0],'',$fixedtxt);
  }
    
  $fixedtxt = str_replace('Wind chill','Wind-chill',$fixedtxt);
  preg_match('|Wind-chill (.*)\.|Ui',$fixedtxt,$wchillstr);
  $orgwc = $wchillstr[0];
  preg_match('|Wind (.*)m\/s\.|Ui',$fixedtxt,$windstr);
  $fixedtxt = str_replace($windstr[0],"",$fixedtxt);
  preg_match('|Wind (.*)\.|Ui',$fixedtxt,$windstr);
  $fixedtxt = str_replace($windstr[0],"",$fixedtxt);
  if($lang == "fi"){ // Few finnish fixes
    $wchillstr[0] = str_replace('to',"and",$wchillstr[0]);
    if(preg_match('|and|',$wchillstr[0])) {
      $wchillstr[0] = str_replace('.'," valilla.",$wchillstr[0]);
    }
    $fixedtxt = str_replace($orgwc,$wchillstr[0],$fixedtxt);
  } // Eof finnish fixes
  $fixedtxt = str_replace('Wind-chill','Wind chill',$fixedtxt);
  //PoP
  preg_match('|Chance of precipitation(.*)percent.|Ui',$fixedtxt,$windstr);
  $fixedtxt = str_replace($windstr[0],"",$fixedtxt);
  // Rain
  preg_match('|Precipitation(.*)mm\.|Ui',$fixedtxt,$windstr);
  $fixedtxt = str_replace($windstr[0],"",$fixedtxt);
    
  $fixedtxt = str_replace("Heat index up to"," Heat index:",$fixedtxt);
  $fixedtxt = str_replace(" mostly less than"," less than",$fixedtxt);
  $fixedtxt = str_replace("mix of snow and sleet","snow",$fixedtxt);

  preg_match('|UV(.*)\. |Ui',$fixedtxt,$windstr);
  $fixedtxt = str_replace($windstr[0],"",$fixedtxt);
    
  preg_match('|Low(.*)&deg;.|',$fixedtxt,$wcstr);
  $fixedtxt = str_replace($wcstr[0],"",$fixedtxt);
  preg_match('!but temperatures(.*)(night|afternoon|morning)\. !i',$fixedtxt,$wcstr);
  $fixedtxt = str_replace($wcstr[0],"",$fixedtxt);
  $fixedtxt = str_replace("High risk","Increased risk",$fixedtxt); // Rename "high risk" so the parser not remove it
  $fixedtxt = str_replace("high thin","highthin",$fixedtxt); // Rename "high thin" so the parser not remove it
  $fixedtxt = str_replace("high cloudiness","highcloudiness",$fixedtxt); // Rename "high thin" so the parser not remove it
  preg_match('|High (.*)&deg;.|Ui',$fixedtxt,$wjstr);
  $fixedtxt = str_replace($wjstr[0],"",$fixedtxt);
  if(!preg_match('|thunder|Ui',$windstr[0])) {
    $fixedtxt = str_replace($windstr[0],"",$fixedtxt);
  }
  $fixedtxt = str_replace("Increased risk","High risk",$fixedtxt); // Put "high risk" back ;)
  $fixedtxt = str_replace("highthin","high thin",$fixedtxt); // Put "high risk" back ;)
  $fixedtxt = str_replace("highcloudiness","high cloudiness",$fixedtxt); // Rename "high thin" so the parser not remove it
    
  // Thunder ;)
  $fixedtxt = fixthunder($fixedtxt);
   
  $fixedtxt = $fixedtxt.$snowtxt.$frztxt.$frzltxt.$snowltxt;
  $fixedtxt = preg_replace('/\s\s+/', ' ',$fixedtxt);
  $fixedtxt = str_replace(". .",".",$fixedtxt);
  $fixedtxt = str_replace("..",".",$fixedtxt);
  $fixedtxt = str_replace("</b></span>.","</b></span>",$fixedtxt);
  if ($doTranslate) {
    reset ($Language);
    foreach ($Language as $key => $replacement) {
      $fixedtxt = str_replace($key,$replacement,$fixedtxt);
    }
  }
  //$fixedtxt = preg_replace('!\.\s+([a-z])!es',"'.  ' . strtoupper('\\1')",$fixedtxt);
  //$fixedtxt = ucfirst(strtolower($fixedtxt));
  $fixedtxt = preg_replace_callback('/([.!?])\s*(\w)/', 
     create_function('$matches', 'return strtoupper($matches[0]);'), $fixedtxt);
  if(!mb_detect_encoding($fixedtxt, 'UTF-8', true)){$fixedtxt=utf8_encode($fixedtxt);}
  
  ####################################################
  
  $pldata[$i]=array(
    "time"=>get_lang($wxallday),
    "temp"=>$temp,
    "tempRoundedColor"=>getcsscolor(round($temp)),
    "wdir"=>$wdir,
    "wspd"=>$wspd,
    "bft"=>get_bft($wspd),
    "prec"=>$wxallprec,
    "pop"=>$wxallpop,
    "uv"=>$uvic,
    "icon"=>$wxallbic,
    "txt"=>$fixedtxt
  );
}

####################################################################################################
# FUNCTIONS

function crop($name) {
if(preg_match('|rr;|Ui',$name)) { 
$clen = strpos($name,";");
$name = substr($name, $clen+1, (strlen($name)-$clen));
}
return $name;
}

# Colorize thunder also in plaintext.txt
function fixthunder($str) { 
switch (TRUE) {
    case (preg_match('!Severe thunderstorms likely, with possible tornados.!',$str)):
    $str = str_replace("Severe thunderstorms likely, with possible tornados.",
    ' <span style="color:red"><b>Severe thunderstorms likely, with possible tornados.</b></span>',$str);
    break;
    case (preg_match('!Thunderstorms very likely, some severe.!',$str)):
    $str = str_replace("Thunderstorms very likely, some severe.",
    ' <span style="color:red"><b>Thunderstorms very likely, some severe.</b></span>',$str);
    break;
    case (preg_match('!Thunderstorms very likely, some possibly severe.!',$str)):
    $str = str_replace("Thunderstorms very likely, some possibly severe.",
    ' <span style="color:red"><b></b></span>',$str);
    break;
    case (preg_match('!Scattered thunderstorms likely, some possibly severe.!',$str)):
    $str = str_replace("Scattered thunderstorms likely, some possibly severe.",
    ' <span style="color:red"><b>Scattered thunderstorms likely, some possibly severe.</b></span>',$str);
    break;
    case (preg_match('!Scattered thunderstorms likely.!',$str)):
    $str = str_replace("Scattered thunderstorms likely.",
    ' <span style="color:#EE7621"><b>Scattered thunderstorms likely.</b></span>',$str);
    break;
    case (preg_match('!Scattered thundershowers possible.!',$str)):
    $str = str_replace("Scattered thundershowers possible.",
    ' <span style="color:#EE7621"><b>Scattered thundershowers possible.</b></span>',$str);
    break;
}
return $str;
}

################################################################################
# ICONPARSER plaintext.txt 
# Convert NOAA-iconnames to description used in 3in1 using also prec-amount & temperature
# "Detecing" tscd-number based on the text because its not available in plaintext.txt.
function plaintexticon($raw,$btot,$temp,$pop,$txt,$unit) {
$pltscd = 0;
# thundercheck
# Determine "virtual" tscd-number based on the text in plaintext.txt
switch (TRUE) {
case (preg_match("|Severe thunderstorms likely, with possible tornados|",$txt)):$pltscd=506;break;
case (preg_match("|Thunderstorms very likely, some severe|",$txt)):$pltscd=405;break;
case (preg_match("|Thunderstorms very likely, some possibly severe|",$txt)):$pltscd=403;break;
case (preg_match("|Scattered thunderstorms likely, some possibly severe|",$txt)):$pltscd=303;break;
case (preg_match("|Scattered thunderstorms likely|",$txt)):$pltscd=303;break;
case (preg_match("|Scattered thundershowers possible|",$txt)):$pltscd=303;break;
}

# Clouds
$cover = 0;
switch (TRUE) {
case(preg_match("|ostly cloudy|",$txt)):$cover=80; break;
case(preg_match("|artly cloudy|",$txt)):$cover=40; break;
case(preg_match("|loudy|",$txt)):$cover=100; break;
case(preg_match("|vercast|",$txt)):$cover=100; break;
case(preg_match("|air|",$txt)):$cover=20; break;
case(preg_match("|ostly sunny|",$txt)):$cover=20; break;
}
switch (TRUE) {
case ($cover == 100): $clouds = "ovc"; break;
case ($cover == 80): $clouds = "bkn"; break;
case ($cover == 40): $clouds = "sct"; break;
case ($cover == 20): $clouds = "few"; break;
default: $clouds = "skc"; break;
}

if(preg_match("|fog|",$txt)){$fogcond = 'fog';}else{$fogcond = '';}

$prcond = $clouds.$hard.$cond.$fogcond;

$idata=array(
    "rawcond"=>$prcond ,
    "prec"=>$btot,
    "temp"=>$temp,
    "pop"=>$pop,
    "tsdesc"=>$pltscd,
    "tcdc"=>$cover
  );

return wanewicon($idata,$unit);
} 

function get_lang( $text ) {
  global $LanguageLookup, $doTranslate; 
  if ($doTranslate && isset($LanguageLookup[$text])) {
    $newtext = $LanguageLookup[$text];
  } else {
    $newtext = $text;
  }
  return($newtext);
}