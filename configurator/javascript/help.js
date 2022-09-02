/*
 * Stuff that manages the help functionality
 */

let helpShowing = false;
let helpButton;
function setHelpButton(button) {
	helpButton = button
}

function showHelp(fragment) {
	parent.showHelp && parent.showHelp(fragment);
	helpButton && (helpButton.innerText = "Hide Help")
	helpShowing = true;
}

function hideHelp() {
	parent.hideHelp && parent.hideHelp();
	helpButton && (helpButton.innerText = "Show Help")
	helpShowing = false;
}

function toggleHelp(fragment) {
	if (helpShowing) {
		hideHelp();
	} else {
		showHelp(fragment);
	}
}
