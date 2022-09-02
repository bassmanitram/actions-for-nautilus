
let previous_values = [];
let saved_value;
let current_value_index = 0;
let undo_button;
let redo_button;
let save_button;

function setUndoRedoButtonStates() {
	undo_button.disabled = (current_value_index == 0);
	redo_button.disabled = (current_value_index == (previous_values.length - 1));
}

function setEditorValueFromPreviousValues(editor) {
	editor.setValue(JSON.parse(previous_values[current_value_index]));
	setUndoRedoButtonStates();
}

function undo(e) {
	if (current_value_index > 0) {
		current_value_index--;
		setEditorValueFromPreviousValues(editor);
	}
}

function redo(e) {
	if (current_value_index < (previous_values.length - 1)) {
		current_value_index++;
		setEditorValueFromPreviousValues(editor);
	}
}

function saveConfig(e) {
	e.preventDefault();
	editor.disable();
	save_button.disabled = true;
	var errors = editor.validate();
	if (errors.length > 0) {
		alert("There are validation errors in the data");
		return;
	}
	var data = JSON.stringify(editor.getValue());
	$.ajax({
		url: '/config',
		type: 'post',
		data: data,
		headers: {
			"Content-Type": "application/json"
		},
		error: function (xh, msg, e) {
			console.error(msg, e);
			save_button.disabled = false;
			editor.enable();
			alert("An error ocurred when trying to save the configuration");
		},
		success: function (response) {
			saved_value = data;
			editor.enable();
		}
	});
}

function configChanged(e) {
	new_value = JSON.stringify(editor.getValue());
	if (previous_values[current_value_index] != new_value) {
		/*
		 * The editor changed outside of undo-redo
		 * Everything after the current index is lost
		 * then this change is pushed.
		 */
		previous_values = previous_values.slice(0, current_value_index + 1);
		current_value_index = previous_values.push(new_value) - 1;
		setUndoRedoButtonStates();
	} else {
		//console.log("Editor didn't really change!")
	}
	if (editor.validation_results.length > 0) {
		console.log(editor.validation_results);
		save_button.disabled = true
	} else {
		save_button.disabled = (new_value == saved_value)
	}
}

function finalizeEditorConfig(e) {
	saved_value = JSON.stringify(editor.getValue());
	previous_values[0] = saved_value;

	var button_holder = editor.root.theme.getHeaderButtonHolder();
	editor.root.header.parentNode.insertBefore(button_holder, editor.root.header.nextSibling);

	/*
	 * Create an undo button - icon only
	 */
	undo_button = editor.root.getButton('Undo', 'undo', 'Undo');
	undo_button.classList.add("undoredo");
	undo_button.addEventListener('click', undo);
	button_holder.appendChild(undo_button);

	/*
	 * Create a redo button - icon only
	 */
	redo_button = editor.root.getButton('Redo', 'redo', 'Redo');
	redo_button.classList.add("undoredo");
	redo_button.addEventListener('click', redo);
	button_holder.appendChild(redo_button);

	/*
	 * Set undo/redo button state (disabled at this point)
	 */
	setUndoRedoButtonStates();

	/*
	 * Create a save config button and disable it
	 */
	save_button = editor.root.getButton('Save', 'save', 'Save');
	save_button.addEventListener('click', saveConfig, false);
	save_button.disabled = true
	button_holder.appendChild(save_button);

	/*
	 * Set the help button if the hook functions exist
	 */
	if (window.toggleHelp && window.setHelpButton) {
		let help_button = editor.root.getButton('Show Help', 'refresh', 'Show Help');
		help_button.addEventListener('click', toggleHelp, false);

		/*
		 * Add the buttons to the top of the page
		 */
		button_holder.appendChild(help_button);
		setHelpButton(help_button);
	}

	/*
	 * Wire up the change watcher
	 */
	editor.on('change', configChanged);
}
