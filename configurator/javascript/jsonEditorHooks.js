let previous_values = [];
let saved_value;
let current_value_index = 0;
let undo_button;
let redo_button;
let save_button;
let editor_ready = false;
let root_editor;
let actions_clipboard;

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

function hidePasteButtons(hide) {
	document.getElementsByClassName("json-editor-btntype-paste")
	let result = document.getElementsByClassName("json-editor-btntype-paste");
	for (let i = 0; i < result.length; i++) {
  		result[i].classList.toggle("hide-me", hide)
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
	const errors = editor.validate();
	if (errors.length > 0) {
		alert("There are validation errors in the data");
		return;
	}
	//	console.log(JSON.stringify(convertToBackendFormat(config),null,4));
	//	const data = JSON.stringify(editor.getValue());
	const data = JSON.stringify(convertToBackendFormat(editor.getValue()));
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

	const button_holder = editor.root.theme.getHeaderButtonHolder();
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
//	editor.validate();

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
	let myValue = value;
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
				let reError;
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
			let globError;
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
	 * We do this because validating during editor initialization can be a bad thing.
	 * The main driver code reruns a validate after the editor is loaded and the 
	 * editor_ready flag is set to true.
	 */
	if (!editor_ready) return [];

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

function typeChangeListener() {
	if (this.tab) {
		const element = this.tab;
		const actionType = this.editors[this.type].editors.Basic.editors.type.getValue();
		const disabled = this.editors[this.type].editors.Basic.editors.disabled.getValue();
		element.classList.remove("action-command");
		element.classList.remove("action-menu");
		element.firstChild.classList.remove(iconNames["command"])
		element.firstChild.classList.remove(iconNames["menu"])
		element.classList.add("action-" + actionType);
		element.firstChild.classList.add(iconNames[actionType]);
		element.classList.toggle("disabled", disabled)
	}
}

const exampleAction =
{
	PathPatterns: {
		path_patterns_strict_match: false,
		path_patterns: []
	},
	MimeTypes: {
		mimetypes_strict_match: false,
		mimetypes: []
	},
	FileTypes: {
		filetypes_strict_match: false,
		filetypes: []
	},
	Basic: {
		label: "Example command - open xterm",
		type: "command",
		command_line: "xterm $HOME",
		show_if_true: "",
		cwd: "",
		use_shell: true,
		min_items: 1,
		max_items: 0,
		permissions: "any",
		disabled: false,
		interpolation: "enhanced"
	}
}

class MenuEditor extends JSONEditor.defaults.editors.object {
  onChildEditorChange (editor, eventData) {
    if (editor_ready) this.onChange(true, false, eventData)
  }
  
  setActiveTab(idx) {
	if (idx === 1) this.editors.actions?.resolvePending();
	super.setActiveTab(idx)
  }
}

class ActionsEditor extends JSONEditor.defaults.editors.fmarray {

    onChildEditorChange (editor, eventData) {
      if (editor_ready) this.onChange(true, false, eventData)
    }
  
	setValue(v = [],i) {
		if (v.length == 0 && this.path == "root.actions") {
			v = [ structuredClone(exampleAction) ]
		} 
		
		if (this.path != "root.actions" && v.length > 0) {
			this.pending_actions = v
			v = []
		}
		super.setValue(v, i)
	}

	getValue() {
		return this.pending_actions ?  this.pending_actions : super.getValue()
	}

	resolvePending() {
		if (this.pending_actions) {
			super.setValue(this.pending_actions, true)
			this.pending_actions = null;
		}
	}

	getElementEditor(i) {
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
		 *     BUTTON (a help button)
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
			const helpButton = this.theme.getInfoButton("#action")
			elementEditor.container.insertBefore(helpButton, elementEditor.container.children[4]);

		} else {
			console.log("Unexpected container layout for " + elementEditor.path + " container", elementEditor.container);
		}
		this.jsoneditor.watch(elementEditor.path + '.Basic.type', typeChangeListener.bind(elementEditor));
		this.jsoneditor.watch(elementEditor.path + '.Basic.disabled', typeChangeListener.bind(elementEditor));
		return elementEditor;
	}

	/*
	 * CTRL copy copies to the "clipboard" and we stop the event processor!
	 */
	copyRow(from, to, e) {
		if (e.ctrlKey) {
			const value = window.structuredClone(this.getValue()[from])
			value.Basic.label += " Copy"
			actions_clipboard = value
			hidePasteButtons(false)
			return true
		} else {
			return super.copyRow(from, to, e)
		}
	}

	/*
	 * CTRL delete deletes to the clipboard
	 */
	deleteRow(from, e) {
		let value;
		if (e.ctrlKey) {
			value = window.structuredClone(this.getValue()[from])
		}
		const rc = super.deleteRow(from, e)
		if (value) {
			actions_clipboard = value
			hidePasteButtons(false)
		}
		return rc
	}

	/*
	 * Paste from the clipboard
	 */
	pasteRow() {
		const value = actions_clipboard;
		actions_clipboard = null;

		if (value) {
			this.addRow(value, 0)
			this.refreshValue(true)
			hidePasteButtons(true)
		}
	}

	addControls() {
		super.addControls()
		this._createPasteRowButton()
	}

	_adjustActionsMaxHeight() {
		setTimeout(() => {
			const holder = this.links_holder.parentNode;
			const actions_rect_height = holder.getBoundingClientRect().height
			/*
			 * and the hack :)
			 */
			if (actions_rect_height > 0) {
				const sibling_rect_height = this.row_holder.getBoundingClientRect().height
				const editor_rect_bottom = document.getElementById("editor_holder").getBoundingClientRect().bottom
				const view_port_rect_height = document.getElementsByTagName("html")?.[0]?.getBoundingClientRect().bottom
				const overflow = editor_rect_bottom - (view_port_rect_height - 5)
				const new_max = actions_rect_height - overflow;
				holder.style.setProperty("min-height", sibling_rect_height + "px")
				holder.style.setProperty("max-height",(new_max > sibling_rect_height ? new_max : sibling_rect_height) + "px")
			}				
		}, 5);
	}

	postBuild () {
    	super.postBuild();
		if (this.path == "root.actions") {
			this.links_holder.parentNode.classList.add('a4n-main-actions-list')
			const mObserver = new MutationObserver((list, observer) => {
				this._adjustActionsMaxHeight()
			})
			window.addEventListener('resize', () => {
				clearTimeout(this.resizeTimer); // Clear any previous timer
				this.resizeTimer = setTimeout(() => {
					this._adjustActionsMaxHeight(); // Execute only after resizing stops for 200ms
				}, 200); // Adjust debounce delay as needed (e.g., 100ms, 250ms)
			});
			this._adjustActionsMaxHeight()
			mObserver.observe(this.links_holder, { childList: true })
		}
		hidePasteButtons(true)
    }

	_createPasteRowButton() {
		const button = this.getButton(this.getItemTitle(), 'paste', 'button_paste_row_title', [this.getItemTitle()])
		button.classList.add('json-editor-btntype-paste')
		button.addEventListener('click', (e) => {
			e.preventDefault()
			e.stopPropagation()
			const i = this.rows.length
			const editor = this.pasteRow()
			this.active_tab = this.rows[0].tab
			this.refreshTabs()
			this.refreshValue()
			this.onChange(true)
			this.jsoneditor.trigger('pasteRow', editor)
		})
		this.controls.insertBefore(button, this.controls.children[this.controls.children.length - 1])
		return button
	}
}

class CommandLineEditor extends JSONEditor.defaults.editors.string {
	postBuild(value) {
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
			const use_shell_editor = editor.getEditor(this.path.replace("command_line", "use_shell"))

			input_group.children[0].appendChild(input);
			form_group.appendChild(input_group);

			use_shell_editor.visibleWidget = shell_button;

			// Clicking the button sets the value
			shell_button.onclick = function () {
				use_shell_editor.setValue(!this.classList.contains("boolean-true"));
			};

			// Setting the value changes the style of the button
			use_shell_editor.setValue = function (value, initial) {
				Object.getPrototypeOf(this).setValue.call(this, value, initial);
				this.visibleWidget.classList.toggle("boolean-true", value);
			}
		}
		return rc
	}
}

JSONEditor.defaults.editors.commandLine = CommandLineEditor;
JSONEditor.defaults.editors.actions = ActionsEditor;
JSONEditor.defaults.editors.menu = MenuEditor;

/*
 * Add resolvers
 */
JSONEditor.defaults.resolvers.unshift(schema => {
	if (schema.options?.a4nEditor) {
		return schema.options.a4nEditor
	}
});
