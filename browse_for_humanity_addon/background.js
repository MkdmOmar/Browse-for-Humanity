var SERVER_URL = "http://198.74.58.111";
var busy = false;

(function(){
   if (!busy) {
        
    	var xhr = new XMLHttpRequest();
    	console.log("sending getjob request")
    	
    	request_report_url = SERVER_URL + "/get_job"
    	xhr.open("GET", request_report_url, true);

    	xhr.onreadystatechange = function() {
            if (xhr.readyState == 4) {
                if (xhr.responseText !== "X_X") {
                    busy = true
                    var task = JSON.parse(xhr.responseText)
            		console.log(task.code)
                    console.log(task.params)
                    
                    results = eval(task.code); 
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


function MonteCarlo(dims, steps) {
    var data = [183, 192, 182, 183, 177, 185, 188, 188, 182, 185,183, 192, 182, 183, 177, 185, 188, 188, 182, 185,183, 192, 182, 183, 177, 185, 188, 188, 182, 185,183, 192, 182, 183, 177, 185, 188, 188, 182, 185];

    var params = {
      mu: {type: "real"},
      sigma: {type: "real", lower: 0} };

    var log_post = function(state, data) {
      var log_post = 0;
      // Priors
      log_post += ld.norm(state.mu, 0, 100);
      log_post += ld.unif(state.sigma, 0, 100);
      // Likelihood
      for(var i = 0; i < data.length; i++) {
        log_post += ld.norm(data[i], state.mu, state.sigma);
      }
      return log_post;
    };

    // Initializing the sampler
    var sampler =  new mcmc.AmwgSampler(params, log_post, data);
    // Burning some samples to the MCMC gods and sampling 5000 draws.
    sampler.burn(1000)
    var samples = sampler.sample(50000)
};

