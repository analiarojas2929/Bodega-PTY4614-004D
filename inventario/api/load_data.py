# load_data.py
import json
from api.models import Material

with open('materiales_data.json', 'r') as file:
    data = json.load(file)
    for item in data:
        Material.objects.create(**item)
