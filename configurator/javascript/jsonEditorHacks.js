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
	let backendConfig = {};
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
