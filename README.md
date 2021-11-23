# fieldform-grondwaterkwaliteit-zeeland
Deze repository bevat het Python-script (locations_to_field_form.py) om invoer voor de FieldForm-app (Android en iOS) aan te maken op basis van data van de provincie Zeeland. De provincie Zeeland zal de FieldForm-app gebruiken als hulpmiddel om monsters te nemen van de waterkwalitiet van het grondwater in een set peilbuizen binnen de provincie.

Invoer van het script staat in de map 'input'. De uitvoer (het json-locatie-bestand) wordt weggeschreven in de map 'output'. Deze laatste map is niet aan de repository toegevoegd, aangezien deze gegenereerd kan worden uit de overige bestanden in de repository.

Om het script uit te voeren zijn de volgende Python-packages nodig:
- os
- json
- numpy
- pandas
- pyproj
