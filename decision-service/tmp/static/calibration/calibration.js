const ws = new WebSocket(`ws://${location.host}/ws?type=calibration`);

ws.onopen = () => console.log("Connected to WebSocket");

ws.onmessage = (event) => {
    // Donc ici x et y on considère que c'est der variables de -1 à 1.
    const data = JSON.parse(event.data);
    console.log(data);

    document.getElementById("message").textContent = data.data.value;
};