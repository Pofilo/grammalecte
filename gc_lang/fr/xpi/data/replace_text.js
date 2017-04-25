// replace text in active worker

const dParagraphs = new Map();

let xActiveTextZone = null;
let xCloseButton = null;
let xParentElement = null;

/* events */

self.port.on("setActiveElement", function (bSendTextBack=false) {
	setActiveElement(bSendTextBack);
});

self.port.on("setParagraph", function (iParagraph, sText) {
	dParagraphs.set(iParagraph, sText);
});

self.port.on("getParagraph", function (iParagraph) {
	let sText = dParagraphs.has(iParagraph) ? dParagraphs.get(iParagraph) : getNthParagraph(iParagraph);
	self.port.emit("emitParagraph", iParagraph, sText);
});

self.port.on("rewrite", function () {
	rewrite();
});

self.port.on("getText", function () {
	if (xActiveTextZone !== null) {
		self.port.emit("emitText", xActiveTextZone.value);
	}
});

self.port.on("write", function (sText) {
	if (xActiveTextZone !== null) {
		xActiveTextZone.value = sText;
	}
});

self.port.on("clear", function () {
	clear();
});


/* actions */

function setActiveElement (bSendTextBack=false) {
	try {
		if (document.activeElement.tagName === "TEXTAREA" || document.activeElement.tagName === "INPUT") {
			xActiveTextZone = document.activeElement;
			if (bSendTextBack) {
				self.port.emit("yesThisIsTextZone", xActiveTextZone.value);
			} else {
				self.port.emit("yesThisIsTextZone", "");
			}
			createCloseButton(xActiveTextZone);
			xActiveTextZone.disabled = true;
		} else {
			xActiveTextZone = null;
		}
		dParagraphs.clear();
	} catch (e) {
		console.error("\n" + e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
	}
}

function rewrite () {
	try {
		if (xActiveTextZone !== null) {
			let sText = "";
			let i = 0;
			for (let sParagraph of xActiveTextZone.value.split("\n")) {
				sText += (dParagraphs.has(i)) ? dParagraphs.get(i) + "\n" : sParagraph + "\n";
				i += 1;
			}
			xActiveTextZone.value = sText.slice(0,-1);
		}
	} catch (e) {
		console.error("\n" + e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
	}
}

function clear () {
	try {
		if (xActiveTextZone !== null) {
			xActiveTextZone.disabled = false;
		}
		if (xCloseButton !== null) {
			xParentElement.removeChild(xCloseButton);
			xParentElement = null;
			xCloseButton = null;
		}
		xActiveTextZone = null;
		dParagraphs.clear();
	} catch (e) {
		console.error("\n" + e.fileName + "\n" + e.name + "\nline: " + e.lineNumber + "\n" + e.message);
	}
}

function getNthParagraph (iParagraph) {
	if (xActiveTextZone !== null) {
		let sText = xActiveTextZone.value;
		let i = 0;
		let iStart = 0;
		while (i < iParagraph && ((iStart = sText.indexOf("\n", iStart)) !== -1)) {
			i++;
			iStart++;
		}
		if (i === iParagraph) {
			return ((iEnd = sText.indexOf("\n", iStart)) !== -1) ? sText.slice(iStart, iEnd) : sText.slice(iStart);
		}
		return "# Erreur. Paragraphe introuvable.";
	}
	return "# Erreur. Zone de texte introuvable.";
}

function createCloseButton (xActiveTextZone) {
	xParentElement = xActiveTextZone.parentElement;
	xCloseButton = document.createElement("p");
	xCloseButton.textContent = "× | Débloquer la zone de texte.";
	xCloseButton.title = "Cette action clot le panneau de correction de Grammalecte."
	xCloseButton.style = "padding: 5px; color: #FFF; background-color: #F80; border-radius: 3px; cursor: pointer";
	xCloseButton.onclick = function() {
		self.port.emit("closeGCPanel");
		self.port.emit("closeTFPanel");
		if (xParentElement !== null) {
			xParentElement.removeChild(xCloseButton);
			xParentElement = null;
			xCloseButton = null;
		}
		clear();
	};
	xParentElement.insertBefore(xCloseButton, xActiveTextZone);
}
