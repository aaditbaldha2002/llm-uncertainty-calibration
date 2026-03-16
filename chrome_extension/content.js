// Create floating container
const container = document.createElement("div");
container.id = "truthlens-container";
container.style.position = "fixed";
container.style.bottom = "20px";
container.style.right = "20px";
container.style.width = "350px";
container.style.height = "500px";
container.style.backgroundColor = "#fff";
container.style.border = "1px solid #ccc";
container.style.borderRadius = "10px";
container.style.zIndex = 999999;
container.style.boxShadow = "0 0 15px rgba(0,0,0,0.3)";
container.style.padding = "10px";
container.style.overflowY = "auto";
container.style.cursor = "move";

// Insert your HTML
container.innerHTML = `
  <h3 style="margin:0; cursor:move;">TruthLens</h3>
  <p style="font-size:12px; color:#ff6b6b; text-align:center;">
    Please do not enter personal, sensitive, or confidential information.
  </p>
  <textarea id="question" placeholder="Enter question" style="width:100%; height:60px;"></textarea>
  <textarea id="answer" placeholder="Paste LLM answer" style="width:100%; height:100px;"></textarea>
  <button id="check" style="margin-top:5px;">Evaluate</button>
  <div id="result" style="margin-top:10px; white-space:pre-wrap;"></div>
`;

// Append to body
document.body.appendChild(container);

// Draggable functionality
let isDragging = false, offsetX = 0, offsetY = 0;
const header = container.querySelector("h3");

header.addEventListener("mousedown", (e) => {
    isDragging = true;
    offsetX = e.clientX - container.getBoundingClientRect().left;
    offsetY = e.clientY - container.getBoundingClientRect().top;
});

document.addEventListener("mousemove", (e) => {
    if (isDragging) {
        container.style.left = e.clientX - offsetX + "px";
        container.style.top = e.clientY - offsetY + "px";
        container.style.right = "auto";
        container.style.bottom = "auto";
    }
});

document.addEventListener("mouseup", () => {
    isDragging = false;
});

// Evaluation logic
document.getElementById("check").onclick = async function() {
    const question = document.getElementById("question").value;
    const answer = document.getElementById("answer").value;

    if (!question || !answer) {
        document.getElementById("result").innerText = "Please enter both question and answer.";
        return;
    }

    document.getElementById("result").innerText = "Evaluating...";

    try {
        const response = await fetch("http://127.0.0.1:8000/evaluate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question, answer })
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        const data = await response.json();

        let output = `Final Confidence Score: ${data.confidence.toFixed(2)}\n\n`;
        output += "Claim Similarity Scores:\n";
        data.claim_scores.forEach((score, idx) => { output += `Claim ${idx + 1}: ${score.toFixed(2)}\n`; });
        output += "\nTop Evidence Similarity Scores:\n";
        data.top_scores.forEach((score, idx) => { output += `Evidence ${idx + 1}: ${score.toFixed(2)}\n`; });

        document.getElementById("result").innerText = output;

    } catch (err) {
        console.error(err);
        document.getElementById("result").innerText = "Error evaluating answer. Check server logs.";
    }
};