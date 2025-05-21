/**
 * Global variable to store the ids of the status of the current dragged ace editor.
 */
let draggingAceEditor = false;
let draggingEditorTopOffset = 0;
let aceEditorResizeBar;
let aceEditorWrapper;
let aceEditor;
let mainCardHolder;

let undoDisabled;
let redoDisabled;
let saveDisabled;

/*
 * And the way we handle the JSON editor
 */
class TopLevelObjectEditor extends JSONEditor.defaults.editors.object {
	showEditJSON () {
		if (!this.editjson_holder) return
		this.hideAddProperty()

		/* Start the textarea with the current value */
		this.ace_editor.setValue(JSON.stringify(convertToBackendFormat(this.getValue()), null, 4));

		/* Disable the rest of the form while editing JSON */
		this.disable()

		this.editjson_holder.style.display = ''
		this.editjson_control.disabled = false
		this.editing_json = true

		let windowInnerHeight = window.innerHeight;
		let screenUsed = Math.round(mainCardHolder.getBoundingClientRect().bottom);
		let cardHeight = mainCardHolder.offsetHeight;

		let wrapperMaxHeight = windowInnerHeight - screenUsed + cardHeight - 20;

		aceEditorWrapper.style["min-height"] = `${cardHeight < wrapperMaxHeight ? cardHeight : wrapperMaxHeight}px`;

		let wrapperHeight = Math.round(aceEditorWrapper.getBoundingClientRect().height);
		let editorHeight = Math.round(aceEditor.getBoundingClientRect().height);

		let editorMaxHeight = wrapperMaxHeight - (wrapperHeight - editorHeight);

		aceEditor.style["max-height"] = `${editorMaxHeight}px`
		aceEditor.style["height"] = `${editorMaxHeight}px`

		/*
		* Now hide the main card holder and disable the undo/redo/save buttons
		*/
		mainCardHolder.firstElementChild.style.display = 'none';
		undoDisabled = undo_button.disabled;
		redoDisabled = redo_button.disabled;
		saveDisabled = save_button.disabled;

		undo_button.disabled = true;
		redo_button.disabled = true;
		save_button.disabled = true;

		this.ace_editor.resize()
	}

	saveJSON () {
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

	hideEditJSON () {
		if (!this.editjson_holder) return
		if (!this.editing_json) return

		this.editjson_holder.style.display = 'none'
		this.enable()
		this.editing_json = false

		undo_button.disabled = undoDisabled;
		redo_button.disabled = redoDisabled;
		save_button.disabled = saveDisabled;

		mainCardHolder.firstElementChild.style.display = '';
	}
}

JSONEditor.defaults.editors.topLevelObject = TopLevelObjectEditor;

function aceDragMouseMove (e) {
	// editor height
	const eheight = e.pageY - draggingEditorTopOffset;
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

	aceEditorWrapper.childNodes[3].remove();
	aceEditorWrapper.childNodes[1].remove();
	aceEditorWrapper.firstElementChild.remove();
	aceEditorWrapper.append(aceEditor);
	aceEditorWrapper.append(aceEditorResizeBar);

	mainCardHolder = editor.root.container.getElementsByClassName('card-body')[0];

	editor.root.ace_editor = ace.edit("ace-editor", {
		mode: "ace/mode/json",
		printMargin: false
	});
	editor.root.ace_editor.setTheme("ace/theme/chrome");
	editor.root.ace_editor.session.setTabSize(4);
	makeAceEditorResizable(editor.root.ace_editor);
}