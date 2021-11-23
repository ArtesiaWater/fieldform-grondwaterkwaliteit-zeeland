# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 08:45:34 2021

@author: ruben
"""

import os
import json
import numpy as np
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd


def df2gdf(df, xcol='x', ycol='y'):
    """Make a GeoDataFrame from a DataFrame, assuming it contains points"""
    geometry = [Point((s[xcol], s[ycol])) for i, s in df.iterrows()]
    gdf = gpd.GeoDataFrame(df.copy(), geometry=geometry)
    return gdf


# %% Define locations
# read data
fname = 'Kopie van GWMeetnetZld Bemonsteringsronde 2017 tbv offerte.xlsx'
fname = os.path.join('input', fname)
df = pd.read_excel(fname)
# only select top part of file
df = df.iloc[:np.where(df['NITG-filter'].isnull())[0][0]]
df = df.set_index('NITG-filter')
df = df[~df['X'].isna()]
gdf = df2gdf(df, 'X', 'Y').set_crs(epsg=28992).to_crs(epsg=4326)
gdf['put'] = [x.split('-')[0] for x in gdf.index]
locations = {}
for put in gdf['put'].unique():
    mask = gdf['put'] == put
    g = gdf.loc[mask, 'geometry']
    d0 = {'lat': g.y.mean(), 'lon': g.x.mean()}
    d0['group'] = 'waterkwaliteit'
    d0['sublocations'] = {}
    for i, name in enumerate(gdf.index[mask]):
        d1 = {}
        d1['group'] = 'waterkwaliteit'
        props = {}
        rename = {'MAAIVELD cm_NAP': 'Maaiveld (cm NAP)',
                  'BOVENKANT FILTER cm_NAP': 'Bovenkant filter (cm NAP)',
                  'ONDERKANT FILTER cm_NAP': 'Onderkant filter (cm NAP)'}
        for key in rename:
            props[rename[key]] = gdf.at[name, key]
        for column in ['Perceel 1 Alg. stoffen en sporen',
                       'Perceel 2 Bestrijdings middelen',
                       'Perceel 3 en 4 Overige verontr.']:
            if gdf.at[name, column] > 0:
                value = 'Ja'
            else:
                value = 'Nee'
            props[column] = value
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
ifs['beschadiging'] = {'name': 'Controle beschadiging put en filter',
                       'type': 'choice',
                       'options': ['Ja', 'Nee', 'Onbekend']}
ifs['afdekking'] = {'name': 'Controle correcte afdekking put',
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
with open(os.path.join('output', 'locations.json'), 'w') as outfile:
    json.dump(data, outfile, indent=2)
