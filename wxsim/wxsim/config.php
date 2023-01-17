<?php
############################################################################
# WXSIM Forecast v. 2017.3 (Feb 2017)
############################################################################
#
# Author:	Henkka <nordicweather@gmail.com.net>
#
# Copyright:	(c) 2008-2016 Copyright nordicweather.net.
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

$wxsimlocation     = "Pertteli, Salo";                 # Your location
$latitude = 60.45;
$longitude = 23.23;
$tzabb        = "Europe/Helsinki";
$datestyle    = "d.m.Y";
$timeFormat = "d.m.Y H:i";          # Timeformat
$updatehrs = array(3,6,9,12,15,18,21);  # Hours when wxsim runs
$updateminute = 20; 	              # minutes past full hour for upload time
$jqueryload   = true;                             # Should we load JQuery? (Set to false if your site loads it by default)
$bootstrapload = true;                             # Should we load Bootstrap? (Set to false if your site loads it by default)
$mainwidth    = "100%";                           // Use 100% for responsivity

$path_to_langfiles = "/home/web3/euweather/lang/";
$path_to_lastret = "/home/web3/public_html/test/wxsim/wxsim/lastret.txt";
$path_to_dataphp = "wxsim";
$path_to_js = "js/";
$path_to_css = "css/";

$wxsimversion    = 2017.03;   # internal version

$adblock=''; # Box for showing ads on forecast front-tab.

# IMPORTANT! Units in use, temperature, precip, wind, pressure, snowdepth, visibility
$uoms = array('C','mm','kmh','hPa','cm','km');  
#$uoms = array('C','mm','km/h','hPa','cm','km');
#$uoms = array('F','in','mph','inHg','in','mi');

# Experimental POP-multiplier (POP in lastret * this value = POP).
# Seems POP in lastret have low values between 0 and 10. For "better" value do we multiple it with this value.
# Change if needed.
$popmulti = 10;

############################################################################

$query=$_SERVER["QUERY_STRING"];
$q=explode("|",$query);
if(preg_match("|\||",$query)){
  $lang=$q[0];
}
if($_GET[lang]&&!isset($lang)){$lang=$_GET[lang];}
if($lang == "se"){$lang="sv";$oldlang = "se";}
if($lang == "dk"){$lang="da";$oldlang = "dk";}
if (!isset($lang)) { $lang = "en";}
//include_once($path_to_langfiles.'/ewn.lang.'.$lang.'.php');

##################################################################################
# Translations, add own if needed

if($lang=="fi"){
  define('OVERVIEW','Lyhyesti');
  define('DESCRIPTION','Selitys');
  define('WSXFRC','WXSIM ennuste');
  define('UPDATED','Päivitetty');
  define('NXTUPDATE','Seuraava päivitys');
  define('FULLGRAPH','Näytä koko ennustejakso');
  define('SELECTWUNIT','Yksiköt');
  define('TABLE','Taulukko');
  define('FRCGRAPH','Ennustekäyrä');
  define('GRAPH','Käyrä');
  define('TODAY','Tänään');
  define('TOMORROW','Huomenna');
  define('MIDNIGHTSUN','Yötön yö');
  define('POLARNIGHT','Kaamos');
  define('POP','Saderiski');
  define('HUMIDITY','Ilmankosteus');
  define('SNOW','Lumisade');
  define('TSPROB','Ukkosriski');
  define('FEELS','Tuntuu kuin');
  define('GUST','Puuska');
  define('DEWP', 'Kastepiste');
  define('BARO', 'Ilmanpaine');
  define('TEMP', 'Lämpötila');
  define('WIND', 'Tuuli');
  define('PRECIP', 'Sade');
  $days = array('Sunnnuntai','Maanantai','Tiistai','Keskiviikko','Torstai','Perjantai','Lauantai');
  $months = array('Tam','Hel','Maa','Huh','Tou','Kes','Hei','Elo','Syy','Lok','Mar','Jou');
}
if($lang=="sv"||$lang=="se"){
  define('OVERVIEW','Översikt');
  define('DESCRIPTION','Förklaring');
  define('WSXFRC','WXSIM prognos');
  define('UPDATED','Uppdaterad');
  define('NXTUPDATE','Nästa uppdatering');
  define('FULLGRAPH','Visa hela prognosperioden');
  define('TABLE','Tabell');
  define('SELECTWUNIT','Enheter');
  define('FRCGRAPH','Meteogram');
  define('GRAPH','Meteogram');
  define('TODAY','I dag');
  define('TOMORROW','I morgon');
  define('MIDNIGHTSUN','Midnattssol');
  define('POLARNIGHT','Polarnatt');
  define('HUMIDITY','Luftfuktighet');
  define('SNOW','Snöfall');
  define('POP','Regnrisk');
  define('TSPROB','Åskrisk');
  define('FEELS','Känns som');
  define('GUST','Vindby');
  define('DEWP', 'Daggpunkt');
  define('BARO', 'Lufttryck');
  define('TEMP', 'Temperatur');
  define('WIND', 'Vind');
  define('PRECIP', 'Nederbörd');
  $days = array('Söndag','Måndag','Tisdag','Onsdag','Torsdag','Fredag','Lördag');
  $months = array('Jan','Feb','Mar','Apr','Maj','Jun','Jul','Aug','Sep','Okt','Nov','Dec');
}
if($lang=="da"||$lang=="dk"){
  define('OVERVIEW','Overview');
  define('DESCRIPTION','Description');
  define('WSXFRC','WXSIM vejrudsigt');
  define('UPDATED','Opdateret');
  define('NXTUPDATE','Næste opdatering');
  define('TABLE','Tabel');
  define('FULLGRAPH','Vise hele prognoseperioden');
  define('FRCGRAPH','Vejrudsigtsgraf');
  define('GRAPH','Vejrudsigtsgraf');
  define('SELECTWUNIT','Enhed');
  define('TODAY','I dag');
  define('TOMORROW','I morgen');
  define('MIDNIGHTSUN','Midnatssol');
  define('POLARNIGHT','Polarnat');
  define('POP','PoP');
  define('HUMIDITY','Fugtighed');
  define('SNOW','Sne');
  define('TSPROB','Storm sandsynlighed');
  define('FEELS','Føles som');
  define('GUST','Vindstød');
  define('TEMP','Temperatur');
  define('DEWP','Dugpunkt');
  define('WIND','Vind');
  define('PRECIP','Nedbør');
  define('BARO','Barometer');
  $days = array('Søndag','Mandag','Tirsdag','Onsdag','Torsdag','Fredag','Lørdag');
  $months = array('Jan','Feb','Mar','Apr','Maj','Jun','Jul','Aug','Sep','Okt','Nov','Dec');
}
if($lang=="de"){
  define('OVERVIEW','Overview');
  define('DESCRIPTION','Description');
  define('WSXFRC','WXSIM Wettervorhersage');
  define('UPDATED','Aktualisiert');
  define('NXTUPDATE','Nächste Aktualisierung');
  define('SELECTWUNIT','Einheit');
  define('FULLGRAPH','Gesamte Prognose');
  define('GRAPH','Graphen');
  define('TABLE','Tabelle');
  define('FRCGRAPH','Vorhersagegraphen');
  define('TOMORROW','Morgen');
  define('TODAY', 'Heute');
  define('TONIGHT','Abend');
  define('MIDNIGHTSUN','Mitternachts Sonne');
  define('POLARNIGHT','Polar Nacht');
  define('POP','PoP');
  define('HUMIDITY','Feuchtigkeit');
  define('SNOW','Sneefall');
  define('TSPROB','Risiko für Gewitter');
  define('FEELS','Gefühlt');
  define('GUST','Böe');
  define('TEMP','Temperatur');
  define('DEWP','Taupunkt');
  define('WIND','Wind');
  define('PRECIP','Niederschlag');
  define('BARO','Luftdruck');
  $days = array('Sonntag','Montag','Dienstag','Mittwoch','Donnerstag','Freitag','Samstag');
  $months = array('Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez');
}
if($lang=="nl"){
  define('OVERVIEW','Overview');
  define('DESCRIPTION','Description');
  define('WSXFRC','WXSIM Weervoorspelling');
  define('UPDATED','Bijgewerkt');
  define('NXTUPDATE','Volgende update');
  define('SELECTWUNIT','Eenheid');
  define('FULLGRAPH','Meerdaagse');
  define('TABLE','Tabel');
  define('FRCGRAPH','Verwachtings grafiek');
  define('GRAPH','Grafieken');
  define('TODAY','Vannacht');
  define('TOMORROW','Morgen');
  define('MIDNIGHTSUN','Midzomernacht');
  define('POLARNIGHT','Poolnacht');
  define('POP','Neerslag verwachting');
  define('HUMIDITY','Vochtigheid');
  define('SNOW','Sneeuwval');
  define('TSPROB','Storm prob.');
  define('FEELS','Voelt als');
  define('GUST','Windvlaag');
  define('TEMP','Temperatuur');
  define('DEWP','Dauwpunt');
  define('WIND','Wind');
  define('PRECIP','Neerslag');
  define('BARO','Luchtdruk');
  $days = array('Zondag','Maandag','Dinsdag','Woensdag','Donderdag','Vrijdag','Zaterdag');
  $months = array('Jan','Feb','Maa','Apr','Mei','Jun','Jul','Aug','Sep','Okt','Nov','Dec');
}
if($lang=="it"){
  define('OVERVIEW','Panoramica');
  define('DESCRIPTION','Descrizione');
  define('WSXFRC','Previsioni WXSIM per');
  define('UPDATED','Aggiornato');
  define('NXTUPDATE','Prossimo aggiornamento');
  define('FULLGRAPH','Mostra intero periodo previsionale');
  define('SELECTWUNIT','Unit&agrave;');
  define('GRAPH','Grafici');
  define('TABLE','Table');
  define('FRCGRAPH','Forecastgraph');
  define('TODAY', 'Oggi');
  define('TOMORROW','Domani');
  define('TONIGHT', 'Stasera/Notte');
  define('HUMIDITY','Umidit&agrave;');
  define('SNOW','Nevicata');
  define('TSPROB','TS-prob.');
  define('MIDNIGHTSUN','Midnight Sun');
  define('POLARNIGHT','Polar Night');
  define('POP','PoP');
  define('FEELS','Percepita');
  define('GUST','Raffica');
  define('DEWP', 'Punto di Rugiada');
  define('BARO', 'Pressione');
  define('TEMP', 'Temperatura');
  define('WIND', 'Vento');
  define('PRECIP', 'Precipitazioni');
  $days = array('Domenica','Lunedì','Martedì','Mercoledì','Giovedì','Venerdì','Sabato');
  $months = array('Gen','Feb','Mar','Apr','Mag','Giu','Lug','Ago','Set','Ott','Nov','Dic');
}
if($lang=="en"){
  define('OVERVIEW','Overview');
  define('DESCRIPTION','Description');
  define('WSXFRC','WXSIM forecast');
  define('UPDATED','Updated');
  define('NXTUPDATE','Next update');
  define('FULLGRAPH','Show whole forecastperiod');
  define('SELECTWUNIT','Units');
  define('GRAPH','Graphs');
  define('TABLE','Table');
  define('FRCGRAPH','Forecastgraph');
  define('TOMORROW','Tomorrow');
  define('TODAY', 'Today');
  define('HUMIDITY','Humidity');
  define('SNOW','Snowfall');
  define('TSPROB','TS-prob.');
  define('MIDNIGHTSUN','Midnight Sun');
  define('POLARNIGHT','Polar Night');
  define('POP','PoP');
  define('FEELS','Feels like');
  define('GUST','Gust');
  define('DEWP', 'Dewpoint');
  define('BARO', 'Pressure');
  define('TEMP', 'Temperature');
  define('WIND', 'Wind');
  define('PRECIP', 'Precipitation');
  $days = array('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday');
  $months = array('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec');
}
if($lang=="yy"){
  define('WSXFRC','WXSIM Forecast');
  define('UPDATED','Updated');
  define('NXTUPDATE','Next update');
}

###################################################################################
date_default_timezone_set($tzabb);
$wunit="ms";
if($_COOKIE[ewnwunit]){
  $wunit=$_COOKIE[ewnwunit];
}

if($wxsimtype=="forecast"){
  include __DIR__.'/frc.php';
}

?>