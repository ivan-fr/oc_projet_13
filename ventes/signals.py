import qrcode
from io import BytesIO

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received

from django.conf import settings
from django.core.signing import Signer
from django.core.files import File
from django.db.models import F, Sum, FloatField

from ventes.models import Commande


def payment_notification(sender, **kwargs):
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

        if float(ipn_obj.mc_gross) == float(commande.total_price) and \
                ipn_obj.mc_currency == 'EUR':
            commandes_meetings = commande.from_commande.all()
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
