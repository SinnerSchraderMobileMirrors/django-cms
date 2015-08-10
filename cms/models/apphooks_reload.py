# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class UrlconfRevision(models.Model):
    revision = models.CharField(max_length=255)

    class Meta:
        app_label = 'cms'
