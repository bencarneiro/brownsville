from pathlib import Path

import requests
from django.core.management.base import BaseCommand

from brownsville.models import ListingPhoto

OUTPUT_DIR = Path("/Users/root1/apps/brownsville/app/brownsville/templates/static")


class Command(BaseCommand):
    def handle(self, *args, **options):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        for photo in ListingPhoto.objects.select_related("listing").all():
            filename = f"{photo.listing.mls_number}_{photo.id}.jpg"
            dest = OUTPUT_DIR / filename

            response = requests.get(photo.path, timeout=15)
            response.raise_for_status()
            dest.write_bytes(response.content)

            photo.slug = filename
            photo.save()

            self.stdout.write(f"Saved {filename}")