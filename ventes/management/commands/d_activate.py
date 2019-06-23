from django.core.management.base import BaseCommand
from django.db import transaction

from ventes.models import Commande


class Command(BaseCommand):
    help = 'Update the database for clean commands'

    def handle(self, *args, **options):

        with transaction.atomic():

            commandes = Commande.objects.all()
            commandes_counts = commandes.count()

            self.stdout.write(self.style.SUCCESS(
                f"Il y a {commandes_counts} commandes."
            ))

            i = 0
            for commande in commandes:
                if commande.enabled and commande.payment_status is False:
                    commande.enabled = False
                    commande.save()
                    i += 1

            self.stdout.write(self.style.SUCCESS(
                f"Il y a {i} commande{'s' if i > 1 else ''} désactivé."
            ))
