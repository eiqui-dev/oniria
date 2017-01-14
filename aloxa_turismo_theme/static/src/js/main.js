openerp.website.if_dom_contains('.menu-orderby', function(){
	
	$(document).on('click','.menu-orderby', function(e){
		$("#form-filters input[name='orderby']").val($(this).data('value'));
		$("#form-filters").submit();
	});
	
	$(document).on('click','#view-grid', function(e){
		openerp.jsonRpc('/_set_directory_view/grid', 'call', '').then(function(data){
			if (!data['error'])
			{		
				window.location.reload();
			}
		});
	});
	$(document).on('click','#view-list', function(e){
		openerp.jsonRpc('/_set_directory_view/list', 'call', '').then(function(data){
			if (!data['error'])
			{		
				window.location.reload();
			}
		});
	});
	$(document).on('click','#view-map', function(e){
		openerp.jsonRpc('/_set_directory_view/map', 'call', '').then(function(data){
			if (!data['error'])
			{		
				window.location.reload();
			}
		});
	});
	
});

var $DIRECTORY_MAP=0;
openerp.website.if_dom_contains('#directory-map', function(){
	
    var mapCanvas = document.getElementById('directory-map');
    var mapOptions = {
    	center: new google.maps.LatLng('40.0','-3.5'),
      	zoom: 6,
      	mapTypeControlOptions: {
	      mapTypeIds: [
	        google.maps.MapTypeId.ROADMAP,
	        google.maps.MapTypeId.SATELLITE
	      ],
	      position: google.maps.ControlPosition.BOTTOM_LEFT
	    }
    }
    $DIRECTORY_MAP = new google.maps.Map(mapCanvas, mapOptions);
	
    for (var i=0; i<$DIRECTORY_ADDRESS.length; i+=2)
    	add_address_to_directory_map($DIRECTORY_ADDRESS[i], $DIRECTORY_ADDRESS[i+1])
});

function add_address_to_directory_map(address, url) {
	if ($DIRECTORY_MAP == 0)
		return;
	
	var geocoder = new google.maps.Geocoder();
	geocoder.geocode({'address': address}, function(results, status) {
		if (status === google.maps.GeocoderStatus.OK) {
	    	var marker = new google.maps.Marker({
	    		map: $DIRECTORY_MAP,
	        	position: results[0].geometry.location,
				animation: google.maps.Animation.DROP,
				icon: '/aloxa_turismo_theme/static/src/img/marker-establecimiento.png',
	      	});
			marker.addListener('click', function() {
				window.location.href = url;
			});
	    } else {
	    	console.log('Geocode was not successful for the following reason: ' + status);
	    }
	});
}