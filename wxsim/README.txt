WXSIM Forecast EWN-style - v.2017.2
By Henkka @ nordicweather.net 
Script for showing the forecast.

The script uses lastret.txt. 
Be sure WXSIM generates this and that you upload it to your server.
See wret.jpg for what variables are required and set them up in WRET, you can add more if you want.

NOTES! 
- For thunderstorms are variable TSCD needed in lastret.txt
- The hourly PoP (precip chance) are experimental, for now POP in lastret.txt * 10.

Set the settings in wxsim/config.php + translate the few words there if needed (add your own language if needed).

#####################
# FILES

forecast.php - demo of the the forecast. Copy the PHP-parts of the code to your own page
short.php - demo of the short forecast
graph.php - stand-alone graph

wxsim/data.php - dataparser