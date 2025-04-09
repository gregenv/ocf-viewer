import os
import requests

# === ΠΑΡΑΜΕΤΡΟΙ ===
input_file = "Links.txt"                 # αρχείο με τα links σου
output_folder = "Κατεβασμένα_PDF"        # φάκελος αποθήκευσης
max_files = 1000                         # όριο αριθμού αρχείων που θα κατεβάσει

# === Δημιουργία φακέλου αν δεν υπάρχει ===
os.makedirs(output_folder, exist_ok=True)

# === Διαβάζει τα links ===
with open(input_file, "r", encoding="utf-8") as f:
    links = [line.strip() for line in f if line.strip()]

# === Κατεβάζει PDF ===
for i, url in enumerate(links[:max_files]):
    try:
        ada = url.split("/")[-2]
        filename = f"{i+1:04d}_{ada}.pdf"
        filepath = os.path.join(output_folder, filename)

        response = requests.get(url, timeout=15)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"✔️ {i+1}/{max_files} -> {filename}")
    except Exception as e:
        print(f"❌ Σφάλμα στο {i+1}: {url} -> {e}")

