// JavaScript

let nDefaultPanelHeight = 0;


/*
	Events
*/

self.port.on("sendGrammarOptionsToPanel", function (sGCOptions) {
	setGrammarOptionsOnPanel(JSON.parse(sGCOptions));
});

self.port.on("sendSpellingOptionsToPanel", function (bDicMod, bDicClas, bDicRef, bDicAll) {
	setPanelDictOption("fr-FR-modern", bDicMod);
	setPanelDictOption("fr-FR-classic", bDicClas);
	setPanelDictOption("fr-FR-reform", bDicRef);
	setPanelDictOption("fr-FR-classic-reform", bDicAll);
});

self.port.on("showHelp", function () {
	showHelp();
});

self.port.on("calcDefaultPanelHeight", function () {
	nDefaultPanelHeight = calcPanelHeight();
});

document.getElementById('grammar').addEventListener("click", function(event) {
	if (document.getElementById('grammar_section').style.display === "none" || document.getElementById('grammar_section').style.display === "") {
		self.port.emit("loadGrammarOptions");
		showGrammarOptions();
	} else {
		showHelp();
	}
});

document.getElementById('spelling').addEventListener("click", function(event) {
	if (document.getElementById('spelling_section').style.display === "none" || document.getElementById('spelling_section').style.display === "") {
		self.port.emit("loadSpellingOptions");
		showSpellingOptions();
	} else {
		showHelp();
	}
});

document.getElementById('default_options').addEventListener("click", function (event) {
	self.port.emit('resetOptions');
});

document.getElementById('conjugueur').addEventListener("click", function (event) {
	self.port.emit('openConjugueur');
});

document.getElementById('website').addEventListener("click", function (event) {
	self.port.emit('openURL', "http://www.dicollecte.org/");
});

document.getElementById('mainsponsor').addEventListener("click", function (event) {
	self.port.emit('openURL', "http://lamouette.org/");
});
document.getElementById('mainsponsor2').addEventListener("click", function (event) {
	self.port.emit('openURL', "https://www.algoo.fr/");
});

document.getElementById('othersponsors').addEventListener("click", function (event) {
	self.port.emit('openURL', "http://www.dicollecte.org/#thanks");
});


window.addEventListener(
	"click",
	function (xEvent) {
		let xElem = xEvent.target;
		if (xElem.id) {
			if (xElem.id.startsWith("option_") && xElem.tagName === "INPUT") {
				self.port.emit("setOption", xElem.id.slice(7), xElem.checked);
			}
			if (xElem.id.startsWith("fr-FR-") && xElem.tagName === "INPUT") {
				setPanelDictOption(xElem.id, xElem.checked);
				self.port.emit("changeDictSetting", xElem.id, xElem.checked);
			}
		}
	},
	false
);


/*
	Actions
*/

function calcPanelHeight () {
	return document.getElementById("thanks").offsetTop + document.getElementById("thanks").offsetHeight;
}

function setHeight (n) {
	self.port.emit("setHeight", n);
}

function showHelp () {
	document.getElementById('spelling_section').style.display = "none";
	document.getElementById('grammar_section').style.display = "none";
	document.getElementById('help_section').style.display = "block";
	setHeight(nDefaultPanelHeight);
}

function showGrammarOptions () {
	document.getElementById('grammar_section').style.display = "block";
	document.getElementById('spelling_section').style.display = "none";
	document.getElementById('help_section').style.display = "none";
	setHeight(1000);
}

function showSpellingOptions () {
	document.getElementById('spelling_section').style.display = "block";
	document.getElementById('grammar_section').style.display = "none";
	document.getElementById('help_section').style.display = "none";
	setHeight(1000);
}

function setGrammarOptionsOnPanel (oOptions) {
	for (let sParam in oOptions) {
		//console.log(sParam + ":" + oOptions[sParam]);
		if (document.getElementById("option_"+sParam) !== null) {
			document.getElementById("option_"+sParam).checked = oOptions[sParam];
		}
	}
}

function setPanelDictOption (sNode, bValue) {
	document.getElementById(sNode).checked = bValue;
	document.getElementById(sNode+"_box").style = bValue ? "background-color: hsl(210, 30%, 90%)" : "background-color: hsl(210, 15%, 96%)";
}
