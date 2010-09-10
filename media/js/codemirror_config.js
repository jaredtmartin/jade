$(document).ready(function() {
	var editor = new CodeMirror.fromTextArea("id_body", {
	  width: "90%",
	  height: "300px",
	  parserfile: ["parsexml.js", "parsecss.js", "parsehtmlmixed.js"],
	  stylesheet: ["/media/css/codemirror/xmlcolors.css",
                       "/media/css/codemirror/csscolors.css"],
	  path: "/media/js/codemirror/",
	  content: document.getElementById("id_body").value
	});

	$("textarea#id_body + iframe").css("border", "1px solid rgb(204, 204, 204)");
});
