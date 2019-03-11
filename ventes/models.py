from django.db import models
from catalogue.models import Meeting
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User


class Commande(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    meetings = models.ManyToManyField(Meeting,
                                      through='CommandeMeeting',
                                      through_fields=('from_commande',
                                                      'to_meeting'))


class CommandeMeeting(models.Model):
    from_commande = models.ForeignKey(Commande, on_delete=models.CASCADE,
                                      related_name='from_commande')
    to_meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE,
                                   related_name="to_meeting")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1),
                                                       MaxValueValidator(9)])
    date_meeting = models.DateTimeField()
    qrcode = models.ImageField(upload_to='qrcode/%Y/%m/%d/', null=True,
                               blank=True)

    class Meta:
        unique_together = (('from_commande', 'to_meeting', 'date_meeting'),)
