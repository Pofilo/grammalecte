// JavaScript

/*
	Events
*/

self.port.on("addElem", function (sHtml) {
	let xElem = document.createElement("p");
	xElem.innerHTML = sHtml;
	document.getElementById("results").appendChild(xElem);
});

self.port.on("clear", function () {
	document.getElementById("results").textContent = "";
});

document.getElementById('testall').addEventListener("click", function (event) {
	self.port.emit('allGCTests');
});

document.getElementById('parse').addEventListener("click", function (event) {
	self.port.emit('checkText', document.getElementById('text').value);
});

document.getElementById('close').addEventListener("click", function (event) {
    self.port.emit('closePanel');
});


/*
	Actions
*/
