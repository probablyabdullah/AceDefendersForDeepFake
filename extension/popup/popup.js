const btn = document.getElementById("checkButton");
const autoScreenCheckbox = document.getElementById("autoScreenCheckbox");
const includeImagesCheckbox = document.getElementById("includeImagesCheckbox");
const includeVideosCheckbox = document.getElementById("includeVideosCheckbox");

// Load the current settings and set the checkbox states
chrome.storage.local.get(
  ["autoScreen", "includeImages", "includeVideos"],
  (result) => {
    autoScreenCheckbox.checked = result.autoScreen;
    includeImagesCheckbox.checked = result.includeImages;
    includeVideosCheckbox.checked = result.includeVideos;
  },
);

chrome.tabs.query({ currentWindow: true, active: true }, function(tabs) {
  const tabId = tabs[0].id;
  const url = tabs[0].url;

  chrome.storage.local.get([`lastResult_${tabId}`], (result) => {
    if (result[`lastResult_${tabId}`]) {
      displayResult(result[`lastResult_${tabId}`]);
    }
  });

  btn.addEventListener("click", function() {
    const includeImages = includeImagesCheckbox.checked;
    const includeVideos = includeVideosCheckbox.checked;
    analyzePage(tabId, url, includeImages, includeVideos);
  });
});

autoScreenCheckbox.addEventListener("change", function() {
  chrome.storage.local.set({ autoScreen: autoScreenCheckbox.checked });
});

includeImagesCheckbox.addEventListener("change", function() {
  chrome.storage.local.set({ includeImages: includeImagesCheckbox.checked });
});

includeVideosCheckbox.addEventListener("change", function() {
  chrome.storage.local.set({ includeVideos: includeVideosCheckbox.checked });
});

function analyzePage(tabId, url, includeImages, includeVideos) {
  btn.disabled = true;
  btn.innerHTML = "Checking...";

  fetch("http://127.0.0.1:8080/fact-check", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      url: url,
      image: includeImages,
      video: includeVideos,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      displayResult(data);
      console.log(data);
      chrome.storage.local.set({ [`lastResult_${tabId}`]: data });
    });
}

function displayResult(data) {
  const resultIcon = document.getElementById("resultIcon");
  const output = document.getElementById("output");

  resultIcon.innerHTML = "";
  output.innerHTML = "";

  console.log(data);

  if (data.final_ai_score == "REAL") {
    resultIcon.innerHTML = "✅";
    resultIcon.classList.add("green-tick");
  } else {
    resultIcon.innerHTML = "❌";
    resultIcon.classList.add("red-cross");
  }

  const textResult = data.text
    ? createResultItem("Text Analysis", data.text)
    : "";
  const imageResult = data.image
    ? createResultItem("Image Analysis", data.image)
    : "";
  const videoResult = data.video
    ? createResultItem("Video Analysis", data.video)
    : "";

  const final_blockchain_score = data.final_blockchain_score
    ? data.final_blockchain_score
    : "Not Concluded";

  const resultText = document.createElement("div");
  resultText.innerHTML = `
        <div class="result-item">
            <strong>URL:</strong> <a href="${data.url}" target="_blank">${truncateURL(data.url)}</a>
        </div>
        ${textResult}
        ${imageResult}
        ${videoResult}
        <div class="result-item">
            <strong>Final Blockchain Prediction:</strong> ${final_blockchain_score}<br>
        </div>
        <div class="result-item">
            <strong>Final AI Prediction:</strong> ${data.final_ai_score}
        </div>
    `;
  output.appendChild(resultText);

  btn.disabled = false;
  btn.innerHTML = "Check This Page";
}

function createResultItem(title, data) {
  return `
    <div class="result-item">
        <strong>${title}</strong>
    </div>
    <div class="result-item">
         Not Provoking Sentiment: ${getResultIcon(data.phrase_tool)}
    </div>
    <div class="result-item">
         Well Framed: ${getResultIcon(data.language_tool)}
    </div>
    <div class="result-item">
         Realistic Claims: ${getResultIcon(data.commonsense_tool)}
    </div>
    <div class="result-item">
         Politically Neutral: ${getResultIcon(data.standing_tool)}
    </div>
    <div class="result-item">
         Fact Check: ${getResultIcon(data.fact_check_tool)}
    </div>
  `;
}

function getResultIcon(score) {
  if (score.endsWith("REAL")) {
    return `<span class="result-icon-small green-tick">✅</span>`;
  } else {
    return `<span class="result-icon-small red-cross">❌</span>`;
  }
}

function truncateURL(url) {
  const maxLength = 30;
  if (url.length > maxLength) {
    return url.slice(0, maxLength) + "...";
  }
  return url;
}

// Listen for messages from background.js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log(message);
  if (message.action === "updatePopup") {
    const includeImages = includeImagesCheckbox.checked;
    const includeVideos = includeVideosCheckbox.checked;
    analyzePage(message.tabId, message.url, includeImages, includeVideos);
  }
});
