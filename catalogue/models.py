import json
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from swingtime import models as swingtime


class Contributor(models.Model):
    """Contributor model"""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ['name']


class Author(Contributor):
    pass


class Artist(Contributor):
    pass


class Director(Contributor):
    pass


class Place(models.Model):
    """Place model"""

    with open(settings.DEPARTMENTS_FILE, "r", encoding="utf-8") as file:
        DEPARTMENT_CHOICES = tuple(
            (department['code'], department['code'] + ' - '
             + department['name']) for department in json.load(file))

    name = models.CharField(max_length=50)
    space_available = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(1000)])
    street = models.CharField(max_length=150)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    department = models.CharField(max_length=4,
                                  choices=DEPARTMENT_CHOICES)

    def __str__(self):
        return self.name


class Meeting(swingtime.Event):
    """Meeting model"""

    photo = models.ImageField(upload_to='meeting/%Y/%m/%d/', blank=True,
                              null=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    authors = models.ManyToManyField(Author, blank=True)
    artists = models.ManyToManyField(Artist, blank=True)
    directors = models.ManyToManyField(Director, blank=True)
    price = models.DecimalField(
        default=Decimal(15),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(1), MaxValueValidator(999)]
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)


class Comments(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    texte = models.CharField(max_length=200, null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)
