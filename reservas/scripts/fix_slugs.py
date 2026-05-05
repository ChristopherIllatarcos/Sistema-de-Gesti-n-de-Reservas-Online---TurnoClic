import os
import sys
import django

# 👇 ESTO ES LO QUE TE FALTABA
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

from reservas.models import PerfilNegocio
from django.utils.text import slugify

for p in PerfilNegocio.objects.all():
    if not p.slug:
        base = slugify(p.nombre_negocio)
        slug = base
        counter = 1

        while PerfilNegocio.objects.filter(slug=slug).exclude(id=p.id).exists():
            slug = f"{base}-{counter}"
            counter += 1

        p.slug = slug
        p.save()

print("Slugs corregidos")