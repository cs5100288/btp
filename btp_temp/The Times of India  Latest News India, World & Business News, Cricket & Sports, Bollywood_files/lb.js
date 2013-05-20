/**
 * 
 */

var domain = "http://rewards.indiatimes.com/bp";


function log(action,id){
	var obj   = window._tp_async_data;
	
	if(validate(obj)){
	var request = domain+"/api/alog/gal?uemail="+encodeURI(obj.email);
	request += "&url="+encodeURI(obj.URL);
	request += "&pcode="+encodeURI(obj.host);
	request += "&scode="+encodeURI(obj.channel);
	request += "&oid="+encodeURI(id);
	request += "&uid="+encodeURI(obj.userId);
	request += "&ecode="+encodeURI(action);				
	sendRequest(request);
	}
}

function validate(obj){

	if(
	   !obj.URL        ||
	   !obj.host       ||
	   !obj.channel    ||
	   !obj.email      ||
	   !obj.userId  		
	) {				
		    return false;
		}
		return true;
}

function sendRequest(request) {
	var img = new Image(1,1);
	img.src = request;
}
