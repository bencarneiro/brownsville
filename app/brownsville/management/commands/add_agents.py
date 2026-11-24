from django.core.management.base import BaseCommand
from brownsville.models import Agent

AGENTS = [
    {
        "mls_id": "613",
        "name": "Rene Chacon",
        "phone": "(956) 266-0810",
        "email": "rchacon141@gmail.com",
        "license_number": None,
    },
    {
        "mls_id": "607",
        "name": "Alejandro Cortez",
        "phone": "(956) 521-5662",
        "email": "cortezalejandro@myyahoo.com",
        "license_number": None,
    },
    {
        "mls_id": "614",
        "name": "Andy Cortez",
        "phone": "(956) 459-2286",
        "email": "acortezl@aol.com",
        "license_number": None,
    },
    {
        "mls_id": "558",
        "name": "Elvia Reyna",
        "phone": "(956) 455-4422",
        "email": "elvia_realtysolutions@yahoo.com",
        "license_number": None,
    },
    {
        "mls_id": "554",
        "name": "Nicolas Rodriguez",
        "phone": "(956) 561-0377",
        "email": "nic_rdz_01@hotmail.com",
        "license_number": None,
    },
    {
        "mls_id": "611",
        "name": "Luis Sanchez",
        "phone": "(956) 243-1036",
        "email": "luis.r.sanchez215@gmail.com",
        "license_number": None,
    },
]


class Command(BaseCommand):
    help = "Creates or updates the six agents in the database"

    def handle(self, *args, **options):
        for data in AGENTS:
            agent, created = Agent.objects.update_or_create(
                mls_id=data["mls_id"],
                defaults=data,
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action}: {agent}")