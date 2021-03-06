# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response, RequestContext
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from grappelli import urls as grapelli_urls
from django.conf.urls.static import static
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from apps.fmfn import views

from django.http import HttpResponse

redirect = RedirectView.as_view

urlpatterns = [

	# Search interface
	url(r'^', include([

		url(r'^$', redirect(url = reverse_lazy('search')), name = 'index'),  # GET
		url(r'^search/', include([

			url(r'^$', views.search.search, name = 'search'),  # GET
	 		url(r'^api/$', views.search.search, name = 'filter')  # POST

		]))

	])),

	# Content management
	 url(r'^content/', include([

	 	url(r'create/$', views.materials.create, name = 'create'),  # GET, PUT
	 	url(r'^(?P<content_id>[\d]+)/', include([

	 		url(r'^$',views.materials.view, name = 'view'),  # GET, POST
	 		url(r'^edit/$', views.materials.edit, name = 'edit'),  # GET, POST, DELETE
		    url(r'^download/$', views.materials.download, name = 'download'),  # GET

	 	]))

	 ], namespace = 'content', app_name = 'apps.fmfn')),

	# Tags
	url(r'^tags/(?P<tag_type>type|theme|language)/', include([

        url(r'^$', views.tags.tags, name = 'list'),  # GET
        url(r'^create/$', views.tags.tags, name = 'create', kwargs = { 'action': 'create' }),  # POST
        url(r'^(?P<tag_id>[\d]+)/edit/$', views.tags.tags, name = 'edit', kwargs = { 'action': 'edit' }), # POST
		url(r'^(?P<tag_id>[\d]+)/delete/$', views.tags.tags, name = 'delete', kwargs = { 'action': 'delete' })  # POST

    ], namespace = 'tags', app_name = 'fmfn')),

	# Account management
	url(r'^accounts/', include([

		url(r'^login/$', views.accounts.login, name = 'login'),  # GET, POST
		url(r'^logout/$', views.accounts.logout, name = 'logout'),  # GET
		url(r'^recover/', include([

			url(r'^$', views.accounts.recover, name = 'recover', kwargs = { 'stage': 'recover' }),  # GET, POST
			url(r'^reset/(?P<user_id>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.accounts.recover, name = 'reset', kwargs = { 'stage': 'reset' })  # GET, POST

		]))

	], namespace = 'accounts', app_name = 'apps.fmfn')),
	
	# User management
	url(r'^users/', include([

	 	url(r'^$', views.users.search, name = 'list'),  # GET
	 	url(r'^api/$', views.users.search, name = 'filter'),  # POST
		url(r'^create/$', views.users.create, name = 'create'),  # GET, POST
	 	url(r'^(?P<user_id>[\d]+)/', include([

	 		url(r'^$',  views.users.view, name = 'view'),  # GET, POST
	 		url(r'^edit/$', views.users.edit, name = 'edit')  # GET, POST, DELETE

		]))

	], namespace = 'users', app_name = 'apps.fmfn')),

	# Portfolio (favorites) management
	url(r'^portfolio/', include([

		url(r'^$', views.portfolio.manage, name = 'view'),  # GET
		url(r'^(?P<content_id>[\d]+)/$', views.portfolio.manage, name = 'edit')  # PUT, DELETE

	], namespace = 'portfolio', app_name = 'fmfn')),

	# Management
	url(r'^manage/', include([

		url(r'^statistics/', include([

			url(r'^$', views.reporting.select, name = 'reporting'),  # GET
			url(r'^content/$', views.reporting.materials, name = 'content'),  # GET
			url(r'^users/$', views.reporting.users, name = 'users'),  # GET
			url(r'^comments/$', views.reporting.comments, name = 'comments')  # GET

		])),
		url(r'^reports/', include([

			url(r'^$', views.reports.reports, name = 'list'),  # GET
			url(r'^create/(?P<content_id>[\d]+)/$', views.reports.reports, name = 'create'),  # POST
			url(r'^(?P<report_id>[\d]+)/$', views.reports.reports, name = 'manage')  # PATCH, DELETE

		]))

	], namespace = 'management', app_name = 'apps.fmfn')),

	# Added here as they seem to require their own namespace
	url(r'^manage/advanced/', include(admin.site.urls)),
	url(r'^manage/grappelli/', include(grapelli_urls))

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
