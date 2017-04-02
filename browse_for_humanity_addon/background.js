var SERVER_URL = "http://198.74.58.111";
var busy = false;
// LZW-compress a string
function lzw_encode(s) {
    var dict = {};
    var data = (s + "").split("");
    var out = [];
    var currChar;
    var phrase = data[0];
    var code = 256;
    for (var i=1; i<data.length; i++) {
        currChar=data[i];
        if (dict[phrase + currChar] != null) {
            phrase += currChar;
        }
        else {
            out.push(phrase.length > 1 ? dict[phrase] : phrase.charCodeAt(0));
            dict[phrase + currChar] = code;
            code++;
            phrase=currChar;
        }
    }
    out.push(phrase.length > 1 ? dict[phrase] : phrase.charCodeAt(0));
    for (var i=0; i<out.length; i++) {
        out[i] = String.fromCharCode(out[i]);
    }
    return out.join("");
}



(function(){
   if (!busy) {
        
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
                    results = lzw_encode(doWork(task.inputs));
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




function MonteCarlo(N, steps) {
    console.log("Starting...")
    console.time('someFunction');
    console.log((do_work(N, steps)));
    console.timeEnd('someFunction');
};


