// Grammar checker graph rules

/* jshint esversion:6, -W097 */
/* jslint esversion:6 */
/* global exports */

"use strict";

${string}


var gc_rules_graph = {
    dAllGraph: ${rules_graphsJS},

    dRule: ${rules_actionsJS}
};


if (typeof(exports) !== 'undefined') {
    exports.dAllGraph = gc_rules_graph.dAllGraph;
    exports.dRule = gc_rules_graph.dRule;
}