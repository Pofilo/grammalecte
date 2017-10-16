// JavaScript
// Panel creator

"use strict";


class GrammalecteMessageBox {

    constructor (sId, sTitle, nWidth, nHeight) {
        this.sId = sId;
        this.nWidth = nWidth;
        this.nHeight = nHeight;
        this.xMessageBoxBar = oGrammalecte.createNode("div", {className: "grammalecte_message_box_bar"});
        this.xMessageBoxContent = oGrammalecte.createNode("div", {className: "grammalecte_message_box_content"});
        this.xMessageBox = this._createPanel(sTitle);
        this.center();
    }

    _createPanel (sTitle) {
        try {
            let xMessageBox = oGrammalecte.createNode("div", {id: this.sId, className: "grammalecte_message_box"});
            this.xMessageBoxBar.appendChild(oGrammalecte.createNode("div", {className: "grammalecte_message_box_invisible_marker", textContent: "__grammalecte_panel__"}));
            this.xMessageBoxBar.appendChild(this._createButtons());
            let xTitle = oGrammalecte.createNode("div", {className: "grammalecte_panel_title"});
            xTitle.appendChild(this._createLogo());
            xTitle.appendChild(oGrammalecte.createNode("div", {className: "grammalecte_message_box_label", textContent: sTitle}));
            this.xMessageBoxBar.appendChild(xTitle);
            xMessageBox.appendChild(this.xMessageBoxBar);
            xMessageBox.appendChild(this.xMessageBoxContent);
            return xMessageBox;
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
        let xButtonLine = oGrammalecte.createNode("div", {className: "grammalecte_panel_commands"});
        xButtonLine.appendChild(this._createCloseButton());
        return xButtonLine;
    }

    _createCloseButton () {
        let xButton = oGrammalecte.createNode("div", {className: "grammalecte_close_button", textContent: "×", title: "Fermer la fenêtre"});
        xButton.onclick = function () { this.hide(); }.bind(this);  // better than writing “let that = this;” before the function?
        return xButton;
    }

    insertIntoPage () {
        document.body.appendChild(this.xMessageBox);
    }

    show () {
        this.xMessageBox.style.display = "block";
    }

    hide () {
        this.xMessageBox.style.display = "none";
    }

    setMessage (sMessage) {
    	this.xMessageBoxContent.textContent = sMessage;
    }

    center () {
        this.xMessageBox.style = `top: 50%; left: 50%; width: ${this.nWidth}px; height: ${this.nHeight}px; margin-top: -${this.nHeight/2}px; margin-left: -${this.nWidth/2}px;`;
    }
}
