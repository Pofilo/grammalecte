// JavaScript
// Panel creator

"use strict";


class GrammalectePanel {

    constructor (sId, sTitle, nWidth, nHeight, bFlexible=true) {
        this.sId = sId;
        this.nWidth = nWidth;
        this.nHeight = nHeight;
        this.bFlexible = bFlexible;
        this.xPanelBar = createNode("div", {className: "grammalecte_panel_bar"});
        this.xPanelContent = createNode("div", {className: "grammalecte_panel_content"});
        this.xWaitIcon = this._createWaitIcon();
        this.xPanel = this._createPanel(sTitle);
        this.center();
    }

    _createPanel (sTitle) {
        try {
            let xPanel = createNode("div", {id: this.sId, className: "grammalecte_panel"});
            this.xPanelBar.appendChild(this._createButtons());
            let xTitle = createNode("div", {className: "grammalecte_panel_title"});
            xTitle.appendChild(this._createLogo());
            xTitle.appendChild(createNode("div", {className: "grammalecte_panel_label", textContent: sTitle}));
            this.xPanelBar.appendChild(xTitle);
            xPanel.appendChild(this.xPanelBar);
            xPanel.appendChild(this.xPanelContent);
            return xPanel;
        }
        catch (e) {
            showError(e);
        }
    }

    _createLogo () {
        let xImg = document.createElement("img");
        xImg.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAA3XAAAN1wFCKJt4AAAC8UlEQVQ4jX3TbUgTcRwH8P89ddu5u9tt082aZmpFEU4tFz0QGTUwCi0heniR9MSUIKRaD0RvIlKigsooo+iNFa0XJYuwIjEK19OcDtPElsG0ktyp591t7u7+vUh7MPX3+vf5/n8/+P0BmKJIPUUVlh2rdVVeesWlzEybqg+bFOsoylnqPmNavGFfknV2Omu2Lvja3vxAURKJib3opHizu8riLK6gjRyuKgmoSoMRFENRUqfXTzvBGK62LC2uoFkOl4RhjQ8+qWt7dPNE3sbdp+2LXbsGe9qb4rIo/BfwFy6nWQ4ThWGNDzbcfu29dMDh2nHU7CypYNLmzTda0/L5cNuzmDQi/A4Y27k6eQxLI79wS/11D0AAMNvs6XT6ojVJjJEgTbMy2BT77xBMp09KcpaWV1uc41jQoi0NdUHfjeOO9WWn7AVF7s7n986SithPJGeupBh2PCSP/xxqxAp3eq6wuUV7Wc6MSZIEhA8vHjbfOe/OcW3zmAuKy+nUzAyD2bow8ODaEROFq8AyZ5WBYdEZXGqGxZ61HJV+9HYCJRbTNA0QBA40HWunaKN5dKg/DBKxeCIe09Th/m4MJwiMSZmLEzMQAABQRuNqgu8NYX3doTcMpvCkLbtQZ2AJkrPOZG1zlnY13T+Hy9EehY90h57eqcorcZ/lctZuMzAsOjLEqwNv66/6vZcPYRBC+C3cGaBxhSet2av1BpYgTTY7k5y2JPT41slIR6Axv8R9nnOs+4Pf+2r992uOxGVJwgAAAEINfgt3BGgsESWtWas1iGDyl+CT/u7WpvxNFRc4x7qtBoZFhSFejb7z1fq9NYfjsiT+cwcQavBruCOgU4SIGo18amuoq3Js3FNlynVtH385+s53ze+t8cRkURx3yMTTRBAEQVAUXbFlf3XystJKA2NExeFBdWASDAAA+MQACCEEmqbJ0b6PMC7JwhDU8YFHV5u9NZ64LErT/oW/63tPV6uJwmKoOND78u7Fg5NhAAD4CVbzY9cwrWQrAAAAAElFTkSuQmCC";
        return xImg;
    }

    _createButtons () {
        let xButtonLine = createNode("div", {className: "grammalecte_panel_commands"});
        xButtonLine.appendChild(this.xWaitIcon);
        if (this.sId === "grammalecte_gc_panel") {
            xButtonLine.appendChild(this._createCopyButton());
        }
        xButtonLine.appendChild(this._createMoveButton("stickToTop", "¯", "Coller en haut"));
        xButtonLine.appendChild(this._createMoveButton("stickToLeft", "«", "Coller à gauche"));
        xButtonLine.appendChild(this._createMoveButton("center", "•", "Centrer"));
        xButtonLine.appendChild(this._createMoveButton("stickToRight", "»", "Coller à droite"));
        xButtonLine.appendChild(this._createMoveButton("stickToBottom", "_", "Coller en bas"));
        xButtonLine.appendChild(this._createCloseButton());
        return xButtonLine;
    }

    _createWaitIcon () {
        let xWaitIcon = createNode("div", {className: "grammalecte_spinner"});
        xWaitIcon.appendChild(createNode("div", {className: "bounce1"}));
        xWaitIcon.appendChild(createNode("div", {className: "bounce2"}));
        return xWaitIcon;
    }

    _createCopyButton () {
        let xButton = createNode("div", {id: "grammalecte_clipboard_button", className: "grammalecte_copy_button", textContent: "∑", title: "Copier dans le presse-papiers"});
        xButton.onclick = function () { this.copyTextToClipboard(); }.bind(this);
        return xButton;
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

    insertIntoPage () {
        document.body.appendChild(this.xPanel);
    }

    show () {
        this.xPanel.style.display = "block";
    }

    hide () {
        this.xPanel.style.display = "none";
    }

    center () {
        let nHeight = (this.bFlexible) ? window.innerHeight-100 : this.nHeight;
        this.xPanel.style = `top: 50%; left: 50%; width: ${this.nWidth}px; height: ${nHeight}px; margin-top: -${nHeight/2}px; margin-left: -${this.nWidth/2}px;`;
    }

    stickToLeft () {
        let nHeight = (this.bFlexible) ? window.innerHeight-100 : this.nHeight;
        this.xPanel.style = `top: 50%; left: -2px; width: ${this.nWidth}px; height: ${nHeight}px; margin-top: -${nHeight/2}px;`;
    }

    stickToRight () {
        let nHeight = (this.bFlexible) ? window.innerHeight-100 : this.nHeight;
        this.xPanel.style = `top: 50%; right: -2px; width: ${this.nWidth}px; height: ${nHeight}px; margin-top: -${nHeight/2}px;`;
    }

    stickToTop () {
        let nWidth = (this.bFlexible) ? Math.floor(window.innerWidth/2) : this.nWidth;
        let nHeight = (this.bFlexible) ? Math.floor(window.innerHeight*0.45) : this.nHeight;
        this.xPanel.style = `top: -2px; left: 50%; width: ${nWidth}px; height: ${nHeight}px; margin-left: -${nWidth/2}px;`;
    }

    stickToBottom () {
        let nWidth = (this.bFlexible) ? Math.floor(window.innerWidth/2) : this.nWidth;
        let nHeight = (this.bFlexible) ? Math.floor(window.innerHeight*0.45) : this.nHeight;
        this.xPanel.style = `bottom: -2px; left: 50%; width: ${nWidth}px; height: ${nHeight}px; margin-left: -${nWidth/2}px;`;
    }

    reduce () {
        // todo
    }

    adjustHeight () {
        this.xPanelContent.style.height = this.xPanelContent.firstChild.offsetHeight + "px"; // xPanelContent has only one child
        this.xPanel.style.height = this.xPanelBar.offsetHeight + this.xPanelContent.offsetHeight + 10 + "px";
    }

    logInnerHTML () {
        // for debugging
        console.log(this.xPanel.innerHTML);
    }
    
    startWaitIcon () {
        this.xWaitIcon.style.visibility = "visible";
    }

    stopWaitIcon () {
        this.xWaitIcon.style.visibility = "hidden";
    }

    openURL (sURL) {
        xGrammalectePort.postMessage({
            sCommand: "openURL",
            dParam: {"sURL": sURL},
            dInfo: {}
        });
    }
}
