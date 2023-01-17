var labelStyle = {color: "#fff", fontWeight:300,fontFamily: 'ubuntu'};
var isTouch = 'ontouchstart' in document.documentElement;
if(!isTouch) {$('html').removeClass('touch').addClass('no-touch');}
var haveGPS = false, wiset="ms",wunit,utcdiff,favotimeout,strData,choosedDay=0,twidth,maxGraph,minGraph,compGraph,fullGraph;
var tempdata=[],precdata=[],barodata=[],dewdata=[],feeldata=[],tsdata=[],svgdata=[],windtip=[];
var accloaded=false,lastWX=0,lastWind=0;

var is_phone;
var screenheight = $(window).height();
var screenwidth = $(window).width();

var now = Date.now();

(function(){

  if($.jStorage.get("ewnwunit")){
    wiset=$.jStorage.get("ewnwunit");
    $.cookie("ewnwunit", wiset, { expires : 365 });
  }
  wunit=getWunit(wiset);
  getData();
   
})(jQuery)

/*##############################################################################################
  # FORECAST 
*/

function getData(){
  var dpath = ewnpath+"/data.php?wunit="+wiset+"&lang="+lang;
  wget([dpath], function(points) {
    strData=JSON.parse(points);
    getGraph(0);
  });
}

function getGraph(a){
  tempdata=[],precdata=[],barodata=[],dewdata=[],feeldata=[],tsdata=[],svgdata=[],windtip=[];
  compfmi=[],compyr=[],compsmhi=[],comparome=[],compmf=[],compknmi=[],compdwd=[],compgfs=[],compcmc=[],compwxsim=[];
  day1Min = strData.data[0].timestamp;
  day1Max = day1Min+(gdays*86400);
  $.each(strData.data, function(i, item) {
    if(item.timestamp>=day1Min&&item.timestamp<=day1Max){
      tstamp=item.timestamp*1000;
      tempdata.push([tstamp, parseFloat(item.temp)]);
      feeldata.push([tstamp, parseFloat(item.feels)]);
      dewdata.push([tstamp, parseFloat(item.dewp)]);
      precdata.push([tstamp, parseFloat(item.prec)]);
      tsdata.push([tstamp, parseFloat(item.tsrisk)]);
      barodata.push([tstamp, parseFloat(item.prmsl)]);
      windtip.push([tstamp, parseFloat(fixWspd(item.wspd))]);
      svgdata.push({"time":tstamp, "dir":item.wdir, "bft": item.bft, "cond": item.icon});
    }
  });
  getHC();
  chart = new Highcharts.Chart(tempoptions);
  drawgraphiconswx(svgdata, "hourgraph", 20, 0);
  drawgraphiconswind(svgdata,357);
}

function fixWspd(val){
  if(wiset=="kmh"){return (val*3.6).toFixed(1);}
  else if(wiset=="kts"){return (val*1.94384449).toFixed(1);}
  else if(wiset=="mph"){return (val*2.23693629).toFixed(1);}
  else return (val*1).toFixed(1);
}

function getWunit(wiset){
  if(wiset=="ms"){return "m/s";}
  if(wiset=="kmh"){return "km/h";}
  return wiset;
}

function fixPop(val){
  if(val>0&&val<8){return "<10";}
  if(val>=5){return Math.round(val / 10) * 10;}
  return "0";
}

function fixTs(val){
  if(val>2&&val<8){return "<10";}
  if(val>=5&&val<90){return Math.round(val / 10) * 10;}
  if(val>=90){return 90;}
  return "0";
}

function fixSnowfall(val,valb){
  if(valb>0.1&&valb<1.8){
    if(val>0&&val<1.5){return "<1";}
    if(val>1.5&&val<2.6){return "1-2";}
    if(val>2.6&&val<4){return "2-3";}
    return Math.round(val*0.75);
  }else{
    if(val>0&&val<1){return "<1";}
    if(val>1&&val<2){return "1-2";}
    if(val>2&&val<3){return "2-3";}
    return Math.round(val);
  }
}

function getHC(){
  Highcharts.setOptions({
    colors: ["#DDDF0D", "#55BF3B", "#DF5353", "#7798BF", "#aaeeee", "#ff0066", "#eeaaee", "#ff9900", "#1F5EA8", "#B32E37"],
    lang: {weekdays: days,shortMonths: months,thousandsSep: ""},
    global : { timezoneOffset: utcdiff * 60},               
    chart: {
      defaultSeriesType: "spline",
      backgroundColor: "#2b3d4b",
      plotBorderColor: "#2b3d4b",
      marginRight: 40,
      marginLeft: 40,
      marginTop: 30,
      plotBorderWidth: 0,
      //zoomType: 'x',
      style: labelStyle,
      events: {
        redraw: function(event) {
          if (chart.xAxis) {
            lastWX=0,lastWind=0;
            drawgraphiconswx(svgdata, "hourgraph", 20, 0);
            drawgraphiconswind(svgdata,357);
          }
        }
      }
    },
    title: {text: ""},
    credits: {enabled: false},
    plotOptions: {
      spline: {lineWidth: 1.8, shadow: false, marker: {enabled: false,radius:3,states: {hover: {enabled: true}}}},
      column: {lineWidth:0,pointWidth:null,pointPlacement:-0.5,groupPadding: 0,pointPadding: 0.1,borderWidth: 0,shadow: false},
      areaspline: {lineWidth: 1.5, shadow: false,marker: {enabled: false,radius:3,states: {hover: {enabled: true}}}}
    },
    tooltip: {
      shared: true,
      useHTML: true,
      crosshairs: { width: 0.5,color: "#666"},
      backgroundColor:"#3E576B",borderColor:"#162b3d",style: { "color": "#fff"},
      formatter: function () { 
        var index = this.points[0].point.index;
        var ret = '<b>' + Highcharts.dateFormat("%A %H:%M", this.x) +'</b>';
        ret += "<table>";
        Highcharts.each(this.points, function (point) {
          var series = point.series;
          ret += '<tr><td><span style="color:' + series.color + '">\u25CF</span> ' + series.name +
            ':&nbsp;&nbsp;</td><td style="white-space:nowrap">' + Highcharts.pick(point.point.value, point.y).toFixed(1) +
            series.options.tooltip.valueSuffix + '</td></tr>';
        });
        if(!compGraph){
          ret += '<tr><td style="vertical-align: top">\u25CF '+windtxt+':&nbsp;&nbsp;</td><td style="white-space:nowrap">' + 
            windtip[index][1].toFixed(1)+' '+wunit+'</td></tr>';
        }
        ret += "</table>";
        return ret;
      }
    },
    legend: {enabled: true, y:20,itemStyle: labelStyle,itemHiddenStyle: {color: '#555'},itemHoverStyle: {color: '#555'}},
    exporting: {enabled:false},
    scrollbar: {enabled:false}
  });
  
  xAxis1 = [{ // Bottom X axis
    type: "datetime",
    tickInterval: 3 * 36e5, // two hours
    tickLength: 0,
    lineColor: "#577a96",
    offset: 35,
    showLastLabel: true,
    labels: {format: "{value:%H}",y:16,style: labelStyle}
  },{ // Top X axis
    linkedTo: 0,
    type: 'datetime',
    tickInterval: 24 * 3600 * 1000,
    labels: {
      format: '{value:<span style="font-size:14px;">%A</span>}',
      align: 'left',
      x: 3,
      y: -5,
      style: labelStyle
    },
    opposite: true,
    gridLineWidth: 1.0,
    gridLineColor: "#577a96",
    lineColor: "#577a96",
    tickLength: 20,
    tickColor: "#577a96",
    tickWidth: 1.0,
  }];
  
  tempYAxis = [
    { // Temperature
      title: {text: null},labels: {format: "{value}°",style: labelStyle, x:-4, y:3},
      gridLineWidth: 1,gridLineColor: "#577a96",
      plotLines: [{ value: 0,color: "#577a96",width: 3,zIndex: 2}],maxPadding: 0.05,tickInterval: 1   
    },{ // precipitation axis
      title: {text: null},labels: {enabled: false},gridLineWidth: 0,min:0,minRange:5,tickLength: 0
    },{ // Air pressure 
      title: { text: null},labels:{ x:4, y:3, style:{color: "#fff", fontWeight:300,fontFamily: 'ubuntu'}},maxPadding: 0.05,
      allowDecimals: false,gridLineWidth: 0,opposite: true
    },{ // ts
      title: {text: null},labels: {enabled: false},gridLineWidth: 0,min:0,max:100,tickLength: 0
    }];
    
  if(twidth>650){ptip=true;}else{ptip=false;}
  tempoptions = {
    chart: {marginBottom: 90,renderTo: "hourgraph"},
    xAxis: xAxis1,
    yAxis: tempYAxis,
    series: [{
      name: temptxt,data: smoothline(tempdata),tooltip: {valueSuffix: "°"},color: "#FF3333",negativeColor: "#48AFE8",lineWidth:2,zIndex:3
    },{
      name: dewtxt,data: smoothline(dewdata),tooltip: {valueSuffix: "°"},color: "#698B22",visible: false,zIndex:3
    },{
      name: feeltxt,data: smoothline(feeldata),tooltip: {valueSuffix: "°"},color: "#4F94CD",dashStyle: "shortdot",visible: false,zIndex:3
    },{
      name: barotxt,data: smoothline(barodata),tooltip: {valueSuffix: " hPa"},color: "#9ACD32",dashStyle: "shortdot",yAxis: 2,zIndex:3
    },{
      name: prectxt,data: precdata,tooltip: {valueSuffix: " mm"},color:"#4572A7",type: "column",yAxis: 1,zIndex:2,
      dataLabels: {enabled: ptip,formatter: function () {if (this.y > 0) {return this.y;}},
      style: {fontWeight:300,fontSize: "10px",color:"#fff",textShadow:"0px"}}
    },{
      name: tstxt,data:tsdata,tooltip: {valueSuffix: " %"},color:"#EE7621",type:"areaspline",yAxis: 3,zIndex:1
    }]
  };
  
}

function getGraphVis(arr){
  if(arr.length>0){return true;}else{return false;}
}
  
function smoothline(data) {
  var i = data.length,sum,value;
  while (i--) {
    data[i].value = value = data[i].y; // preserve value for tooltip
    sum = (data[i - 1] || data[i]).y + value + (data[i + 1] || data[i]).y;
    data[i].y = Math.max(value - 0.5, Math.min(sum / 3, value + 0.5));
  }
  return data;
}
  
function drawgraphiconswx(svgdata, mainrec, plotleft, gs){
  var mainrect = $("#"+mainrec+" .highcharts-series-group");
  $(".gr-ic").remove();
  extremes = chart.xAxis[0].getExtremes();
  $.each(svgdata, function(index2,value2){
    $.each(chart.series[gs].points, function(index,value){
      if(value.category == value2.time && value2.time >= extremes.min && value2.time <= extremes.max) {
        var xx = value.plotX + chart.plotLeft - plotleft;
        var yy = value.plotY + chart.plotTop - 50;
        //var yy = 25;
        if(xx-lastWX>32){
          $(mainrect).append('<svg class="svg-ic gr-ic" height="40" width="40" viewBox="0 0 512 512" x ='+xx+' y="'+yy+'"><g>'+geticon(value2.cond)+'</g></svg>');
          lastWX=xx;
        }
      }
    });
  });
}
  
function drawgraphiconswind(svgdata,wicY){
  extremes = chart.xAxis[0].getExtremes();
  $.each(svgdata, function(index2,value2){
    $.each(chart.series[2].points, function(index,value){
      var arrow, x, y,level,path;
      if(value.category == value2.time && value2.time >= extremes.min && value2.time <= extremes.max) {
        level = value2.bft;
        x = value.clientX + chart.plotLeft - 0;
        y = wicY;
        if(x-lastWind>32){
          path = ['M',0,7,'L',-1.5,7,0,10,1.5,7,0,7,0,-10];
          if (level === 0) {path = [];}
          if (level === 2) {path.push('M', 0, -8, 'L', 4, -8);} 
          else if (level >= 3) {path.push(0, -10, 7, -10);}
          if (level === 4) {path.push('M', 0, -7, 'L', 4, -7);} 
          else if (level >= 5) {path.push('M', 0, -7, 'L', 7, -7);}
          if (level === 5) {path.push('M', 0, -4, 'L', 4, -4);} 
          else if (level >= 6) {path.push('M', 0, -4, 'L', 7, -4);}
          if (level === 7) {path.push('M', 0, -1, 'L', 4, -1);} 
          else if (level >= 8) {path.push('M', 0, -1, 'L', 7, -1);}
          
          if (level === 0) {arrow = chart.renderer.circle(x, y, 10).attr({fill: 'none'});}
          else {
            arrow = chart.renderer.path(path).attr({rotation: parseInt(value2.dir, 10),translateX: x,translateY: y});
          }
          arrow.attr({stroke: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'white','stroke-width': 1.5,zIndex: 5,'class':'gr-ic'})
            .add();
          lastWind=x;
        }
      }
    });
  });
}
  
function drawwindbox() {
  var xAxis = chart.xAxis[0],x,pos,max,isLong,isLast,i;
  for (pos = xAxis.min, max = xAxis.max, i = 0; pos <= max + 36e5; pos += 36e5, i ++) {
    isLast = pos === max + 36e5;
    x = Math.round(xAxis.toPixels(pos)) + (isLast ? 0.5 : -0.5);
    if (this.resolution > 36e5) {
      isLong = pos % this.resolution === 0;
    } else {
      isLong = i % 3 === 0;
    }
    isLong = 0;
    chart.renderer.path(['M', x, chart.plotTop + chart.plotHeight + (isLong ? 0 : 28),
      'L', x, chart.plotTop + chart.plotHeight + 32, 'Z'])
      .attr({'stroke': chart.options.chart.plotBorderColor,'stroke-width': 1})
      .add();
  }
}

/*##############################################################################################
  # MISC
*/

function locateme(){
  if(navigator.geolocation){
    haveGPS = true;
    function positionSuccess(location) {
      geo={lat:location.coords.latitude,lon:location.coords.longitude,time:now};
      $.jStorage.set("frcloc", JSON.stringify(geo));
      $.jStorage.setTTL("frcloc", 3600);
      $.cookie("frcloc", JSON.stringify(geo), { expires : 1 });
      url='https://'+window.location.hostname+window.location.pathname+'?lang='+lang+'&lat='+location.coords.latitude+'&lon='+location.coords.longitude+p;
      window.location.href=url;
    }
    function positionFail(failure) {
      if(failure.message.indexOf("Only secure origins are allowed") == 0) {
        url='https://'+window.location.hostname+window.location.pathname+'?lang='+lang+'&lat='+geoiplat+'&lon='+geoiplon+p;
        window.location.href=url;
      }else{
        alert("The localization failed, try again.");
      }
    }
    var options = { enableHighAccuracy: true,timeout: 10000,maximumAge: 240000};
    navigator.geolocation.getCurrentPosition(positionSuccess, positionFail,options);
  }
}

function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

function wget(urls, fn) {
  var results = [],complete = 0,total = urls.length;
  urls.forEach(function(url, i) {
    var request = new XMLHttpRequest();
    request.open('GET', url, true);
    request.onload = function () {
      if (request.status < 200 && request.status > 400) return;
      results[i] = request.responseText;
      complete++;
      if (complete === total) fn.apply(null, results);
    };
    request.send();
  });
}

function getbrowser(){
    var ua= navigator.userAgent, tem, 
    M= ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];
    if(/trident/i.test(M[1])){
        tem=  /\brv[ :]+(\d+)/g.exec(ua) || [];
        return {name:'IE',version:(tem[1] || '')};
    }
    if(M[1]=== 'Chrome'){
        tem= ua.match(/\b(OPR|Edge)\/(\d+)/);
        if(tem!= null) return {name:tem[1].replace('OPR', 'Opera'),version:tem[2]};
    }
    M= M[2]? [M[1], M[2]]: [navigator.appName, navigator.appVersion, '-?'];
    if((tem= ua.match(/version\/(\d+)/i))!= null) M.splice(1, 1, tem[1]);
    return {name:M[0],version:M[1]};
};

/*##############################################################################################
  # SVG-ICONS
*/

function getwindicon_svg(val,dir,gst,bft,wunit){
  wlimita=14;
  wlimitb=21;
  if(wunit == "km/h"){wlimita=50;wlimitb=76;}
  if(wunit == "mph"){wlimita=31;wlimitb=47;}
  if(wunit == "kts"){wlimita=27;wlimitb=41;}
  wi = Math.round(fixWspd(val));
  wcolor=wiconcolor(wi,wlimita,wlimitb);
  if (typeof gst !== 'undefined') {
    gsttip=' data-toggle="tooltip" data-placement="top" title="'+bft+' bft, '+txtgust+' '+Math.round(fixWspd(gst))+' '+wunit+'"';
  }else{
    gsttip=' data-toggle="tooltip" data-placement="top" title="'+bft+' bft"';
  }
  wline='<div style="width:50px;margin:0 auto;"'+gsttip+'><svg class="svg" viewBox="0 0 104 104" height="48" width="48"><g class="wind"><path d="M76.002,51.998c0,13.26-10.746,24.004-24.002,24.004 c-13.254,0-24.002-10.744-24.002-24.004c0-13.254,10.748-24,24.002-24C65.256,27.998,76.002,38.744,76.002,51.998z" stroke-width="6.0721" stroke="'+wcolor+'" fill="#3E576B"></path><polygon points="65.966,81.677 62.416,85.361 58.875,89.044 55.332,92.72 51.794,96.4 48.345,92.626 44.91,88.851 41.468,85.08 38.031,81.31 45.105,82.21 51.992,83.193 59.154,82.404" stroke-width="4.0721" stroke="'+wcolor+'" fill="#3E576B" transform="rotate('+dir+',52,52)"></polygon><text dy="7pt" y="49%" x="50%" style="font-family:ubuntu;font-size:20pt;" fill="#fff">'+wi+'</text></g></svg></div>';
  return wline;
}

function wiconcolor(i,wlimita,wlimitb){
  if(i<wlimita){return "#88a4ba";}
  else if (i<wlimitb){return "#F89C26";}
  else {return "#FF4040";}
}

var shapes = new Array();
shapes["cloud"]="d=\"M441.953,142.352c-4.447-68.872-61.709-123.36-131.705-123.36c-59.481,0-109.766,39.346-126.264,93.429c-9.244-3.5-19.259-5.431-29.729-5.431c-42.84,0-78.164,32.08-83.322,73.523c-0.309-0.004-0.614-0.023-0.924-0.023c-36.863,0-66.747,29.883-66.747,66.747s29.883,66.746,66.747,66.746c4.386,0,8.669-0.436,12.819-1.243c20.151,27.069,52.394,44.604,88.734,44.604c31.229,0,59.429-12.952,79.533-33.772c15.071,15.091,35.901,24.428,58.913,24.428c31.43,0,58.783-17.42,72.955-43.127c11.676,5.824,24.844,9.106,38.777,9.106c48.047,0,86.998-38.949,86.998-86.996C508.738,185.895,480.252,151.465,441.953,142.352z\"/>";
shapes["lightning"]="class=\"lightning\" fill-rule=\"evenodd\" clip-rule=\"evenodd\" d=\"m 3.4723994,8.5185577 3.0304576,-7.0710678 6.944799,0 -5.0191957,5.08233 4.1353117,0 -8.1127873,9.0913731 2.0834396,-7.1342026 z\"/>";
shapes["tornado"]="class=\"tornado\" fill-rule=\"evenodd\" d=\"M3.51795549,3.09677419 C4.55956613,1.38647295 9.11409512,0 16.017284,0 C22.9204728,0 27.3855446,1.64705965 28.5166124,3.09677419 C30.0790285,5.09935736 27.6364411,9.83203892 20.1837273,14.4516129 C13.8294775,18.3903027 9.14478347,22.2210455 12.8924519,23.7419355 C21.8177932,27.3640441 17.0588943,32 17.0588943,32 C17.0588943,32 17.0588947,28.9032253 13.934062,27.8709677 C8.65191269,26.1260613 6.64278758,24.7741935 4.55956617,22.7096774 C2.98366184,21.147923 1.2876824,16.2185972 6.64278762,11.3548387 C9.30758236,8.93454683 1.51950057,6.37819267 3.51795549,3.09677419 Z M27,4.03225806 C27,2.37540373 22.0751325,1.03225806 16,1.03225806 C9.92486745,1.03225806 5,2.37540373 5,4.03225806 C5,5.6891124 9.92486745,7.03225806 16,7.03225806 C22.0751325,7.03225806 27,5.6891124 27,4.03225806 Z M27,4.03225806\"/>";
shapes["hurricane"]="class=\"hurricane\" d=\"M 21.05263,282.71812 C 21.05263,263.14772 5.13832,247.26423 -14.46943,247.26423 C -20.99403,247.26423 -27.10709,249.01667 -32.36199,252.08515 C -25.97086,231.2175 -15.39876,214.28402 -1.84069,207.37258 C -28.92355,216.4934 -47.76995,248.20401 -50,282.68374 C -50,302.25413 -34.07718,318.17761 -14.46943,318.1776 C -8.02952,318.1776 -1.98598,316.46325 3.22446,313.46822 C -3.19061,334.0152 -13.85506,350.53308 -27.272,357.37258 C -0.62131,348.3973 18.34408,316.45182 21.05263,282.71812 z\"/>";
shapes["waterdrop"]="class=\"waterdrop\" fill-rule=\"evenodd\" clip-rule=\"evenodd\" d=\"M150.2 464.6h-.1c-15.5 0-28.1-12.7-28.1-28.2v-4c0-.3 0-.5.1-.8v-.3c1.4-11.6 9.6-22.2 16.9-31.7 5.9-7.6 10.9-14.1 10.9-19.5 0-.1.1-.1.2-.1h.1c.1 0 .1 0 .1.1 0 5.4 5.1 12 10.9 19.5 8 10.3 17 22 17 35v1.8c0 15.5-12.5 28.2-28 28.2zm25-42.9c0 .1 0 .1.1.2-.1-.1-.1-.2-.1-.2zm.4 1l.1.3-.1-.3zm.4 1l.1.4c0-.1-.1-.2-.1-.4zm.3 1.1l.2.5c-.1-.2-.1-.4-.2-.5zm.4 1l.3 1.1c-.1-.3-.2-.7-.3-1.1zm.4 1.6c.1.2.1.4.1.6l-.1-.6zm.2 1.1l.1.6c0-.2 0-.4-.1-.6zm.3 1.1l.1.6c-.1-.2-.1-.4-.1-.6zm.1 1.1c0 .2 0 .4.1.5 0-.1 0-.3-.1-.5zm.2 1.2v.5-.5zm.1 1.2v.4-.4z\"/>";
shapes["ice"]="class=\"ice\" points=\"153.317,416 173.313,457.373 194,416 \"/>";
shapes["snowflake"]="class=\"snowflake\" points=\"266.125,427.569 246.082,427.598 244.383,427.773 245.355,426.434 255.378,409.032 240.345,400.389 230.34,417.775 229.65,419.32 228.951,417.768 218.906,400.423 203.895,409.101 213.865,426.307 214.939,427.812 213.062,427.642 193.209,427.667 193.232,445.077 213.062,445.05 214.963,444.874 213.821,446.511 203.969,463.614 219.002,472.26 228.933,455.003 229.695,453.328 230.408,454.903 240.441,472.227 255.452,463.548 245.362,446.141 244.406,444.835 245.928,445.008 266.147,444.981 \"/>";
shapes["hail"]="class=\"hail\" cx=\"277.678\" cy=\"436.324\" r=\"26.895\"/>";
shapes["sun_1"]="class=\"sun_center\" d=\"M255.725,324.881c-37.958,0-68.84-30.882-68.84-68.84s30.881-68.839,68.84-68.839c37.958,0,68.839,30.881,68.839,68.839S293.683,324.881,255.725,324.881z\"/>";
shapes["sun_2"]="class=\"sun\" d=\"M128.363,195.126l11.058-19.152l34.855,20.125c-4.398,5.948-8.128,12.354-11.126,19.111L128.363,195.126z M267,115h-22v40.574c3-0.383,7.158-0.577,10.739-0.577c3.759,0,8.261,0.212,11.261,0.633V115z M196.093,174.419c5.982-4.368,12.412-8.059,19.18-11.011l-20.202-34.99l-19.152,11.058L196.093,174.419z M383.61,195.126l-11.058-19.152L337.33,196.31c4.384,5.96,8.097,12.377,11.076,19.142L383.61,195.126z M155.064,267c-0.387-4-0.583-7.198-0.583-10.8c0-3.736,0.21-7.2,0.626-11.2H115v22H155.064z M336.055,139.475l-19.153-11.058l-20.307,35.176c6.763,2.987,13.176,6.705,19.13,11.092L336.055,139.475z M316.9,383.665l19.153-11.059l-20.169-34.932c-5.949,4.399-12.354,8.132-19.109,11.131L316.9,383.665z M139.421,336.108l34.649-20.005c-4.38-5.965-8.087-12.385-11.062-19.148l-34.646,20.001L139.421,336.108z M397,267v-22h-40.659c0.415,4,0.626,7.464,0.626,11.2c0,3.602-0.196,6.8-0.583,10.8H397zM372.552,336.108l11.058-19.152l-35.062-20.243c-2.955,6.768-6.646,13.196-11.016,19.177L372.552,336.108z M195.072,383.665l20.019-34.674c-6.766-2.968-13.188-6.671-19.159-11.046l-20.012,34.661L195.072,383.665z M267,397v-40.149c-3,0.42-7.504,0.632-11.261,0.632c-3.581,0-7.739-0.193-10.739-0.577V397H267z M335.66,256.041c0-44.077-35.859-79.936-79.936-79.936c-44.077,0-79.937,35.859-79.937,79.936c0,44.077,35.859,79.937,79.937,79.937C299.801,335.978,335.66,300.118,335.66,256.041z M312.563,256.041c0,31.342-25.498,56.84-56.839,56.84c-31.342,0-56.84-25.498-56.84-56.84c0-31.341,25.498-56.839,56.84-56.839C287.065,199.202,312.563,224.7,312.563,256.041z\"/>";
shapes["moon"]="class=\"moon\" d=\"M248.082,263.932c-31.52-31.542-39.979-77.104-26.02-116.542c-15.25,5.395-29.668,13.833-41.854,26.02  c-43.751,43.75-43.751,114.667,0,158.395c43.729,43.73,114.625,43.752,158.374,0c12.229-12.186,20.646-26.604,26.021-41.854  C325.188,303.91,279.604,295.451,248.082,263.932z\"/>";
shapes["fog"]="class=\"fog\" d=\"M392,432H120v23h272V432z\"/>";
shapes["nan"]="class=\"nan\" d=\"M 273.79665,278.39483 L 176.01526,278.41797 C 176.01516,262.63035 180.66722,249.81298 184.24805,239.96582 C 187.82867,230.11898 193.15907,221.12648 200.23926,212.98828 C 207.31921,204.85046 223.22902,190.52755 247.96875,170.01953 C 261.15216,159.27758 267.74395,149.43059 267.74414,140.47852 C 267.74395,131.52696 265.0991,124.56896 259.80957,119.60449 C 254.51968,114.64058 246.50374,112.15849 235.76172,112.1582 C 224.20558,112.15849 214.64342,115.98336 207.0752,123.63281 C 199.50672,131.28282 194.6646,144.62916 192.54883,163.67188 L 97.822266,151.95313 C 101.07745,117.12268 113.73206,89.087225 135.78613,67.84668 C 157.84009,46.606799 191.65353,35.986692 237.22656,35.986328 C 272.70814,35.986692 301.35395,43.392284 323.16406,58.203125 C 352.78619,78.222978 367.59737,104.91566 367.59766,138.28125 C 367.59737,152.11613 363.7725,165.46247 356.12305,178.32031 C 348.47304,191.17859 332.84805,206.88496 309.24805,225.43945 C 291.37819,235.59876 274.96586,253.5497 274.54302,262.53489 L 273.79665,278.39483 z M 175.70313,312.35352 L 275.06836,312.35352 L 275.06836,400 L 175.70313,400 L 175.70313,312.35352 z\"/>";

function geticon(ic){
  var svg;
  switch (ic) {
    case "hurricane":
      svg='<path transform="scale(2) translate(140,-155)" '+shapes["hurricane"];
      break;
    case "tornado":
      svg='<path transform="scale(8) translate(16,18)" '+shapes["tornado"];
      break;
    case "tornadothunder":
      svg='<path transform="scale(5) translate(25,55)" '+shapes["tornado"]+'<path transform="scale(0.60) translate(170,170)" class="thundercloud" '+shapes["cloud"]+'<path transform="scale(12) translate(18,21)" '+shapes["lightning"];
      break;
    case "heavy_thunder":
      svg='<path transform="scale(0.60) translate(170,170)" class="thundercloud" '+shapes["cloud"]+'<path transform="scale(12) translate(8,21)" '+shapes["lightning"]+'<path transform="scale(12) translate(18,21)" '+shapes["lightning"];
      break;
    case "rainthunder":
      svg='<path transform="scale(0.60) translate(170,170)" class="thundercloud" '+shapes["cloud"]+'<path transform="scale(12) translate(8,21)" '+shapes["lightning"]+'<path transform="translate(120,-50)" '+shapes["waterdrop"]+'<path transform="translate(190,-50)" '+shapes["waterdrop"];
      break;
    case "hailthunder":
      svg='<path transform="scale(0.60) translate(170,170)" class="thundercloud" '+shapes["cloud"]+'<path transform="scale(12) translate(8,21)" '+shapes["lightning"]+'<circle  transform="translate(0,-75)" '+shapes["hail"]+'<circle  transform="translate(70,-75)" '+shapes["hail"];
      break;
    case "snowthunder":
      svg='<path transform="scale(0.60) translate(170,170)" class="thundercloud" '+shapes["cloud"]+'<path transform="scale(12) translate(8,21)" '+shapes["lightning"]+'<polygon transform="translate(35,-70)" '+shapes["snowflake"]+'<polygon transform="translate(125,-70)" '+shapes["snowflake"];
      break;
    case "rainthundershower":
      svg='<path transform="scale(0.80) translate(0,-20)" '+shapes["sun_1"]+'<path transform="scale(0.80) translate(0,-20)" '+shapes["sun_2"]+'<path transform="scale(0.60) translate(170,170)" class="thundercloud" '+shapes["cloud"]+'<path transform="scale(12) translate(8,21)" '+shapes["lightning"]+'<path transform="translate(120,-50)" '+shapes["waterdrop"]+'<path transform="translate(190,-50)" '+shapes["waterdrop"];
      break;
    case "hailthundershower":
      svg='<path transform="scale(0.80) translate(0,-20)" '+shapes["sun_1"]+'<path transform="scale(0.80) translate(0,-20)" '+shapes["sun_2"]+'<path transform="scale(0.60) translate(170,170)" class="thundercloud" '+shapes["cloud"]+'<path transform="scale(12) translate(8,21)" '+shapes["lightning"]+'<circle  transform="translate(0,-75)" '+shapes["hail"]+'<circle  transform="translate(70,-75)" '+shapes["hail"];
      break;
    case "snowthundershower":
      svg='<path transform="scale(0.80) translate(0,-20)" '+shapes["sun_1"]+'<path transform="scale(0.80) translate(0,-20)" '+shapes["sun_2"]+'<path transform="scale(0.60) translate(170,170)" class="thundercloud" '+shapes["cloud"]+'<path transform="scale(12) translate(8,21)" '+shapes["lightning"]+'<polygon transform="translate(35,-70)" '+shapes["snowflake"]+'<polygon transform="translate(125,-70)" '+shapes["snowflake"];
      break;
    case "nt_rainthundershower":
      svg='<path transform="scale(0.85) translate(20,-50)" '+shapes["moon"]+'<path transform="scale(0.60) translate(170,170)" class="thundercloud" '+shapes["cloud"]+'<path transform="scale(12) translate(8,21)" '+shapes["lightning"]+'<path transform="translate(120,-50)" '+shapes["waterdrop"]+'<path transform="translate(190,-50)" '+shapes["waterdrop"];
      break;
    case "nt_hailthundershower":
      svg='<path transform="scale(0.85) translate(20,-50)" '+shapes["moon"]+'<path transform="scale(0.60) translate(170,170)" class="thundercloud" '+shapes["cloud"]+'<path transform="scale(12) translate(8,21)" '+shapes["lightning"]+'<circle  transform="translate(0,-75)" '+shapes["hail"]+'<circle  transform="translate(70,-75)" '+shapes["hail"];
      break;
    case "nt_snowthundershower":
      svg='<path transform="scale(0.85) translate(20,-50)" '+shapes["moon"]+'<path transform="scale(0.60) translate(170,170)" class="thundercloud" '+shapes["cloud"]+'<path transform="scale(12) translate(8,21)" '+shapes["lightning"]+'<polygon transform="translate(35,-70)" '+shapes["snowflake"]+'<polygon transform="translate(125,-70)" '+shapes["snowflake"];
      break;
    case "clear":
      svg='<path '+shapes["sun_1"]+'<path '+shapes["sun_2"];
      break;
    case "mostlyclear":
      svg='<path '+shapes["sun_1"]+'<path '+shapes["sun_2"]+'<path transform="scale(0.30) translate(760,760)" class="light_cloud" '+shapes["cloud"];
      break;
    case "partlycloudy":
      svg='<path transform="scale(0.80) translate(40,70)" '+shapes["sun_1"]+'<path transform="scale(0.80) translate(40,70)" '+shapes["sun_2"]+'<path transform="scale(0.42) translate(420,500)" class="middle_cloud" '+shapes["cloud"];
      break;
    case "mostlycloudy":
      svg='<path transform="scale(0.80) translate(20,50)" '+shapes["sun_1"]+'<path transform="scale(0.80) translate(20,50)" '+shapes["sun_2"]+'<path transform="scale(0.50) translate(280,360)" class="dark_cloud" '+shapes["cloud"];
      break;
    case "nt_clear":
      svg='<path '+shapes["moon"];
      break;
    case "nt_mostlyclear":
      svg='<path '+shapes["moon"]+'<path transform="scale(0.30) translate(760,760)" class="light_cloud" '+shapes["cloud"];
      break;
    case "nt_partlycloudy":
      svg='<path transform="scale(0.92) translate(30,10)" '+shapes["moon"]+'<path transform="scale(0.42) translate(420,500)" class="middle_cloud" '+shapes["cloud"];
      break;
    case "nt_mostlycloudy":
      svg='<path transform="scale(0.85) translate(40,40)" '+shapes["moon"]+'<path transform="scale(0.50) translate(260,360)" class="dark_cloud" '+shapes["cloud"];
      break;
    case "cloudy":
      svg='<path transform="scale(0.60) translate(160,260)" class="dark_cloud" '+shapes["cloud"];
      break;
    case "rain4":
      svg='<path transform="scale(0.60) translate(170,170)" class="dark_cloud" '+shapes["cloud"]+'<path transform="translate(5,-50)" '+shapes["waterdrop"]+'<path transform="translate(75,-50)" '+shapes["waterdrop"]+'<path transform="translate(145,-50)" '+shapes["waterdrop"]+'<path transform="translate(215,-50)" '+shapes["waterdrop"];
      break;
    case "rain3":
      svg='<path transform="scale(0.60) translate(170,170)" class="dark_cloud" '+shapes["cloud"]+'<path transform="translate(15,-50)" '+shapes["waterdrop"]+'<path transform="translate(110,-50)" '+shapes["waterdrop"]+'<path transform="translate(205,-50)" '+shapes["waterdrop"];
      break;
    case "rain2":
      svg='<path transform="scale(0.60) translate(170,170)" class="dark_cloud" '+shapes["cloud"]+'<path transform="translate(65,-50)" '+shapes["waterdrop"]+'<path transform="translate(165,-50)" '+shapes["waterdrop"];
      break;
    case "rain1":
      svg='<path transform="scale(0.60) translate(170,170)" class="dark_cloud" '+shapes["cloud"]+'<path transform="translate(115,-50)" '+shapes["waterdrop"];
      break;
    case "rainshowers":
      svg='<path transform="scale(0.80) translate(20,10)" '+shapes["sun_1"]+'<path transform="scale(0.80) translate(20,10)" '+shapes["sun_2"]+'<path transform="scale(0.50) translate(280,310)" class="dark_cloud" '+shapes["cloud"]+'<path transform="translate(115,-40)" '+shapes["waterdrop"];
      break;
    case "moderaterainshowers":
      svg='<path transform="scale(0.80) translate(20,10)" '+shapes["sun_1"]+'<path transform="scale(0.80) translate(20,10)" '+shapes["sun_2"]+'<path transform="scale(0.50) translate(280,310)" class="dark_cloud" '+shapes["cloud"]+'<path transform="translate(65,-40)" '+shapes["waterdrop"]+'<path transform="translate(165,-40)" '+shapes["waterdrop"];
      break;
    case "heavyrainshowers":
      svg='<path transform="scale(0.80) translate(20,10)" '+shapes["sun_1"]+'<path transform="scale(0.80) translate(20,10)" '+shapes["sun_2"]+'<path transform="scale(0.50) translate(280,310)" class="dark_cloud" '+shapes["cloud"]+'<path transform="translate(40,-40)" '+shapes["waterdrop"]+'<path transform="translate(115,-40)" '+shapes["waterdrop"]+'<path transform="translate(190,-40)" '+shapes["waterdrop"];
      break;
    case "nt_rainshowers":
      svg='<path transform="scale(0.85) translate(40,10)" '+shapes["moon"]+'<path transform="scale(0.50) translate(280,310)" class="dark_cloud" '+shapes["cloud"]+'<path transform="translate(115,-40)" '+shapes["waterdrop"];
      break;
    case "nt_moderaterainshowers":
      svg='<path transform="scale(0.85) translate(40,10)" '+shapes["moon"]+'<path transform="scale(0.50) translate(280,310)" class="dark_cloud" '+shapes["cloud"]+'<path transform="translate(65,-40)" '+shapes["waterdrop"]+'<path transform="translate(165,-40)" '+shapes["waterdrop"];
      break;
    case "nt_heavyrainshowers":
      svg='<path transform="scale(0.85) translate(40,10)" '+shapes["moon"]+'<path transform="scale(0.50) translate(280,310)" class="dark_cloud" '+shapes["cloud"]+'<path transform="translate(40,-40)" '+shapes["waterdrop"]+'<path transform="translate(115,-40)" '+shapes["waterdrop"]+'<path transform="translate(190,-40)" '+shapes["waterdrop"];
      break;
    case "freezingrain":
      svg='<path transform="scale(0.60) translate(170,170)" class="dark_cloud" '+shapes["cloud"]+'<polygon transform="scale(1.5) translate(-50,-185)" '+shapes["ice"]+'<path transform="translate(115,-50)" '+shapes["waterdrop"]+'<path transform="translate(205,-50)" '+shapes["waterdrop"];
      break;
    case "drizzle":
      svg='<path transform="scale(0.60) translate(170,170)" class="dark_cloud" '+shapes["cloud"]+'<path transform="scale(0.60) translate(85,170)" '+shapes["waterdrop"]+'<path transform="scale(0.60) translate(165,170)" '+shapes["waterdrop"]+'<path transform="scale(0.60) translate(245,170)" '+shapes["waterdrop"]+'<path transform="scale(0.60) translate(325,170)" '+shapes["waterdrop"]+'<path transform="scale(0.60) translate(405,170)" '+shapes["waterdrop"]+'<path transform="scale(0.60) translate(485,170)" '+shapes["waterdrop"];
      break;
    case "freezingdrizzle":
      svg='<path transform="scale(0.60) translate(170,170)" class="dark_cloud" '+shapes["cloud"]+'<polygon transform="scale(1.2) translate(-35,-135)" '+shapes["ice"]+'<path transform="scale(0.60) translate(215,170)" '+shapes["waterdrop"]+'<path transform="scale(0.60) translate(295,170)" '+shapes["waterdrop"]+'<path transform="scale(0.60) translate(375,170)" '+shapes["waterdrop"]+'<path transform="scale(0.60) translate(455,170)" '+shapes["waterdrop"];
      break;
    case "snow3":
      svg='<path transform="scale(0.60) translate(170,170)" class="dark_cloud" '+shapes["cloud"]+'<polygon transform="translate(-60,-60)" '+shapes["snowflake"]+'<polygon transform="translate(30,-60)" '+shapes["snowflake"]+'<polygon transform="translate(120,-60)" '+shapes["snowflake"];
      break;
    case "snow2":
      svg='<path transform="scale(0.60) translate(170,170)" class="dark_cloud" '+shapes["cloud"]+'<polygon transform="translate(-25,-60)" '+shapes["snowflake"]+'<polygon transform="translate(90,-60)" '+shapes["snowflake"];break;
    case "snow1":
      svg='<path transform="scale(0.60) translate(170,170)" class="dark_cloud" '+shapes["cloud"]+'<polygon transform="translate(35,-60)" '+shapes["snowflake"];
      break;
    case "heavysnowshowers":
      svg='<path transform="scale(0.80) translate(20,10)" '+shapes["sun_1"]+'<path transform="scale(0.80) translate(20,10)" '+shapes["sun_2"]+'<path transform="scale(0.50) translate(280,310)" class="dark_cloud" '+shapes["cloud"]+'<polygon transform="translate(-55,-55)" '+shapes["snowflake"]+'<polygon transform="translate(35,-55)" '+shapes["snowflake"]+'<polygon transform="translate(125,-55)" '+shapes["snowflake"];
      break;
    case "moderatesnowshowers":
      svg='<path transform="scale(0.80) translate(20,10)" '+shapes["sun_1"]+'<path transform="scale(0.80) translate(20,10)" '+shapes["sun_2"]+'<path transform="scale(0.50) translate(280,310)" class="dark_cloud" '+shapes["cloud"]+'<polygon transform="translate(-25,-55)" '+shapes["snowflake"]+'<polygon transform="translate(90,-55)" '+shapes["snowflake"];
      break;
    case "snowshowers":
      svg='<path transform="scale(0.80) translate(20,10)" '+shapes["sun_1"]+'<path transform="scale(0.80) translate(20,10)" '+shapes["sun_2"]+'<path transform="scale(0.50) translate(280,310)" class="dark_cloud" '+shapes["cloud"]+'<polygon transform="translate(35,-55)" '+shapes["snowflake"];
      break;
    case "nt_heavysnowshowers":
      svg='<path transform="scale(0.85) translate(40,10)" '+shapes["moon"]+'<path transform="scale(0.50) translate(280,310)" class="dark_cloud" '+shapes["cloud"]+'<polygon transform="translate(-55,-55)" '+shapes["snowflake"]+'<polygon transform="translate(35,-55)" '+shapes["snowflake"]+'<polygon transform="translate(125,-55)" '+shapes["snowflake"];
      break;
    case "nt_moderatesnowshowers":
      svg='<path transform="scale(0.85) translate(40,10)" '+shapes["moon"]+'<path transform="scale(0.50) translate(280,310)" class="dark_cloud" '+shapes["cloud"]+'<polygon transform="translate(-25,-55)" '+shapes["snowflake"]+'<polygon transform="translate(90,-55)" '+shapes["snowflake"];
      break;
    case "nt_snowshowers":
      svg='<path transform="scale(0.85) translate(40,10)" '+shapes["moon"]+'<path transform="scale(0.50) translate(280,310)" class="dark_cloud" '+shapes["cloud"]+'<polygon transform="translate(35,-55)" '+shapes["snowflake"];
      break;
    case "heavysleet":
      svg='<path transform="scale(0.60) translate(170,170)" class="dark_cloud" '+shapes["cloud"]+'<polygon transform="translate(-55,-60)" '+shapes["snowflake"]+'<path transform="translate(115,-50)" '+shapes["waterdrop"]+'<polygon transform="translate(125,-60)" '+shapes["snowflake"];
      break;
    case "sleet":
      svg='<path transform="scale(0.60) translate(170,170)" class="dark_cloud" '+shapes["cloud"]+'<path transform="translate(60,-50)" '+shapes["waterdrop"]+'<polygon transform="translate(90,-60)" '+shapes["snowflake"];
      break;
    case "heavysleetshowers":
      svg='<path transform="scale(0.80) translate(20,10)" '+shapes["sun_1"]+'<path transform="scale(0.80) translate(20,10)" '+shapes["sun_2"]+'<path transform="scale(0.50) translate(280,310)" class="dark_cloud" '+shapes["cloud"]+'<polygon transform="translate(-55,-55)" '+shapes["snowflake"]+'<path transform="translate(115,-40)" '+shapes["waterdrop"]+'<polygon transform="translate(125,-55)" '+shapes["snowflake"];
      break;
    case "sleetshowers":
      svg='<path transform="scale(0.80) translate(20,10)" '+shapes["sun_1"]+'<path transform="scale(0.80) translate(20,10)" '+shapes["sun_2"]+'<path transform="scale(0.50) translate(280,310)" class="dark_cloud" '+shapes["cloud"]+'<path transform="translate(60,-40)" '+shapes["waterdrop"]+'<polygon transform="translate(90,-55)" '+shapes["snowflake"];
      break;
    case "nt_heavysleetshowers":
      svg='<path transform="scale(0.85) translate(40,10)" '+shapes["moon"]+'<path transform="scale(0.50) translate(280,310)" class="dark_cloud" '+shapes["cloud"]+'<polygon transform="translate(-55,-55)" '+shapes["snowflake"]+'<path transform="translate(115,-40)" '+shapes["waterdrop"]+'<polygon transform="translate(125,-55)" '+shapes["snowflake"];
      break;
    case "nt_sleetshowers":
      svg='<path transform="scale(0.85) translate(40,10)" '+shapes["moon"]+'<path transform="scale(0.50) translate(280,310)" class="dark_cloud" '+shapes["cloud"]+'<path transform="translate(60,-40)" '+shapes["waterdrop"]+'<polygon transform="translate(90,-55)" '+shapes["snowflake"];
      break;
    case "hail":
      svg='<path transform="scale(0.60) translate(170,170)" class="dark_cloud" '+shapes["cloud"]+'<circle  transform="translate(-120,-75)" '+shapes["hail"]+'<circle  transform="translate(-50,-75)" '+shapes["hail"]+'<circle  transform="translate(20,-75)" '+shapes["hail"]+'<circle  transform="translate(90,-75)" '+shapes["hail"];
      break;
    case "fog":
      svg='<path '+shapes["sun_1"]+'<path '+shapes["sun_2"]+'<path transform="translate(0,-75)" '+shapes["fog"]+'<path transform="translate(0,-120)" '+shapes["fog"]+'<path transform="translate(0,-165)" '+shapes["fog"]+'<path transform="translate(0,-210)" '+shapes["fog"]+'<path transform="translate(0,-255)" '+shapes["fog"]+'<path transform="translate(0,-300)" '+shapes["fog"];
      break;
    case "nt_fog":
      svg='<path '+shapes["moon"]+'<path transform="translate(0,-75)" '+shapes["fog"]+'<path transform="translate(0,-120)" '+shapes["fog"]+'<path transform="translate(0,-165)" '+shapes["fog"]+'<path transform="translate(0,-210)" '+shapes["fog"]+'<path transform="translate(0,-255)" '+shapes["fog"]+'<path transform="translate(0,-300)" '+shapes["fog"];
      break;
    default:
      svg='<path transform="scale(0.50) translate(250,300)" '+shapes["nan"];
      break;
  }
  return svg;
}

if(!dateFormat){
var dateFormat = function () {
	var	token = /d{1,4}|m{1,4}|yy(?:yy)?|([HhMsTt])\1?|[LloSZ]|"[^"]*"|'[^']*'/g,
		timezone = /\b(?:[PMCEA][SDP]T|(?:Pacific|Mountain|Central|Eastern|Atlantic) (?:Standard|Daylight|Prevailing) Time|(?:GMT|UTC)(?:[-+]\d{4})?)\b/g,
		timezoneClip = /[^-+\dA-Z]/g,
		pad = function (val, len) {
			val = String(val);
			len = len || 2;
			while (val.length < len) val = "0" + val;
			return val;
		};

	return function (date, mask, utc) {
		var dF = dateFormat;
		if (arguments.length == 1 && Object.prototype.toString.call(date) == "[object String]" && !/\d/.test(date)) {
			mask = date;
			date = undefined;
		}
		date = date ? new Date(date) : new Date;
		if (isNaN(date)) throw SyntaxError("invalid date");
		mask = String(dF.masks[mask] || mask || dF.masks["default"]);
		if (mask.slice(0, 4) == "UTC:") {
			mask = mask.slice(4);
			utc = true;
		}

		var	_ = utc ? "getUTC" : "get",
			d = date[_ + "Date"](),
			D = date[_ + "Day"](),
			m = date[_ + "Month"](),
			y = date[_ + "FullYear"](),
			H = date[_ + "Hours"](),
			M = date[_ + "Minutes"](),
			s = date[_ + "Seconds"](),
			L = date[_ + "Milliseconds"](),
			o = utc ? 0 : date.getTimezoneOffset(),
			flags = {
				d:    d,
				dd:   pad(d),
				ddd:  dF.i18n.dayNames[D],
				dddd: dF.i18n.dayNames[D + 7],
				m:    m + 1,
				mm:   pad(m + 1),
				mmm:  dF.i18n.monthNames[m],
				mmmm: dF.i18n.monthNames[m + 12],
				yy:   String(y).slice(2),
				yyyy: y,
				h:    H % 12 || 12,
				hh:   pad(H % 12 || 12),
				H:    H,
				HH:   pad(H),
				M:    M,
				MM:   pad(M),
				s:    s,
				ss:   pad(s),
				l:    pad(L, 3),
				L:    pad(L > 99 ? Math.round(L / 10) : L),
				t:    H < 12 ? "a"  : "p",
				tt:   H < 12 ? "am" : "pm",
				T:    H < 12 ? "A"  : "P",
				TT:   H < 12 ? "AM" : "PM",
				Z:    utc ? "UTC" : (String(date).match(timezone) || [""]).pop().replace(timezoneClip, ""),
				o:    (o > 0 ? "-" : "+") + pad(Math.floor(Math.abs(o) / 60) * 100 + Math.abs(o) % 60, 4),
				S:    ["th", "st", "nd", "rd"][d % 10 > 3 ? 0 : (d % 100 - d % 10 != 10) * d % 10]
			};

		return mask.replace(token, function ($0) {
			return $0 in flags ? flags[$0] : $0.slice(1, $0.length - 1);
		});
	};
}();

// Some common format strings
dateFormat.masks = {
	"default":      "ddd mmm dd yyyy HH:MM:ss",
	shortDate:      "m/d/yy",
	mediumDate:     "mmm d, yyyy",
	longDate:       "mmmm d, yyyy",
	fullDate:       "dddd, mmmm d, yyyy",
	shortTime:      "h:MM TT",
	mediumTime:     "h:MM:ss TT",
	longTime:       "h:MM:ss TT Z",
	isoDate:        "yyyy-mm-dd",
	isoTime:        "HH:MM:ss",
	isoDateTime:    "yyyy-mm-dd'T'HH:MM:ss",
	isoUtcDateTime: "UTC:yyyy-mm-dd'T'HH:MM:ss'Z'"
};

// Internationalization strings
dateFormat.i18n = {
	dayNames: fdaynames,
	monthNames: [
		"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
		"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"
	]
};

// For convenience...
Date.prototype.format = function (mask, utc) {
	return dateFormat(this, mask, utc);
};
}else{
dateFormat.i18n = {
	dayNames: days,
	monthNames: [
		"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
		"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"
	]
};
}