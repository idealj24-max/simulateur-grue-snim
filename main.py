import streamlit as st
import time

# 1. CONFIGURATION DE L'INTERFACE SIMULATEUR
st.set_page_config(page_title="Simulateur Grue SNIM Pro", page_icon="🏗️", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stApp { background-color: #0f172a; }
    h1 { color: #f59e0b; text-align: center; font-family: 'Arial Black', sans-serif; font-size: 24px; }
    h2 { color: #38bdf8; font-size: 18px; }
    .success-box { background-color: #14532d; padding: 15px; border-radius: 8px; border: 2px solid #22c55e; color: #f0fdf4; }
    .danger-box { background-color: #7f1d1d; padding: 15px; border-radius: 8px; border: 2px solid #ef4444; color: #fef2f2; }
    .warning-box { background-color: #78350f; padding: 15px; border-radius: 8px; border: 2px solid #eab308; color: #fffbeb; }
    .score-text { font-size: 24px; font-weight: bold; text-align: center; color: #38bdf8; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div style='text-align: center; font-size: 45px;'>🏗️🎓⚡</div>", unsafe_allow_html=True)
st.markdown("<h1>SIMULATEUR DE LEVAGE & SYSTÈME D'EXAMEN v2.0</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Centre de Formation Technique SNIM - Grue Mobile Terex & Grove</p>", unsafe_allow_html=True)

# 2. CONFIGURATION DE LA MACHINE (PANNEAU LATÉRAL)
st.sidebar.markdown("### 🎛️ CONFIGURATION DE LA GRUE")
modele_grue = st.sidebar.selectbox("Sélectionnez le modèle de grue :", ["Terex Demag AC 100 (100 Tonnes)", "Grove GMK 5130 (130 Tonnes)"])

if "Terex" in modele_grue:
    capacite_max = 100.0
    longueur_fleche_max = 50
    rayon_max = 40
else:
    capacite_max = 130.0
    longueur_fleche_max = 60
    rayon_max = 48

# 3. INTERFACE COMMANDES EN CABINE
st.markdown("---")
st.markdown("## 🕹️ Commandes de la Cabine & Environnement")

col1, col2 = st.columns(2)
with col1:
    poids_charge = st.number_input("Poids de la charge à lever (en Tonnes) :", min_value=0.5, max_value=200.0, value=12.0, step=0.5)
    longueur_fleche = st.slider("Longueur de la flèche déployée (mètres) :", min_value=10, max_value=longueur_fleche_max, value=25)
    rayon_travail = st.slider("Rayon de travail / Portée (mètres) :", min_value=3, max_value=rayon_max, value=12)

with col2:
    stabilisateurs = st.radio("Déploiement des stabilisateurs (Outriggers) :", ["0% (Sur pneus)", "50% Étroit", "100% Pleine extension"])
    st.markdown("**⚠️ Éléments Environnementaux Critiques :**")
    vitesse_vent = st.slider("Vitesse du vent détectée par l'anémomètre (m/s) :", min_value=0, max_value=25, value=6)
    lignes_electriques = st.radio("Présence de lignes électriques haute tension à proximité :", ["Non", "Oui (Moins de 6 mètres sans coupure de ligne)"])
    etat_elingues = st.radio("État du matériel de levage (Élingues/Manilles) :", ["Parfait état (Vérifiées)", "Usées / Légers fils coupés (Non vérifiées)"])

# 4. CHECK-LIST DE SÉCURITÉ OBLIGATOIRE
st.markdown("### 🔍 Check-list Obligatoire de l'Élève")
col_chk1, col_chk2 = st.columns(2)
with col_chk1:
    calage_ok = st.checkbox("Plaques de calage installées sous les vérins")
with col_chk2:
    zone_balisee = st.checkbox("Zone de pivotement balisée (Risque de coincement)")

# 5. MOTEUR DE PHYSIQUE ET PARAMÈTRES DE CALCUL
facteur_securite = 1.0
if stabilisateurs == "0% (Sur pneus)":
    facteur_securite = 0.15
elif stabilisateurs == "50% Étroit":
    facteur_securite = 0.60

capacite_reelle_autorisee = (capacite_max * (12 / (rayon_travail + (longueur_fleche * 0.1)))) * facteur_securite
capacite_reelle_autorisee = min(capacite_reelle_autorisee, capacite_max)
pourcentage_utilisation = (poids_charge / capacite_reelle_autorisee) * 100

# 6. ENCLENCHEMENT DU LEVAGE ET NOTATION DU CANDIDAT
st.markdown("---")
if st.button("🚀 ENCLENCHER LA MANOEUVRE DE LEVAGE EXAMEN"):
    with st.spinner("Analyse des paramètres de levage en cours..."):
        time.sleep(2)
        
        # Initialisation du barème de notation sur 20 points
        score = 20
        erreurs = []
        accident_majeur = False
        cause_accident = ""

        # Détection des fautes de sécurité et calcul du score
        if not calage_ok:
            score -= 4
            erreurs.append("Oubli des plaques de calage (Risque d'enfoncement du sol).")
        if not zone_balisee:
            score -= 3
            erreurs.append("Zone de pivotement non balisée (Danger pour le personnel au sol).")
            
        # ACCIDENT 1 : Surcharge (Bascule de l'engin)
        if pourcentage_utilisation > 100:
            accident_majeur = True
            score = 0
            cause_accident = f"🚨 SURCHARGE CRITIQUE : Le CEC affiche {pourcentage_utilisation:.1f}%. La grue {modele_grue} a basculé vers l'avant. La charge est trop lourde pour le rayon de travail sélectionné."
            
        # ACCIDENT 2 : Lignes Électriques Haute Tension
        elif lignes_electriques == "Oui (Moins de 6 mètres sans coupure de ligne)":
            accident_majeur = True
            score = 0
            cause_accident = "⚡ ÉLECTROCUTION : Arc électrique formé entre la flèche de la grue et la ligne haute tension. Risque mortel immédiat pour le grutier et le chef de manœuvre."
            
        # ACCIDENT 3 : Rupture d'élingue
        elif etat_elingues == "Usées / Légers fils coupés (Non vérifiées)":
            accident_majeur = True
            score = 0
            cause_accident = "💥 RUPTURE DE CHARGE : Les élingues endommagées ont cédé sous la tension. La charge a chuté au sol, détruisant le matériel."

        # ACCIDENT 4 : Vent Violent (Effet de voile)
        elif vitesse_vent > 9:
            accident_majeur = True
            score = 0
            cause_accident = f"💨 FORCE DU VENT CRITIQUE : Levage interdit à {vitesse_vent} m/s (Maximum autorisé : 9 m/s). Le vent a déporté la charge hors de l'axe, provoquant la torsion de la flèche télescopique."

        # Pénalité zone orange (Sûreté limite)
        elif pourcentage_utilisation > 85:
            score -= 3
            erreurs.append("Levage en zone critique (Supérieur à 85% de la capacité maximale).")

        # 7. AFFICHAGE DES RÉSULTATS DE L'EXAMEN
        st.markdown("## 📊 Verdict de la Commission d'Évaluation SNIM")
        
        if accident_majeur:
            st.markdown(f"""
                <div class='danger-box'>
                    <h3>❌ ÉCHEC CRITIQUE : ACCIDENT MAJEUR SUR LE CHANTIER</h3>
                    <p>{cause_accident}</p>
                    <p class='score-text'>NOTE FINALE : {score}/20</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            if score == 20:
                st.markdown(f"""
                    <div class='success-box'>
                        <h3>✅ EXAMEN RÉUSSI - SANS FAUTE</h3>
                        <p>Le levage s'est déroulé en parfaite conformité avec les règles de sécurité constructeur de la grue {modele_grue}.</p>
                        <p class='score-text'>NOTE FINALE : {score}/20 (Mention Excellent)</p>
                    </div>
                """, unsafe_allow_html=True)
            elif score >= 12:
                st.markdown(f"""
                    <div class='warning-box'>
                        <h3>⚠️ EXAMEN RÉUSSI AVECAVERTISSEMENTS</h3>
                        <p>La charge a été déplacée, mais des fautes opérationnelles ou de sécurité ont été commises.</p>
                        <p><b>Pénalités appliquées :</b> {" | ".join(erreurs)}</p>
                        <p class='score-text'>NOTE FINALE : {score}/20 (Mention Passable)</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='danger-box'>
                        <h3>❌ EXAMEN ÉCHOUÉ (Note insuffisante)</h3>
                        <p>Le candidat a commis trop d'infractions de sécurité pour être validé sur le terrain.</p>
                        <p><b>Fautes commises :</b> {" | ".join(erreurs)}</p>
                        <p class='score-text'>NOTE FINALE : {score}/20</p>
                    </div>
                """, unsafe_allow_html=True)
