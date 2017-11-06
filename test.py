from main import find_routes
import pprint

office_coordinate = (37.425822, -122.100192)
embarcadero_coordinate = (37.792740, -122.397068)
departure_time = "18:00:00"

solutions = find_routes(office_coordinate, embarcadero_coordinate, departure_time)

for i in range(len(solutions.keys())):
    print solutions[i+1]
