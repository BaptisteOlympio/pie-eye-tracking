async function send_ip() {
  const ip = document.getElementById("ip").value;
  const port = document.getElementById("port").value;

  const response = await fetch("/connect_video_service", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ip: ip, port: port})
  });
  const data = await response.json()
  document.getElementById("response").innerText = data.status;
}

const ws = new WebSocket(`ws://${location.host}/ws?type=video`);
ws.binaryType = "arraybuffer";

ws.onmessage = (event) => {
  const blob = new Blob([event.data], { type: "image/jpeg" });
  const url = URL.createObjectURL(blob);
  const img = document.getElementById("video");
  img.src = url;
};

// WebSocket pour recevoir les données de gaze
const wsGaze = new WebSocket(`ws://${location.host}/ws?type=gaze`);

wsGaze.onmessage = (event) => {
  const gazeData = JSON.parse(event.data);
  document.getElementById("gaze-x").innerText = gazeData.gaze_x.toFixed(4);
  document.getElementById("gaze-y").innerText = gazeData.gaze_y.toFixed(4);
};

wsGaze.onerror = (error) => {
  console.error("Erreur WebSocket gaze:", error);
};
