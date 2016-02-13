
var http = require('http');
var io = require('socket.io');
var zerorpc = require('zerorpc');

var server = http.createServer();
server.listen(8001, '192.168.1.9');

var listener = io.listen(server);

var client = new zerorpc.Client();
client.connect("tcp://127.0.0.1:4242");



listener.on('connection', function(socket) {
	console.log('We have a connection!');
	
	socket.emit("server_successful_connection");
	client.invoke("getAlarm", function(error, res, more) {
		console.log('Attempting to get alarm')
		console.log(res);
		socket.emit("server_alarm_successfully_set", res);
	});
	client.invoke("getMP3Library", function(error, res, more) {
		socket.emit("server_MP3Library_fetched", res);
	});
	client.invoke("getAlarmSongIndex", function(error, res, more) {
		resString = res.toString();
		socket.emit("server_alarmSongIndex_fetched", resString);
	});
	
	socket.on('client_alarm_set_request', function(data) {
		console.log('Client side |alarm_set_request|: ' + data);
		var jsonObject = JSON.parse(data);
		client.invoke("setAlarm", jsonObject.hour, jsonObject.minute, function(error, res, more) {
			if (res === 'success') {
				socket.emit("server_alarm_successfully_set", data);
			}
		});
	});
	socket.on('client_play_request', function(data) {
		client.invoke("playMP3", data, function(error, res, more) {
			// do nothing
		});
	});
	socket.on('client_pause_request', function(data) {	
		client.invoke("pauseMP3", function(error, res, more) {
			// do nothing
		});
	});
	socket.on('client_alarmSongIndex_set', function(data) {	
		client.invoke("setAlarmSongIndex", data, function(error, res, more) {
			// do nothing
		});
	});
	socket.on('disconnect', function(data) {
		console.log('We have a socket disconnected');
		socket.emit('server_client_disconnected');
	});
});

console.log('Server started');
