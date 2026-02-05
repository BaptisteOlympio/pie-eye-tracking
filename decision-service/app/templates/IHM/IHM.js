// var ws_protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
// var ws = new WebSocket(ws_protocol + window.location.host + "/ws");
const ws = new WebSocket(`ws://${location.host}/ws?type=IHM`);



ws.onmessage = function (event) {
  try {
    var data = JSON.parse(event.data);
    
    // Si c'est toujours un string, il faut parser une 2ème fois
    if (typeof data === 'string') {
      console.log("⚠️ Double encodage détecté, 2ème parse...");
      data = JSON.parse(data);
    }

   
    // Protection contre labels undefined
    var labels = data.labels || {"UP": "", "DOWN": "", "LEFT": "", "RIGHT": "", "CENTER": ""};
    
    if (!data.labels) {
      console.error("⚠️ ATTENTION: data.labels est undefined! Utilisation de valeurs par défaut.");
    }

    // 1. INFO PIÈCE
    document.getElementById("room-display").innerText = data.room_name || "Pièce Inconnue";

    // 2. INFO QUEUE (LISTE) - GROS FORMAT
    var queueContainer = document.getElementById("queue-container");
    if (data.queue && data.queue.length > 0) {
      var htmlContent = "";
      data.queue.forEach((item) => {
        var activeClass = item.active ? "active" : "";
        var marker = item.active ? "➤ " : "";
        htmlContent += `
                <div class="queue-item ${activeClass}">
                    <span>${marker}${item.name}</span>
                    <span>${item.state}</span>
                </div>`;
      });
      queueContainer.innerHTML = htmlContent;
    } else {
      queueContainer.innerHTML =
        "<div style='opacity:0.5; font-size: 1rem'>Menu Principal<br>Sélectionnez une pièce</div>";
    }

    // 3. THÈME CENTRAL (Couleur Lumière)
    var centerEl = document.getElementById("CENTER");
    // On nettoie les anciennes classes
    centerEl.classList.remove("neutral", "light-on", "light-off");
    // On ajoute la nouvelle classe envoyée par Python
    if (data.center_theme) centerEl.classList.add(data.center_theme);

    // 4. TEXTES BOUTONS
    ["UP", "DOWN", "LEFT", "RIGHT", "CENTER"].forEach((id) => {
      var el = document.getElementById(id);
      if (el) {
        if (labels[id] !== undefined) el.innerText = labels[id];
        if (labels[id] === "") el.classList.add("disabled");
        else el.classList.remove("disabled");
      }
    });

    // 5. ANIMATION ROUE
    var dir = data.direction;
    var percent = data.percent;
    var isValid = data.validated;

    document.getElementById("debug-text").innerText =
      "SIMU: " + (data.debug_info || "Wait");

    ["UP", "DOWN", "LEFT", "RIGHT", "CENTER"].forEach((segmentId) => {
      var el = document.getElementById(segmentId);
      if (!el || el.innerText === "") return;

      if (segmentId === dir && dir !== "CENTER") {
        if (isValid) {
          el.classList.add("validated");
          el.style.background = "#4CAF50";
        } else {
          el.classList.remove("validated");
          el.style.background = `conic-gradient(#4CAF50 ${percent}%, #2a2a2a ${percent}%)`;
          el.style.color = "white";
        }
      } else {
        el.classList.remove("validated");
        // Attention : On ne reset pas le background du CENTRE ici, car il est géré par les classes CSS (light-on/off)
        if (segmentId !== "CENTER") {
          el.style.background = "#2a2a2a";
          el.style.color = "#ddd";
        } else {
          // Le centre garde sa couleur de classe, on reset juste l'échelle si besoin
        }
      }
    });
    
  } catch (error) {
    console.error("❌ ERREUR dans ws.onmessage:", error);
    console.error("Stack:", error.stack);
  }
};
