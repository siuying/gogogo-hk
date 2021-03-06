
/** MQuery - Query multi-models by using mget in the same time
 * 
 * @constructor 
 */

gogogo.MQuery = function(model){
    this.model = model;
    this.id_list = [];
}

/** Push an ID to the query list
 * 
 */

gogogo.MQuery.prototype.push = function(id){
    this.id_list.push(id);
}

/** Concat an ID list
 * 
 */

gogogo.MQuery.prototype.concat = function(list){
    this.id_list = this.id_list.concat(list);
}

/** Query
 * 
 * @param dict A dictionary of the object table. If the query object is not existed in the table , it will be added automatically.
 * 
 */

gogogo.MQuery.prototype.query = function(dict,callback){
    var mquery = this;
    var ids = [];
    var total = this.id_list.length;
    var count = 0;
    
    var done = function() {
        if (callback) {
            var result = [];
            
            $.each(mquery.id_list,function(i,id){
                result.push(dict[id]);
            });
        
            callback(result);
        }
    }
    
    var counter = function(num){
        count+=num;
        if (count == total){
            done();
        }
    }
    
    counter(0);
    
    $.each(this.id_list,function(i,id){
        var object = dict[id];
        if (object==undefined){
            object = new mquery.model(id);
            dict[id] = object;
        }
        
        if (!object.complete){
            if( !object.querying) {
                ids.push(id);
                object.block();
            } else {
                object.query(function(){
                    counter(1);
                });
            }
        } else {
            counter(1);
        }
    });
    
    if (ids.length == 0) {
        counter(0);
    } else {
        this._query(ids,dict,function(num){
            counter(num);
        });
                
    }
    
}

/** For recursive query 
 * 
 */

gogogo.MQuery.prototype._query = function(ids,dict,callback){
    var ids_string = ids.join(",");
    if (ids_string.length > 1800 ) {
        var m = ids.length / 2;
        this._query(ids.slice(0,m) , dict, callback );
        this._query(ids.slice(m) , dict , callback);
        return;
    }
    
    var model = new mquery.model();
                   
    var api = "/api/" + model.modelType + "/mget?ids=" + ids_string;
    var cache = jQuery.ajaxSettings.cache;
    jQuery.ajaxSettings.cache = true; // Prevent the "_" parameter
    
    $.getJSON(api, null , function(response) {	
        if (response.stat == "ok"){
            $.each(response.data,function(i,item) {
                var object = dict[item.id];
                object.updateFromJson(item,true);
                object.unblock();
            });
        }
        
        callback(ids.length);
        
    });
    jQuery.ajaxSettings.cache = cache;	            
}

