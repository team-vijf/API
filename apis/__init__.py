from flask_restplus import Api
from flask import url_for

from .private import api as private
from .public import api as public

authorizations = {
    'Token' : {
        'type' : 'apiKey',
        'in' : 'header',
        'name' : 'X-API-KEY'
    }
}

motd = '''
<img src="https://buddygodutch.nl/wp-content/uploads/2016/08/Hogeschool-Utrecht.png">
<h3>Welkom bij de Lokaalbezetting API!</h3>

<p>
Met deze API kun je als student of staff van de Hogeschool Utrecht de actuele lokaalbezetting opvragen. Om deze informatie op te vragen via de API vraag je een public access API KEY aan onder /access/public.
</p>

<p>
De private endpoints worden alleen gebruikt door de sensor devices die de lokaalbezetting meten en instanties van de web-app die deze informatie weergeeft aan de gebruiker.
</p>
<h3>Hoe achterhalen we de actuele lokaalbezetting?</h3>

<p>
<img src="https://i.imgur.com/4YSBFZz.png" height="350">
</p>
'''


api = Api(
    title='Lokaalbezetting API',
    version='0.1',
    doc='/',
    default='Request Access',
    default_label='These endpoints can be used to request private or public access to the API.',
    authorizations=authorizations,
    description=motd
)

api.add_namespace(private, path='/private')
api.add_namespace(public, path='/public')
