
// Set
/*jslint esversion: 6*/

if (Set.prototype.grammalecte === undefined) {
    Set.prototype.gl_update = function (aSet) {
        for (let elem of aSet) {
            this.add(elem);
        }
    };

    Set.prototype.grammalecte = true;
}
