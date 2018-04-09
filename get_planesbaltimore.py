import simplejson as json
import pandas as pd
from shapely.geometry import shape, Point
import os

with open('london.geojson') as f:
    baltijs = json.load(f)

balti = shape(baltijs['features'][0]['geometry'])
notoverbalti = 0

# __________________________________

master_appearances = []
balti_ids = set()

for root, dirs, files in os.walk("data/2017-06-04"):

    for file in files:

        if file.endswith(".json"):
            with open(os.path.join(root, file),"rt") as f:
                flights = json.load(f)

                for plane in flights['acList']:

                    plane_appearance = {}

                    if 'Reg' in plane.keys():
                        plane_appearance['Reg'] = plane['Reg']


                    plane_appearance['Id'] = plane['Id']

                    if 'Op' in plane.keys():
                        plane_appearance['Op'] = plane['Op']

                    if 'Call' in plane.keys():
                        plane_appearance['Call'] = plane['Call']


                    if 'Cos' in plane.keys():


                        lats = plane['Cos'][0::4]
                        longs = plane['Cos'][1::4]
                        timestamps = plane['Cos'][2::4]

                        appearances_count = len(lats)

                        for i in range(0,appearances_count):

                            plane_appearance['_lat'] = lats[i]
                            plane_appearance['_long'] = longs[i]
                            plane_appearance['_timestamp'] = timestamps[i]

                            # Create a shapely Point for our new lat/long
                            planepoint = Point(plane_appearance['_long'],plane_appearance['_lat'])

                            # Check is that point is in DC
                            if balti.contains(planepoint):

                                # Append appearance to DC appearances list (just append the plane, not appearance)
                                balti_ids.add(plane_appearance["Id"])

                            else:
                                notoverbalti += 1

                            # Also append the appearance to our master appearances list
                            master_appearances.append(plane_appearance)

                    elif "Lat" in plane.keys() and "Long" in plane.keys():

                        plane_appearance['_lat'] = plane['Lat']
                        plane_appearance['_long'] = plane['Long']
                        plane_appearance['_timestamp'] = plane['PosTime']

                        planepoint = Point(plane['Long'],plane['Lat'])


                        # Check is that point is in DC
                        if balti.contains(planepoint):

                            # Append appearance to DC appearances list
                            balti_ids.add(plane_appearance["Id"])

                        else:
                            notoverbalti += 1

                        # Also append the appearance to our master appearances list
                        master_appearances.append(plane_appearance)

#Json.dumps converts it to a string instead
balti_appearances = [point for point in master_appearances if point["Id"] in balti_ids]

pdoverbalti = pd.DataFrame(balti_appearances)
pdoverbalti.to_csv("londonday.csv", sep=',', encoding='utf-8')
