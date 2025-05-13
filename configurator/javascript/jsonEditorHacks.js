const primitives = [
	'boolean',
	'number',
	'string'
]

const basicDefaults = {
	show_if_true: "",
	cwd: "",
	use_shell: false,
	min_items: 1,
	max_items: 0,
	permissions: "any",
	disabled: false,
	sort: "manual"
}

/*
 * Flatten UI model to backend model and eliminate defaults
 */
function basicToBackend(target, source) {
	for (const [key, value] of Object.entries(source)) {
		let dflt = basicDefaults[key]
		if (dflt == undefined || dflt != value) {
			target[key] = value;
		}
	}
	if (target.type == "command") {
		if (target.interpolation != "original") {
			target.use_old_interpolation = false
		}
		delete target.interpolation
	}
	return target
}

function nonBasicToBackend(target, source, info) {
	if (source[info.prefix].length > 0) {
		target[info.prefix] = source[info.prefix]
	}
	const strict_match_key = `${info.prefix}_strict_match`;
	if (source[strict_match_key]) {
		target[strict_match_key] = source[strict_match_key]
	}
	return target
}

const ui_structs = {
	"Basic": { toBackend: basicToBackend, info: null },
	"FileTypes": { toBackend: nonBasicToBackend, info: { prefix: "filetypes" } },
	"PathPatterns": { toBackend: nonBasicToBackend, info: { prefix: "path_patterns" } },
	"MimeTypes": { toBackend: nonBasicToBackend, info: { prefix: "mimetypes" } },
}

let use_shell_button_template;
function get_use_shell_button_template() {
	if (!use_shell_button_template) { 
		use_shell_button_template = document.querySelector("#use_shell_button")
	}
	return use_shell_button_template
}

/*
 * These two are to do with the fact that a tab in JSON Editor cannot
 * be formatted nicely unless the property information is itself in objects.
 * 
 * So these convert to/from the backend format by doing that
 */
function convertToBackendFormat(internalConfig) {
	var backendConfig = {};
	for (const [key, value] of Object.entries(internalConfig)) {
		const transformer = ui_structs[key]
		if (transformer) {
			backendConfig = (transformer.toBackend)(backendConfig, value, transformer.info)
		} else if (key == "actions") {
			backendConfig.actions = value.map(convertToBackendFormat);
		} else {
			backendConfig[key] = value;
		}
	}
	return backendConfig;
}

// Kick of the model transform from external to internal
function convertToFrontendFormat(backendConfig) {
	const internalConfig = {
		actions: [],
		sort: "manual",
		debug: false
	}
	for (const [key, value] of Object.entries(backendConfig)) {
		if (key == "actions") {
			internalConfig.actions = value.map(convertActionToFrontendFormat);
		} else {
			internalConfig[key] = value;
		}
	}
	return internalConfig;
}

// Return the current action
function convertActionToFrontendFormat(externlAction) {
	const is_command = externlAction.type == "command";
	const internalAction = is_command ? {
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
			label: "",
			type: "command",
			command_line: "",
			show_if_true: "",
			cwd: "",
			use_shell: false,
			min_items: 1,
			max_items: 0,
			permissions: "any",
			disabled: false,
			interpolation: "original"
		}
	} : {
		Basic: {
			label: "",
			type: "menu",
			sort: "manual",
			disabled: false
		},
		actions:[]
	};
	for (const [key, value] of Object.entries(externlAction)) {
		if ((!is_command) && key == "actions") {
			internalAction.actions = value.map(convertActionToFrontendFormat);
		} else if (is_command && key == "use_old_interpolation") {
			internalAction.Basic.interpolation = value ? "original" : "improved"
		} else if (is_command && key.startsWith("mimetypes")) {
			internalAction.MimeTypes[key] = value
		} else if (is_command && key.startsWith("filetypes")) {
			internalAction.FileTypes[key] = value
		} else if (is_command && key.startsWith("path_patterns")) {
			internalAction.PathPatterns[key] = value
		} else if (primitives.includes(typeof value)) {
			internalAction.Basic[key] = value;
		}
	}
	return internalAction;
}

/*********************
 * *******************
 * *******************
 * 
 * How to fiddle with the editor DOM!
 *
 * *******************
 * *******************
 *********************/

/*
 * Part 1
 *
 * The tab selectors have icons and classes we can use - now we have to
 * switch them as necessary
 */
defaultMultiRefreshHeaderText = JSONEditor.defaults.editors.multiple.prototype.refreshHeaderText;
JSONEditor.defaults.editors.multiple.prototype.refreshHeaderText = function (value) {
	var returnValue = defaultMultiRefreshHeaderText.bind(this)(value);
	if (/\.actions\.[0-9]+$/.test(this.path) && this.tab) {
		var element = this.tab;
		var actionType = this.value.Basic.type;
		var existingActionType = this.a4nActionType;
		if (actionType != existingActionType) {
			if (existingActionType) {
				element.classList.remove("action-" + existingActionType);
				element.firstChild.classList.remove(iconNames[existingActionType])
			}
			element.classList.add("action-" + actionType);
			element.firstChild.classList.add(iconNames[actionType]);
		}
		this.a4nActionType = actionType;
		element.classList.toggle("disabled", this.value.Basic.disabled)
	}
	return returnValue;
}

/*
 * Part 2
 *
 * Action object editors also need some reordering
 */
defaultArrayGetElementEditor = JSONEditor.defaults.editors.array.prototype.getElementEditor;
JSONEditor.defaults.editors.array.prototype.getElementEditor = function (value) {
	var returnValue = defaultArrayGetElementEditor.bind(this)(value);
	if (/\.actions\.[0-9]+$/.test(returnValue.path)) {
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
		if (returnValue.container.children.length == 5
			&& returnValue.container.children[0].tagName == "B"
			&& returnValue.container.children[1].tagName == "LABEL"
			&& returnValue.container.children[2].tagName == "SELECT"
			&& returnValue.container.children[3].tagName == "DIV"
			&& returnValue.container.children[4].tagName == "SPAN"
		) {
			returnValue.container.children[2].setAttribute("title", "Select the type of action");
			returnValue.container.children[2].classList.add("a4n-action-type-chooser");
			returnValue.container.insertBefore(returnValue.container.children[4], returnValue.container.children[2]);
		} else {
			console.log("Unexpected container layout for " + returnValue.path + " container", returnValue.container);
		}
	}
	return returnValue;
}

/* 
 * Part 4
 *
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
 * Part 5
 *
 * Custom validator for min_items and max_items. Must return an array of errors or an empty array if valid.
 */
JSONEditor.defaults.custom_validators.push((schema, value, path) => {
	/*
	 * We check the Basic block for min_items/max_items consistency
	 */
	const errors = [];

	if (path.endsWith(".Basic")
	&& path.includes(".actions.")
	&& value.type == 'command'
	&& typeof value.min_items == 'number'
	&& typeof value.max_items == 'number'
	&& value.min_items > 1
	&& value.max_items > 0
	&& value.min_items > value.max_items) {
		//console.log(path, value);
		/*
		 * Report the error for min_items
		 */
		errors.push({
			path: path,
			property: 'min_items',
			message: `min_items must be less than or equal to max_items if max_items is activated and greater than zero`
		});
	}
	return errors;
});

/*
 * Part 6
 *
 * The "strict match" switches need to be tweaked!
 */
defaultSelectPostBuild = JSONEditor.defaults.editors.select.prototype.postBuild;
JSONEditor.defaults.editors.select.prototype.postBuild = function (value) {
	const returnValue = defaultSelectPostBuild.bind(this)(value);
	if (this.path.endsWith("_strict_match")) {
		const form_group = this.container.children[0];
		form_group.classList.add("a4n-strict-match");
	}
	return returnValue
}

/*
 * Part 7
 *
 * The use_shell option is boolean, but it's nicer as a prelude
 * button on the command_line - so this is where we do that
 * (for this to work, use_shell MUST be set up before command_line,
 * hence the ordering in the UI schema)
 */ 
defaultStringPostBuild = JSONEditor.defaults.editors.string.prototype.postBuild;
JSONEditor.defaults.editors.string.prototype.postBuild = function (value) {
	const returnValue = defaultStringPostBuild.bind(this)(value);
	if (this.path.endsWith("Basic.command_line")) {
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
	}
	return returnValue
}

/*
 * Prebuild is wrong
 */
//const defaultArrayPreBuild = JSONEditor.defaults.editors.array.prototype.preBuild;
JSONEditor.defaults.editors.array.prototype.preBuild = function() {
//	super.preBuild()

    this.rows = []
    this.row_cache = []

    this.hide_delete_buttons = _check_boolean_option(this.options.disable_array_delete, this.jsoneditor.options.disable_array_delete, true)
    this.hide_delete_all_rows_buttons = this.hide_delete_buttons || _check_boolean_option(this.options.disable_array_delete_all_rows, this.jsoneditor.options.disable_array_delete_all_rows, true)
    this.hide_delete_last_row_buttons = this.hide_delete_buttons || _check_boolean_option(this.options.disable_array_delete_last_row, this.jsoneditor.options.disable_array_delete_last_row, true)
    this.hide_move_buttons = _check_boolean_option(this.options.disable_array_reorder, this.jsoneditor.options.disable_array_reorder, true)
    this.hide_add_button = _check_boolean_option(this.options.disable_array_add, this.jsoneditor.options.disable_array_add, true)
    this.show_copy_button = _check_boolean_option(this.options.enable_array_copy, this.jsoneditor.options.enable_array_copy, true)
    this.array_controls_top = _check_boolean_option(this.options.array_controls_top, this.jsoneditor.options.array_controls_top, true)
	console.log(this)
}

/*
 * Too long to use a piggyback, so we replace!
 */
//const defaultCreateCopyButton = JSONEditor.defaults.editors.array.prototype._createCopyButton
JSONEditor.defaults.editors.array.prototype._createCopyButton = function(i, holder) {
    const button = this.getButton(this.getItemTitle(), 'copy', 'button_copy_row_title', [this.getItemTitle()])
    button.classList.add('copy', 'json-editor-btntype-copy')
    button.setAttribute('data-i', i)
    button.addEventListener('click', e => {
	  console.log(this);
	  const value = this.getValue();
	  const path = this.options.path;
      e.preventDefault();
      e.stopPropagation();

      const i = e.currentTarget.getAttribute('data-i') * 1
	  const newOne = value[i]
	  value.push(newOne)

      this.setValue(value)
//	  this.active_tab = this.rows[i + 1].tab
//      this.refreshValue(true)
//      this.onChange(true)
	  this.jsoneditor.getEditor(`${path}.${value.length - 1}.Basic.label`).setValue(newOne.Basic.label + " Copy")
      this.jsoneditor.trigger('copyRow', this.rows[i + 1])
    })

    holder.appendChild(button)
    return button
}

function _check_boolean_option(local, global, value) {
    return typeof local ==  'boolean' ? local : global == value
}
