# We import the dependencies
import csv
import json
# This is needed to create a lxml element object that has a css selector
import time
from lxml.etree import fromstring
# The requests library
import requests


class EmporisScraper:

    API_url = 'https://www.emporis.com/buildings/map'
    scraped_buildings = []

    def get_building_info(self, longitude, latitude, delta):

        data = {
            'north': str(latitude + delta),
            'east': str(longitude + delta),
            'south': str(latitude),
            'west': str(longitude)
        }
        # Making the post request
        t0 = time.time()
        response = requests.get(self.API_url, params=data)

        response_delay = time.time() - t0
        time.sleep(5 * response_delay)  # wait 5x longer than it took them to respond
        if response.status_code != 200:
            print('not 200' + str(response.status_code))

        print(response.status_code)
        # print('\n')
        return response.json()

    def parse_buildings(self, buildings):

        for building in buildings:
            part1 = building['details']
            part2 = dict(zip(('latitude', 'longitude'), (building['coords'][0], building['coords'][1])))
            self.scraped_buildings.append({**part1, **part2})

    def run(self, boundaries):
        """

        :param boundaries:
        bounds is a list of [Long1, Lat1, Long2, Lat2]
        Long1,Lat1 is the coordinates of lower left corner of the rectangle
        Long2,Lat2 is the coordinates of upper right corner of the rectangle

        """
        delta = 0.06
        # iterate over grids of squares with size delta x delta
        i = 1
        longitude = boundaries[0]

        while longitude < boundaries[2]:

            latitude = boundaries[1]

            while latitude < boundaries[3]:

                data = self.get_building_info(longitude, latitude, delta)
                self.parse_buildings(data)

                latitude += delta
                i += 1

                if i % 6 == 0:
                    time.sleep(3)
                    # print(len(self.scraped_buildings))
                else:
                    time.sleep(1)

                print('\n')
                print('i=' + str(i))
                print('number of buildings =' + str(len(self.scraped_buildings)))

            longitude += delta
            print(longitude, latitude)

        self.save_data()

    def save_data(self):

        data = self.scraped_buildings

        with open('building_data.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

        columns = [x for row in data for x in row.keys()]
        columns = list(set(columns))

        with open('building_data_penang.csv', 'w') as out_file:
            csv_w = csv.writer(out_file, lineterminator='\n')
            csv_w.writerow(columns)

            for i_r in data:
                csv_w.writerow(map(lambda x: i_r.get(x, ""), columns))

        #
        # with open('building_data.csv', 'w') as out_file:
        #     # csv_w = csv.writer(out_file)
        #     # csv_w.writerow(columns)
        #     output = csv.writer(out_file, lineterminator='\n')
        #     output.writerow(columns)  # header row
        #     for row in data:
        #         output.writerow(row.values())


if __name__ == '__main__':
    scraper = EmporisScraper()

    # bounds = [101.624090, 3.091952, 101.734982, 3.174507]
    # bounds = [101.624090, 3.091952, 101.68409, 3.151952]
    # Selangor boundaries
    # bounds = [100.921895, 2.499052, 102.017055, 3.821812]

    # KK Sabah
    # bounds = [115.839728, 5.685089, 116.361896, 6.250996]

    # Eastern
    # bounds = [101.683176, 3.806320, 103.909784, 6.322343]
    bounds = [100.162627, 5.058447, 100.577164, 5.613265]

    scraper.run(bounds)
