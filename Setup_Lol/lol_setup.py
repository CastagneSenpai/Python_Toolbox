import subprocess
import time
import pygetwindow as gw
import pyautogui
import win32gui
import win32process
from concurrent.futures import ThreadPoolExecutor

# Fonction pour déplacer les fenêtres vers le second écran
def move_to_left_screen_and_maximize(window_title):
    try:
        # Récupère la fenêtre par son titre
        window = gw.getWindowsWithTitle(window_title)[0]
        
        # Dimensions de l'écran principal pour calculer la position
        primary_screen_width, _ = pyautogui.size()
        
        window.moveTo(-primary_screen_width, 0)  # Envoie à gauche de l'écran principal
        time.sleep(0.5)
        window.maximize()  # Met la fenêtre en plein écran
    except IndexError:
        print(f"Fenêtre '{window_title}' non trouvée.")
    except Exception as e:
        print(f"Erreur lors du déplacement de la fenêtre : {e}")

# Fonction pour récupérer le titre de la fenêtre via le PID du processus
def get_window_title_by_pid(target_pid):
    """Trouver la fenêtre qui correspond au PID donné."""
    def callback(hwnd, hwnds):
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        if found_pid == target_pid and win32gui.IsWindowVisible(hwnd):
            hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    if hwnds:
        return win32gui.GetWindowText(hwnds[0])  # Titre de la première fenêtre trouvée
    return None

# Fonction pour attendre l'ouverture de la fenêtre associée à un processus donné
def wait_for_window_by_pid(pid, expected_title_part, timeout=30):
    """Attend jusqu'à ce qu'une fenêtre correspondant au PID et au titre partiel soit trouvée."""
    elapsed = 0
    while elapsed < timeout:
        window_title = get_window_title_by_pid(pid)
        if window_title and expected_title_part in window_title:
            return window_title
        time.sleep(1)
        elapsed += 1
    return None

# Fonction pour démarrer un processus et attendre que sa fenêtre s'ouvre pour la déplacer
def launch_and_move_application(executable_path, args, expected_title_part):
    process = subprocess.Popen([executable_path] + args)
    window_title = wait_for_window_by_pid(process.pid, expected_title_part)
    if window_title:
        move_to_left_screen_and_maximize(window_title)

def main():
    print("Beginning of script...")

    # Définition des applications à lancer en parallèle
    applications = [
        (r"D:\Program Files (x86)\Overwolf\OverwolfLauncher.exe", ["-launchapp", "pibhbkkgefgheeglaeemkkfjlhidhcedalapdggh"], "Porofessor"),
        (r"C:\Users\rcasta911e\AppData\Local\Discord\Update.exe", ["--processStart", "Discord.exe"], "Discord"),
        (r"D:\Programmes\Riot Games\Riot Client\RiotClientServices.exe", ["--launch-product=league_of_legends", "--launch-patchline=live"], "League")
    ]

    # Utilise ThreadPoolExecutor pour exécuter les tâches en parallèle
    with ThreadPoolExecutor(max_workers=len(applications)) as executor:
        futures = [executor.submit(launch_and_move_application, *app) for app in applications]

    print("End of script...")

if __name__ == "__main__":
    main()
