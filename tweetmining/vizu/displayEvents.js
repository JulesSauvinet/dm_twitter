/**
 * Created by jules on 17/01/2017.
 */

//TODO SCALE LES RADIUS D'EVENTS !

var width = 500, height = 500;
var mapEvents = L.map('mapEvents').setView([40.730610,-73.935242], 11);

L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/streets-v9/tiles/256/{z}/{x}/{y}?' +
    'access_token={accessToken}',
    {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">' +
    'OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
    'Imagery © <a href="http://mapbox.com">Mapbox</a>',
    maxZoom: 18,
    id: '256',
    accessToken: 'pk.eyJ1IjoianVsb3M2OSIsImEiOiJjaXkxdjhzYXIwMDAxMzNxdG1kbHhnajA0In0.oUD_1_fTqA3iANvnNfW_FA'
    })
    .addTo(mapEvents);


var svg1 = d3.select(mapEvents.getPanes().overlayPane).append("svg"),
    g1 = svg1.append("g").attr("class", "leaflet-zoom-hide");


var mapTweets = L.map('mapTweets').setView([40.730610,-73.935242], 11);

L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/streets-v9/tiles/256/{z}/{x}/{y}?' +
    'access_token={accessToken}',
    {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">' +
    'OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
    'Imagery © <a href="http://mapbox.com">Mapbox</a>',
    maxZoom: 18,
    id: '256',
    accessToken: 'pk.eyJ1IjoianVsb3M2OSIsImEiOiJjaXkxdjhzYXIwMDAxMzNxdG1kbHhnajA0In0.oUD_1_fTqA3iANvnNfW_FA'
    })
    .addTo(mapTweets);


var svg2 = d3.select(mapTweets.getPanes().overlayPane).append("svg"),
    g2 = svg2.append("g").attr("class", "leaflet-zoom-hide");


var color = d3.scale.linear()
  .interpolate(d3.interpolateHcl)
  .range(["rgb(237,248,233)", "rgb(0,109,44)"]);

var color2 = d3.scale.linear()
  .interpolate(d3.interpolateHcl)
  .range(["orange", "red"]).domain([0,50]);

var opacity = d3.scale.linear()
  .interpolate(d3.interpolateHcl)
  .range([0,1]).domain([0,100]);

var tooltip = d3.select('#mapContainer').append('div')
            .attr('class', 'hidden tooltip');

var days = [];
var tweetsdays = [];
var dayTweet = {};


function create_date(tweet){
  return tweet.timestamp_year+"-"+tweet.timestamp_month+"-"+tweet.timestamp_day;
}

var markers = new L.FeatureGroup();

function removeAllMarkers(){
    mapTweets.removeLayer(markers);
    markers.clearLayers();
}

var circles = new L.FeatureGroup();

function removeAllCircles(){
    mapEvents.removeLayer(circles);
    circles.clearLayers();
}

function updateViz(value, events, tweets){
    d3.select('#days').html(days[value-1]);

    removeAllMarkers();
    removeAllCircles();

    drawMap(value-1, events);
}

var tweetIcon = L.icon({
    iconUrl: 'tweet.png',

    iconSize:     [25, 30], // size of the icon
    iconAnchor:   [11, 11], // point of the icon which will correspond to marker's location
    popupAnchor:  [-2, -20] // point from which the popup should open relative to the iconAnchor
});


function drawMap(currentDay, events) {

  events = events.filter(function(e) {
    return e.date.split(" ")[0] === d3.select('#days').html();
  });

  events.forEach(function(event){
    var totPixels = (width * height);
    var totWorldMeters = 510000000000;
    var metersPerPixel = (totWorldMeters / totPixels);
    var scaledRadius = 0;

    //scale the radius given in meters to pixels on the map
    scaledRadius = (100 * (event.radius / metersPerPixel));
    if(scaledRadius < 5) {
        scaledRadius = 500;
    }

    //console.log(scaledRadius);
    var circle = L.circle([ event.position.split(";")[1],event.position.split(";")[0]], {
        color: 'red',
        fillColor: color2(event.userNumber),
        fillOpacity: opacity(event.tweetsNumbert),
        radius: scaledRadius
    });

    var toDisplay =  "User number  : " +  event.userNumber + "</br>"
             + "Tweets number  : " +  event.tweetsNumbert + "</br>"
             + "Hashtags  : ";

    var hashtags = event.importantHashtags.split("|");
    var idx = 1;
    hashtags.forEach(function(hashtag){
        toDisplay+= hashtag;
        if (idx !== hashtags.length)
            toDisplay += ', ';
        idx++;
    }) ;

    circle.bindPopup(toDisplay);

    circles.addLayer(circle);
  });

  mapEvents.addLayer(circles);

  var date = tweetsdays[currentDay];

  //TEMPORAIRE
  var i = 0;
  dayTweet[date].forEach(function(tweet){
      if (i<=500){
          if (tweet.geo_lat !== "null") {
              var marker = L.marker([tweet.geo_lng, tweet.geo_lat], {icon : tweetIcon});
              markers.addLayer(marker);
          }
      }
      i++;
  });
  mapTweets.addLayer(markers);
}

function processData(error,eventsData, tweets) {

    if (error) throw  error;

    var nbDays=0;
    var i =0;
    //console.log(eventsData);
    eventsData.forEach(function(event) {
        var day = event.date.split(" ")[0];
        if (!days.includes(day)){
            days.push(day);
            nbDays++;
        }
        i++;
    });

    d3.select('#slider')[0][0].max = nbDays;

    var nbDays=0;

    tweets.forEach(function(tweet) {
        var day = create_date(tweet);
        if (!tweetsdays.includes(day)){
            tweetsdays.push(day);
            nbDays++;
        }
        if(!dayTweet[day]){
            dayTweet[day] = [];
        }
        dayTweet[day].push(tweet);
    });

    drawMap(1, eventsData);

    d3.select('#days').html(days[0]);

    d3.select("#slider").on("input", function() {
        updateViz(+this.value, eventsData);
    });
}

queue()
  //chargement des evenements geolocalise de tweets
  .defer(d3.csv, "vizuFile.csv")
  //chargement des données de tweets
  .defer(d3.csv, "smallTweets3.csv")
  .await(processData);
