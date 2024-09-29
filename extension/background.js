chrome.runtime.onInstalled.addListener(() => {
    // Create a context menu item for toggling Auto-Screen
    chrome.contextMenus.create({
        id: "toggleAutoScreen",
        title: "Toggle Auto-Screen",
        contexts: ["action"]
    });

    // Initialize autoScreen setting in local storage
    chrome.storage.local.set({ autoScreen: false });
});

chrome.contextMenus.onClicked.addListener((info) => {
    // Handle context menu item click
    if (info.menuItemId === "toggleAutoScreen") {
        // Get the current autoScreen value from local storage
        chrome.storage.local.get(["autoScreen"], (result) => {
            const newStatus = !result.autoScreen;
            // Update the autoScreen value in local storage
            chrome.storage.local.set({ autoScreen: newStatus });
            // Notify the user of the new status
            alert(`Auto-Screen is now ${newStatus ? 'ON' : 'OFF'}`);
        });
    }
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // Check if the page has finished loading
    if (changeInfo.status === "complete") {
        // Get the current autoScreen value from local storage
        chrome.storage.local.get(["autoScreen"], (result) => {
            if (result.autoScreen) {
                // Analyze the page if autoScreen is enabled
                updatePopup(tabId, tab.url);
            }
        });
    }
});

// Function to send a message to the popup
function updatePopup(tabId, url) {
    console.log(tabId, url);
    chrome.runtime.sendMessage({ action: "updatePopup", tabId: tabId, url: url }, (response) => {
        if (chrome.runtime.lastError) {
            // If the popup is not open, store the data in local storage
            if (chrome.runtime.lastError) {
                console.log("Popup is not open");
            }
        }
    });
}