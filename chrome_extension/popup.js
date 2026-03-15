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
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question,
                answer: answer
            })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        // Build output
        let output = `Final Confidence Score: ${data.confidence.toFixed(2)}\n\n`;

        output += "Per-Claim Scores & HF Verdicts:\n";
        data.claims.forEach((claim, idx) => {
            const score = data.claim_scores[idx].toFixed(2);
            const verdict = data.hf_verdicts[idx] || "N/A";
            output += `- "${claim}": Score = ${score}, HF Verdict = ${verdict}\n`;
        });

        output += "\nTop Evidence:\n";
        data.top_evidence.forEach((ev, idx) => {
            const score = data.top_scores[idx].toFixed(2);
            output += `- (${score}) ${ev}\n`;
        });

        document.getElementById("result").innerText = output;

    } catch (err) {
        console.error(err);
        document.getElementById("result").innerText = "Error evaluating answer. Check server logs.";
    }
};