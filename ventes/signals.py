import datetime
from io import BytesIO

import qrcode
from django.conf import settings
from django.core.files import File
from django.core.signing import Signer
from django.db.models import F, Sum, Q
from django.db.models import FloatField
from django.db.models.functions import Coalesce
from django.utils import timezone
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED

from catalogue.models import Meeting
from ventes.models import Commande


def payment_notification(sender, **kwargs):
    """signal traitment of paypal process"""

    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # WARNING !
        # Check that the receiver email is the same we previously
        # set on the `business` field. (The user could tamper with
        # that fields on the payment form before it goes to PayPal)
        if ipn_obj.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
            # Not a valid payment
            return

        # ALSO: for the same reason, you need to check the amount
        # received, `custom` etc. are all what you expect or what
        # is allowed.

        signer = Signer()
        id_commande = int(signer.unsign(ipn_obj.custom))

        commande = Commande.objects.prefetch_related(
            "from_commande",
            'from_commande__to_meeting') \
            .annotate(
            total_price=Sum(
                F('from_commande__quantity')
                * F('from_commande__to_meeting__price'),
                output_field=FloatField()
            )
        ).filter(pk=id_commande).get()

        if "%.2f" % float(ipn_obj.mc_gross) == "%.2f" % float(commande.total_price * 1.021) and \
                ipn_obj.mc_currency == 'EUR':
            commandes_meetings = commande.from_commande.all()

            if not commande.enabled:
                for commande_meeting in commandes_meetings:
                    meeting = Meeting.objects.filter(
                        pk=commande_meeting.to_meeting.pk) \
                        .annotate(
                        nombre_de_place_reserve=Coalesce(Sum(
                            F('to_meeting__quantity'),
                            filter=Q(
                                to_meeting__date_meeting=commande_meeting.date_meeting
                            ) & (Q(to_meeting__from_commande__enabled=True)
                                 | (Q(to_meeting__from_commande__too_late_accepted_payment=True)
                                    & Q(to_meeting__from_commande__payment_status=True)))
                        ), 0)
                    ).annotate(
                        place_restante=F('place__space_available')
                                       - F('nombre_de_place_reserve')
                                       - commande_meeting.quantity
                    ).first()

                    if meeting.place_restante < 0:
                        commande.too_late_accepted_payment = False
                        break

                    now = datetime.datetime.now()

                    recurrences = meeting.recurrences

                    if recurrences:
                        occurrences = recurrences.occurrences(
                            dtstart=now + datetime.timedelta(
                                minutes=30)) or None
                    else:
                        commande.too_late_accepted_payment = False
                        break

                    if not occurrences:
                        commande.too_late_accepted_payment = False
                        break
                    occurrences = [timezone.make_aware(date.replace(second=0))
                                   for date
                                   in occurrences]
                    if commande_meeting.date_meeting not in occurrences:
                        commande.too_late_accepted_payment = False
                        break

                    commande.too_late_accepted_payment = True

            if commande.enabled or (not commande.enabled and
                                    commande.too_late_accepted_payment):
                for commande_meeting in commandes_meetings:
                    blob = BytesIO()
                    qrcode_img = qrcode.make(
                        signer.sign(commande_meeting.pk)
                    )
                    qrcode_img.save(blob, 'JPEG')
                    commande_meeting.qrcode.save(str(hash(commande.date))
                                                 + '.jpg', File(blob))

            commande.payment_status = True
            commande.save()


valid_ipn_received.connect(payment_notification)
