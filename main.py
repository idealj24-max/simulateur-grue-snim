
import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURATION DE L'INTERFACE MOBILE
st.set_page_config(page_title="Simulateur 3D Grue SNIM", page_icon="🏗️", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #f3f4f6; }
    h1 { color: #f59e0b; text-align: center; font-family: 'Arial Black', sans-serif; font-size: 22px; }
    .stApp { background-color: #0b0f19; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🏗️ SIMULATEUR 3D INDOOR - CABINE TEREX/GROVE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; margin-top:-15px;'>Pilotez la flèche en temps réel depuis les commandes tactiles ci-dessous</p>", unsafe_allow_html=True)

# 2. LE CŒUR DU SIMULATEUR : CODE DE RENDU 3D (THREE.JS / WEBGL)
# Ce bloc crée une scène 3D, une cabine virtuelle, et anime le bras de la grue directement sur l'écran du téléphone
code_simulateur_3d = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cloudflare.com"></script>
    <style>
        body { margin: 0; overflow: hidden; background-color: #0b0f19; font-family: sans-serif; }
        #canvas-container { width: 100%; height: 350px; position: relative; border-radius: 12px; overflow: hidden; border: 2px solid #38bdf8; }
        .controls-panel { display: flex; justify-content: space-around; padding: 15px; background: #1e293b; border-radius: 12px; margin-top: 15px; }
        .btn-joystick { background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%); color: white; border: none; padding: 15px 25px; font-weight: bold; border-radius: 10px; font-size: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); touch-action: manipulation; }
        .btn-joystick:active { background: #0284c7; }
        .telemetry { position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7); color: #22c55e; padding: 8px; border-radius: 5px; font-family: monospace; font-size: 12px; pointer-events: none; border: 1px solid #22c55e; }
    </style>
</head>
<body>

    <div id="canvas-container">
        <div class="telemetry">🧭 SÉCURITÉ CEC : OK<br>ANGLE FLÈCHE : <span id="angle-display">30</span>°</div>
    </div>

    <div class="controls-panel">
        <button class="btn-joystick" onclick="bougerFleche(0.02)">🕹️ LEVER LE BRAS</button>
        <button class="btn-joystick" onclick="bougerFleche(-0.02)">🕹️ BAISSER LE BRAS</button>
    </div>

    <script>
        // Initialisation de la scène 3D Three.js
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x111827); // Couleur du ciel de nuit industrielle

        // Caméra placée à l'intérieur de la cabine (Vue Grutier)
        const camera = new THREE.PerspectiveCamera(60, container.clientWidth / 350, 0.1, 1000);
        camera.position.set(0, 1.5, 0); // Position des yeux du pilote

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(container.clientWidth, 350);
        container.appendChild(renderer.domElement);

        // Lumières du chantier
        const light = new THREE.AmbientLight(0xffffff, 0.7);
        scene.add(light);
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.5);
        dirLight.position.set(5, 10, 7);
        scene.add(dirLight);

        // 1. CRÉATION DU SOL DU CHANTIER SNIM
        const floorGeo = new THREE.PlaneGeometry(100, 100);
        const floorMat = new THREE.MeshStandardMaterial({ color: 0x334155 });
        const floor = new THREE.Mesh(floorGeo, floorMat);
        floor.rotation.x = -Math.PI / 2;
        scene.add(floor);

        // 2. CRÉATION DES MONTANTS DE LA CABINE VISIBLE (Vue Intérieure)
        const cabineMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, wireframe: false });
        
        // Tableau de bord devant le grutier
        const dashGeo = new THREE.BoxGeometry(1.5, 0.4, 0.6);
        const dash = new THREE.Mesh(dashGeo, cabineMat);
        dash.position.set(0, 1, -0.6);
        scene.add(dash);

        // Montant gauche de la vitre
        const montantLGeo = new THREE.BoxGeometry(0.05, 2, 0.05);
        const montantL = new THREE.Mesh(montantLGeo, cabineMat);
        montantL.position.set(-0.7, 1.5, -0.8);
        scene.add(montantL);

        // Montant droit de la vitre
        const montantR = montantL.clone();
        montantR.position.set(0.7, 1.5, -0.8);
        scene.add(montantR);

        // 3. CRÉATION DU BRAS DE LA GRUE (La Flèche télescopique externe)
        const pivotFleche = new THREE.Group();
        pivotFleche.position.set(0, 2, -1); // Le pivot est fixé à l'avant-haut de la cabine
        scene.add(pivotFleche);

        const flecheGeo = new THREE.BoxGeometry(0.3, 0.3, 8); // Un long bras de 8 mètres de long
        const flecheMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b }); // Couleur jaune Terex/Grove
        const flecheMesh = new THREE.Mesh(flecheGeo, flecheMat);
        flecheMesh.position.set(0, 0, -4); // Décalage pour que le bras pivote depuis sa base
        pivotFleche.add(flecheMesh);

        // Position de départ de la flèche (inclinée vers le haut)
        pivotFleche.rotation.x = -0.5; 

        // Rendu de l'animation
        function animate() {
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
        }
        animate();

        # Fonction de contrôle activée par les leviers tactiles de l'étudiant
        window.bougerFleche = function(valeur) {
            // Limites de sécurité pour éviter que le bras traverse le sol
            if (pivotFleche.rotation.x + valeur < -1.2 && pivotFleche.rotation.x + valeur > -0.1) {
                pivotFleche.rotation.x += valeur;
                
                // Calcul de l'angle réel en degrés pour l'écran de sécurité
                let angleDegres = Math.round(Math.abs(pivotFleche.rotation.x) * (180 / Math.PI));
                document.getElementById('angle-display').innerText = angleDegres;
            }
        }

        // Ajustement automatique de la taille si l'élève tourne son téléphone
        window.addEventListener('resize', () => {
            camera.aspect = container.clientWidth / 350;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, 350);
        });
    </script>
</body>
</html>
"""

# 3. AFFICHAGE DU COMPOSANT DANS VOTRE APPLICATION STREAMLIT
# Nous injectons le code 3D de manière fluide au milieu de l'écran du smartphone
components.html(code_simulateur_3d, height=450)

# Message de consignes pour l'étudiant sous le simulateur
st.info("💡 Instructions d'examen : Actionnez les leviers tactiles pour monter ou descendre la flèche télescopique jaune. Surveillez l'ordinateur de sécurité CEC en haut à gauche pour éviter tout angle critique de basculement.")
