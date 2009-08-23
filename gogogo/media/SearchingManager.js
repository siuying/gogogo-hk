/** Map Items Searching Manager
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

	var manager = this;
			
	GEvent.addListener(map, "moveend", function(){
		if (manager.autoRefresh 
			&& manager.map.getZoom() >= manager.minZoom) {
			
			/// @TODO - Fix for user who own an extremely large monitor?
			var prefix = hashBounds(manager.map.getBounds(), 6);
			
			for (var i = 0 ; i < prefix.length ;i++) {
			    if (manager.geohash_prefix_list[prefix[i]] == undefined){
			        manager.geohash_prefix_list[prefix[i]] = true;
			        manager.search(prefix[i]);
                }
            }
			
			/*
			
			var bounds = manager.getBounds();
			
			if (!bounds.equals(manager.lastBounds)){
				manager.refresh(bounds);	
				manager.lastBounds = bounds;
			}
			*/
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
