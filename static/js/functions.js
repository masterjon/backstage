$(document).ready(function(){
	$("#lang-form select").change(function(){
		$("#lang-form").submit();
	})
$('#shows-link').hover(function() {
  $(this).find('#menu-shows').stop(true, true).delay(200).fadeIn();
}, function() {
  $(this).find('#menu-shows').stop(true, true).delay(200).fadeOut();
});

$('.carousel').carousel({
  interval: 4000
  })
});
  
