function ToggleAddon() {
    console.log("Toggle")
    chrome.extension.sendMessage({type: "ToggleAddon"}, function(response) {});
    window.close()
}

document.getElementById('ToggleButton').addEventListener('click', ToggleAddon);