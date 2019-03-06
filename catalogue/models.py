import json

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from swingtime import models as swingtime


class Contributor(models.Model):
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
    with open(settings.DEPARTMENTS_FILE, "r", encoding="utf-8") as file:
        DEPARTMENT_CHOICES = tuple(
            (department['code'], department['code'] + ' - '
             + department['name']) for department in json.load(file))

    name = models.CharField(max_length=50)
    space_available = models.PositiveIntegerField(default=1,
                                                  validators=
                                                  [MinValueValidator(1),
                                                   MaxValueValidator(1000)])
    street = models.CharField(max_length=150)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    department = models.CharField(max_length=4,
                                  choices=DEPARTMENT_CHOICES)

    def __str__(self):
        return self.name


class Meeting(swingtime.Event):
    photo = models.ImageField(upload_to='meeting/%Y/%m/%d/')
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    authors = models.ManyToManyField(Author, blank=True)
    artists = models.ManyToManyField(Artist, blank=True)
    directors = models.ManyToManyField(Director, blank=True)
    price = models.FloatField(default=15.0, validators=[MinValueValidator(1),
                                                        MaxValueValidator(150)])

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)
