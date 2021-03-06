# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.db.models import *
from django.conf import settings
from _base import Model

class Download(Model):
	"""" Record of a material download 
	"""

	user = ForeignKey(settings.AUTH_USER_MODEL,
		related_name = '+',
		related_query_name = 'downloads',
		verbose_name = _('user')
	)
	material = ForeignKey('fmfn.Material',
		related_name = '+',
		related_query_name = 'downloads',
		verbose_name = _('material')
	)
	date = DateTimeField(
		auto_now_add = True,
		verbose_name = _('date')
	)

	class Meta(object):
		verbose_name = _('download')
		verbose_name_plural = _('downloads')
		app_label = 'fmfn'
