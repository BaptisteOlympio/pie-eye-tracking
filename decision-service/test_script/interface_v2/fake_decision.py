import sys
import threading
import time

# --- Code spécifique pour le mode Terminal/Docker ---
import select
import tty
import termios

class TerminalInput:
    """Stratégie de repli pour Docker : lit l'entrée standard"""
    def __init__(self, callback_press, callback_release):
        self.running = True
        self.cb_press = callback_press
        self.cb_release = callback_release
        self.old_settings = termios.tcgetattr(sys.stdin)
        self.last_input_time = 0
        
        # Thread de lecture
        self.t_read = threading.Thread(target=self._loop_read, daemon=True)
        self.t_read.start()
        
        # Thread de reset (pour simuler le relâchement)
        self.t_reset = threading.Thread(target=self._loop_reset, daemon=True)
        self.t_reset.start()

    def stop(self):
        self.running = False
        time.sleep(0.1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def _loop_read(self):
        try:
            tty.setcbreak(sys.stdin.fileno())
            while self.running:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    if key == '\x1b': # Détection séquence ANSI (Flèches)
                        seq = sys.stdin.read(2)
                        self.last_input_time = time.time()
                        if seq == '[A': self.cb_press('UP')
                        elif seq == '[B': self.cb_press('DOWN')
                        elif seq == '[C': self.cb_press('RIGHT')
                        elif seq == '[D': self.cb_press('LEFT')
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def _loop_reset(self):
        while self.running:
            time.sleep(0.05)
            # Si pas d'input depuis 150ms, on considère que c'est relâché
            if time.time() - self.last_input_time > 0.15 and self.last_input_time != 0:
                self.cb_release()
                self.last_input_time = 0

# --- La Classe Principale ---
class FakeEyeTracker:
    def __init__(self):
        self.current_data = {"direction": "CENTER", "x": 0, "y": 0}
        self.mode = "UNKNOWN"

        # TENTATIVE 1 : Pynput (Idéal pour Local)
        try:
            from pynput import keyboard
            # On tente de créer le listener pour voir si le DISPLAY est dispo
            self.listener = keyboard.Listener(on_press=self._pynput_press, on_release=self._pynput_release)
            self.listener.start()
            # On vérifie si le thread est vivant (pynput meurt vite si pas de display)
            self.listener.wait() 
            if self.listener.running:
                self.mode = "PYNPUT (Local)"
                self.keyboard_module = keyboard
            else:
                raise ImportError("Pynput failed to start")
                
        except (ImportError, Exception):
            # TENTATIVE 2 : Fallback Docker (Terminal standard)
            self.mode = "DOCKER/TERMINAL"
            self.terminal_handler = TerminalInput(self._docker_press, self._docker_release)

    # --- Callbacks PYNPUT ---
    def _pynput_press(self, key):
        k = self.keyboard_module.Key
        if key == k.up: self._update("UP", 0, 1)
        elif key == k.down: self._update("DOWN", 0, -1)
        elif key == k.left: self._update("LEFT", -1, 0)
        elif key == k.right: self._update("RIGHT", 1, 0)

    def _pynput_release(self, key):
        k = self.keyboard_module.Key
        if key in [k.up, k.down, k.left, k.right]:
            self._update("CENTER", 0, 0)

    # --- Callbacks DOCKER ---
    def _docker_press(self, direction_str):
        mapping = {
            "UP": (0, 1), "DOWN": (0, -1),
            "LEFT": (-1, 0), "RIGHT": (1, 0)
        }
        x, y = mapping.get(direction_str, (0,0))
        self._update(direction_str, x, y)

    def _docker_release(self):
        self._update("CENTER", 0, 0)

    # --- Méthode commune ---
    def _update(self, direction, x, y):
        self.current_data = {"direction": direction, "x": x, "y": y}

    def get_gaze_data(self):
        return self.current_data
    
    def get_mode(self):
        return self.mode

# --- EXEMPLE ---
if __name__ == "__main__":
    tracker = FakeEyeTracker()
    print(f"--- Fake Eye Tracker Démarré ---")
    print(f"Mode détecté : {tracker.get_mode()}")
    print("Utilisez les flèches (Ctrl+C pour quitter)")
    
    try:
        while True:
            data = tracker.get_gaze_data()
            sys.stdout.write(f"\r[{data['direction']}] X:{data['x']} Y:{data['y']}   ")
            sys.stdout.flush()
            time.sleep(0.05)
    except KeyboardInterrupt:
        if hasattr(tracker, 'terminal_handler'):
            tracker.terminal_handler.stop()
        print("\nBye")
