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

st.markdown("<h1>🏗️ SIMULATEUR COCKPIT GRUE 3D PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; margin-top:-10px;'>Poste de pilotage virtuel avec commandes hydrauliques réactives</p>", unsafe_allow_html=True)

# MOTEUR GRAPHIQUE INTERACTIF : COCKPIT + VOLANT + JOYSTICKS + FLECHE + CABLE + CROCHET
code_simulateur_ultime = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cloudflare.com"></script>
    <style>
        body { margin: 0; overflow: hidden; background-color: #0b0f19; font-family: sans-serif; }
        #canvas-container { width: 100%; height: 420px; position: relative; border-radius: 12px; overflow: hidden; border: 3px solid #f59e0b; }
        .dashboard-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 12px; background: #1e293b; border-radius: 12px; margin-top: 10px; }
        .control-lever { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; border: none; padding: 14px; font-weight: bold; border-radius: 8px; font-size: 13px; box-shadow: 0 4px 6px rgba(0,0,0,0.4); touch-action: manipulation; }
        .control-lever:active { background: #d97706; }
        .telemetry-screen { position: absolute; top: 12px; left: 12px; background: rgba(15, 23, 42, 0.9); color: #38bdf8; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 11px; pointer-events: none; border: 1px solid #334155; line-height: 1.5; }
    </style>
</head>
<body>

    <div id="canvas-container">
        <div class="telemetry-screen">
            💻 ORDINATEUR DE BORD CEC<br>
            -----------------------<br>
            • FLÈCHE : <span id="ang-txt">35</span>°<br>
            • CÂBLE : <span id="cab-txt">3.0</span> m<br>
            • CHARGE : <span id="status-txt" style="color:#22c55e;">SÉCURISÉE</span>
        </div>
    </div>

    <div class="dashboard-buttons">
        <button class="control-lever" onclick="piloterGrue('lever')">🕹️ MANETTE GAUCHE : LEVER BRAS</button>
        <button class="control-lever" onclick="piloterGrue('baisser')">🕹️ MANETTE GAUCHE : BAISSER BRAS</button>
        <button class="control-lever" onclick="piloterGrue('enrouler')">🪝 MANETTE DROITE : ENROULER CÂBLE</button>
        <button class="control-lever" onclick="piloterGrue('derouler')">🪝 MANETTE DROITE : DÉROULER CÂBLE</button>
    </div>

    <script>
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xbae6fd); // Ciel bleu de chantier

        const camera = new THREE.PerspectiveCamera(60, container.clientWidth / 420, 0.1, 1000);
        camera.position.set(0, 1.2, 0); // Position des yeux à l'intérieur du cockpit

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(container.clientWidth, 420);
        container.appendChild(renderer.domElement);

        const light = new THREE.AmbientLight(0xffffff, 0.9);
        scene.add(light);
        const dLight = new THREE.DirectionalLight(0xffffff, 0.4);
        dLight.position.set(5, 15, 5);
        scene.add(dLight);

        // 1. SOL ET ENVIRONNEMENT EXTERIEUR
        const groundGeo = new THREE.PlaneGeometry(300, 300);
        const groundMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8 });
        const ground = new THREE.Mesh(groundGeo, groundMat);
        ground.rotation.x = -Math.PI / 2;
        scene.add(ground);

        // Élément de décor (Conteneur rouge sur le chantier)
        const targetGeo = new THREE.BoxGeometry(3, 2.5, 5);
        const targetMat = new THREE.MeshStandardMaterial({ color: 0xef4444 });
        const conteneur = new THREE.Mesh(targetGeo, targetMat);
        conteneur.position.set(4, 1.25, -12);
        scene.add(conteneur);

        // 2. INTERIEUR DE LA CABINE (TABLEAU DE BORD, VOLANT, JOYSTICKS)
        const cabMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.6 });
        const steelMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.8 });

        // Console centrale arrondie
        const dashGeo = new THREE.CylinderGeometry(0.7, 0.7, 1.6, 16, 1, false, 0, Math.PI);
        const dash = new THREE.Mesh(dashGeo, cabMat);
        dash.rotation.z = Math.PI / 2;
        dash.rotation.x = Math.PI / 2;
        dash.position.set(0, 0.7, -0.6);
        scene.add(dash);

        // Volant de la grue mobile
        const steerGeo = new THREE.TorusGeometry(0.16, 0.02, 6, 18);
        const volant = new THREE.Mesh(steerGeo, steelMat);
        volant.position.set(-0.35, 0.8, -0.5);
        volant.rotation.x = 1.1;
        scene.add(volant);

        // Supports des Joysticks d'accoudoir
        const baseJoyL = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.25, 0.25), cabMat);
        baseJoyL.position.set(-0.6, 0.6, -0.1);
        scene.add(baseJoyL);
        const baseJoyR = baseJoyL.clone();
        baseJoyR.position.set(0.6, 0.6, -0.1);
        scene.add(baseJoyR);

        // Tiges physiques des Joysticks
        const stickGeo = new THREE.CylinderGeometry(0.01, 0.01, 0.18);
        const joystickG = new THREE.Mesh(stickGeo, steelMat);
        joystickG.position.set(-0.6, 0.72, -0.1);
        scene.add(joystickG);
        const joystickD = joystickG.clone();
        joystickD.position.set(0.6, 0.72, -0.1);
        scene.add(joystickD);

        // 3. LA FLÈCHE JAUNE EXTÉRIEURE TEREX / GROVE
        const pivotFleche = new THREE.Group();
        pivotFleche.position.set(0, 1.6, -1.1); // Sortie à l'avant du pare-brise
        scene.add(pivotFleche);

        const flecheMesh = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.35, 12), new THREE.MeshStandardMaterial({ color: 0xf59e0b }));
        flecheMesh.position.set(0, 0, -6);
        pivotFleche.add(flecheMesh);

        // 4. LE MECANISME CÂBLE ET CROCHET
        const pivotCrochet = new THREE.Group();
        pivotCrochet.position.set(0, 0, -12); // Fixé au bout de la flèche de 12m
        pivotFleche.add(pivotCrochet);

        let longCable = 3.5;
        const cableGeo = new THREE.CylinderGeometry(0.015, 0.015, 1, 6);
        const cableMesh = new THREE.Mesh(cableGeo, new THREE.MeshStandardMaterial({ color: 0x64748b }));
        pivotCrochet.add(cableMesh);

        const crochetMesh = new THREE.Mesh(new THREE.TorusGeometry(0.14, 0.03, 6, 16, Math.PI), new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.9 }));
        crochetMesh.rotation.x = Math.PI;
        pivotCrochet.add(crochetMesh);

        // Position d'inclinaison initiale de la grue
        pivotFleche.rotation.x = -0.6;

        function rafraichirCable() {
            cableMesh.scale.y = longCable;
            cableMesh.position.y = -longCable / 2;
            crochetMesh.position.y = -longCable;
            document.getElementById('cab-txt').innerText = longCable.toFixed(1);
        }
        rafraichirCable();

        // BOUCLE PRINCIPALE D'ANIMATION GRAPHIQUE
        function animate() {
            requestAnimationFrame(animate);
            // Assure que le câble descend toujours verticalement vers le sol
            pivotCrochet.quaternion.copy(pivotFleche.quaternion).invert();
            renderer.render(scene, camera);
        }
        animate();

        // ACTIONNEMENT DES LEVIERS DE LA CABINE
        window.piloterGrue = function(action) {
            if (action === 'lever' && pivotFleche.rotation.x > -1.35) {
                pivotFleche.rotation.x -= 0.02;
                joystickG.rotation.x = -0.3; // Incliner manette gauche vers l'avant
            } 
            else if (action === 'baisser' && pivotFleche.rotation.x < -0.2) {
                pivotFleche.rotation.x += 0.02;
                joystickG.rotation.x = 0.3; // Incliner manette gauche vers l'arrière
            } 
            else if (action === 'derouler' && longCable < 7.0) {
                longCable += 0.15;
                rafraichirCable();
                joystickD.rotation.x = 0.3; // Incliner manette droite
            } 
            else if (action === 'enrouler' && longCable > 1.2) {
                longCable -= 0.15;
                rafraichirCable();
                joystickD.rotation.x = -0.3;
            }

            // Calcul de l'angle et mise à jour de la sécurité
            let deg = Math.round(Math.abs(pivotFleche.rotation.x) * (180 / Math.PI));
            document.getElementById('ang-txt').innerText = deg;
            
            const stTxt = document.getElementById('status-txt');
            if (deg < 32) {
                stTxt.innerText = "🚨 CRITIQUE !";
                stTxt.style.color = "#ef4444";
            } else {
                stTxt.innerText = "SÉCURISÉE";
                stTxt.style.color = "#22c55e";
            }

            // Retour automatique des joysticks au point mort après l'action
            setTimeout(() => { joystickG.rotation.x = 0; joystickD.rotation.x = 0; }, 120);
        }

        window.addEventListener('resize', () => {
            camera.aspect = container.clientWidth / 420;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, 420);
        });
    </script>
</body>
</html>
"""

components.html(code_simulateur_ultime, height=520)

