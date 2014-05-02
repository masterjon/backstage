$(function() {
		
		$( ".datepicker" ).datepicker({
			inline: true,
			defaultDate: +0
		});
		var table=$("#report-table").html()
		$("#tabl").val("<table>"+table+"</table>")


});