# Create your views here.

from django.http import HttpResponse
from django.http import Http404
from django.template import Context, loader
from django.conf import settings

from django.utils import simplejson
from StringIO import StringIO

from gogogo.models import *
from gogogo.geo.geohash import Geohash
#import json

def default(o):
	"""
	``default(obj)`` is a function that should return a serializable version
    of obj or raise TypeError for JSON generation
    """

	if isinstance(o,db.GeoPt):
		return (o.lat,o.lon)
	elif isinstance(o,db.Key):
		return o.name()
	else:
		raise TypeError("%r is not JSON serializable" % (o,))

class ApiResponse(HttpResponse):	
	"""
		Standard response of Gogogo API 
	"""
	def __init__ (self , data=None,error=None):
		
		if error:
			self.stat = "fail"
		else:
			self.stat = "ok"
			
		self.data = data
		self.error = error
		text = self.to_json()
		
		HttpResponse.__init__(self,text)
	
	def to_json(self):
		text = StringIO()
		
		if self.stat == "ok":
			fields = {'stat' : self.stat , 'data' : self.data }
		else:
			fields = {'stat' : self.stat , 'error' : self.error }
		
		simplejson.dump(fields,text,default=default,ensure_ascii=False)
		
		return text.getvalue()


def agency_list(request):
	"""
	Handle api/agency/list
	"""
	query = Agency.all()
	text = StringIO()
	
	result = []
	for agency in query:
		result.append(create_entity(agency,request))
	
	return ApiResponse(data=result)

def stop_search(request,lat0,lng0,lat1,lng1):
	"""
		Search stop (api/stop/search)
	"""
	lat0 = float(lat0)
	lng0 = float(lng0)
	lat1 = float(lat1)
	lng1 = float(lng1)
	
	if lat0 < lat1:
		minlat = lat0
		maxlat = lat1
	else:
		minlat = lat1
		maxlat = lat0
	
	if lng0 < lng1:
		minlng = lng0
		maxlng = lng1
	else:
		minlng = lng1
		maxlng = lng0
		
	#TODO: Check the distance. Prevent to dump the database that will spend too much bandwidth
	hash0 = str(Geohash( (minlng,minlat) ))
	hash1 = str(Geohash( (maxlng,maxlat) ))

	result = []
	
	lang = MLStringProperty.get_current_lang(request)	
	
	query = Stop.all().filter("geohash >=" , hash0).filter("geohash <=" , hash1)
	
	for stop in query:
		#TODO: Check again for real lat/lng value
		entity = {
			"id" : stop.key().name(),
			"name" : MLStringProperty.trans(stop.name,lang),
			"url" : stop.url,
			"latlang" : stop.latlng,
			"agency" : stop.agency,
		}
		result.append(entity)
	
	return ApiResponse(data=result)

def shape_get(request,id):
	key = db.Key.from_path(Shape.kind(),id)
	
	object = db.get(key)
	
	if object:
		return ApiResponse(data=create_entity(object,request))
	else:
		return ApiResponse(error="Shape not found")