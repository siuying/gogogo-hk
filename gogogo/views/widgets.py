from google.appengine.ext import db

from django.core.urlresolvers import reverse
from django import forms
from django.forms.widgets import Input
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.utils.encoding import StrAndUnicode, force_unicode
from django.template import Context, loader , RequestContext
from django.conf import settings

from gogogo.models.cache import getCachedObjectOr404
from gogogo.models.utils import id_or_name
from gogogo.models import Stop
import cgi

class Pathbar:
	"""
	Create a path bar
	
	Template: gogogo/widgets/pathbar.html
	"""
	def __init__(self,sep=">"):
		self.path = []
		self.sep = sep
		
	def append(self,name,viewname,args):
		url = reverse(viewname,args=args)
		self.path.append((name , url ))

		
class ReferenceLinkWidget(Input):
	"""
	Render the link to a database object(Use with ReferenceLinkField)
	"""
	
	input_type = 'hidden'
	
	def render(self, name, value, attrs=None):
		
		input = super(ReferenceLinkWidget, self).render(name, value, attrs)	
		
		ret = ""
		if value is not None:
			object = getCachedObjectOr404(key = value)
			ret = mark_safe(input + "<a href='%s'>%s</a>" % (object.get_absolute_url() , unicode(object) ))
		
		return ret

class ReferenceLinkField(forms.Field):	
	"""
	A read-only field with a link to the target of reporting object
	"""

	def __init__(self,  *args, **kwargs):
		
		if 'widget' not in kwargs:
			kwargs.update( { 'widget' : ReferenceLinkWidget() })
				
		super(ReferenceLinkField, self).__init__(*args, **kwargs)

		
	def clean(self,value):
		
		value = super(ReferenceLinkField, self).clean(value)
		if not value:
			return None
		instance = db.get(value)
		if instance is None:
			raise db.BadValueError(self.error_messages['invalid_choice'])
		return instance

class LatLngInputWidget(forms.Widget):	
    def __init__(self, attrs=None):
        super(LatLngInputWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if value is None: value = "%s,%s" % (settings.GOGOGO_DEFAULT_LOCATION[0],settings.GOGOGO_DEFAULT_LOCATION[1])
        
        final_attrs = self.build_attrs(attrs, name=name)
        if value != '':
            final_attrs['value'] = force_unicode(value)
        
        t = loader.get_template('gogogo/widgets/latlnginputwidget.html')	
        c = Context({
            'final_attrs': mark_safe(flatatt(final_attrs)),
            'value' : value,
            'id' : final_attrs['id'],
            'map_id' : "map_%s" % final_attrs['id'],
            'model_manager' : "model_manager_%s" % final_attrs['id'],
            'cluster_manager' : "cluster_manager_%s" % final_attrs['id'],
            'marker_id' : "marker_%s" % final_attrs['id']
        })
            
        return mark_safe(	t.render(c) )

class StopListEditor(forms.Widget):
    """
    Stop list editor
    """

    def render(self, name, value, attrs=None):
        if value is None: value = "%s,%s" % (settings.GOGOGO_DEFAULT_LOCATION[0],settings.GOGOGO_DEFAULT_LOCATION[1])
        
        final_attrs = self.build_attrs(attrs, name=name)
        if value != '':
            final_attrs['value'] = force_unicode(self._gen_value(value))
        
        t = loader.get_template('gogogo/widgets/stoplisteditor.html')	
        c = Context({
            'final_attrs': mark_safe(flatatt(final_attrs)),
            'value' : value,
            'id' : final_attrs['id'],
            'map_id' : "map_%s" % final_attrs['id'],
            'sortable_id' : "sortable_%s" % final_attrs['id'],
            'model_manager' : "model_manager_%s" % final_attrs['id'],
            'cluster_manager' : "cluster_manager_%s" % final_attrs['id'],
            'marker_id' : "marker_%s" % final_attrs['id']
        })
            
        return mark_safe(	t.render(c) )
    
    def _gen_value(self,value):
        
        return ",".join([str(v.id_or_name()) for v in value])
        
class StopListField(forms.Field):

    def __init__(self,  *args, **kwargs):
        
        if 'widget' not in kwargs:
            kwargs.update( { 'widget' : StopListEditor() })
                
        super(StopListField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if self.required and not value:
            raise ValidationError(gettext(u'This field is required.'))
        elif not self.required and not value:
            return []
        if isinstance(value,basestring):
            value = value.split(",")
            
        if not isinstance(value, (list, tuple)):
            raise ValidationError(gettext(u'Enter a list of values.'))
        
        final_values = []
        for val in value:
            key = db.Key.from_path(Stop.kind(),id_or_name(val))
            final_values.append(key)
        return final_values
