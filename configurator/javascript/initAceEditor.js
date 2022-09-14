/**
 * Global variable to store the ids of the status of the current dragged ace editor.
 */
let draggingAceEditor = false;
let draggingEditorTopOffset = 0;
let aceEditorResizeBar;
let aceEditorWrapper;
let aceEditor;

function aceDragMouseMove (e) {
	// editor height
	var eheight = e.pageY - draggingEditorTopOffset;
	// Set aceEditorWrapper height
	aceEditor.style.height = `${eheight}px`;

	// Set aceEditorResizeBar opacity while dragging (set to 0 to not show)
	aceEditorResizeBar.style.opacity = 0.15;
}

function aceDragMouseDown(e) {
	e.preventDefault();

	draggingAceEditor = true;

	draggingEditorTopOffset = e.pageY - aceEditor.offsetHeight;

	// Set editor opacity to 0 to make transparent so our aceEditorWrapper div shows
	aceEditor.style.opacity = 1;

	// handle mouse movement
	document.addEventListener('mousemove', aceDragMouseMove)
}

function aceDragMouseUp (e) {
	if (draggingAceEditor) {

		document.removeEventListener('mousemove', aceDragMouseMove);

		// Set aceEditorResizeBar opacity back to 1
		aceEditorResizeBar.style.opacity = 1;

		// Set height on actual editor element, and opacity back to 1
		aceEditor.style.height = `${aceEditor.offsetHeight}px`;
		aceEditor.style.opacity = 1;

		// Trigger ace editor resize()
		editor.root.ace_editor.resize();

		draggingAceEditor = false;
	}
}

function makeAceEditorResizable(editor) {
	draggingAceEditor = false;
	aceEditorResizeBar.addEventListener('mousedown', aceDragMouseDown);
	document.addEventListener('mouseup', aceDragMouseUp);
}

function initAceEditor(editor) {
	aceEditorResizeBar = document.getElementById("ace-editor_dragbar");
	aceEditor = document.getElementById("ace-editor");
	aceEditorWrapper = editor.root.editjson_holder;
	aceEditorWrapper.id = "ace-editor_wrapper"

	aceEditorWrapper.childNodes[2].remove();
	aceEditorWrapper.firstElementChild.replaceWith(aceEditor);
	aceEditor.after(aceEditorResizeBar);

	let cardHolder = editor.root.container.getElementsByClassName('card-body')[0];
	aceEditorWrapper.style["min-height"] = `${cardHolder.offsetHeight}px`;

	editor.root.ace_editor = ace.edit("ace-editor", {
		mode: "ace/mode/json",
		printMargin: false
	});
	editor.root.ace_editor.setTheme("ace/theme/chrome");
	editor.root.ace_editor.session.setTabSize(4);
	makeAceEditorResizable(editor.root.ace_editor);
}