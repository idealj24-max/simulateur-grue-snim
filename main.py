import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURATION DE L'INTERFACE MOBILE
st.set_page_config(page_title="Simulateur 3D Grue SNIM Pro", page_icon="🏗️", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #f3f4f6; }
    h1 { color: #f59e0b; text-align: center; font-family: 'Arial Black', sans-serif; font-size: 22px; margin-bottom: 0px; }
    .stApp { background-color: #0b0f19; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🏗️ SIMULATEUR GRUE 3D MULTI-VUES</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Module d'évaluation pour les centres de formation SNIM & KINROSS</p>", unsafe_allow_html=True)

# 2. INTÉGRATION DE LA SCÈNE COMPLÈTE EN THREE.JS (MOTEUR GRAPHIQUE INTERACTIF)
code_simulateur_graphique = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cloudflare.com"></script>
    <style>
        body { margin: 0; overflow: hidden; background-color: #0b0f19; font-family: sans-serif; }
        #canvas-container { width: 100%; height: 380px; position: relative; border-radius: 12px; overflow: hidden; border: 2px solid #f59e0b; }
        .controls-panel { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 12px; background: #1e293b; border-radius: 12px; margin-top: 10px; }
        .btn-joystick { background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%); color: white; border: none; padding: 12px; font-weight: bold; border-radius: 8px; font-size: 14px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); touch-action: manipulation; }
        .btn-joystick:active { background: #0284c7; }
        .btn-cam { background: linear-gradient(135deg, #a855f7 0%, #7e22ce 100%) !important; grid-column: span 2; }
        .telemetry { position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.85); color: #38bdf8; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 11px; pointer-events: none; border: 1px solid #334155; line-height: 1.4; }
    </style>
</head>
<body>

    <div id="canvas-container">
        <div class="telemetry">
            📊 ÉCRAN DE BORD ORDINATEUR CEC<br>
            ---------------------------<br>
            • STATUT : <span id="status-display" style="color:#22c55e; font-weight:bold;">SÉCURISÉ</span><br>
            • ANGLE DE FLÈCHE : <span id="angle-display">30</span>°<br>
            • RELEVAGE CÂBLE : <span id="cable-display">0</span> cm
        </div>
    </div>

    <div class="controls-panel">
        <button class="btn-joystick" onclick="bougerFleche(0.015)">🕹️ LEVER LA FLÈCHE</button>
        <button class="btn-joystick" onclick="bougerFleche(-0.015)">🕹️ BAISSER LA FLÈCHE</button>
        <button class="btn-joystick" onclick="ajusterCable(-0.1)">🪝 ENROULER LE CÂBLE</button>
        <button class="btn-joystick" onclick="ajusterCable(0.1)">🪝 DÉROULER LE CÂBLE</button>
        <button class="btn-joystick btn-cam" onclick="changerCamera()">🎥 CHANGER DE VUE (CABINE / CHANTIER)</button>
    </div>

    <script>
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0f172a); // Ambiance de chantier

        // CONFIGURATION DES DEUX CAMÉRAS (VUE INTÉRIEURE ET VUE EXTÉRIEURE)
        const camCabine = new THREE.PerspectiveCamera(65, container.clientWidth / 380, 0.1, 1000);
        camCabine.position.set(0, 1.5, -0.2); // Position exacte du grutier dans son siège

        const camChantier = new THREE.PerspectiveCamera(65, container.clientWidth / 380, 0.1, 1000);
        camChantier.position.set(7, 6, 8); // Vue aérienne extérieure du site minier
        camChantier.lookAt(0, 3, -4);

        let activeCamera = camCabine; // La caméra par défaut est la vue de l'intérieur

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(container.clientWidth, 380);
        container.appendChild(renderer.domElement);

        // SYSTÈME D'ÉCLAIRAGE
        const light = new THREE.AmbientLight(0xffffff, 0.8);
        scene.add(light);
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.6);
        dirLight.position.set(10, 20, 10);
        scene.add(dirLight);

        // 1. SOL DU SITE MINIÈRE DE LA SNIM
        const floorGeo = new THREE.PlaneGeometry(200, 200);
        const floorMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.8 });
        const floor = new THREE.Mesh(floorGeo, floorMat);
        floor.rotation.x = -Math.PI / 2;
        scene.add(floor);

        // 2. LA CABINE DU PILOTE (MONTANTS ET TABLEAU DE BORD)
        const cabineMat = new THREE.MeshStandardMaterial({ color: 0x1e293b });
        const dashGeo = new THREE.BoxGeometry(1.6, 0.4, 0.5);
        const dash = new THREE.Mesh(dashGeo, cabineMat);
        dash.position.set(0, 0.9, -0.6);
        scene.add(dash);

        const montantLGeo = new THREE.BoxGeometry(0.06, 2.5, 0.06);
        const montantL = new THREE.Mesh(montantLGeo, cabineMat);
        montantL.position.set(-0.75, 1.6, -0.7);
        scene.add(montantL);

        const montantR = montantL.clone();
        montantR.position.set(0.75, 1.6, -0.7);
        scene.add(montantR);

        // 3. LA FLÈCHE TÉLESCOPIQUE JAUNE (TEREX / GROVE)
        const pivotFleche = new THREE.Group();
        pivotFleche.position.set(0, 1.8, -0.9); // Axe de rotation au dessus du tableau de bord
        scene.add(pivotFleche);

        const flecheGeo = new THREE.BoxGeometry(0.4, 0.4, 10);
        const flecheMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.3 }); // Jaune industriel
        const flecheMesh = new THREE.Mesh(flecheGeo, flecheMat);
        flecheMesh.position.set(0, 0, -5); // Positionnement le long de l'axe Z négatif
        pivotFleche.add(flecheMesh);

        // 4. LE ENSEMBLE CÂBLE ET CROCHET AU BOUT DE LA FLÈCHE
        const pivotCrochet = new THREE.Group();
        pivotCrochet.position.set(0, 0, -10); // Placé à l'extrémité de la flèche de 10m
        pivotFleche.add(pivotCrochet);

        // Création du câble métallique vertical
        let longueurCable = 3.0; // Longueur initiale
        const cableGeo = new THREE.CylinderGeometry(0.02, 0.02, longueurCable, 8);
        const cableMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8 }); // Gris acier
        const cableMesh = new THREE.Mesh(cableGeo, cableMat);
        // Ajustement de la position pour que le câble descende verticalement
        cableMesh.position.y = -longueurCable / 2;
        pivotCrochet.add(cableMesh);

        # Le Crochet de levage
        const crochetGeo = new THREE.TorusGeometry(0.15, 0.04, 8, 24, Math.PI);
        const crochetMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.8 });
        const crochetMesh = new THREE.Mesh(crochetGeo, crochetMat);
        crochetMesh.rotation.x = Math.PI;
        crochetMesh.position.y = -longueurCable;
        pivotCrochet.add(crochetMesh);

        // Position de départ sécurisée de la flèche inclinée
        pivotFleche.rotation.x = -0.6;

        // ANIMATION ET SÉCURISATION DU RESTE DES AXES
        function animate() {
            requestAnimationFrame(animate);
            
            // Forcer le câble et le crochet à toujours rester parfaitement verticaux, peu importe l'inclinaison de la flèche
            pivotCrochet.quaternion.copy(pivotFleche.quaternion).invert();
            
            renderer.render(scene, activeCamera);
        }
        animate();

        // COMMANDE TACTILE 1 : CONFIGURATION DE LA FLÈCHE
        window.bougerFleche = function(valeur) {
            let futurAngle = pivotFleche.rotation.x + valeur;
            // Limites angulaires de sécurité du constructeur (Entre ~15° et ~75°)
            if (futurAngle < -0.25 && futurAngle > -1.35) {
                pivotFleche.rotation.x = futurAngle;
                
                let angleDegres = Math.round(Math.abs(pivotFleche.rotation.x) * (180 / Math.PI));
                document.getElementById('angle-display').innerText = angleDegres;
                analyserRisque(angleDegres);
            }
        }

        // COMMANDE TACTILE 2 : CONTROLE DU CÂBLE / MOUFLAGE
        window.ajusterCable = function(valeur) {
            if (longueurCable + valeur >= 1.0 && longueurCable + valeur <= 6.5) {
                longueurCable += valeur;
                
                // Redimensionner dynamiquement le câble
                cableMesh.scale.y = longueurCable / 3.0;
                cableMesh.position.y = -longueurCable / 2;
                
                // Repositionner le crochet à la base du câble modifié
                crochetMesh.position.y = -longueurCable;
                
                // Mettre à jour l'afficheur CEC (affichage en cm relatifs)
                document.getElementById('cable-display').innerText = Math.round((longueurCable - 3) * 100);
            }
        }

        // COMMANDE TACTILE 3 : SWITCH CAMÉRA INTERACTIVE
        window.changerCamera = function() {
            if (activeCamera === camCabine) {
                activeCamera = camChantier;
            } else {
                activeCamera = camCabine;
            }
        }

        // ORDINATEUR DE SÉCURITÉ EN TEMPS RÉEL (ALARMES CEC)
        function analyserRisque(angle) {
            const statusBox = document.getElementById('status-display');
            if (angle < 30) {
                statusBox.innerText = "🚨 ALARME SURCHARGE / BASCULEMENT !";
                statusBox.style.color = "#ef4444";
            } else if (angle < 45) {
                statusBox.innerText = "⚠️ ATTENTION PORTEE LIMITE";
                statusBox.style.color = "#eab308";
            } else {
                statusBox.innerText = "SÉCURISÉ";
                statusBox.style.color = "#22c55e";
            }
