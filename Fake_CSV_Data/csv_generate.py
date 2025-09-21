import csv
import random
import string
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# On définit le nombre de lignes voulues et les statuts à générer en fonction de proportions voulues
n = 113 
statuses = (['Email Sent'] * int(n * 0.05) +
            ['Email Opened'] * int(n * 0.75) +
            ['Clicked Link'] * int(n * 0.10) +
            ['Submitted Data'] * (n - int(n * 0.05) - int(n * 0.75) - int(n * 0.10)))
random.shuffle(statuses)

# Fonction pour générer un ID aléatoire 
def random_id(length=5):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

# Fonction pour générer une IP aléatoire 
def random_ip():
    return ".".join(str(random.randint(1, 255)) for _ in range(4))

# On crée une liste de faux noms, prénoms et postes
first_names = ["Lucas", "Emma", "Nathan", "Léa", "Sophie", "Julien", "Marie", "Thomas", "Clara", "Hugo", "Paul"]
last_names = ["Martin", "Bernard", "Dubois", "Durand", "Lefevre", "Moreau", "Simon", "Laurent", "Garcia", "Michel"]
positions = ["Développeur", "RH", "Commercial", "Comptable", "Chef de projet", "Stagiaire", "Technicien", "Directeur"]
base_date = datetime.now()

# On remplit le CSV avec des valeurs aléatoires
rows = []
for status in statuses:
    send_dt = base_date + timedelta(seconds=random.randint(0, 3600))
    modified_dt = send_dt + timedelta(seconds=random.randint(0, 120))
    first = random.choice(first_names)
    last = random.choice(last_names)
    email = f"{first.lower()}.{last.lower()}@entreprise.com"
    position = random.choice(positions)
    ip = random_ip() if status in ["Email Opened", "Clicked Link", "Submitted Data"] else ""
    rows.append({
        "id": random_id(),
        "status": status,
        "ip": ip,
        "latitude": round(random.uniform(-90, 90), 6) if ip else 0,
        "longitude": round(random.uniform(-180, 180), 6) if ip else 0,
        "send_date": send_dt.isoformat() + "Z",
        "reported": random.choice(["False", "False", "False", "True"]),
        "modified_date": modified_dt.isoformat() + "Z",
        "email": email,
        "first_name": first,
        "last_name": last,
        "position": position
})

# On sauvegarde le fichier CSV généré  
data_file = "phishing_results.csv"
fieldnames = rows[0].keys()
with open(data_file, "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

file_path = "phishing_results.csv"

# On récupère les résultats des statuts
nb_email_sent = 0
nb_email_opened = 0
nb_clicked_link = 0
nb_submitted_data = 0

with open(file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        status = row['status'].strip().lower()
        
        if status in ('email sent', 'email opened', 'clicked link', 'submitted data'):
            nb_email_sent += 1
        if status in ('email opened', 'clicked link', 'submitted data'):
            nb_email_opened += 1
        if status in ('clicked link', 'submitted data'):
            nb_clicked_link += 1
        if status == 'submitted data':
            nb_submitted_data += 1

# On affiche les résultats de la campagne factice
print("========= Résultats de la campagne de phishing =========")
print(f"- Nombre total d'e-mails envoyés : {nb_email_sent}")
print(f"- Nombre de mails ouverts : {nb_email_opened}")
print(f"- Nombre de clics sur le lien : {nb_clicked_link}")
print(f"- Nombre de soumissions de données : {nb_submitted_data}")

# On génère le premier graphique
labels = ["Emails envoyés", "Mails ouverts", "Liens cliqués", "Données soumises"]
values = [nb_email_sent, nb_email_opened, nb_clicked_link, nb_submitted_data]

plt.figure(figsize=(8, 5))
colors = ["#4CAF50", "#2196F3", "#FFC107", "#F44336"]
bars = plt.bar(labels, values, color=colors, width=0.6)
for bar, value in zip(bars, values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
             str(value), ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.title("Résultats de la campagne", fontsize=14, fontweight='bold')
plt.xlabel("Statuts", fontsize=12)
plt.ylabel("Nombre d'occurrences", fontsize=12)
plt.xticks(rotation=15, fontsize=10)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# On génère le second graphique
nb_not_opened = max(nb_email_sent - nb_email_opened, 0)
labels_pie = ["Non lus", "Mails ouverts", "Liens cliqués", "Données soumises"]
values_pie = [nb_not_opened, nb_email_opened, nb_clicked_link, nb_submitted_data]
colors_pie = ["#9E9E9E", "#2196F3", "#FFC107", "#F44336"]

plt.figure(figsize=(6, 6))
wedges, texts, autotexts = plt.pie(
    values_pie,
    labels=labels_pie,
    colors=colors_pie,
    autopct=lambda p: f'{p:.1f}%' if p > 0 else '',
    startangle=90,
    wedgeprops={'edgecolor': 'white'}
)

plt.title("Répartition des utilisateurs", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()