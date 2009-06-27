
from django.core.urlresolvers import reverse as _reverse
from gogogo.models import *

def reverse(object):
	"""
	Return the link to the object
	"""
	
	if isinstance(object,Agency):
		ret = _reverse('gogogo.views.transit.agency',args=[object.key().name()] )
	elif isinstance(object,Route):
		ret = _reverse('gogogo.views.transit.route',args=[object.agency.key().name(),object.key().name()] )
	else:
		raise ValueError("gogogo.views.db.reverse() do not support %s" % object.kind() )	

	return ret
