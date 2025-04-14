const primitives = [
	'boolean',
	'number',
	'string'
]

const ui_structs = [
	"Basic",
	"FileTypes",
	"PathPatterns",
	"MimeTypes"
]

/*
 * These two are to do with the fact that a tab in JSON Editor cannot
 * be formatted nicely unless the property information is itself in objects.
 * 
 * So these convert to/from the backend format by doing that
 */
function convertToBackendFormat(internalConfig) {
	var backendConfig = {};
	for (const [key, value] of Object.entries(internalConfig)) {
		if (ui_structs.includes(key)) {
			backendConfig = Object.assign(backendConfig, value)
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
	let internalConfig = {
		actions: [],
		sort: "manual",
		debug: false
	}
	for (const [key, value] of Object.entries(backendConfig)) {
		if (key == "actions") {
			internalConfig.actions = value.map(action => convertActionToFrontendFormat(action));
		} else {
			internalConfig[key] = value;
		}
	}
	console.log("Front end config",JSON.stringify(internalConfig,null,4))
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
		}
	}: {
		Basic: {
			label: "",
			type: "menu",
			sort: "manual",
			disabled: false
		},
		actions:[]
	};
	let basic;
	for (const [key, value] of Object.entries(externlAction)) {
		if (key == "actions") {
			internalAction.actions = value.map(action => convertActionToFrontendFormat(action));
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
		var actionDisabled = this.value.Basic.disabled;
		var existingActionType = this.a4nActionType;
		if (actionDisabled) {
			element.classList.add("disabled");
		} else {
			element.classList.remove("disabled");
		}
		if (actionType != existingActionType) {
			if (existingActionType) {
				element.classList.remove("action-" + existingActionType);
				element.firstChild.classList.remove(iconNames[existingActionType])
			}
			element.classList.add("action-" + actionType);
			element.firstChild.classList.add(iconNames[actionType]);
		}
		this.a4nActionType = actionType;
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
		 *     LABEL (CSS will hide this)
		 *     SELECT (choice between menu and command
		 *     DIV (the object editor for the  menu/command)
		 *     SPAN (the buttons)
		 * 
		 * What we want is
		 *     LABEL
		 *     SPAN
		 *     SELECT
		 *     DIV
		 * 
		 * And, while we are at it, we put an a4n-specific class on the selector
		 * to make it easier to style, and add a tooltip
		 */
		if (returnValue.container.children.length == 4
			&& returnValue.container.children[0].tagName == "LABEL"
			&& returnValue.container.children[1].tagName == "SELECT"
			&& returnValue.container.children[2].tagName == "DIV"
			&& returnValue.container.children[3].tagName == "SPAN"
		) {
			returnValue.container.children[1].setAttribute("title", "Select the type of action");
			returnValue.container.children[1].classList.add("a4n-action-type-chooser");
			returnValue.container.insertBefore(returnValue.container.children[3], returnValue.container.children[1]);
		} else {
			console.log("Unexpected container layout for " + returnValue.path + " container", returnValue.container);
		}
	}
	return returnValue;
}

/*
 * Part 3
 *
 * We want a tooltip on the opt-in checkboxes.
 * 
 * Complicated (but interesting) way - use an ::after:hover CSS setup
 * Easy way: just ad a title
 */
const abstractEditorPrototype = Object.getPrototypeOf(JSONEditor.defaults.editors.object.prototype);
const defaultSetOptInCheckbox = abstractEditorPrototype.setOptInCheckbox
abstractEditorPrototype.setOptInCheckbox = function (value) {
	var returnValue = defaultSetOptInCheckbox.bind(this)(value);
	this.optInCheckbox.setAttribute("title", "Enable/disable optional setting in the configuration");
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
defaultPostBuild = JSONEditor.AbstractEditor.prototype.postBuild
JSONEditor.AbstractEditor.prototype.postBuild = function (value) {
	const returnValue = defaultPostBuild.bind(this)(value);
	if (this.path.endsWith("_strict_match")) {
		const form_group = this.container.children[0];
		form_group.classList.add("a4n-strict-match");
	}
	return returnValue
}
