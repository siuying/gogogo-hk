/** Map Items Searching Manager
 * 
 * 
 * Signals:
 *  
 *  overlayAdded - Triggered when a list of overlays are added to map
 * 
 * 
 * All the subclass should implement the following functions:
 * 
 * _search(prefix,callback) - Search items in specific region. 
 * The result should be passed to callback, then SearchingManager
 * will store the result. And allow user to query by search()
 * 
 * _createOverlays(items) - Create overlay items and add to the map.
 * 
 * Argumemts:
 * items - A list of storage instance (Returned by _search() )
 * 
 * Return : A list of overlay objects
 * 
 * @constructor 
 */

gogogo.SearchingManager = function (map){
	this.map = map;
	
	/// The min zooming for searching 
	this.minZoom = 17;
	
	/// Auto refresh when the map is moved.
	this.autoRefresh = true;

    /// Deprecated
	this.lastBounds = new GLatLngBounds();
	
	/// Store previous queryed geohas prefix
	this.geohash_prefix_list = new Object();
	
	/// Store previous created GOverlay objects
	this.overlays = new Object();

	var manager = this;
			
	GEvent.addListener(map, "moveend", function(){
	     if (manager.autoRefresh 
		    && manager.map.getZoom() >= manager.minZoom) {
		    
		    /// @FIXME - Fix for user who own an extremely large monitor?
		    var prefix = hashBounds(manager.map.getBounds(), 6);
		    
            $(prefix).each( function(i,prefix){
                manager.search(prefix,function (result){
                    if (manager.overlays[prefix] == undefined
                        && manager._createOverlays != undefined
                        ) {
                          manager.overlays[prefix] = manager._createOverlays(result);
                          if (manager.overlays[prefix].length > 0){
                              $(manager).trigger("overlayAdded",manager.overlays[prefix]);
                          }
                          
                        }
                });		
    	    });
	    }
	});	
}

gogogo.SearchingManager.ceil = function(pt) {
	var f = 50;
	return new GLatLng( Math.ceil(pt.lat() * f ) / f , Math.ceil(pt.lng() * f ) / f )
}

gogogo.SearchingManager.floor = function(pt) {
	var f = 50;
	return new GLatLng( Math.floor(pt.lat() * f ) / f , Math.floor(pt.lng() * f ) / f )
}

/**
 *  Returns the truncated rectangular region of the map view in geographical coordinates.
 */

gogogo.SearchingManager.prototype.getBounds = function() {
	var bounds = this.map.getBounds();

	var sw1 = bounds.getSouthWest();
	var ne1 = bounds.getNorthEast();
	
	var sw2 = gogogo.SearchingManager.floor(sw1);
	var ne2 = gogogo.SearchingManager.ceil(ne1);

	return new GLatLngBounds(sw2,ne2);
}

/**
 * Search items in specific region. 
 * 
 * @param prefix The prefix of the region (geohash)
 * @param callback A callback function that will be involved for every element found in the region
 */

gogogo.SearchingManager.prototype.search = function(prefix,callback) {
        
    if (this.geohash_prefix_list[prefix] == undefined){
	    this.geohash_prefix_list[prefix] = [];
	    var geohash_prefix_list = this.geohash_prefix_list[prefix];
	    
		this._search(prefix,function(list) {
		   geohash_prefix_list = list;
		   if (callback)
                callback(list);
        });
    } else if (callback){
        callback(this.geohash_prefix_list[prefix]);
    }
}
