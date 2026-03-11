document.getElementById("check").onclick = async function() {

const question = document.getElementById("question").value
const answer = document.getElementById("answer").value

const response = await fetch("http://127.0.0.1:8000/evaluate", {

method: "POST",

headers: {
"Content-Type": "application/json"
},

body: JSON.stringify({
question: question,
answer: answer
})

})

const data = await response.json()

document.getElementById("result").innerText =
"Confidence Score: " + data.confidence

}