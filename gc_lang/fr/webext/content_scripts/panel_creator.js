// JavaScript
// Panel creator

"use strict";


function createPanelFrame (sId, sTitle) {
    try {
        let xPanel = createNode("div", {id: sId, className: "grammalecte_panel"});
        let xBar = createNode("div", {className: "grammalecte_title_bar"});
        xBar.appendChild(createCloseButton(xPanel));
        let xTitle = createNode("div", {className: "grammalecte_title"});
        xTitle.appendChild(createLogo());
        xTitle.appendChild(createNode("div", {className: "grammalecte_label", textContent: "Grammalecte · " + sTitle}));
        xBar.appendChild(xTitle);
        xPanel.appendChild(xBar);
        //xPanel.appendChild(createNode("div", {className: "grammalecte_empty_space_under_title_bar"}));
        xPanel.appendChild(createNode("div", {id: sId+"_content", className: "grammalecte_panel_content"}));
        return xPanel;
    }
    catch (e) {
        showError(e);
    }
}

function createCloseButton (xParentNode) {
    let xButton = document.createElement("div");
    xButton.className = "grammalecte_close_button";
    xButton.textContent = "×";
    xButton.onclick = function () {
        xParentNode.style.display = "none";
    }
    return xButton;
}


/*
    Common functions
*/
function createNode (sType, oAttr) {
    try {
        let xNode = document.createElement(sType);
        Object.assign(xNode, oAttr);
        return xNode;
    }
    catch (e) {
        showError(e);
    }
}

function createCheckbox (sId, bDefault, sClass="")  {
    let xInput = document.createElement("input");
    xInput.type = "checkbox";
    xInput.id = sId;
    xInput.className = sClass;
    xInput.dataset.default = bDefault;
    return xInput;
}

function createLabel (sForId, sLabel, sClass="") {
    let xLabel = document.createElement("label");
    xLabel.setAttribute("for", sForId);
    xLabel.textContent = sLabel;
    return xLabel;
}

function createLogo () {
    let xImg = document.createElement("img");
    xImg.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAA3XAAAN1wFCKJt4AAAC8UlEQVQ4jX3TbUgTcRwH8P89ddu5u9tt082aZmpFEU4tFz0QGTUwCi0heniR9MSUIKRaD0RvIlKigsooo+iNFa0XJYuwIjEK19OcDtPElsG0ktyp591t7u7+vUh7MPX3+vf5/n8/+P0BmKJIPUUVlh2rdVVeesWlzEybqg+bFOsoylnqPmNavGFfknV2Omu2Lvja3vxAURKJib3opHizu8riLK6gjRyuKgmoSoMRFENRUqfXTzvBGK62LC2uoFkOl4RhjQ8+qWt7dPNE3sbdp+2LXbsGe9qb4rIo/BfwFy6nWQ4ThWGNDzbcfu29dMDh2nHU7CypYNLmzTda0/L5cNuzmDQi/A4Y27k6eQxLI79wS/11D0AAMNvs6XT6ojVJjJEgTbMy2BT77xBMp09KcpaWV1uc41jQoi0NdUHfjeOO9WWn7AVF7s7n986SithPJGeupBh2PCSP/xxqxAp3eq6wuUV7Wc6MSZIEhA8vHjbfOe/OcW3zmAuKy+nUzAyD2bow8ODaEROFq8AyZ5WBYdEZXGqGxZ61HJV+9HYCJRbTNA0QBA40HWunaKN5dKg/DBKxeCIe09Th/m4MJwiMSZmLEzMQAABQRuNqgu8NYX3doTcMpvCkLbtQZ2AJkrPOZG1zlnY13T+Hy9EehY90h57eqcorcZ/lctZuMzAsOjLEqwNv66/6vZcPYRBC+C3cGaBxhSet2av1BpYgTTY7k5y2JPT41slIR6Axv8R9nnOs+4Pf+2r992uOxGVJwgAAAEINfgt3BGgsESWtWas1iGDyl+CT/u7WpvxNFRc4x7qtBoZFhSFejb7z1fq9NYfjsiT+cwcQavBruCOgU4SIGo18amuoq3Js3FNlynVtH385+s53ze+t8cRkURx3yMTTRBAEQVAUXbFlf3XystJKA2NExeFBdWASDAAA+MQACCEEmqbJ0b6PMC7JwhDU8YFHV5u9NZ64LErT/oW/63tPV6uJwmKoOND78u7Fg5NhAAD4CVbzY9cwrWQrAAAAAElFTkSuQmCC";
    return xImg;
}

function loadImage (sContainerClass, sImagePath) {
    let xRequest = new XMLHttpRequest();
    xRequest.open('GET', browser.extension.getURL("")+sImagePath, false);
    xRequest.responseType = "arraybuffer";
    xRequest.send();
    let blobTxt = new Blob([xRequest.response], {type: 'image/png'});
    let img = document.createElement('img');
    img.src = (URL || webkitURL).createObjectURL(blobTxt); // webkitURL is obsolete: https://bugs.webkit.org/show_bug.cgi?id=167518
    Array.filter(document.getElementsByClassName(sContainerClass), function (oElem) {
        oElem.appendChild(img);
    });
}
