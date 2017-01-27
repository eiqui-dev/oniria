"use strict;"
openerp.website.if_dom_contains('.menu-orderby', function(){
	
	$(document).on('click','.menu-orderby', function(e){
		$("#form-filters input[name='orderby']").val($(this).data('value'));
		$("#form-filters").submit();
	});
	
	$(document).on('click','#view-form', function(e){
		openerp.jsonRpc('/_set_directory_view/form', 'call', '').then(function(data){
			if (!data['error'])
			{
				window.location.href = '/establecimiento/'+data['slug']+'?sri=0';
			}
		});
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

openerp.website.if_dom_contains('.open-map-image', function(){
	$(document).on('click','.open-map-image',function(ev){
		var address = $(this).data('address');
		$("#map-viewer img").attr("src", get_google_map_image_url(address, 565, 388, address, 16));
		ev.preventDefault();
	});
});

/** PANEL: ESTABLECIMIENTOS **/
openerp.website.if_dom_contains('.crear-link-est', function(){
	$(document).on('click', '.crear-link-est', function(ev){
		var $this = $(this);
		$('form#create_link #est_id').val($this.data('id'));
		$('form#create_link #prod_id').val('');
		$('#modalNewLink').modal('show');
		ev.preventDefault();
	});
	
	// DATE TIME PICKERS
	var DTPickerOptions = {
		'locale': 'es',
	    'firstDayOfWeek': 1,
	    'changeMonth': true,
	    'changeYear': true,
	    'futureOnly': true,
	};
	
	$('#modalNewLink #date_start').appendDtpicker($.extend({}, DTPickerOptions, { 'minDate': moment().utc() }));
	$('#modalNewLink #date_end').appendDtpicker(DTPickerOptions);
});
openerp.website.if_dom_contains('.anhadir-producto', function(){
	$(document).on('click', '.anhadir-producto', function(ev){
		var $this = $(this);
		$('form#add_product #est_id').val($this.data('id'));
		$('#modalAddProduct').modal('show');
		ev.preventDefault();
	});
	
});
openerp.website.if_dom_contains('.anhadir-imagen', function(){
	$(document).on('click', '.anhadir-imagen', function(ev){
		var $this = $(this);
		$('form#add_image #est_id').val($this.data('id'));
		$('#modalAddImage').modal('show');
		ev.preventDefault();
	});
	
});
openerp.website.if_dom_contains('.create-ticket', function(){
	$(document).on('click', '.create-ticket', function(ev){
		var $this = $(this);
		$('form#create_ticket #event_id').val($this.data('id'));
		$('#modalNewTicket').modal('show');
		ev.preventDefault();
	});
	
	// DATE TIME PICKERS
	var DTPickerOptions = {
		'locale': 'es',
	    'firstDayOfWeek': 1,
	    'changeMonth': true,
	    'changeYear': true,
	    'futureOnly': true,
	};
	
	$('#modalNewTicket #deadline').appendDtpicker(DTPickerOptions);
});

/** PANEL: PRODUCTOS **/
openerp.website.if_dom_contains('.crear-link-prod', function(){
	$(document).on('click', '.crear-link-prod', function(ev){
		var $this = $(this);
		$('form#create_link #prod_id').val($this.data('id'));
		$('form#create_link #est_id').val('');
		$('#modalNewLink').modal('show');
		ev.preventDefault();
	});
	
	// DATE TIME PICKERS
	var DTPickerOptions = {
		'locale': 'es',
	    'firstDayOfWeek': 1,
	    'changeMonth': true,
	    'changeYear': true,
	    'futureOnly': true,
	};
	
	$('#modalNewLink #date_start').appendDtpicker($.extend({}, DTPickerOptions, { 'minDate': moment().utc() }));
	$('#modalNewLink #date_end').appendDtpicker(DTPickerOptions);
});


/** PANTALLA: CREAR EVENTO **/
openerp.website.if_dom_contains('#crear_evento_container', function(){
	// DATE TIME PICKERS
	var DTPickerOptions = {
		'locale': 'es',
	    'firstDayOfWeek': 1,
	    'changeMonth': true,
	    'changeYear': true,
	    'futureOnly': true,
	};
	
	$('#date_begin').appendDtpicker($.extend({}, DTPickerOptions, { 'minDate': moment().utc() }));
	$('#date_end').appendDtpicker(DTPickerOptions);
});

/** CREAR NUEVO PRODUCTO **/
openerp.website.if_dom_contains('#crear_producto_container', function(){
	$(document).on('change','#type', function(ev){
		refresh_create_product_form();
	});
	
	function refresh_create_product_form()
	{
		var $type = $('#type');
		if ($type.val() == 'vino' || $type.val() == 'vinagre')
		{
			$('#panel-right').removeClass('col-md-8').addClass('col-md-4');
			$('#panel-middle').show('slow');
			$('#subtipo').prop('required', true);
			$('#uva').prop('required', true);
			$('#anhada').prop('required', true);
			$('#bodega').prop('required', true);
		}
		else
		{
			$('#panel-right').removeClass('col-md-4').addClass('col-md-8');
			$('#panel-middle').hide('normal');
			$('#subtipo').prop('required', false);
			$('#uva').prop('required', false);
			$('#anhada').prop('required', false);
			$('#bodega').prop('required', false);
		}
	}
	
	refresh_create_product_form();
});

/** SOLICITUD BANNER **/
var $PREVIEW_BANNER_URI = '';
var $BANNER_TYPE = {size:'S', position:'Portada'};
openerp.website.if_dom_contains('#formnewbanner', function(){
	$(document).on('change','#fileimage',function(){
	    readURL(this);
	});
	
	$(document).on('change','#solicitud_link_container select',function(){
		refresh_create_link_page();
	});
	
	$(document).on('change', '#solicitud_link_container input', function(){
		refresh_create_link_page();
	})
	$(document).on('keyup', "#solicitud_link_container input[type='text']", function(){
		refresh_create_link_page();
	})
	
	refresh_create_link_page();
	
	/*var url = window.location.hostname === 'blueimp.github.io' ?
            '//jquery-file-upload.appspot.com/' : 'server/php/';
	$('#fileupload').fileupload({
	    url: url,
	    dataType: 'json',
	    done: function (e, data) {
	        $.each(data.result.files, function (index, file) {
	            $('<p/>').text(file.name).appendTo('#files');
	        });
	    },
	    progressall: function (e, data) {
	        var progress = parseInt(data.loaded / data.total * 100, 10);
	        $('#progress .progress-bar').css(
	            'width',
	            progress + '%'
	        );
	    }
	}).prop('disabled', !$.support.fileInput)
	    .parent().addClass($.support.fileInput ? undefined : 'disabled');*/
});

function refresh_create_link_page()
{
	// Formulario
	var $typesel = $('#typelink');
	var $option = $($typesel[0].options[$typesel[0].selectedIndex]);
	$BANNER_TYPE.size = $option.data('size');
	$BANNER_TYPE.position = $option.data('position');
	
	if ("Portada" === $BANNER_TYPE.position)
	{
		$('#linkaction').hide();
		$('#linkaction').prop('disabled', true);
		$('#linkurl').show();
		$('#panel-middle').hide('normal');
	}
	else if ("Directorio" === $BANNER_TYPE.position)
	{
		var selIndex = $('#linkaction')[0].selectedIndex+1;
		var html = "<option value='product'>Producto</option>"+
						"<option value='establishment'>Establecimiento</option>";
		$('#linkaction').html(html);
		$('#linkaction').show();
		$('#linkaction').prop('disabled', false);
		$("#linkaction :nth-child("+selIndex+")").prop('selected', true);
		$('#linkurl').hide();
		$('#panel-middle').show('slow');
	}
	
	// Crear Producto o Establecimimiento
	var action = $('#linkaction').val();
	if (action == 'product')
	{
		$('#formnewestablishment').hide();
		$('#formnewproduct').show('');
	}
	else if (action == 'establishment')
	{
		$('#formnewestablishment').show();
		$('#formnewproduct').hide('');
	}
	
	// Preview
	if ("Portada" === $BANNER_TYPE.position)
	{
		var cols = {'S':[6,1], 'M': [8,2], 'L':[12,4]};
		var spaces = cols[$BANNER_TYPE.size];
		var banner_url = '#';
		if ($('#linkurl input').val())
			banner_url = 'http://'+$('#linkurl input').val();

		var html = "<div id='preview_container'><a target='_blank' href='"+banner_url+"'>"+
				"<img class='img img-responsive' alt='Preview' src='"+$PREVIEW_BANNER_URI+"' /></a></div>";
		$('#bannerpreview').html(html);
		$('#preview_container').addClass('col-md-'+spaces[0]);
		$('#preview_container').addClass('oe-height-'+spaces[1]);
	}
	else if ("Directorio" === $BANNER_TYPE.position)
	{
		var banner_name = "";
		if (action == 'product')
			banner_name = $('#product_name input').val()
		else if (action == 'establishment')
			banner_name = $('#establishment_name input').val()
			
		var html = "<div class='product'>"+
		"<div class='product-img'>"+	
		"<a class='product-image' title='' href='#'>"+
		"<img class='img img-responsive' alt='Preview' src='"+$PREVIEW_BANNER_URI+"' />"+
		"</a>"+
		"</div>"+
		"<div class='pro-info'>"+
		"<div class='title'>"+
		"<a itemprop='name' href='#'></a>"+												
		"</div>"+
		"</div>";
		$('#bannerpreview').html(html);
		$("#bannerpreview a[itemprop='name']").text(banner_name);
		$('#bannerpreview img').removeClass('col-md-3');
	}
}

function readURL(input)
{
    if (input.files && input.files[0])
    {
        var reader = new FileReader();

        reader.onload = function(e){
        	$PREVIEW_BANNER_URI = e.target.result;
        	refresh_create_link_page();
        }

        reader.readAsDataURL(input.files[0]);
    }
}


/** DETALLE ESTABLECIMIENTO **/
function initializeGMapsEstablecimiento(lat, long, address) {
    var $mapCanvas = $('#map_est');
    var sitePos = new google.maps.LatLng(lat, long);
    var mapOptions = {
    	center: sitePos,
      	zoom: 18,
      	mapTypeControlOptions: {
	      mapTypeIds: [
	        google.maps.MapTypeId.ROADMAP,
	        google.maps.MapTypeId.SATELLITE
	      ],
	      position: google.maps.ControlPosition.BOTTOM_LEFT
	    }
    }
	var map = new google.maps.Map($mapCanvas[0], mapOptions);
					    
	var geocoder = new google.maps.Geocoder();
	geocoder.geocode({'address': address}, function(results, status) {
		if (status === google.maps.GeocoderStatus.OK) {
			var center = results[0].geometry.location;
	    	map.setCenter(center);
	    	var marker = new google.maps.Marker({
	    		map: map,
	        	position: results[0].geometry.location,
				animation: google.maps.Animation.DROP,
	      	});
	    	var resizeEvent = new Event('resize');
	    	window.dispatchEvent(resizeEvent);
	    } else {
	    	console.log('Geocode was not successful for the following reason: ' + status);
	    }
	});
}
/** FIN: DETALLE ESTABLECIMIENTO **/

/** RUTAS **/
function calculateAndDisplayRoute(directionsService, directionsDisplay, orig, dest, waypts)
{
	directionsService.route({
		origin: orig,
		destination: dest,
		waypoints: waypts,
		travelMode: 'DRIVING'
	}, function(response, status){
		if (status == 'OK')
			directionsDisplay.setDirections(response);
		else
			window.alert('La petición al servicio \'Directions\' ha fallado por '+status);
	});
}

var gDirectionsService = null;
var gDirectionsDisplay = null;
var gDest = null;
var gWayPoints = null;
var gWPID = 0;
function initializeGMapsRutas(addressOrig, addressDest, waypts) {
    var $mapCanvas = $('#map');
    gDirectionsService = new google.maps.DirectionsService;
    gDirectionsDisplay = new google.maps.DirectionsRenderer;
    var sitePos = new google.maps.LatLng(0, 0);
    var mapOptions = {
    	center: sitePos,
      	zoom: 18,
      	mapTypeControlOptions: {
	      mapTypeIds: [
	        google.maps.MapTypeId.ROADMAP,
	        google.maps.MapTypeId.SATELLITE
	      ],
	      position: google.maps.ControlPosition.BOTTOM_LEFT
	    }
    }

    google.maps.controlStyle = 'azteca';
	var map = new google.maps.Map($mapCanvas[0], mapOptions);
	gDirectionsDisplay.setMap(map);
    
    var waypoints = [];
    for (var i in waypts)
    {
    	waypoints.push({
    		'location': waypts[i],
    		stopover: true
    	});
    }
    
    gDest = addressDest;
    gWayPoints = waypoints;
    calculateAndDisplayRoute(gDirectionsService, gDirectionsDisplay, addressOrig, gDest, gWayPoints);
}

function geo_success(geoPos)
{
	$('#geoInfo').text("Pos Actual: "+geoPos.coords.latitude+","+geoPos.coords.longitude);
	var googlePos = new google.maps.LatLng(geoPos.coords.latitude, geoPos.coords.longitude);
	calculateAndDisplayRoute(gDirectionsService, gDirectionsDisplay, googlePos, gDest, gWayPoints);
}
function geo_error(error)
{
	var errorType = [
	  "Unknown Error",
	  "Permission denied by the user",
	  "Position of the user not available",
	  "Request timed out"
	];
	
	var errMsg = errorType[error.code];
	if (error.code == 0 || error.code == 2)
		errMsg += " - "+error.message;
	
	$('#geoInfo').text(errMsg);
}

openerp.website.if_dom_contains('#geoLocation', function(){
	var geo_options = {
		enableHighAccuracy: true, 
		maximumAge: 30000, 
		timeout: 27000
	};
	
	if ("geolocation" in navigator)
		gWPID = navigator.geolocation.watchPosition(geo_success, geo_error, geo_options);
	else
		$('#geoInfo').text("HTML5 Not Supported");
});
/** FIN: RUTAS **/


/** VISTA MAPA **/
var $DIRECTORY_MAP=0;
var $MARKER_CLUSTER=false;
openerp.website.if_dom_contains('#directory-map', function(){
	
    var mapCanvas = document.getElementById('directory-map');
    var mapOptions = {
    	center: new google.maps.LatLng('43.3435742','-4.0637602'),
      	zoom: 10,
      	mapTypeControlOptions: {
	      mapTypeIds: [
	        google.maps.MapTypeId.ROADMAP,
	        google.maps.MapTypeId.SATELLITE
	      ],
	      position: google.maps.ControlPosition.BOTTOM_LEFT
	    }
    };
    $DIRECTORY_MAP = new google.maps.Map(mapCanvas, mapOptions);
	
    // Define Marker Clusterer
    $MARKER_CLUSTER = new MarkerClusterer($DIRECTORY_MAP, [],
            {imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'});
    // Put markers
    for (var i=0; i<$DIRECTORY_ADDRESS.length; i+=2)
    	add_address_to_directory_map($DIRECTORY_ADDRESS[i], $DIRECTORY_ADDRESS[i+1]);
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
			$MARKER_CLUSTER.addMarker(marker);
			
			// Center camera on markers
			var markers = $MARKER_CLUSTER.getMarkers();
			var bounds = new google.maps.LatLngBounds();
			markers.forEach(function(item, index){ bounds.extend(item.getPosition()); });
			$DIRECTORY_MAP.fitBounds(bounds);
	    } else {
	    	console.log('Geocode was not successful for the following reason: ' + status);
	    }
	});
}

function get_google_map_image_url(address, w, h, center, zoom)
{
	var url = "https://maps.google.com/maps/api/staticmap?";
	url += "center="+center;
	url += "&zoom="+zoom+"&size="+w+"x"+h+"&maptype=roadmap&markers=color:red|label:A|";
	url += address+"&sensor=false";
	
	return url;
}