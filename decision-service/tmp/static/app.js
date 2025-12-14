console.log("Frontend loaded.");

const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

// Connect to WebSocket and auto-reconnect on close
function connectWS() {
    const ws = new WebSocket(`ws://${location.host}/ws`);

    ws.onopen = () => console.log("Connected to WebSocket");
    
    ws.onmessage = (event) => {
        // Donc ici x et y on considère que c'est der variables de -1 à 1.
        const data = JSON.parse(event.data);
        const x = data.x * canvas.width ;
        const y = data.y * canvas.height;

        // Draw the red dot
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.beginPath();
        ctx.arc(x, y, 10, 0, 2 * Math.PI);
        ctx.fillStyle = "red";
        ctx.fill();
    };

    ws.onclose = () => {
        console.log("Disconnected. Reconnecting in 1s...");
        setTimeout(connectWS, 1000);
    };

    ws.onerror = (err) => {
        console.error("WebSocket error:", err);
        ws.close();
    };
}

// Start WebSocket connection
connectWS();