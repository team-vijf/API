from core import db

buildings = [
    {"name": "HL15",
     "streetName": "Heidelberglaan",
     "buildingNumber": "15"},

    {"name": "PL101",
     "streetName": "Padualaan",
     "buildingNumber": "101"}]

floors = [
    {"floorNumber": "0",
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

    structureExists = database.query('''SELECT to_regclass('public.buildings');''')
    if len(structureExists) < 1:
        database.query(open('project.sql', 'r').read())

    # for building in buildings:
    #     database.query('''INSERT INTO buildings ( name, streetname, buildingnumber) VALUES ( '{}', '{}', '{}' )'''.format(building['name'],
    #                                                                                                                       building['streetName'],
    #                                                                                                                       building['buildingNumber']))

    # for floor in floors:
    #     database.query('''INSERT INTO floors VALUES ( '{}', '{}', '{}', '{}' )'''.format(floor['id'],
    #                                                                                      floor['floorNumber'],
    #                                                                                      floor['name_buildings']))
