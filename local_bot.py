import time
import os
from datetime import datetime
import pytz
from playwright.sync_api import sync_playwright
from PIL import Image

# Coordonnées des remontées
POINTS = {"ARRONDAZ": (255, 1088), "PUNTA_BAGNA": (827, 480)}

def get_color_status(img, x, y):
    r, g, b = img.getpixel((x, y))
    if g > r + 30 and g > 100: return "V"  # VERT
    if r > 180 and g > 120 and b < 100: return "B" # ORANGE -> BLEU
    return "R" # ROUGE

def run():
    print("--- SCANNER LOCAL DÉMARRÉ ---")
    last_status = ""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1500})
        
        while True:
            try:
                # 1. Scan de la page
                page.goto("https://valfrejus.digisnow.app/map/1/fr?fullscreen=true", wait_until="networkidle")
                page.wait_for_timeout(5000)
                page.screenshot(path="temp.png")
                
                # 2. Analyse
                img = Image.open("temp.png")
                s_arr = get_color_status(img, *POINTS["ARRONDAZ"])
                s_pun = get_color_status(img, *POINTS["PUNTA_BAGNA"])
                new_status = f"A:{s_arr},P:{s_pun}"
                
                # 3. Mise à jour GitHub seulement si changement
                if new_status != last_status:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Nouveau statut : {new_status}")
                    with open("status.txt", "w") as f:
                        f.write(new_status)
                    
                    # Commandes Git pour envoyer vers ton nouveau compte
                    os.system('git add status.txt')
                    os.system('git commit -m "Auto-update from PC"')
                    os.system('git push')
                    last_status = new_status
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Pas de changement.")
                    
            except Exception as e:
                print(f"Erreur : {e}")
            
            time.sleep(30) # Attend 30 secondes

if __name__ == "__main__":
    run()
