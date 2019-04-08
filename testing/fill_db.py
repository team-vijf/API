from core import db

buildings = [
    {"id": "GUID",
     "streetName": "Heidelberglaan",
     "buildingNumber": "15"},

    {"id": "buildingPL",
     "name": "PL101",
     "streetName": "Padualaan",
     "buildingNumber": "101"}]

floors = [
    {"floorNumber": "0",
     "id": "lowerHL",
     "id_buildings": "HL15"},

    {"floorNumber": "1",
     "id": "firstHL",
     "name_buildings": "HL15"},

    {"floorNumber": "2",
     "id": "secondHL",
     "name_buildings": "HL15"},

    {"floorNumber": "0",
     "id": "lowerPL",
     "name_buildings": "PL101"},

    {"floorNumber": "1",
    "id": "firstPL",
     "name_buildings": "PL101"},

    {"floorNumber": "2",
    "id": "secondPL",
     "name_buildings": "PL101"}
    ]

classrooms = [
    {"classcode": "HL15-0.063",
     "free": "true"},

    {"classcode": "HL15-0.019",
     "free": "true"},

    {"classcode": "PL101-1.223",
     "free": "true"},

    {"classcode": "PL101-2.164",
     "free": "true"}
    ]


if __name__  == "__main__":
    database = db.Database()
    database.connect()

    # database.query(open('project.sql', 'r').read())

    for building in buildings:
        database.query('''INSERT INTO buildings VALUES ( '{}', '{}', '{}', '{}' )'''.format(building['id'],
                                                                                            building['name'],
                                                                                            building['streetName'],
                                                                                            building['buildingNumber']))

    for floor in floors:
        database.query('''INSERT INTO floors VALUES ( '{}', '{}', '{}', '{}' )'''.format(floor['id'],
                                                                                         floor['floorNumber'],
                                                                                         floor['name_buildings']))
