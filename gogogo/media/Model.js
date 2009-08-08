
/** Model class 
 * 
 * Based class of all model object from gogogo server.
 * 
 * @constructor 
 * 
 * Signals:
 * 
 * 	complete - The query is completed.
 */

gogogo.Model = function(id){

	// The object contains complete information of the model object
	this.complete = false
	
	// TRUE if it is querying the complete information of the model object from server
	this.querying = false;
	
	/// Store the detailed information of the model.
	this.info = Object(); 
	
	// The ID of the stop
	this.id = id;
}

/**
 * Update from JSON
 */
gogogo.Model.prototype.updateFromJson = function(json){
	var trip = this;
	
	for (attr in json){
		this.info[attr] = json[attr];
	}
	
}

/**
 * Query the complete information from server
 * 
 * @param callback The callback function to be involved after the operation. (It is invalid only in the first query)
 * 
 */

gogogo.Model.prototype.query = function(callback) {
	if (this.querying)
		return;
	
	this.querying = true;
	
	api = "/api/" + this.modelType + "/get/" + this.id;
	var cache = jQuery.ajaxSettings.cache;
	jQuery.ajaxSettings.cache = true; // Prevent the "_" parameter
	
	var	model = this;
	
	$.getJSON(api, null , function(response) {	
		if (response.stat == "ok"){
			
			model.updateFromJson(response.data);
			model.complete = true;
			
			$(model).trigger("complete",response);
		}
		
		if (callback!=undefined)
			callback(model,response);
		
		model.querying = false;
	});
	jQuery.ajaxSettings.cache = cache;	
}
