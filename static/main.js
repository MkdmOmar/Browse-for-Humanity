$(document).ready(function(e) {
	jobsAdded = {}
	$("#createJob").click(function(e) { // can be submit too
		e.preventDefault()
		var text = $("#job_field").val()
		isValid = isJSON(JSON.stringify(text))
		if (isValid && text != "") {
			$("#job_field").val('')
			$("#selectedJobs").append(
				"<div class='container-fluid'>" +
					"<blockquote><p style='float:left'>" + text +
					"<button class='btn-xs removeButton'>x</button>" +
					"</p></blockquote>" +
				"</div>")
			newJob = JSON.parse(text)
			jobsAdded[text] = newJob

			$(".removeButton").click(function(e) {
				e.preventDefault()
				text = $(this).closest('p').val()
				delete jobsAdded[text]

				$(this).closest('div').remove()
			})
		}
		else {
			$("#job_field").val('')
			$("#jsonPopup").show()
			$("#jsonPopup").delay(750).fadeOut();
		}
	});

	$("#submitJobs").click(function(e) {
		e.preventDefault()

		// submit to server


	})

	function isJSON(str) {
		try {
			JSON.parse(str);
		} catch (e) {
			console.log(e)
			return false;
		}
		return true;
	}

});
