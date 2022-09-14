/**
 * Global variable to store the ids of the status of the current dragged ace editor.
 */
let draggingAceEditor = false;
let draggingEditorTopOffset = 0;
let aceEditorResizeBar;
let aceEditorWrapper;
let aceEditorWrapperExtra;
let aceEditor;

/*
 * And the way we handle JSON editors
 */
JSONEditor.defaults.editors.object.prototype.showEditJSON = function() {
	if (!this.editjson_holder) return
	this.hideAddProperty()


	/* Start the textarea with the current value */
	this.ace_editor.setValue(JSON.stringify(convertToBackendFormat(this.getValue()), null, 4));

	/* Disable the rest of the form while editing JSON */
	this.disable()

	this.editjson_holder.style.display = ''
	this.editjson_control.disabled = false
	this.editing_json = true

	aceEditorWrapperExtra = aceEditorWrapper.offsetHeight - aceEditor.offsetHeight;
	console.log(aceEditorWrapperExtra,aceEditorWrapper.offsetHeight,aceEditor.offsetHeight);
} 
JSONEditor.defaults.editors.object.prototype.copyJSON = function() {
	if (!this.editjson_holder) return
	const ta = document.createElement('textarea')
	ta.value = JSON.stringify(convertToFrontendFormat(JSON.parse(this.ace_editor.getValue())))
	ta.setAttribute('readonly', '')
	ta.style.position = 'absolute'
	ta.style.left = '-9999px'
	document.body.appendChild(ta)
	ta.select()
	document.execCommand('copy')
	document.body.removeChild(ta)
}
JSONEditor.defaults.editors.object.prototype.saveJSON = function() {
	if (!this.editjson_holder) return	
	try {
	  const json = JSON.parse(this.ace_editor.getValue())
	  this.setValue(convertToFrontendFormat(json))
	  this.hideEditJSON()
	  this.onChange(true)
	  } catch (e) {
		console.log(e)
	  window.alert('invalid JSON')
	  throw e
	}
}

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

	//let absTop = e.screenY - aceEditor.offsetHeight

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