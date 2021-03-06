$(document).foundation('alert', 'reflow');
$('#admins').bind('submit', function(e) {                               
    e.preventDefault();                                                    
    $url = "/admin_mod/action=add";
    if ($("#admin_id").val().indexOf("uq") == 0) {
	$url += "&user=";
	$url += $("#admin_id").val();
	if ($('#write_access').prop('checked')) {
	    $url += "&write=true";
	}
	if ($('#read_access').prop('checked')) {
	    $url += "&read=true";
	}
	if ($("#admins input:checkbox:checked").length >= 1) {
	    console.log("everything ok");
	    console.log($url);
	    window.location = $url;
	} else {
	    console.log("no perms");
	    $("#admin_err").html(function() {
		return "<div data-alert class='alert-box warning radius text-center'>" +
		    "<b>No permissions specified.</b>" + "<a href='#' class='close'>&times;</a>" + "</div>";
		});
	    $(document).foundation();
	    $(document).foundation('alert', 'reflow');
	}
    } else {
	$("#admin_err").html(function() {
	    return "<div data-alert class='alert-box warning radius text-center'>" +
		"<b>Please enter a valid user.</b>" + "<a href='#' class='close'>&times;</a>" + "</div>";
	    });
	$(document).foundation();
	$(document).foundation('alert', 'reflow');
    }
});

$('#search').bind('submit', function(e) {                               
    e.preventDefault();                                                    
    $filters = 0;
    $url = "/download/"
    if($("#module").val() != "None") {
	$url += "MODULE_ID=".concat($("#module").val());
	$filters++;
    }
    if($("#orgunit").val() != "None") {
	if($filters > 0) {
	    $url += "&";
	}
	$url += "ORG_UNIT=".concat($("#orgunit").val());
	$filters++;
    }
    if($("#userid").val() != "") {
	if($filters > 0) {
	    $url += "&";
	}
	$url += "USER_ID=".concat($("#userid").val());
	$filters++;
    }
    if($filters == 0) {
	$url += "nofilter";
    }
    window.location = $url;
});

$('.view__statistics').on("click", function(e) {
    if (!$('.quick__add').hasClass('hidden')) {
	$('.quick__add').toggleClass('hidden');
    }
    $('.quick__filter').toggleClass('hidden');
});

$('.admin__trigger').on("click", function(e) {
    if (!$('.quick__filter').hasClass('hidden')) {
	$('.quick__filter').toggleClass('hidden');
    }
    $('.quick__add').toggleClass('hidden');
});

$('.manage__modules').on("click", function(e) {
    window.location = "/module-manager";
});

$('.manage__administrators').on("click", function(e) {
    window.location = "/admin";
});

$(document).on('close.fndtn.alert', function(event) {
    $(document).foundation();
});
