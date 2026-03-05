import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.products.utils import parse_multipart_data
from apps.products.api.serializers.product_update_serializer import ProductFullUpdateSerializer

# What Axios sends exactly:
raw_data = {
    'images[0][id]': '5',
    'images[0][is_primary]': 'true',
    'images[0][is_secondary]': 'false',
    'images[1][is_primary]': 'false', 
    'images[1][is_secondary]': 'true'
}

parsed_data = parse_multipart_data(raw_data)
print("Parsed array:", parsed_data)

s = ProductFullUpdateSerializer(data=parsed_data, partial=True)
print("Is valid?", s.is_valid())
if not s.is_valid():
    print("Errors:", s.errors)
