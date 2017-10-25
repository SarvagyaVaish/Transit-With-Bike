import urllib
import urllib2
import json
from api_keys import GOOGLE_MAPS_KEY

def get_biking_time(start_point, end_point):
    assert len(start_point.split(',')) == 2
    assert len(end_point.split(',')) == 2

    url = 'https://maps.googleapis.com/maps/api/directions/json'
    params = {
        'origin': start_point,
        'destination': end_point,
        'mode': 'bicycling',
        'key': GOOGLE_MAPS_KEY,
    }

    url_values = urllib.urlencode(params)
    full_url = url + '?' + url_values
    response = urllib2.urlopen(full_url)

    response_text = response.read()
    json_data = json.loads(response_text)

    duration = None
    if json_data['status'] == "OK":
        if json_data.has_key('routes') and \
                json_data['routes'][0].has_key('legs') and \
                json_data['routes'][0]['legs'][0].has_key('duration') and \
                json_data['routes'][0]['legs'][0]['duration'].has_key('value'):
            assert len(json_data['routes']) == 1  # guaranteed if alternatives = 0
            assert len(json_data['routes'][0]['legs']) == 1  # guaranteed when no waypoints are specified
            duration = json_data['routes'][0]['legs'][0]['duration']['value']

    return duration


print get_biking_time("37.425822,-122.100192", "37.407323,-122.107069")
