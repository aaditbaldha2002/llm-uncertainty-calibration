chrome.action.onClicked.addListener((tab) => {
    const url = tab.url;
    if (!url.startsWith("http") && !url.startsWith("https")) {
        alert("TruthLens cannot run on internal Chrome pages.");
        return;
    }
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ["content.js"]
    });
});