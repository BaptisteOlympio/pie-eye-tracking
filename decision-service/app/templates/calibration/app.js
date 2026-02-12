const canvas = document.getElementById('calibration-canvas');
const ctx = canvas.getContext('2d');
const messageOverlay = document.getElementById('message-overlay');

function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.onresize = resize;
resize();

const ws = new WebSocket(`ws://${location.host}/ws?type=calibration`);

ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    const data = response.data;

    if (data.type === "instruction") {
        messageOverlay.textContent = data.value;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    } 
    else if (data.type === "target") {
        drawTarget(data.x * canvas.width, data.y * canvas.height);
    }
};

function drawTarget(x, y) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Cercle rouge extérieur
    ctx.beginPath();
    ctx.arc(x, y, 15, 0, Math.PI * 2);
    ctx.fillStyle = "red";
    ctx.fill();
    // Point noir central pour la fixation fovéale
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fillStyle = "black";
    ctx.fill();
}