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
        let output = `✅ Confidence Score: ${data.confidence.toFixed(2)}\n\n`;

        output += "🔹 Per-Claim Scores:\n";
        data.claims.forEach((claim, idx) => {
            output += `- "${claim}": ${data.claim_scores[idx].toFixed(2)}\n`;
        });

        output += "\n📚 Top Evidence:\n";
        data.evidence.forEach((ev, idx) => {
            output += `- (${data.evidence_scores[idx].toFixed(2)}) ${ev}\n`;
        });

        document.getElementById("result").innerText = output;

    } catch (err) {
        console.error(err);
        document.getElementById("result").innerText = "Error evaluating answer. Check server logs.";
    }
};