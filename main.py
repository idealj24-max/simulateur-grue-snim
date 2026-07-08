import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Simulateur Cockpit Grue SNIM", page_icon="🏗️", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #f3f4f6; }
    h1 { color: #f59e0b; text-align: center; font-family: 'Arial Black', sans-serif; font-size: 22px; }
    .stApp { background-color: #0b0f19; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🏗️ SIMULATEUR COCKPIT REALISTE TEREX / GROVE</h1>", unsafe_allow_html=True)

# CODE DU SIMULATEUR AVEC INTEGRATION DE TEXTURES ET TABLEAU DE BORD AVANCÉ
code_simulateur_cockpit = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cloudflare.com"></script>
    <style>
        body { margin: 0; overflow: hidden; background-color: #0b0f19; font-family: sans-serif; }
        #canvas-container { width: 100%; height: 400px; position: relative; border-radius: 12px; overflow: hidden; border: 3px solid #f59e0b; }
        .joystick-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 12px; background: #1e293b; border-radius: 12px; margin-top: 10px; }
        .btn-mvt { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; border: none; padding: 15px; font-weight: bold; border-radius: 8px; font-size: 14px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); touch-action: manipulation; }
        .btn-mvt:active { background: #d97706; }
    </style>
</head>
<body>

    <div id="canvas-container"></div>

    <div class="joystick-layout">
        <button class="btn-mvt" onclick="actionnerLevier('lever')">🕹️ POUSSER LEVIER GAUCHE (LEVER)</button>
        <button class="btn-mvt" onclick="actionnerLevier('baisser')">🕹️ TIRER LEVIER GAUCHE (BAISSER)</button>
    </div>

    <script>
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();
        
        // Ajout d'un ciel réaliste en arrière-plan (Vue extérieure)
        scene.background = new THREE.Color(0xbae6fd); // Ciel bleu clair de Nouadhibou

        const camera = new THREE.PerspectiveCamera(60, container.clientWidth / 400, 0.1, 1000);
        camera.position.set(0, 1.2, 0); // Position exacte des yeux du grutier au centre du cockpit

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(container.clientWidth, 400);
        container.appendChild(renderer.domElement);

        // LUMIÈRES D'AMBIANCE
        const light = new THREE.AmbientLight(0xffffff, 0.9);
        scene.add(light);

        // 1. LE DECOR EXTÉRIEUR (Chantier SNIM)
        const groundGeo = new THREE.PlaneGeometry(500, 500);
        const groundMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0 }); // Sol clair
        const ground = new THREE.Mesh(groundGeo, groundMat);
        ground.rotation.x = -Math.PI / 2;
        scene.add(ground);

        // Ajouter des obstacles extérieurs visibles à travers la vitre (ex: conteneurs)
        const boxGeo = new THREE.BoxGeometry(3, 3, 6);
        const boxMat = new THREE.MeshStandardMaterial({ color: 0xef4444 });
        const conteneur = new THREE.Mesh(boxGeo, boxMat);
        conteneur.position.set(5, 1.5, -15);
        scene.add(conteneur);

        // 2. CONSTRUCIION DU COCKPIT RÉALISTE (Vue Intérieure)
        const interiorMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.5 });
        const metalMat = new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.8 });

        # Coque arrière et toit de la cabine
        const cabineGeo = new THREE.BoxGeometry(2, 2.2, 2);
        const cabineMesh = new THREE.Mesh(cabineGeo, new THREE.MeshStandardMaterial({ color: 0x0f172a, wireframe: true }));
        cabineMesh.position.set(0, 1.1, 0);
        scene.add(cabineMesh);

        # VRAI TABLEAU DE BORD ARRONDIE (Console centrale)
        const dashGeo = new THREE.CylinderGeometry(0.8, 0.8, 1.6, 24, 1, false, 0, Math.PI);
        const dash = new THREE.Mesh(dashGeo, interiorMat);
        dash.rotation.z = Math.PI / 2;
        dash.rotation.x = Math.PI / 2;
        dash.position.set(0, 0.7, -0.7);
        scene.add(dash);

        # ÉCRAN DE BORD LUMINEUX (CEC Numérique intégré au tableau de bord)
        const screenGeo = new THREE.PlaneGeometry(0.4, 0.25);
        const screenMat = new THREE.MeshBasicMaterial({ color: 0x0284c7 });
        const ecranBord = new THREE.Mesh(screenGeo, screenMat);
        ecranBord.position.set(0, 0.85, -0.68);
        ecranBord.rotation.x = -0.2;
        scene.add(ecranBord);

        # LE VOLANT DE DIRECTION
        const torusGeo = new THREE.TorusGeometry(0.18, 0.02, 8, 24);
        const volant = new THREE.Mesh(torusGeo, metalMat);
        volant.position.set(-0.3, 0.8, -0.55);
        volant.rotation.x = 1.2;
        scene.add(volant);

        # LES DEUX MANETTES DE CONTROLE (Joysticks latéraux)
        const joyBaseGeo = new THREE.BoxGeometry(0.15, 0.3, 0.3);
        const joyBaseL = new THREE.Mesh(joyBaseGeo, interiorMat);
        joyBaseL.position.set(-0.6, 0.6, -0.2);
        scene.add(joyBaseL);

        const joyBaseR = joyBaseL.clone();
        joyBaseR.position.set(0.6, 0.6, -0.2);
        scene.add(joyBaseR);

        // Tiges des manettes
        const stickGeo = new THREE.CylinderGeometry(0.01, 0.01, 0.2);
        const manetteG = new THREE.Mesh(stickGeo, metalMat);
        manetteG.position.set(-0.6, 0.75, -0.2);
        scene.add(manetteG);

        // 3. LA FLÈCHE EXTÉRIEURE DE LA GRUE VISIBLE DEPUIS LA VITRE
        const pivotFleche = new THREE.Group();
        pivotFleche.position.set(0, 1.5, -1.2);
        scene.add(pivotFleche);

        const mainFleche = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.4, 12), new THREE.MeshStandardMaterial({ color: 0xf59e0b }));
        mainFleche.position.set(0, 0, -6);
        pivotFleche.add(mainFleche);

        pivotFleche.rotation.x = -0.5;

        // ANIMATION DU RENDU
        function animate() {
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
        }
        animate();

        // INTELLIGENCE DES COMMANDES TACTILES
        window.actionnerLevier = function(direction) {
            if (direction === 'lever' && pivotFleche.rotation.x > -1.3) {
                pivotFleche.rotation.x -= 0.02;
                manetteG.rotation.x = -0.3; // Inclinaison de la manette réaliste
            } else if (direction === 'baisser' && pivotFleche.rotation.x < -0.2) {
                pivotFleche.rotation.x += 0.02;
                manetteG.rotation.x = 0.3;
            }
            setTimeout(() => { manetteG.rotation.x = 0; }, 150); // Retour au point mort
        }

        window.addEventListener('resize', () => {
            camera.aspect = container.clientWidth / 400;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, 400);
        });
    </script>
</body>
</html>
"""

components.html(code_simulateur_cockpit, height=500)

st.info("💡 **Note technique :** Vous êtes au centre de la cabine de pilotage. Devant vous se trouvent le volant de manœuvre, l'écran de contrôle bleu et la manette de gauche. À travers le pare-brise, vous voyez le chantier extérieur et la grande flèche télescopique jaune s'animer.")
