import streamlit as st
import streamlit.components.v1 as components

# CONFIGURATION DE L'ECRAN MOBILE STREAMLIT
st.set_page_config(page_title="Simulateur Cockpit 3D Pro", page_icon="🏗️", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #f3f4f6; }
    h1 { color: #f59e0b; text-align: center; font-family: 'Arial Black', sans-serif; font-size: 22px; margin-bottom: 5px; }
    .stApp { background-color: #0b0f19; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🏗️ SIMULATEUR COCKPIT GRUE PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; margin-top:-10px;'>Poste de pilotage virtuel avec commandes hydrauliques réactives</p>", unsafe_allow_html=True)

# SIMULATEUR GRAPHIQUE NATIF INTÉGRÉ (FONCTIONNE SANS BIBLIOTHÈQUE EXTERNE)
code_simulateur_natif = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; background-color: #0f172a; font-family: sans-serif; overflow: hidden; }
        
        /* Fenêtre de la cabine */
        #view-container { 
            width: 100%; 
            height: 300px; 
            background: linear-gradient(to bottom, #bae6fd 0%, #e0f2fe 70%, #94a3b8 70%, #64748b 100%);
            position: relative; 
            border-radius: 12px; 
            border: 3px solid #f59e0b;
            overflow: hidden;
        }

        /* Décors extérieurs (Chantier SNIM) */
        .conteneur-rouge {
            width: 80px; height: 50px; background-color: #ef4444; position: absolute;
            bottom: 35px; right: 40px; border-radius: 4px; border-bottom: 5px solid #b91c1c;
        }

        /* LA FLÈCHE DE LA GRUE (S'anime au mouvement) */
        #fleche-grue {
            width: 30px; 
            height: 250px; 
            background-color: #f59e0b; 
            position: absolute;
            bottom: 80px; 
            left: 50%;
            transform: translateX(-50%) rotate(35deg);
            transform-origin: bottom center;
            transition: transform 0.1s ease-out;
            border-radius: 4px;
            box-shadow: inset -5px 0px rgba(0,0,0,0.1);
        }

        /* LE CÂBLE DE LEVAGE (S'allonge) */
        #cable-acier {
            width: 2px;
            height: 100px;
            background-color: #475569;
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            transition: height 0.1s ease-out;
        }

        /* LE CROCHET DE LEVAGE */
        #crochet {
            width: 16px;
            height: 16px;
            border: 3px solid #1e293b;
            border-radius: 50%;
            position: absolute;
            bottom: -16px;
            left: 50%;
            transform: translateX(-50%);
            background-color: transparent;
        }

        /* DESIGN DE L'INTÉRIEUR DU COCKPIT (Pare-brise et Montants) */
        .cockpit-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            border: 15px solid #1e293b; box-sizing: border-box; pointer-events: none;
        }
        .tableau-bord {
            width: 100%; height: 80px; background-color: #1e293b;
            position: absolute; bottom: 0; left: 0; border-top: 4px solid #334155;
        }
        .volant {
            width: 70px; height: 30px; border: 6px solid #475569; border-radius: 50%;
            position: absolute; bottom: 25px; left: 20%; transform: rotateX(60deg);
        }

        /* LES LES JOYSTICKS D'ACCOUDOIR */
        .manette-base {
            width: 20px; height: 40px; background-color: #334155; position: absolute; bottom: 0;
        }
        #manette-g { left: 40px; }
        #manette-d { right: 40px; }
        .tige-manette {
            width: 4px; height: 25px; background-color: #94a3b8; position: absolute;
            top: -20px; left: 8px; transform-origin: bottom center; transition: transform 0.1s;
        }

        /* ORDINATEUR DE BORD CEC VISIBLE À L'ÉCRAN */
        .telemetry-screen { 
            position: absolute; top: 20px; left: 20px; 
            background: rgba(15, 23, 42, 0.9); color: #38bdf8; 
            padding: 8px; border-radius: 6px; font-family: monospace; 
            font-size: 11px; pointer-events: none; border: 1px solid #334155; line-height: 1.4;
            z-index: 10;
        }

        /* BOUTONS DE COMMANDE */
        .dashboard-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 12px; background: #1e293b; border-radius: 12px; margin-top: 10px; }
        .control-lever { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; border: none; padding: 14px; font-weight: bold; border-radius: 8px; font-size: 13px; box-shadow: 0 4px 6px rgba(0,0,0,0.4); touch-action: manipulation; }
        .control-lever:active { background: #d97706; }
    </style>
</head>
<body>

    <div id="view-container">
        <!-- Écran CEC -->
        <div class="telemetry-screen">
            💻 ORDINATEUR DE BORD CEC<br>
            -----------------------<br>
            • FLÈCHE : <span id="ang-txt">35</span>°<br>
            • CÂBLE : <span id="cab-txt">3.0</span> m<br>
            • CHARGE : <span id="status-txt" style="color:#22c55e;font-weight:bold;">SÉCURISÉE</span>
        </div>

        <!-- Décors extérieurs vus à travers la vitre -->
        <div class="conteneur-rouge"></div>

        <!-- Le Bras articulé de la grue extérieure -->
        <div id="fleche-grue">
            <!-- Le Câble et le crochet suspendus au bout -->
            <div id="cable-acier">
                <div id="crochet"></div>
            </div>
        </div>

        <!-- Cadre intérieur de la cabine grutier -->
        <div class="cockpit-overlay"></div>
        <div class="tableau-bord">
            <div class="volant"></div>
            <div class="manette-base" id="manette-g"><div class="tige-manette" id="tige-g"></div></div>
            <div class="manette-base" id="manette-d"><div class="tige-manette" id="tige-d"></div></div>
        </div>
    </div>

    <div class="dashboard-buttons">
        <button class="control-lever" onclick="piloterGrue('lever')">🕹️ MANETTE GAUCHE : LEVER BRAS</button>
        <button class="control-lever" onclick="piloterGrue('baisser')">🕹️ MANETTE GAUCHE : BAISSER BRAS</button>
        <button class="control-lever" onclick="piloterGrue('enrouler')">🪝 MANETTE DROITE : ENROULER CÂBLE</button>
        <button class="control-lever" onclick="piloterGrue('derouler')">🪝 MANETTE DROITE : DÉROULER CÂBLE</button>
    </div>

    <script>
        let currentAngle = 35;
        let currentCable = 100; // en pixels

        const fleche = document.getElementById('fleche-grue');
        const cable = document.getElementById('cable-acier');
        const tigeG = document.getElementById('tige-g');
        const tigeD = document.getElementById('tige-d');
        
        const angTxt = document.getElementById('ang-txt');
        const cabTxt = document.getElementById('cab-txt');
        const statusTxt = document.getElementById('status-txt');

        window.piloterGrue = function(action) {
            if (action === 'lever' && currentAngle < 75) {
                currentAngle += 2;
                tigeG.style.transform = "rotateX(-25deg)";
            } else if (action === 'baisser' && currentAngle > 15) {
                currentAngle -= 2;
                tigeG.style.transform = "rotateX(25deg)";
            } else if (action === 'derouler' && currentCable < 180) {
                currentCable += 10;
                tigeD.style.transform = "rotateX(25deg)";
            } else if (action === 'enrouler' && currentCable > 40) {
                currentCable -= 10;
                tigeD.style.transform = "rotateX(-25deg)";
            }

            // Animation visuelle de la flèche et du câble
            // On compense la rotation de la flèche pour que le câble descende toujours verticalement
            fleche.style.transform = "translateX(-50%) rotate(" + (90 - currentAngle) + "deg)";
            cable.style.transform = "translateX(-50%) rotate(" + -(90 - currentAngle) + "deg)";
            cable.style.height = currentCable + "px";

            // Mise à jour de l'ordinateur de bord
            angTxt.innerText = currentAngle;
            cabTxt.innerText = (currentCable / 33).toFixed(1);

            // Système d'alarme de sécurité
            if (currentAngle < 32) {
                statusTxt.innerText = "🚨 CRITIQUE !";
                statusTxt.style.color = "#ef4444";
            } else {
                statusTxt.innerText = "SÉCURISÉE";
                statusTxt.style.color = "#22c55e";
            }

            // Retour automatique des manettes physiques au point mort
            setTimeout(() => {
                tigeG.style.transform = "rotateX(0deg)";
                tigeD.style.transform = "rotateX(0deg)";
            }, 150);
        }

        // Configuration initiale de la grue au démarrage
        fleche.style.transform = "translateX(-50%) rotate(" + (90 - currentAngle) + "deg)";
        cable.style.transform = "translateX(-50%) rotate(" + -(90 - currentAngle) + "deg)";
    </script>
</body>
</html>
"""

components.html(code_simulateur_natif, height=480)

st.info("⚠️ **Mise à jour réussie :** Le moteur d'affichage a été converti pour s'adapter parfaitement aux écrans des smartphones. Si le rectangle noir persiste, rafraîchissez simplement la page sur votre téléphone.")
