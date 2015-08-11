# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import uuid

from django.core.cache import cache
from django.db import models

from cms.utils import get_cms_setting

CMS_URL_CONF_VERSION_KEY = get_cms_setting("CACHE_PREFIX") + 'URL_CONF_VERSION'
CACHE_DURATION = get_cms_setting('CACHE_DURATIONS')['content']


class UrlconfRevision(models.Model):
    revision = models.CharField(max_length=255)

    class Meta:
        app_label = 'cms'

    @staticmethod
    def _set_cache(revision):
        if not get_cms_setting('PAGE_CACHE'):
            return

        cache.set(
            CMS_URL_CONF_VERSION_KEY,
            revision,
            CACHE_DURATION
        )

    def save(self, *args, **kwargs):
        """
        Simply forces this model to be a singleton and to update the cache,
        if configured.
        """
        self.pk = 1
        self._set_cache(self.revision)
        super(UrlconfRevision, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_revision(cls, revision=None):
        """
        Convenience method for getting or creating revision in a cache-friendly
        way, if available, else, get from database backend (and store in the
        cache for next time).
        """
        if get_cms_setting('PAGE_CACHE'):
            revision = cache.get(CMS_URL_CONF_VERSION_KEY, None)
            if revision is not None:
                return revision, False

        if revision is None:
            revision = str(uuid.uuid4())
        obj, created = cls.objects.get_or_create(
            pk=1, defaults=dict(revision=revision))
        cls._set_cache(obj.revision)
        return obj.revision, created

    @classmethod
    def update_revision(cls, revision):
        """ Convenience method for updating the revision. """
        if revision is None:
            revision = str(uuid.uuid4())
        obj, created = cls.objects.get_or_create(
            pk=1, defaults=dict(revision=revision))
        if not created:
            obj.revision = revision
            obj.save()
