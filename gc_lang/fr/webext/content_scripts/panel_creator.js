// JavaScript
// Panel creator

"use strict";

console.log("[Content script] Panel creator");


class GrammalectePanel {

    constructor (sId, sTitle, nWidth, nHeight, bMovable=true) {
        this.sId = sId;
        this.sContentId = sId+"_content";
        this.nWidth = nWidth;
        this.nHeight = nHeight;
        this.bMovable = bMovable;
        this.xContentNode = createNode("div", {className: "grammalecte_panel_content"});
        this.xWaitIcon = this._createWaitIcon();
        this.xPanelNode = this._createPanel(sTitle);
        this.center();
    }

    _createPanel (sTitle) {
        try {
            let xPanel = createNode("div", {id: this.sId, className: "grammalecte_panel"});
            let xBar = createNode("div", {className: "grammalecte_panel_bar"});
            xBar.appendChild(this._createButtons());
            let xTitle = createNode("div", {className: "grammalecte_panel_title"});
            xTitle.appendChild(createLogo());
            xTitle.appendChild(createNode("div", {className: "grammalecte_panel_label", textContent: sTitle}));
            xBar.appendChild(xTitle);
            xPanel.appendChild(xBar);
            xPanel.appendChild(this.xContentNode);
            return xPanel;
        }
        catch (e) {
            showError(e);
        }
    }

    _createButtons () {
        let xButtonLine = createNode("div", {className: "grammalecte_panel_commands"});
        xButtonLine.appendChild(this.xWaitIcon);
        if (this.bMovable) {
            xButtonLine.appendChild(this._createMoveButton("stickToTop", "¯", "Coller en haut"));
            xButtonLine.appendChild(this._createMoveButton("stickToLeft", "«", "Coller à gauche"));
            xButtonLine.appendChild(this._createMoveButton("center", "•", "Centrer"));
            xButtonLine.appendChild(this._createMoveButton("stickToRight", "»", "Coller à droite"));
            xButtonLine.appendChild(this._createMoveButton("stickToBottom", "_", "Coller en bas"));
        }
        xButtonLine.appendChild(this._createCloseButton());
        return xButtonLine;
    }

    _createWaitIcon () {
        let xWaitIcon = createNode("div", {className: "grammalecte_spinner"});
        xWaitIcon.appendChild(createNode("div", {className: "bounce1"}));
        xWaitIcon.appendChild(createNode("div", {className: "bounce2"}));
        return xWaitIcon;
    }

    _createMoveButton (sAction, sLabel, sTitle) {
        let xButton = createNode("div", {className: "grammalecte_move_button", textContent: sLabel, title: sTitle});
        xButton.onclick = function () { this[sAction](); }.bind(this);
        return xButton;
    }

    _createCloseButton () {
        let xButton = createNode("div", {className: "grammalecte_close_button", textContent: "×", title: "Fermer la fenêtre"});
        xButton.onclick = function () { this.hide(); }.bind(this);  // better than writing “let that = this;” before the function?
        return xButton;
    }

    setContentNode (xNode) {
        this.xContentNode.appendChild(xNode);
    }

    insertIntoPage () {
        document.body.appendChild(this.xPanelNode);
    }

    show () {
        this.xPanelNode.style.display = "block";
    }

    hide () {
        this.xPanelNode.style.display = "none";
    }

    center () {
        let nHeight = window.innerHeight-100;
        this.xPanelNode.style = `top: 50%; left: 50%; width: ${this.nWidth}px; height: ${nHeight}px; margin-top: -${nHeight/2}px; margin-left: -${this.nWidth/2}px;`;
    }

    stickToLeft () {
        let nHeight = window.innerHeight-100;
        this.xPanelNode.style = `top: 50%; left: -2px; width: ${this.nWidth}px; height: ${nHeight}px; margin-top: -${nHeight/2}px;`;
    }

    stickToRight () {
        let nHeight = window.innerHeight-100;
        this.xPanelNode.style = `top: 50%; right: -2px; width: ${this.nWidth}px; height: ${nHeight}px; margin-top: -${nHeight/2}px;`;
    }

    stickToTop () {
        let nWidth = Math.floor(window.innerWidth/2);
        this.xPanelNode.style = `top: -2px; left: 50%; width: ${nWidth}px; height: ${Math.floor(window.innerHeight*0.45)}px; margin-left: -${nWidth/2}px;`;
    }

    stickToBottom () {
        let nWidth = Math.floor(window.innerWidth/2);
        this.xPanelNode.style = `bottom: -2px; left: 50%; width: ${nWidth}px; height: ${Math.floor(window.innerHeight*0.45)}px; margin-left: -${nWidth/2}px;`;
    }

    reduce () {
        // todo
    }

    logInnerHTML () {
        // for debugging
        console.log(this.xPanelNode.innerHTML);
    }
    
    startWaitIcon () {
        this.xWaitIcon.style.visibility = "visible";
    }

    stopWaitIcon () {
        this.xWaitIcon.style.visibility = "hidden";
    }
}


/*
    Common functions
*/
function createNode (sType, oAttr, oDataset=null) {
    try {
        let xNode = document.createElement(sType);
        Object.assign(xNode, oAttr);
        if (oDataset) {
            Object.assign(xNode.dataset, oDataset);
        }
        return xNode;
    }
    catch (e) {
        showError(e);
    }
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
