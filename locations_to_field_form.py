# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 08:45:34 2021

@author: ruben
"""

import os
import json
import pandas as pd
import pyproj


# %% Define locations
# read data
fname = 'GWMeetnetZld Bemonsteringsronde 2021 tbv json FieldForm.xlsx'
fname = os.path.join('input', fname)
df = pd.read_excel(fname)
df = df.set_index('NITGcode')
df = df[~df['X'].isna()]
# get latitude and longitude of locations
transformer = pyproj.Transformer.from_crs(28992, 4326)
df['lat'], df['lon'] = transformer.transform(df['X'], df['Y'])
# get the put-name of each location
df['put'] = [x.split('-')[0] for x in df.index]
locations = {}
for put in df['put'].unique():
    mask = df['put'] == put
    d0 = {'lat': df.loc[mask, 'lat'].mean(), 'lon': df.loc[mask, 'lon'].mean()}
    d0['group'] = 'waterkwaliteit'
    d0['sublocations'] = {}
    for i, name in enumerate(df.index[mask]):
        d1 = {}
        d1['group'] = 'waterkwaliteit'
        props = {}
        rename = {'Maaiveld [cm NAP]': 'Maaiveld [cm NAP]',
                  'Bovenkant Filter [cm NAP]': 'Bovenkant Filter [cm NAP]',
                  'Onderkant Filter [cm NAP]': 'Onderkant Filter [cm NAP]',
                  'Lengte dichte buis [m]': 'Lengte dichte buis [m]'}
        for key in rename:
            props[rename[key]] = float(df.at[name, key])
        for column in ['Perceel  1',
                       'Perceel 2',
                       'Perceel 3',
                       'Perceel 4',
                       'Perceel 5']:
            if df.at[name, column] > 0:
                value = 'Ja'
            else:
                value = 'Nee'
            props[column] = value
        if isinstance(df.at[name, 'KRW_GWL'], str):
            props['KRW_GWL'] = df.at[name, 'KRW_GWL']
        if df.at[name, 'KRW_Meetpunt']:
            props['KRW_Meetpunt'] = 'Ja'
        else:
            props['KRW_Meetpunt'] = 'Nee'
        if isinstance(df.at[name, 'Opmerking'], str):
            props['Opmerking'] = df.at[name, 'Opmerking']
        d1['properties'] = props
        d0['sublocations'][name] = d1
    locations[put] = d0

# %% Define inputfields
ifs = {}
ifs['landgebruik'] = {'name': 'Dominant landgebruik',
                      'type': 'choice',
                      # 'hint': 'max 2 selecteren',
                      'options': ['Grasland',
                                  'Akkerbouw',
                                  'Glastuinbouw, bomen-&bollenteelt',
                                  'Bos, natuur en water',
                                  'Bebouwd',
                                  'Industrie']}

# Gegevens Put
ifs['beschadiging'] = {'name': 'Beschadiging put en filter?',
                       'type': 'choice',
                       'options': ['Ja', 'Nee', 'Onbekend']}
ifs['afdekking'] = {'name': 'Correcte afdekking put?',
                    'type': 'choice',
                    'options': ['Ja', 'Nee', 'Onbekend']}

# Gegevens filter
# ifs['grondwaterstand'] = {'type': 'number', 'name': 'Grondwaterstand',
#                           'hint': 'cm tov bovenkant peilfilter/stijgbuis'}
ifs['gws_voor_pompen'] = {'name': 'Grondwaterstand voor het voorpompen [cm] *',
                          'type': 'number',
                          'hint': 'cm tov bovenkant peilfilter/stijgbuis'}
ifs['gws_na_pompen'] = {'name': 'Grondwaterstand na het voorpompen [cm] *',
                        'type': 'number',
                        'hint': 'cm tov bovenkant peilfilter/stijgbuis'}
ifs['bovenkant_peilfilter'] = {'name': 'Bovenkant peilfilter [cm]',
                               'type': 'number',
                               'hint': 'cm+mv'}
ifs['onderkant_peilfilter'] = {'name': 'Onderkant peilfilter [cm]',
                               'type': 'number',
                               'hint': 'cm tov bovenkant peilfilter/stijgbuis'}

# Voorpompen
ifs['pomptype'] = {'name': 'Pomptype *',
                   'type': 'choice',
                   'options': ['onderwaterpomp', 'peristaltischePomp',
                               'vacuümpomp', 'anders', 'onbekend']}
ifs['lengte_waterkolom'] = {'name': 'Lengte waterkolom [cm]',
                            'type': 'number',
                            'hint': 'cm'}
ifs['inwendige_diameter_filter'] = {'name': 'Inwendige diameter filter [mm]',
                                    'type': 'number',
                                    'hint': 'mm'}
# ifs['voorpompvolume'] = {'name': 'Voorpompvolume',
#                          'type': 'number',
#                          'hint': 'l'}
ifs['voorpompdebiet'] = {'name': 'Voorpompdebiet [l/min]',
                         'type': 'number',
                         'hint': 'l/min; maximaal 8 l/min'}
ifs['bemonsteringsdebiet'] = {'name': 'Bemonsteringsdebiet [l/min]',
                              'type': 'number',
                              'hint': 'l/min'}
ifs['toestroming_filter'] = {'name': 'Toestroming filter',
                             'type': 'choice',
                             'options': ['Goed', 'Matig', 'Slecht']}

# Veldmetingen
for t in [0, 3, 6]:
    ifs[f'zuurgraad_{t}'] = {'name': f'Zuurgraad na {t} minuten [pH]',
                             'type': 'number',
                             'hint': 'pH'}

    ifs[f'geleidbaarheid_{t}'] = {'name': f'Geleidbaarheid na {t} minuten [µS/cm]',
                                  'type': 'number',
                                  'hint': 'µS/cm'}
ifs['zuurstof'] = {'name': 'Zuurstof (O2) [mg/l] *',
                   'type': 'number',
                   'hint': 'mg/l'}
ifs['temperatuur'] = {'name': 'Temperatuur [ºC] *',
                      'type': 'number',
                      'hint': 'ºC'}
ifs['temperatuur_moeilijk'] = {'name': 'Temperatuur moeilijk te bepalen *',
                               'type': 'choice',
                               'options': ['Ja', 'Nee', 'Onbekend']}
ifs['waterstofcarbonaat'] = {'name': 'Waterstofcarbonaat (HCO3) [mg/l] *',
                             'type': 'number',
                             'hint': 'mg/l'}
ifs['troebelheid'] = {'name': 'Troebelheid [NTU] *',
                      'type': 'number',
                      'hint': 'NTU'}
ifs['bicarbonaat'] = {'name': 'Bicarbonaat [mg/l] *',
                      'type': 'number',
                      'hint': 'mg/l'}
ifs['afwijking_meetapparatuur'] = {'name': 'Afwijking meetapparatuur *',
                                   'type': 'choice',
                                   'options': ['Ja', 'Nee', 'Onbekend']}
ifs['contaminatie_door_verbrandingsmotor'] = {'name': 'Contaminatie door verbrandingsmotor *',
                                              'type': 'choice',
                                              'options': ['Ja', 'Nee', 'Onbekend']}

# Monsterneming
options = [
    #    'NEN5744v1991',
    'NEN5744v2011-A1v2013',
    #    'NEN5745v1997',
    #    'NTA8017v2008',
    #    'NTA8017v2016',
    'SIKBProtocol2002vanafV4',
    'onbekend',
]
ifs['bemonsteringsprocedure'] = {'name': 'Bemonsteringsprocedure *',
                                 'type': 'choice',
                                 'options': options}
ifs['inline_filter_afwijkend'] = {'name': 'Inline filter afwijkend *',
                                  'type': 'choice',
                                  'options': ['Ja', 'Nee', 'Onbekend']}
ifs['slang_hergebruikt'] = {'name': 'Slang hergebruikt *',
                            'type': 'choice',
                            'options': ['Ja', 'Nee', 'Onbekend']}
ifs['monster_belucht'] = {'name': 'Monster belucht *',
                          'type': 'choice',
                          'options': ['Ja', 'Nee', 'Onbekend']}
# Analysepakketten
for i in range(1, 6):
    ifs[f'perceel_{i}'] = {'name': f'Perceel {i} *',
                           'type': 'choice',
                           'options': ['Ja', 'Nee']}
ifs['afwijkend_gekoeld'] = {'name': 'Afwijkend gekoeld *',
                            'type': 'choice',
                            'options': ['Ja', 'Nee', 'Onbekend']}

# Visuele waarnemingen
kleuren = [
    'kleurloos',
    'wit',
    'grijs',
    'zwart',
    'rood',
    'oranje',
    'geel',
    'groen',
    'blauw',
    'paars',
    'bruin',
    'roestbruin',
    'beige',
    'creme',
]
ifs['kleur'] = {'name': 'Kleur *',
                'type': 'choice',
                'options': kleuren}
bijkleuren = kleuren
ifs['bijkleur'] = {'name': 'Bijkleur *',
                   'type': 'choice',
                   'options': bijkleuren}
ifs['kleursterkte'] = {'name': 'Kleursterkte *',
                       'type': 'choice',
                       'options': ['zeer licht', 'licht', 'neutraal', 'donker',
                                   'zeer donker']}
# Bijzonderheden
ifs['bijzonderheden'] = {'name': 'Bijzonderheden',
                         'type': 'text',
                         'hint': 'Overige informatie'}

# %% Define groups
groups = {'waterkwaliteit': {'name': 'Waterwaliteit *',
                             'color': 'orange',
                             'inputfields': list(ifs.keys())}}

# %% Add data to json-file
data = {'inputfields': ifs,
        'groups': groups,
        'locations': locations}

if not os.path.isdir('output'):
    os.makedirs('output')
fname = 'locations_{}.json'.format(pd.to_datetime('now').strftime('%Y%m%d'))
with open(os.path.join('output', fname), 'w') as outfile:
    json.dump(data, outfile, indent=2)
