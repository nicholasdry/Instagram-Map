from bs4 import BeautifulSoup
from urllib.request import urlopen
import googlemaps
import argparse
from requests.exceptions import HTTPError

parser = argparse.ArgumentParser()
parser.add_argument("-user", help="The username of who you want to plot")
args = parser.parse_args()

username = args.user

# Locations is a dictionary with all of the location names and their lat longs setup.
def output_html_map(locations):
    output_html = open("{0}-locations.html".format(username), "w")
    
    output_html.write("""
                        <html>
                            <head>
                                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.2.0/dist/leaflet.css"
                                integrity="sha512-M2wvCLH6DSRazYeZRIm1JnYyh22purTM+FDB5CsyxtQJYeKq83arPe5wgbNmcFXGqiSH2XR8dT/fJISVA1r/zQ=="
                                crossorigin=""/>
                                <script src="https://unpkg.com/leaflet@1.2.0/dist/leaflet.js"
                                integrity="sha512-lInM/apFSqyy1o6s89K4iQUKg6ppXEgsVxT35HbzUupEVRh2Eu9Wdl4tHj7dZO0s1uvplcYGmt3498TtHq+log=="
                                crossorigin=""></script>
                                <style>
                                    #mapid { height: 100%; }
                                </style>
    
                            </head>
                            <body>
                                <div style="position: fixed; top: 15px; right 15px; z-index=1;">
                                    <h2>Hello</h2>
                                </div>
                                <div id="mapid">

                                </div>
                                <script>
                                    var mymap = L.map('mapid').setView([51.505, -0.09], 13);
        
                                    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
                                        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
                                        maxZoom: 18,
                                        id: 'mapbox.streets',
                                        accessToken: 'MAP KEY'
                                    }).addTo(mymap); 
                        
                                    """)
    # Now iterate through the dictionary and drop the lat and long in there.
    count = 0
    for location in locations.keys():
        curr_location = locations[location]
        lat = curr_location['lat']
        lng = curr_location['lng']

        output_html.write("""
                            var marker{0} = L.marker([{1}, {2}]).addTo(mymap);
                            marker{3}.bindPopup("{4}");
                        """.format(count, lat, lng, count, location))
        count = count + 1

    output_html.write("""
                                </script>
                            </body>
                        </html>
                        """)

    output_html.close()


url_str = "https://www.instagram.com/{0}/".format(username)

url_obj = urlopen(url_str)
soup = BeautifulSoup(url_obj, "html.parser")

links = soup.find_all("a", href=True)

post_locations = []

for post in links:
    if "/p/" in str(post):
        # We know we have a new post, so lets go to this location and grab the location.
        post_url = "https://www.instagram.com{0}?taken-by={1}".format(post['href'], username)
        while True:
            try:
                post_obj = urlopen(post_url)
                break
            except HTTPError:
                print("Trying again.")
        post_soup = BeautifulSoup(post_obj, "html.parser")
        post_links = post_soup.find_all("a", href=True)

        for post_link in post_links:
            if "/explore/locations/" in str(post_link):
                # We found a new location, lets add it.
                post_locations.append(post_link.text)

# Now here we have all the locations this person has been. Let's use the google map api to find them.
gmaps = googlemaps.Client(key='GOOGLE MAPS KEY')

locations_with_latlong = {}

for place in post_locations:

    # This has alot of information
    geocode = gmaps.geocode(place)

    locations_with_latlong[place] = geocode[0]['geometry']['location']

# Now that we have a dictionary of all of the locations setup lets begin the output of the html file.
output_html_map(locations_with_latlong)