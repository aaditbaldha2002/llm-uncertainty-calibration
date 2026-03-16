chrome.action.onClicked.addListener((tab) => {
    const url = tab.url;
    if (!url.startsWith("http") && !url.startsWith("https")) {
        alert("TruthLens cannot run on internal Chrome pages.");
        return;
    }

    // Prevent duplicate injection if container already exists
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => document.getElementById("truthlens-container") !== null
    }, (results) => {
        if (results && results[0].result) return;
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ["content.js"]
        });
    });
});