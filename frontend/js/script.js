var user = "";   //global variable for nickname
var stranger = "";   //global variable for stranger nickname (chatwith)
var time = 15000;   //timeout in ms, same as server variable
var get_msg_last_time = 0;   //last time (millis()) of getting new message - used for handling server fall or unexpected erros
var mode = "LONG POLL"

//----------settings functions---------
function set_user() {   //for setting up new nickname
	user = document.getElementById("user").value;
	document.getElementById("info-user").innerHTML = user;
}

function set_stranger() {   //for settings up new stranger nickname
	stranger = document.getElementById("stranger").value;
	document.getElementById("info-stranger").innerHTML = stranger;
}

function set_mode() {
	mode = document.querySelector('input[name="mode"]:checked').value;
}
//----------settings functions---------


//----------requests and assitants functions----------
function ajax(type, path, data, timeout, completion_handler, timeout_handler) {   //ajax XHR wrapper
	var xhr = new XMLHttpRequest();
 
	xhr.onload = function() {
		if (this.status === 200) {
			completion_handler(this.responseText);   //call gived function
		}
		else if (this.status === 204) {   //no data
			timeout_handler();   //call timeout function because server closed connection with return code 204 - no conten (data)
		}
		else {
			console.log(this.status);
			fail("Unknown status: " + this.status + " status text: " + this.statusText);
		}
	};

	xhr.open(type, path, true);

	if (timeout > 0) {
		xhr.timeout = timeout;   //set timeout if timeout is bigger than 0
		xhr.ontimeout = timeout_handler
	}

	var fin = {};   //create new object (for JSON)
	fin.user = user;   //save nickname
	fin.stranger = stranger;   //save stranger nickname
	fin.mode = mode
	var json = JSON.stringify(fin);   //create JSON

	xhr.setRequestHeader("info", json);   //add JSON to header

	console.log(data)
	xhr.send(data);   //send data
}


function fail(msg) {   //display fail messages in special box
	var fail_box_content = document.getElementById("fail-box").innerHTML;
	document.getElementById("fail-box").innerHTML = fail_box_content + "<span>" + msg + "</span><br>";
}
//----------requests and assitants functions----------


//----------functions for sending and receiving messages (and also displaying)---------
function send_msg() {   //for sending new message via ajax and displaying in message box
	var send_box = document.getElementById("send-box");   //get index to send-box element
	var message = send_box.value;   //get mesg from input textbox

	if (message.length < 1) {   //skip blank messages
		send_box.placeholder = "Minimum length is 1 character!";
	} else {
		send_box.placeholder = "";   //remove placeholder from input message text box
		console.log(message)
		ajax(
			"POST",
			"submit_msg",
			message,
			-1,
			function () {},
			function () {});   //send new message to server without timeout

		var chat_box = document.getElementById("chat-box");   //get index to chat-box element
		var chat_box_content = chat_box.innerHTML;   //get current data from chat box
		chat_box.innerHTML = chat_box_content + "<span><b>You: </b>" + message + "</span><br>";   //put current data + new data to chat box
		chat_box.scrollTop = chat_box.scrollHeight;   //scroll into view in chat box

		send_box.value = "";   //clear input message text box value
	}
}


function new_msg(msg) {   //function for displaying new message from stranger
	var chat_box = document.getElementById("chat-box");   //get index to chat-box element
	var chat_box_content = chat_box.innerHTML;   //get current data from chat box
	chat_box.innerHTML = chat_box_content + "<span><b>Stranger: </b>" + msg + "</span><br>";   //put current data + new data to chat box
	chat_box.scrollTop = chat_box.scrollHeight;   //scrol into view in chat box

	check_msg();   //call function check_msg to create ajax request with timeout
}


function check_msg() {   //for calling ajax and setting up new interval
	if (mode === "LONG POLL") {
		ajax("GET", "get_msg", "", time, new_msg, check_msg);
	} else if (mode === "POLL") {
		ajax("GET", "get_msg", "", -1, new_msg, check_msg)
	}
	get_msg_last_time = Date.now();
	//setTimeout(check_msg, time);   //set timeout to call new function (call after timeout)
}
//----------functions for sending and receiving messages (and also displaying)---------



//----------startup----------
set_user();
set_stranger();

check_msg();

// setInterval(renew_check_msg_cycle, 5000);   //check for renewing ajax connection every 5 seconds
//----------startup----------