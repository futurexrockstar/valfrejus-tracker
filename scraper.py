import os
import time
from datetime import datetime
import pytz
from playwright.sync_api import sync_playwright
from PIL import Image

def get_color_status(img, x, y):
    try:
        r, g, b = img.getpixel((x, y))
        # VERT (Ouvert)
        if g > r + 30 and g > 100: return "V"
        # ORANGE (Plan) -> On renvoie B (Bleu) pour tes LEDs
        if r > 180 and g > 120 and b < 100: return "B"
        # Sinon ROUGE (Fermé)
        return "R"
    except:
        return "R"

def is_active_time():
    tz = pytz.timezone('Europe/Paris')
    now = datetime.now(tz)
    
    # 1. Dates : 15 déc au 20 avril
    m, d = now.month, now.day
    in_season = (m == 12 and d >= 15) or (1 <= m <= 3) or (m == 4 and d <= 20)
    
    # 2. Heures : 08:40 à 16:30
    current_time = now.strftime("%H:%M")
    is_daytime = "08:40" <= current_time <= "16:30"
    
    return in_season and is_daytime

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1500})
        
        # Boucle de 14 minutes pour les scans toutes les 30 secondes
        start_time = time.time()
        while (time.time() - start_time) < 840:
            if is_active_time():
                try:
                    page.goto("https://valfrejus.digisnow.app/map/1/fr?fullscreen=true", wait_until="networkidle")
                    page.wait_for_timeout(5000) # Attente des pastilles
                    
                    page.screenshot(path="temp.png")
                    img = Image.open("temp.png")

                    # Tes coordonnées (Arrondaz et Punta Bagna)
                    s_arr = get_color_status(img, 255, 1088)
                    s_pun = get_color_status(img, 827, 480)

                    result = f"A:{s_arr},P:{s_pun}"
                    
                    # Mise à jour du fichier
                    with open("status.txt", "w") as f:
                        f.write(result)
                    
                    # Push vers GitHub
                    os.system('git config --global user.name "SkiBot"')
                    os.system('git config --global user.email "bot@github.com"')
                    os.system('git add status.txt')
                    os.system('git commit -m "Update" || echo "no change"')
                    os.system('git push')
                    
                except Exception as e:
                    print(f"Erreur: {e}")
            
            time.sleep(30)
        browser.close()

if __name__ == "__main__":
    run()
