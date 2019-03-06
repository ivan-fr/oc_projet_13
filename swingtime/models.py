from django.contrib.contenttypes.fields import GenericForeignKey, \
    GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from treebeard.al_tree import AL_Node
from swingtime.fields import RecurrenceField

__all__ = (
    'Note',
    'EventType',
    'Event',
)


class Note(models.Model):
    '''
    A generic model for adding simple, arbitrary notes to other models such as
    ``Event`` or ``Occurrence``.
    '''
    note = models.TextField(_('note'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_('content type'),
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField(_('object id'))
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')

    def __str__(self):
        return self.note


class EventType(AL_Node):
    '''
    Simple ``Event`` classifcation.
    '''
    parent = models.ForeignKey('self',
                               related_name='children_set',
                               null=True,
                               db_index=True,
                               on_delete=models.CASCADE)
    sib_order = models.PositiveIntegerField(null=True)
    label = models.CharField(_('label'), max_length=50, unique=True)

    class Meta:
        verbose_name = _('event type')
        verbose_name_plural = _('event types')

    def __str__(self):
        return self.label


class Event(models.Model):
    '''
    Container model for general metadata and associated ``Occurrence`` entries.
    '''
    title = models.CharField(_('title'), max_length=32)
    event_type = models.ForeignKey(
        EventType,
        verbose_name=_('event type'),
        on_delete=models.CASCADE
    )

    recurrences = RecurrenceField(default=None, null=True)
    notes = GenericRelation(Note, verbose_name=_('notes'))

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ('title',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('swingtime-event', args=[str(self.id)])
