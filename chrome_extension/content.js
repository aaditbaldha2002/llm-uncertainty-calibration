// Create floating container
const container = document.createElement("div");
container.id = "truthlens-container";
container.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 360px;
    max-height: 600px;
    background-color: #0b0c10;
    border: 1px solid #1f2833;
    border-radius: 12px;
    z-index: 999999;
    box-shadow: 0 0 20px rgba(102, 252, 241, 0.15);
    padding: 20px 24px;
    overflow-y: auto;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #c5c6c7;
    box-sizing: border-box;
`;

container.innerHTML = `
    <div id="truthlens-header" style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        cursor: move;
    ">
        <h3 id="truthlens-title" style="
            margin: 0;
            color: #66fcf1;
            font-size: 20px;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-shadow: 0 0 8px rgba(102, 252, 241, 0.6);
            cursor: move;
        ">TruthLens</h3>
        <button id="truthlens-close" style="
            background: transparent;
            border: 1px solid #ff4c4c;
            color: #ff4c4c;
            border-radius: 6px;
            width: 28px;
            height: 28px;
            font-size: 15px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0;
            transition: background 0.2s ease, color 0.2s ease;
            flex-shrink: 0;
        ">✕</button>
    </div>

    <p style="
        font-size: 11px;
        color: #ff6b6b;
        text-align: center;
        margin: 0 0 14px;
        line-height: 1.5;
    ">Please do not enter personal, sensitive, or confidential information.</p>

    <textarea id="tl-question" placeholder="Enter question" style="
        width: 100%;
        height: 70px;
        margin-bottom: 12px;
        padding: 12px;
        border: 1px solid #1f2833;
        border-radius: 10px;
        background-color: #1f2833;
        color: #c5c6c7;
        resize: vertical;
        outline: none;
        font-size: 13px;
        box-sizing: border-box;
        font-family: inherit;
        transition: border 0.25s ease, box-shadow 0.25s ease;
    "></textarea>

    <textarea id="tl-answer" placeholder="Paste LLM answer" style="
        width: 100%;
        height: 100px;
        margin-bottom: 12px;
        padding: 12px;
        border: 1px solid #1f2833;
        border-radius: 10px;
        background-color: #1f2833;
        color: #c5c6c7;
        resize: vertical;
        outline: none;
        font-size: 13px;
        box-sizing: border-box;
        font-family: inherit;
        transition: border 0.25s ease, box-shadow 0.25s ease;
    "></textarea>

    <button id="tl-check" style="
        width: 100%;
        padding: 12px;
        background: linear-gradient(135deg, #45a29e, #66fcf1);
        color: #0b0c10;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0.5px;
        transition: background 0.25s ease, transform 0.1s ease, box-shadow 0.25s ease;
    ">Evaluate</button>

    <div id="tl-result" style="
        margin-top: 16px;
        width: 100%;
        padding: 12px;
        border-radius: 10px;
        background-color: #1f2833;
        color: #c5c6c7;
        font-size: 13px;
        min-height: 50px;
        word-wrap: break-word;
        box-sizing: border-box;
        box-shadow: inset 0 0 8px rgba(70, 162, 158, 0.3);
        display: none;
    "></div>
`;

document.body.appendChild(container);

// ── Close button ──────────────────────────────────────────
const closeBtn = document.getElementById("truthlens-close");
closeBtn.addEventListener("click", () => container.remove());
closeBtn.addEventListener("mouseenter", () => {
    closeBtn.style.background = "#ff4c4c";
    closeBtn.style.color = "#0b0c10";
});
closeBtn.addEventListener("mouseleave", () => {
    closeBtn.style.background = "transparent";
    closeBtn.style.color = "#ff4c4c";
});

// ── Evaluate button hover ─────────────────────────────────
const checkBtn = document.getElementById("tl-check");
checkBtn.addEventListener("mouseenter", () => {
    checkBtn.style.background = "linear-gradient(135deg, #66fcf1, #45a29e)";
    checkBtn.style.transform = "scale(1.03)";
    checkBtn.style.boxShadow = "0 0 12px rgba(102, 252, 241, 0.6)";
});
checkBtn.addEventListener("mouseleave", () => {
    checkBtn.style.background = "linear-gradient(135deg, #45a29e, #66fcf1)";
    checkBtn.style.transform = "scale(1)";
    checkBtn.style.boxShadow = "none";
});

// ── Textarea focus effects ────────────────────────────────
["tl-question", "tl-answer"].forEach(id => {
    const el = document.getElementById(id);
    el.addEventListener("focus", () => {
        el.style.borderColor = "#45a29e";
        el.style.boxShadow = "0 0 10px rgba(70, 162, 158, 0.7)";
    });
    el.addEventListener("blur", () => {
        el.style.borderColor = "#1f2833";
        el.style.boxShadow = "none";
    });
});

// ── Draggable ─────────────────────────────────────────────
let isDragging = false, offsetX = 0, offsetY = 0;
const dragHandle = document.getElementById("truthlens-header");

dragHandle.addEventListener("mousedown", (e) => {
    if (e.target.id === "truthlens-close") return;
    isDragging = true;
    offsetX = e.clientX - container.getBoundingClientRect().left;
    offsetY = e.clientY - container.getBoundingClientRect().top;
});

document.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    container.style.left = e.clientX - offsetX + "px";
    container.style.top = e.clientY - offsetY + "px";
    container.style.right = "auto";
    container.style.bottom = "auto";
});

document.addEventListener("mouseup", () => { isDragging = false; });

// ── Evaluation logic ──────────────────────────────────────
document.getElementById("tl-check").addEventListener("click", async () => {
    const question = document.getElementById("tl-question").value.trim();
    const answer = document.getElementById("tl-answer").value.trim();
    const resultDiv = document.getElementById("tl-result");

    if (!question || !answer) {
        resultDiv.style.display = "block";
        resultDiv.style.border = "1px solid #ff4c4c";
        resultDiv.style.color = "#ff4c4c";
        resultDiv.innerHTML = "Please enter both a question and an answer.";
        return;
    }

    // Loading state
    resultDiv.style.display = "block";
    resultDiv.style.border = "none";
    resultDiv.style.color = "#66fcf1";
    resultDiv.innerHTML = `
        <div style="text-align:center; animation: tl-pulse 1s infinite;">
            Evaluating...
        </div>
        <style>
            @keyframes tl-pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.4; }
            }
        </style>
    `;

    try {
        const response = await fetch("http://127.0.0.1:8000/evaluate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question, answer })
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        const data = await response.json();

        const confidence = data.confidence;

        // Verdict thresholds
        let verdict, verdictColor, emoji;
        if (confidence >= 0.7) {
            verdict = "Likely Factual";
            verdictColor = "#45a29e";
            emoji = "✅";
        } else if (confidence >= 0.4) {
            verdict = "Partially Supported";
            verdictColor = "#f0a500";
            emoji = "⚠️";
        } else {
            verdict = "Potential Hallucination";
            verdictColor = "#ff4c4c";
            emoji = "🚨";
        }

        // Structured result output
        resultDiv.style.border = `1px solid ${verdictColor}`;
        resultDiv.style.color = "#c5c6c7";
        resultDiv.style.boxShadow = `0 0 10px ${verdictColor}33`;
        resultDiv.innerHTML = `
            <div style="text-align:center; margin-bottom:12px;">
                <div style="font-size:26px; margin-bottom:4px;">${emoji}</div>
                <div style="font-size:16px; font-weight:700; color:${verdictColor};">
                    ${verdict}
                </div>
                <div style="font-size:12px; color:#c5c6c7; margin-top:4px;">
                    Confidence Score: 
                    <strong style="color:${verdictColor};">
                        ${confidence.toFixed(2)}
                    </strong>
                </div>
            </div>

            <hr style="border: none; border-top: 1px solid #2a2f3a; margin: 10px 0;">

            <div style="font-size:12px;">
                <div style="color:#66fcf1; font-weight:700; margin-bottom:6px;">
                    Claim Scores
                </div>
                ${data.claim_scores.map((score, idx) => `
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 4px 0;
                        border-bottom: 1px solid #1f2833;
                    ">
                        <span style="color:#c5c6c7;">Claim ${idx + 1}</span>
                        <span style="
                            font-weight: 700;
                            color: ${score >= 0.7 ? '#45a29e' : 
                                    score >= 0.4 ? '#f0a500' : '#ff4c4c'};
                        ">${score.toFixed(2)}</span>
                    </div>
                `).join('')}
            </div>

            <div style="font-size:12px; margin-top:12px;">
                <div style="color:#66fcf1; font-weight:700; margin-bottom:6px;">
                    Top Evidence Scores
                </div>
                ${data.top_scores.map((score, idx) => `
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 4px 0;
                        border-bottom: 1px solid #1f2833;
                    ">
                        <span style="color:#c5c6c7;">Evidence ${idx + 1}</span>
                        <span style="font-weight:700; color:#45a29e;">
                            ${score.toFixed(2)}
                        </span>
                    </div>
                `).join('')}
            </div>
        `;

    } catch (err) {
        console.error(err);
        resultDiv.style.border = "1px solid #ff4c4c";
        resultDiv.style.color = "#ff4c4c";
        resultDiv.innerHTML = `
            <div style="text-align:center;">
                <div style="font-size:20px; margin-bottom:6px;">❌</div>
                <div style="font-weight:700;">Connection Error</div>
                <div style="font-size:11px; margin-top:4px; color:#c5c6c7;">
                    Make sure the backend is running on port 8000
                </div>
            </div>
        `;
    }
});