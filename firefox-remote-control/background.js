// Background script for Firefox remote control
let port = null;

// Connect to native messaging host
function connect() {
  port = browser.runtime.connectNative("browser_remote_control");

  port.onMessage.addListener((message) => {
    console.log("Received command:", message);
    handleCommand(message);
  });

  port.onDisconnect.addListener(() => {
    console.log("Disconnected from native host");
    port = null;
  });

  console.log("Connected to native messaging host");
}

// Handle commands from Python
async function handleCommand(command) {
  try {
    let response = { id: command.id, success: true };

    switch(command.action) {
      case "open_url":
        await browser.tabs.create({ url: command.url });
        response.message = "URL opened";
        break;

      case "get_html":
        const tabs = await browser.tabs.query({ active: true, currentWindow: true });
        const tab = tabs[0];
        const html = await browser.tabs.executeScript(tab.id, {
          code: "document.documentElement.outerHTML"
        });
        response.html = html[0];
        break;

      case "execute_script":
        const activeTabs = await browser.tabs.query({ active: true, currentWindow: true });
        const activeTab = activeTabs[0];
        const result = await browser.tabs.executeScript(activeTab.id, {
          code: command.code
        });
        response.result = result[0];
        break;

      case "get_url":
        const currentTabs = await browser.tabs.query({ active: true, currentWindow: true });
        response.url = currentTabs[0].url;
        break;

      case "close_tab":
        const tabsToClose = await browser.tabs.query({ active: true, currentWindow: true });
        await browser.tabs.remove(tabsToClose[0].id);
        response.message = "Tab closed";
        break;

      default:
        response.success = false;
        response.error = "Unknown action: " + command.action;
    }

    if (port) {
      port.postMessage(response);
    }
  } catch (error) {
    if (port) {
      port.postMessage({
        id: command.id,
        success: false,
        error: error.message
      });
    }
  }
}

// Auto-connect on startup
connect();
