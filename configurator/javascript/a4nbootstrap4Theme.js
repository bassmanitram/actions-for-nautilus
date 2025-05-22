/*********************
 * *******************
 * *******************
 * 
 * To get some of the behavior we want we have to extend the default
 * Bootstrap4 theme class
 * 
 * *******************
 * *******************
 *********************/
class a4nbootstrap4Theme extends JSONEditor.defaults.themes.bootstrap5 {
	constructor(jsoneditor) {
		super(jsoneditor);
		this.openHelp = function (event) {
			const targetFragment = event.srcElement.getAttribute('data-help-label');
			window.showHelp && showHelp(targetFragment);
		};
	}

	/*
	 * We want a 3/9 split instead of a 2/10 split used by the superclass
	 */
	getTabHolder (propertyName) {
		const el = document.createElement('div')
		const pName = (typeof propertyName === 'undefined') ? '' : propertyName
		el.innerHTML = `<div class='col-md-3' id='${pName}'><ul class='nav flex-column nav-pills'></ul></div><div class='col-md-9'><div class='tab-content' id='${pName}'></div></div>`
		el.classList.add('row')
		return el
	}

	/*
	 * Add a click handler to the info button
	 */
	getInfoButton(text) {
		const info = text.startsWith("#") ? (infoText[text] ? infoText[text] : { text }) : { text };
		const button = super.getInfoButton(info.text);
		button.addEventListener('click', this.openHelp, false);
		if (info.help_label) {
			button.setAttribute('data-help-label', info.help_label);
		}
		return button;
	}

	/*
	 * We want to insert an icon before the tab selector label text 
	 * and have activation/deactivation classes associated with the 
	 * view
	 */
	getTab(text, id) {
		const element = super.getTab(text, id);
		if (/\.actions\.[0-9]+$/.test(id)) {
			const ite = document.createElement('i');
			ite.classList.add("fas")
			element.insertBefore(ite, element.firstChild);
			element.classList.add("action-command");
		}
		return element;
	}

	/*
	 * The theme "markTabActive" and markTabInactive functions assume that first
	 * child element in the link is the anchor ... but it's not any more - it's the <i>
	 * 
	 * So we have to "correct" those two functions - these are copies that are
	 * so-corrected
	 */
	markTabActive(row) {
		if (row.tab.classList.contains("action-command") || row.tab.classList.contains("action-menu")) {
			row.tab.firstChild.nextSibling.classList.add('active');
			row.tab.classList.add('active');
		} else {
			row.tab.firstChild.classList.add('active');
		}

		if (typeof row.rowPane !== 'undefined') {
			row.rowPane.classList.add('active');
		} else {
			row.container.classList.add('active');
		}
	}

	markTabInactive(row) {
		if (row.tab.classList.contains("action-command")
			|| row.tab.classList.contains("action-menu")) {
			row.tab.firstChild.nextSibling.classList.remove('active');
			row.tab.classList.remove('active');
		} else {
			row.tab.firstChild.classList.remove('active');
		}

		if (typeof row.rowPane !== 'undefined') {
			row.rowPane.classList.remove('active');
		} else {
			row.container.classList.remove('active');
		}
	}
}
