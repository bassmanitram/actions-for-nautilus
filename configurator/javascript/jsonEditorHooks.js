let previous_values = [];
let saved_value;
let current_value_index = 0;
let undo_button;
let redo_button;
let save_button;
let editor_ready = false;
let root_editor;

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

function toggleJSONEditor(e) {
	e.preventDefault();
	e.stopPropagation();
	editor.root.toggleEditJSON();
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
//	console.log(JSON.stringify(convertToBackendFormat(config),null,4));
//	var data = JSON.stringify(editor.getValue());
	var data = JSON.stringify(convertToBackendFormat(editor.getValue()));
	//console.log(data);
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
	const new_value = JSON.stringify(editor.getValue());
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
		//console.log(JSON.stringify(editor.getValue(),null,4));
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
	 * Create a edit JSON config button and disable it
	 */
	json_button = editor.root.getButton('JSON', 'edit', 'JSON');
	json_button.classList.add("a4n-edit-json");
//	json_button.classList.add("json-editor-btntype-editjson")
	json_button.addEventListener('click', toggleJSONEditor, false);
	button_holder.appendChild(json_button);

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
	editor_ready = true;
	editor.validate();

	/*
	 * Seriously hack the main object JSON editor
	 *
	 * We move it to the main card container, set its textarea height to the
	 * height of that, change classes etc.
	 */
	let cardHolder = editor.root.container.getElementsByClassName('card-body')[0];
	cardHolder.appendChild(editor.root.editjson_holder);
	editor.root.editjson_holder.classList.add("a4n-editjson_holder");

	/*
	 * And NOW replace the JSON editor text area with the ACE editor
	 */
	initAceEditor(editor);
}

/* 
 * Custom validator for glob and regular expression patterns. Must return an array of errors or an empty array if valid.
 */
JSONEditor.defaults.custom_validators.push((schema, value, path) => {
	/*
	 * We do this because validating during editor initialization can be a bad thing.
	 * The main driver code reruns a validate after the editor is loaded and the 
	 * editor_ready flag is set to true.
	 */
	if (!editor_ready) return [];
	var myValue = value;
	const errors = [];
	if (schema.format === "pattern") {
		if (myValue.startsWith("!")) {
			/*
			 * It's a negation pattern - remove for further checking
			 */
			myValue = myValue.substring(1);
		}
		if (myValue.trim().length < 1) {
			errors.push({
				path: path,
				property: 'path_patterns',
				message: 'Cannot be empty'
			});
		} else if (myValue.startsWith("re:")) {
			myValue = myValue.substring(3);
			if (myValue.trim().length < 1) {
				errors.push({
					path: path,
					property: 'path_patterns',
					message: 'Regular expression cannot be empty'
				});
			} else {
				var reError = null;
				try {
					/*
					 * Python REs and JS REs are both based on Perl REs, meaning that for
					 * all but the most complex cases they should be equivalent - so a simple
					 * "compile" here using JS RegExp should be enough to ensure that an RE
					 * is usable in the implementation (which is in python)
					 */
					new RegExp(myValue);
				} catch (e) {
					reError = e;
				}
				if (reError) {
					errors.push({
						path: path,
						property: 'path_patterns',
						message: `Invalid regular expression pattern: ${reError.message}`
					});

				}
			}
		} else {
			var globError = null;
			try {
				/*
				 * Python fnmatch is basically the same as the -wholename parameter of the UNIX find
				 * command ... and no library in JS is that simple! So we do our own home-baked conversion
				 * to a regular expression, which is, effectively:
				 * 
				 *     - . becomes \.
				 *     - * becomes .*
				 *     - ? becomes .
				 *     - [! becomes [^
				 *     - everything else remains the same
				 */
				const globRE = new RegExp("^" + myValue.replaceAll(".", "\\.").replaceAll("*", ".*").replaceAll("?", ".").replace("[!", "[^") + "$");
			} catch (e) {
				globError = e;
			}
			if (globError) {
				errors.push({
					path: path,
					property: 'path_patterns',
					message: `Invalid glob expression pattern: ${globError.message}`
				});
			}
		}
	}
	return errors;
});

/* 
 * Custom validator for min_items and max_items. Must return an array of errors or an empty array if valid.
 */
JSONEditor.defaults.custom_validators.push((schema, value, path) => {
	/*
	 * We check the Basic block for min_items/max_items consistency
	 */
	const errors = [];

	if (value.type == 'command'
	&& typeof value.min_items == 'number'
	&& typeof value.max_items == 'number'
	&& value.max_items > 0
	&& value.min_items > value.max_items) {
		//console.log(path, value);
		/*
		 * Report the error for min_items
		 */
		errors.push({
			path: path,
			property: 'min_items',
			message: `min_items must be less than or equal to max_items if max_items is greater than zero`
		});
	}
	return errors;
});

function typeChangeListener(parm) {
	if (this.tab) {
		const element = this.tab;
		const actionType = this.editors[this.type].editors.Basic.editors.type.getValue();
		const disabled = this.editors[this.type].editors.Basic.editors.disabled.getValue();
		console.log("CHANGE", actionType, disabled)
		element.classList.remove("action-command");
		element.classList.remove("action-menu");
		element.firstChild.classList.remove(iconNames["command"])
		element.firstChild.classList.remove(iconNames["menu"])
		element.classList.add("action-" + actionType);
		element.firstChild.classList.add(iconNames[actionType]);
		element.classList.toggle("disabled", disabled)
	}
}

class ActionsEditor extends JSONEditor.defaults.editors.array {
	getElementEditor (i) {
		const elementEditor = super.getElementEditor(i);
		/*
		 * THIS is the completed container that we need to swap around a bit
		 *
		 * There should be four elements:
		 *     B (CSS will hide this)
		 *     LABEL (also hidden)
		 *     SELECT (choice between menu and command
		 *     DIV (the object editor for the  menu/command)
		 *     SPAN (the buttons)
		 * 
		 * What we want is
		 *     B
		 *     LABEL
		 *     SPAN
		 *     SELECT
		 *     DIV
		 * 
		 * And, while we are at it, we put an a4n-specific class on the selector
		 * to make it easier to style, and add a tooltip
		 */
		if (elementEditor.container.children.length == 5
			&& elementEditor.container.children[0].tagName == "B"
			&& elementEditor.container.children[1].tagName == "LABEL"
			&& elementEditor.container.children[2].tagName == "SELECT"
			&& elementEditor.container.children[3].tagName == "DIV"
			&& elementEditor.container.children[4].tagName == "SPAN"
		) {
			elementEditor.container.children[2].setAttribute("title", "Select the type of action");
			elementEditor.container.children[2].classList.add("a4n-action-type-chooser");
			elementEditor.container.insertBefore(elementEditor.container.children[4], elementEditor.container.children[2]);
		} else {
			console.log("Unexpected container layout for " + elementEditor.path + " container", elementEditor.container);
		}
		this.jsoneditor.watch(elementEditor.path + '.Basic.type',typeChangeListener.bind(elementEditor));
		this.jsoneditor.watch(elementEditor.path + '.Basic.disabled',typeChangeListener.bind(elementEditor));
		return elementEditor;
	}
}

class CommandLineEditor extends JSONEditor.defaults.editors.string {
	postBuild (value) {
		const rc = super.postBuild(value);
		const form_group = this.container.children[0];
		form_group.classList.add("a4n-command-line");
		const input = form_group.children[2];
		if (input.tagName == "INPUT") {
			/*
				* Add the prepend button for the use_shell option
				* and hook it up to the editor
				*/
			const input_group = get_use_shell_button_template().content.cloneNode(true)
			const shell_button = input_group.querySelector("button");
			const use_shell_editor = editor.getEditor(this.path.replace("command_line","use_shell"))

			input_group.children[0].appendChild(input);
			form_group.appendChild(input_group);

			use_shell_editor.visibleWidget = shell_button;

			// Clicking the button sets the value
			shell_button.onclick = function(){
				use_shell_editor.setValue(!this.classList.contains("boolean-true"));
			};	

			// Setting the value changes the style of the button
			use_shell_editor.setValue = function(value, initial) {
				Object.getPrototypeOf(this).setValue.call(this, value, initial);
				this.visibleWidget.classList.toggle("boolean-true",value);
			}
		}
		return rc
	}
}

JSONEditor.defaults.editors.commandLine = CommandLineEditor;
JSONEditor.defaults.editors.actions = ActionsEditor;

/*
 * Add resolvers
 */
JSONEditor.defaults.resolvers.unshift(schema => {
	if(schema.options?.a4nEditor) {
		return schema.options.a4nEditor
	}
});
