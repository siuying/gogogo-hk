from gogogo.models import *
from ragendja.auth.decorators import staff_only
from ragendja.dbutils import get_object_or_404
from django import forms
from django.forms import ModelForm
from ragendja.template import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse as _reverse
from gogogo.models.utils import createEntity , entityToText
from gogogo.models.cache import updateCachedObject
from datetime import datetime
from gogogo.models import TitledStringListField
from gogogo.models.MLStringProperty import MLStringProperty , to_key_name
from gogogo.models.utils import id_or_name
from gogogo.views.widgets import LatLngInputWidget
from gogogo.models.forms import AgencyForm , StopForm , TripForm , RouteForm , FareTripForm
from gogogo.models.changelog import createChangelog

import logging

_supported_model = {
	'route' : (Route,RouteForm),
	'agency' : (Agency,AgencyForm),
	'trip' : (Trip,TripForm),
	'stop': (Stop,StopForm),
    'faretrip' : (FareTrip,FareTripForm),
}

def next_key_name(model_class,key_name):
    """
    Get the next available key
    """
    if key_name == None:
        return key_name # Use numeric key
    
    entity = model_class.get(db.Key.from_path(model_class.kind() , key_name))

    if not entity:
        return key_name
    else:
        count = 0
        while True:
            count += 1
            new_key_name = key_name + "-" + str(count)
            entity = model_class.get(db.Key.from_path(model_class.kind() , new_key_name))
            if not entity:
                return new_key_name 

def _getModelInfo(kind):
    return _supported_model[kind]

def _createModel(kind,parent = None):
    value = id_or_name(parent)
    key_name = None
    if kind == "route":
        agency = None
                
        if parent:
            agency = db.Key.from_path(Agency.kind() , value)
            
        return Route(key_name = key_name,agency = agency)
    elif kind == "agency":
            
        return Agency(key_name = key_name)
    elif kind == "trip":
        route = None
        
        if parent:
            route = db.Key.from_path(Route.kind() , value)
        
        return Trip(route = route , key_name = key_name)
    elif kind == "stop":
        return Stop()
    elif kind =="faretrip":
        trip = None
            
        if parent:
            trip = db.Key.from_path(Trip.kind(),value)
            
        return FareTrip(trip = trip , key_name = key_name)
        
    raise ValueError

def _createModelByForm(model,form):
    args = {"auto_set_key_name" : True}
    for prop in model.properties().values():
        if prop.name in form.cleaned_data:
            args[prop.name] = form.cleaned_data[prop.name]
    
    return model(**args)

@staff_only
def add(request,kind):
    """
    Add new entry to database
    """

    (model,model_form) = _getModelInfo(kind)

    if request.method == 'POST':
        form = model_form(request.POST)
        
        if form.is_valid():
            instance = _createModelByForm(model,form)
            form = model_form(request.POST,instance = instance)

            instance = form.save(commit=False)		
            
            instance.save()

            changelog = createChangelog(None,instance,form.cleaned_data['log_message'])

            changelog.save()
            
            return HttpResponseRedirect(instance.get_absolute_url())
    elif request.method == 'GET':
        parent = None
        if "parent" in request.GET:
            parent = request.GET['parent']
        instance = _createModel(kind,parent)
        form = model_form(instance=instance)
        
    else:
        form = model_form()
        
    message = ""

    return render_to_response( 
        request,
        'gogogo/db/edit.html'
        ,{ "form" : form , 
           "kind" : kind,
           "message" : message,
           "history_link" : _reverse('gogogo.views.db.changelog.list') + "?kind=%s" % kind,
           "action" : _reverse('gogogo.views.db.add',args=[kind]) ,
           })		


@staff_only
def edit(request,kind,object_id):
    """
    Edit model
    """

    (model,model_form) = _getModelInfo(kind)

    message = ""

    id = None
    key_name = None
    try:
        id = int(object_id)
    except ValueError:
        key_name = object_id

    object = get_object_or_404(model,key_name = key_name , id=id)

    if request.method == 'POST':
        form = model_form(request.POST,instance=object)
        if form.is_valid():
            
            #Old object was changed by the from, so it need to get a new copy
            object = get_object_or_404(model,key_name = key_name , id=id)
            new_object = form.save(commit = False)
            
            changelog = createChangelog(object,new_object,form.cleaned_data['log_message'])
            if changelog:                
            
                db.put([new_object,changelog])
                updateCachedObject(new_object)
                #TODO - Update loader cache
                
                return HttpResponseRedirect(new_object.get_absolute_url())
            else:
                message = _("Nothing changed. The form will not be saved")

    else:
        form = model_form(instance=object)

    view_object_link = None
    if object : 
        view_object_link = object.get_absolute_url()
        
    return render_to_response( 
        request,
        'gogogo/db/edit.html'
        ,{ "form" : form , 
           "object" : object,
           "kind" : kind,
           "message" : message,
           "history_link" : _reverse('gogogo.views.db.changelog.list') + "?kind=%s" % kind,
           "view_object_link" : view_object_link,
           "action" : _reverse('gogogo.views.db.edit',args=[kind,object_id]) ,
           })		
