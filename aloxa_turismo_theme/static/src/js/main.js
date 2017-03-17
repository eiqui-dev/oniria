"use strict;"
openerp.website.if_dom_contains('.menu-orderby', function(){
	
	$(document).on('click','.menu-orderby', function(e){
		$("#form-filters input[name='orderby']").val($(this).data('value'));
		$("#form-filters").submit();
	});
	
	$(document).on('click','#view-form', function(e){
		var link_target = this.dataset.linkTarget;
		openerp.jsonRpc('/_set_directory_view/form', 'call', '').then(function(data){
			if (!data['error'])
			{
				var url = window.location.href.split('?');
				window.location.href = '/directorio/'+link_target+'s?'+(url[1] || '');
			}
		});
	});
	
	$(document).on('click','#view-grid', function(e){
		var link_target = this.dataset.linkTarget;
		openerp.jsonRpc('/_set_directory_view/grid', 'call', '').then(function(data){
			if (!data['error'])
			{		
				var url = window.location.href.split('?');
				window.location.href = '/directorio/'+link_target+'s?'+(url[1] || '');
			}
		});
	});
	$(document).on('click','#view-list', function(e){
		var link_target = this.dataset.linkTarget;
		openerp.jsonRpc('/_set_directory_view/list', 'call', '').then(function(data){
			if (!data['error'])
			{		
				var url = window.location.href.split('?');
				window.location.href = '/directorio/'+link_target+'s?'+(url[1] || '');
			}
		});
	});
	$(document).on('click','#view-map', function(e){
		var link_target = this.dataset.linkTarget;
		openerp.jsonRpc('/_set_directory_view/map', 'call', '').then(function(data){
			if (!data['error'])
			{		
				var url = window.location.href.split('?');
				window.location.href = '/directorio/'+link_target+'s?'+(url[1] || '');
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

/** PANEL: establishmentS **/
openerp.website.if_dom_contains('.crear-link-est', function(){
	$(document).on('click', '.crear-link-est', function(ev){
		var $this = $(this);
		$('form#create_link #est_id').val($this.data('id'));
		$('form#create_link #prod_id').val('');
		$('#modalNewLink').modal('show');
		ev.preventDefault();
	});
	
	// DATE TIME PICKERS
	var DTPickerOptions = { };
	$('#modalNewLink #date_start').datetimepicker(DTPickerOptions);
	$('#modalNewLink #date_end').datetimepicker($.extend({}, DTPickerOptions, { 'useCurrent': false }));
	$("#modalNewLink #date_start").on("dp.change", function (e) {
        $('#modalNewLink #date_end').data("DateTimePicker").minDate(e.date);
    });
    $("#modalNewLink #date_end").on("dp.change", function (e) {
        $('#modalNewLink #date_start').data("DateTimePicker").maxDate(e.date);
    });
});
openerp.website.if_dom_contains('.anhadir-product', function(){
	$(document).on('click', '.anhadir-product', function(ev){
		var $this = $(this);
		$('form#add_product #est_id').val($this.data('id'));
		$('#modalAddProduct').modal('show');
		ev.preventDefault();
	});
	
});
openerp.website.if_dom_contains('.anhadir-image', function(){
	$(document).on('click', '.anhadir-image', function(ev){
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
	var DTPickerOptions = { };
	$('#modalNewTicket #deadline').datetimepicker(DTPickerOptions);
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
	var DTPickerOptions = { };
	$('#modalNewLink #date_start').datetimepicker(DTPickerOptions);
	$('#modalNewLink #date_end').datetimepicker($.extend({}, DTPickerOptions, { 'useCurrent': false }));
	$("#modalNewLink #date_start").on("dp.change", function (e) {
        $('#modalNewLink #date_end').data("DateTimePicker").minDate(e.date);
    });
    $("#modalNewLink #date_end").on("dp.change", function (e) {
        $('#modalNewLink #date_start').data("DateTimePicker").maxDate(e.date);
    });
});

/** PANTALLA: CREAR EVENTO **/
openerp.website.if_dom_contains('#crear_evento_container', function(){
	// DATE TIME PICKERS
	var DTPickerOptions = { };
	$('#date_begin').datetimepicker(DTPickerOptions);
	$('#date_end').datetimepicker($.extend({}, DTPickerOptions, { 'useCurrent': false }));
	$("#date_begin").on("dp.change", function (e) {
        $('#date_end').data("DateTimePicker").minDate(e.date);
    });
    $("#date_end").on("dp.change", function (e) {
        $('#date_begin').data("DateTimePicker").maxDate(e.date);
    });
});

/** CREAR NUEVO PRODUCTO **/
openerp.website.if_dom_contains('#crear_product_container', function(){
	$(document).on('change','#type', function(ev){
		refresh_create_product_form();
	});
	
	function refresh_create_product_form()
	{
		var $type = $('#type');
		if ($type.val() == 'wine' || $type.val() == 'vinagre')
		{
			$('#panel-right').removeClass('col-md-8').addClass('col-md-4');
			$('#panel-middle').show('slow');
			$('#subtype').prop('required', true);
			$('#grape').prop('required', true);
			$('#anhada').prop('required', true);
			$('#winecellar').prop('required', true);
		}
		else
		{
			$('#panel-right').removeClass('col-md-4').addClass('col-md-8');
			$('#panel-middle').hide('normal');
			$('#subtype').prop('required', false);
			$('#grape').prop('required', false);
			$('#anhada').prop('required', false);
			$('#winecellar').prop('required', false);
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
		var html = "<option value='product'>Product</option>"+
						"<option value='establishment'>establishment</option>";
		$('#linkaction').html(html);
		$('#linkaction').show();
		$('#linkaction').prop('disabled', false);
		$("#linkaction :nth-child("+selIndex+")").prop('selected', true);
		$('#linkurl').hide();
		$('#panel-middle').show('slow');
	}
	
	// Crear Product o Establecimimiento
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


/** DETALLE establishment **/
function initializeGMaps(querySelector, lat, long, address) {
    var mapCanvas = document.querySelector(querySelector) || false;
    if (!mapCanvas)
    	return;
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
	var map = new google.maps.Map(mapCanvas, mapOptions);
					    
    if (address) {
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
}
/** FIN: DETALLE establishment **/

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
			window.alert('La petición al service \'Directions\' ha fallado por '+status);
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
var $INFO_WINDOW=false;
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
    if ($NOT_SHOW_GOOGLE_POIS) {
    	mapOptions['styles'] = [
	    	{
	            featureType: "poi",
	            elementType: "labels",
	            stylers: [
	                  { visibility: "off" }
	            ]
	        }
	    ];
    }
    $DIRECTORY_MAP = new google.maps.Map(mapCanvas, mapOptions);
	
    // Info Window
    var $INFO_WINDOW = new google.maps.InfoWindow();
    // Define Marker Clusterer
    $MARKER_CLUSTER = new MarkerClusterer($DIRECTORY_MAP, [],
            {
    			imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m',
    			zoomOnClick: false,
            });
    
    $MARKER_CLUSTER.addListener("clusterclick", function (cluster) {
        clusterClicked = true;
        console.log(cluster);
        
        var html = '<ul>';
        var markers = cluster.getMarkers();
        markers.forEach(function(item, index){ 
        	html += "<li><a href='"+item.url+"'>"+item.title+"</a></li>";
        });
        html += '</ul>';
        $INFO_WINDOW.close();
        $INFO_WINDOW.setContent(html);
        $INFO_WINDOW.setPosition(cluster.getCenter());
        $INFO_WINDOW.open($DIRECTORY_MAP);
    });
    // Put markers
    for (var i=0; i<$DIRECTORY_ADDRESS.length; i+=3)
    	add_address_to_directory_map($DIRECTORY_ADDRESS[i], $DIRECTORY_ADDRESS[i+1], $DIRECTORY_ADDRESS[i+2]);
});

function add_address_to_directory_map(address, url, title) {
	if ($DIRECTORY_MAP == 0)
		return;
	
	var geocoder = new google.maps.Geocoder();
	geocoder.geocode({'address': address}, function(results, status) {
		if (status === google.maps.GeocoderStatus.OK) {
	    	var marker = new google.maps.Marker({
	    		map: $DIRECTORY_MAP,
	        	position: results[0].geometry.location,
				animation: google.maps.Animation.DROP,
				icon: '/aloxa_turismo_theme/static/src/img/marker-establishment.png',
	      	});
	    	marker['url'] = url;
	    	marker['title'] = title;
			marker.addListener('click', function() {
				window.location.href = this.url;
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


/** VISTA FORM **/
openerp.website.if_dom_contains('.btn-form-nav', function(){
	$(document).on('click', '.btn-form-nav', function(e){
		var link_target = this.dataset.linkTarget;
		var sri = 'sri='+this.dataset.sri;
		var url = window.location.href.split('?');
		var params = url[1] || '';
		if (params.match(/sri=\d+/)) {
			params = params.replace(/sri=\d+/,sri);
		} else {
			params += '&'+sri;
		}
		window.location.href = link_target+'?'+params;
	});
});

/** BUSCADOR **/
/*openerp.website.if_dom_contains('.searchbar', function(){
	$(document).on('mouseleave', '.searchbar', function(e){
		var $this = $(this);
		$this.find('.input-group-btn').css({'border-top-left-radius':'4px','border-bottom-left-radius':'4px'});
		var $squery = $this.find('.search-query');
		if (!$squery.val()) {
			$squery.animate({width: '0%', opacity: '0.0'}, function(){ $(this).css('display', 'none'); });
		}
	});
	$(document).on('mouseenter', '.searchbar .input-group-btn > a', function(e){
		var $this = $(this);
		var $sbar = $this.closest('.searchbar');
		$this.parent().css({borderTopLeftRadius:0,borderBottomLeftRadius:0});
		var $squery = $sbar.find('.search-query');
		$squery.css('display', 'inherit');
		$squery.animate({width: '100%', opacity:'1.0'});
	});
	
	if (!$('.searchbar .search-query').val()) {
		$('.searchbar .search-query').css({width:'0%', opacity:'0.0', display:'none'});
	}
});*/

