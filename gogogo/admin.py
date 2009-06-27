from django.contrib import admin
from django import forms
from ragendja.forms import *
from gogogo.models import *

class AgencyAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'url', 'timezone', 
            'phone',
            'icon'
            
            )
        }),

    )
    
    list_display = ('Agency_ID','Agency_Name','url')	
    
    search_fields = ('name',)
    
    def Agency_Name(self,obj):
    	return u' | '.join(obj.name)
    	
    def Agency_ID(self,obj):
    	#return obj.aid
    	return obj.key().name()

admin.site.register(Agency, AgencyAdmin)

class StopAdmin(admin.ModelAdmin):	
	fieldsets = (
        (None, {
            'fields': (
            	'code', 
            	'name',
            	'desc',
            	'latlng',
            	'geohash',
            	'url',
            	'location_type',
            	'parent_station',
            	'inaccuracy',
            	)
        }),
    )
    
	search_fields = ('name',)
	
	list_display = ('Stop_ID','Stop_Name',)
	
	def Stop_ID(self,obj):
		return obj.key().name()
	
	def Stop_Name(self,obj):
		return u' | '.join(obj.name)

admin.site.register(Stop, StopAdmin)

class RouteAdmin(admin.ModelAdmin):
	fieldsets = (
        (None, {
            'fields': (
     				'agency','short_name','long_name','desc','type','url','color','text_color'
            	)
        }),
    )	
	
admin.site.register(Route, RouteAdmin)

class TripAdmin(admin.ModelAdmin):
	list_display = ('Trip_ID',)	
	
	def Trip_ID(self,obj):
		return obj.key().name()
	
admin.site.register(Trip, TripAdmin)	

class ShapeAdmin(admin.ModelAdmin):
	list_display = ('Shape_ID',)	
	
	def Shape_ID(self,obj):
		return obj.key().name()
	
admin.site.register(Shape, ShapeAdmin)	

class ChangelogAdmin(admin.ModelAdmin):
	pass
	
admin.site.register(Changelog, ChangelogAdmin)	
