var SERVER_URL = "http://198.74.58.111";
var busy = false;
var on = true;

chrome.runtime.onMessage.addListener( function(request,sender,sendResponse)
{
    if( request.type == "ToggleAddon" )
    {
        console.log("Toggling Addon")
        on = !on;
    }
});


(function(){
   if (!busy && on) {
        
    	var xhr = new XMLHttpRequest();
    	console.log("sending getjob request")
    	
    	request_report_url = SERVER_URL + "/get_job"
    	xhr.open("GET", request_report_url, true);

    	xhr.onreadystatechange = function() {
            if (xhr.readyState == 4) {
                if (xhr.responseText !== "X_X") {
                    
                    console.log(xhr.responseText)
                    var task = JSON.parse(xhr.responseText)
            		    console.log(task.code)
                    console.log(task.params)
                    
                    results = eval(task.code);
                    busy = true 
                    results = doWork(task.inputs);
                    console.log(results)
                    
                    var xhr2 = new XMLHttpRequest();
                    console.log("Reporting result")
                    
                    submit_result_url = SERVER_URL + "/submit_result" + "?job_id=" + encodeURIComponent(task.job_id) + 
                                        "&task_id=" + encodeURIComponent(task.task_id) + "&result=" + encodeURIComponent(results)
                    xhr2.open("GET", submit_result_url, true);
                    xhr2.onreadystatechange = function() {
                                                           if (xhr.readyState == 4) {
                                                              console.log("Response: " + xhr2.responseText)
                                                           }
                                                        }
                    
                    xhr2.send();
                    busy = false
                }

        	}
    	}
    	xhr.send();
    }
    else {
        console.log("Busy")
    }
	setTimeout(arguments.callee, 5000);
})();




