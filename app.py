import streamlit as st
from datetime import date
from docx import Document
from io import BytesIO

st.set_page_config(page_title="Eco Pediátrico", layout="wide")

st.title("🫀 Generador de Ecocardiograma Pediátrico")

# =========================================================
# FUNCIONES GENERALES
# =========================================================
def calcular_superficie_corporal(peso, talla):
    try:
        peso_float = float(peso)
        talla_float = float(talla)
        sc = 0.024265 * (peso_float ** 0.5378) * (talla_float ** 0.3964)
        return round(sc, 3)
    except:
        return ""


def calcular_gradiente_bernoulli(velocidad):
    try:
        v = float(velocidad)
        gradiente = 4 * (v ** 2)
        return round(gradiente, 1)
    except:
        return ""


def clasificar_hap(psap):
    try:
        p = float(psap)
        if p < 30:
            return "Sin hipertensión pulmonar"
        elif 30 <= p < 45:
            return "Hipertensión pulmonar leve"
        elif 45 <= p < 65:
            return "Hipertensión pulmonar moderada"
        else:
            return "Hipertensión pulmonar severa"
    except:
        return ""
    
def calcular_fevi_teicholz(lvedd_mm, lvesd_mm):
    try:
        dd_cm = float(lvedd_mm) / 10
        ds_cm = float(lvesd_mm) / 10

        vtd = (7 * (dd_cm ** 3)) / (2.4 + dd_cm)
        vts = (7 * (ds_cm ** 3)) / (2.4 + ds_cm)

        if vtd <= 0:
            return ""

        fevi = ((vtd - vts) / vtd) * 100
        return round(fevi, 1)
    except:
        return ""
# =========================================================
# PARÁMETROS PHN PARA Z-SCORE
# =========================================================
PHN_PARAMS = {
    "ANN": {"alpha": 0.50, "mean": 1.48, "sd": 0.14, "unit": "cm"},
    "ROOT": {"alpha": 0.50, "mean": 2.06, "sd": 0.18, "unit": "cm"},
    "STJ": {"alpha": 0.50, "mean": 1.69, "sd": 0.16, "unit": "cm"},
    "AAO": {"alpha": 0.50, "mean": 1.79, "sd": 0.18, "unit": "cm"},
    "ARCHPROX": {"alpha": 0.50, "mean": 1.53, "sd": 0.23, "unit": "cm"},
    "ARCHDIST": {"alpha": 0.50, "mean": 1.36, "sd": 0.19, "unit": "cm"},
    "ISTH": {"alpha": 0.50, "mean": 1.25, "sd": 0.18, "unit": "cm"},
    "MPA": {"alpha": 0.50, "mean": 1.82, "sd": 0.24, "unit": "cm"},
    "RPA": {"alpha": 0.50, "mean": 1.07, "sd": 0.18, "unit": "cm"},
    "LPA": {"alpha": 0.50, "mean": 1.10, "sd": 0.18, "unit": "cm"},
    "LVEDD": {"alpha": 0.45, "mean": 3.89, "sd": 0.33, "unit": "cm"},
    "LVPWT": {"alpha": 0.40, "mean": 0.57, "sd": 0.09, "unit": "cm"},
    "LVST": {"alpha": 0.40, "mean": 0.58, "sd": 0.09, "unit": "cm"},
    "MVAP": {"alpha": 0.50, "mean": 2.31, "sd": 0.24, "unit": "cm"},
    "MVLAT": {"alpha": 0.50, "mean": 2.23, "sd": 0.22, "unit": "cm"},
    "TVAP": {"alpha": 0.50, "mean": 2.36, "sd": 0.28, "unit": "cm"},
    "TVLAT": {"alpha": 0.50, "mean": 2.36, "sd": 0.29, "unit": "cm"},
    "PVLAX": {"alpha": 0.50, "mean": 2.01, "sd": 0.28, "unit": "cm"},
    "PVSAX": {"alpha": 0.50, "mean": 1.91, "sd": 0.24, "unit": "cm"},
    "LMCA": {"alpha": 0.45, "mean": 2.95, "sd": 0.57, "unit": "mm"},
    "LAD": {"alpha": 0.45, "mean": 1.90, "sd": 0.34, "unit": "mm"},
    "RCA": {"alpha": 0.45, "mean": 2.32, "sd": 0.55, "unit": "mm"},
}
def calcular_zscore_phn(abrev, valor_mm, bsa):
    try:
        if valor_mm == "" or bsa == "":
            return ""

        params = PHN_PARAMS.get(abrev)
        if not params:
            return ""

        valor = float(valor_mm)
        bsa = float(bsa)

        # convertir mm → cm si aplica
        if params["unit"] == "cm":
            valor = valor / 10

        indexed = valor / (bsa ** params["alpha"])
        z = (indexed - params["mean"]) / params["sd"]

        return round(z, 2)
    except:
        return ""
    
def crear_word(texto):
    doc = Document()
    for linea in texto.split("\n"):
        doc.add_paragraph(linea)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# =========================================================
# PARÁMETROS REALES PHN PARA Z-SCORE
# Fórmula: z = ((medida / BSA**alpha) - mean) / sd
# OJO: algunas estructuras PHN están en cm y otras en mm
# =========================================================
PHN_PARAMS = {
    "ANN": {"alpha": 0.50, "mean": 1.48, "sd": 0.14, "unit": "cm"},
    "ROOT": {"alpha": 0.50, "mean": 2.06, "sd": 0.18, "unit": "cm"},
    "STJ": {"alpha": 0.50, "mean": 1.69, "sd": 0.16, "unit": "cm"},
    "AAO": {"alpha": 0.50, "mean": 1.79, "sd": 0.18, "unit": "cm"},
    "ARCHPROX": {"alpha": 0.50, "mean": 1.53, "sd": 0.23, "unit": "cm"},
    "ARCHDIST": {"alpha": 0.50, "mean": 1.36, "sd": 0.19, "unit": "cm"},
    "ISTH": {"alpha": 0.50, "mean": 1.25, "sd": 0.18, "unit": "cm"},
    "LMCA": {"alpha": 0.45, "mean": 2.95, "sd": 0.57, "unit": "mm"},
    "LAD": {"alpha": 0.45, "mean": 1.90, "sd": 0.34, "unit": "mm"},
    "RCA": {"alpha": 0.45, "mean": 2.32, "sd": 0.55, "unit": "mm"},
    "PVSAX": {"alpha": 0.50, "mean": 1.91, "sd": 0.24, "unit": "cm"},
    "PVLAX": {"alpha": 0.50, "mean": 2.01, "sd": 0.28, "unit": "cm"},
    "MPA": {"alpha": 0.50, "mean": 1.82, "sd": 0.24, "unit": "cm"},
    "RPA": {"alpha": 0.50, "mean": 1.07, "sd": 0.18, "unit": "cm"},
    "LPA": {"alpha": 0.50, "mean": 1.10, "sd": 0.18, "unit": "cm"},
    "LVEDD": {"alpha": 0.45, "mean": 3.89, "sd": 0.33, "unit": "cm"},
    "LVPWT": {"alpha": 0.40, "mean": 0.57, "sd": 0.09, "unit": "cm"},
    "LVST": {"alpha": 0.40, "mean": 0.58, "sd": 0.09, "unit": "cm"},
    "MVAP": {"alpha": 0.50, "mean": 2.31, "sd": 0.24, "unit": "cm"},
    "MVLAT": {"alpha": 0.50, "mean": 2.23, "sd": 0.22, "unit": "cm"},
    "TVAP": {"alpha": 0.50, "mean": 2.36, "sd": 0.28, "unit": "cm"},
    "TVLAT": {"alpha": 0.50, "mean": 2.36, "sd": 0.29, "unit": "cm"},
}
# =========================================================
# FILIACIÓN
# =========================================================
st.subheader("Datos de filiación")

col1, col2, col3 = st.columns(3)

with col1:
    nombre = st.text_input("Nombre")
    edad_numero = st.number_input("Edad", min_value=0, step=1)
    edad_unidad = st.selectbox("Unidad de edad", ["días", "meses", "años"])
    peso = st.text_input("Peso (kg)")

with col2:
    talla = st.text_input("Talla (cm)")
    superficie_corporal = calcular_superficie_corporal(peso, talla)
    sc_texto = f"{superficie_corporal} m²" if superficie_corporal != "" else ""
    st.text_input("Superficie corporal (m²)", value=sc_texto, disabled=True)
    institucion = st.text_input("Institución")
    eps = st.text_input("EPS")

with col3:
    tipo_documento = st.selectbox("Tipo documento", ["CC", "TI", "RC", "CE"])
    numero_documento = st.text_input("Documento")
    fecha = st.date_input("Fecha", value=date.today())

st.divider()

# =========================================================
# MODO INFORME
# =========================================================
st.subheader("Modo de informe")

col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    modo_normal = st.checkbox("🟢 Eco normal automático")

with col_m2:
    psap_normal = st.text_input("PSAP (mmHg)")

with col_m3:
    fevi = st.text_input("FEVI (%)")

st.divider()

# =========================================================
# HALLAZGOS GENERALES
# =========================================================
st.subheader("Hallazgos generales")

col_g1, col_g2, col_g3 = st.columns(3)

with col_g1:
    ventana_acustica = st.selectbox("Ventana acústica", ["Buena", "Regular", "Limitada"])
    situs = st.selectbox("Situs", ["solitus", "inversus", "ambiguus"])

with col_g2:
    cardia = st.selectbox("Cardia", ["Levocardia", "Dextrocardia", "Mesocardia"])
    apex = st.selectbox("Apex", ["Levoapex", "Dextroapex", "Mesoapex"])

with col_g3:
    concordancia = st.selectbox(
        "Concordancia",
        ["Concordancia AV y VA", "Discordancia AV", "Discordancia VA", "Discordancia AV y VA"]
    )

st.subheader("Doppler cuantitativo")

col_d1, col_d2, col_d3 = st.columns(3)

with col_d1:
    vp_vel = st.text_input("Velocidad válvula pulmonar (m/s)", key="vp_vel")
    vp_grad = calcular_gradiente_bernoulli(vp_vel)
    vp_grad_texto = f"{vp_grad} mmHg" if vp_grad != "" else ""
    st.text_input("Gradiente pulmonar (mmHg)", value=vp_grad_texto, disabled=True, key="vp_grad_calc")

with col_d2:
    vao_vel = st.text_input("Velocidad válvula aórtica (m/s)", key="vao_vel")
    vao_grad = calcular_gradiente_bernoulli(vao_vel)
    vao_grad_texto = f"{vao_grad} mmHg" if vao_grad != "" else ""
    st.text_input("Gradiente aórtico (mmHg)", value=vao_grad_texto, disabled=True, key="vao_grad_calc")

with col_d3:
    aorta_vel = st.text_input("Velocidad aorta descendente (m/s)", key="aorta_vel")
    aorta_grad = calcular_gradiente_bernoulli(aorta_vel)
    aorta_grad_texto = f"{aorta_grad} mmHg" if aorta_grad != "" else ""
    st.text_input("Gradiente aorta (mmHg)", value=aorta_grad_texto, disabled=True, key="aorta_grad_calc")

st.divider()

# =========================================================
# DEFECTOS ESTRUCTURALES
# =========================================================
st.subheader("Defectos estructurales")

tab1, tab2, tab3 = st.tabs(["CIA", "CIV", "PCA"])

# ------------------ CIA ------------------
with tab1:
    sia = st.selectbox("Septum interauricular", ["íntegro", "con defecto"], key="sia")

    if sia == "con defecto":
        tipo_cia = st.selectbox(
            "Tipo CIA",
            ["Ostium Secundum", "Ostium Primum", "Seno venoso superior", "Seno venoso inferior"],
            key="tipo_cia"
        )
        diam_cia = st.text_input("Diámetro CIA (mm)", key="diam_cia")
        shunt_cia = st.selectbox(
            "Shunt CIA",
            ["izquierda a derecha", "bidireccional", "derecha a izquierda"],
            key="shunt_cia"
        )
        gradiente_cia = st.text_input("Gradiente CIA (mmHg)", key="grad_cia")

        if tipo_cia == "Ostium Secundum":
            st.markdown("**Bordes CIA ostium secundum (mm)**")
            borde_vci = st.text_input("Borde vena cava inferior", key="borde_vci")
            borde_vcs = st.text_input("Borde vena cava superior", key="borde_vcs")
            borde_vp = st.text_input("Borde venas pulmonares", key="borde_vp")
            borde_aortico = st.text_input("Borde aórtico", key="borde_aortico")
            borde_contraaortico = st.text_input("Borde contraaórtico", key="borde_contraaortico")
            borde_valvas_av = st.text_input("Borde válvulas AV", key="borde_valvas_av")
        else:
            borde_vci = ""
            borde_vcs = ""
            borde_vp = ""
            borde_aortico = ""
            borde_contraaortico = ""
            borde_valvas_av = ""
    else:
        tipo_cia = ""
        diam_cia = ""
        shunt_cia = ""
        gradiente_cia = ""
        borde_vci = ""
        borde_vcs = ""
        borde_vp = ""
        borde_aortico = ""
        borde_contraaortico = ""
        borde_valvas_av = ""

# ------------------ CIV ------------------
with tab2:
    siv = st.selectbox("Septum interventricular", ["íntegro", "con defecto"], key="siv")

    if siv == "con defecto":
        tipo_civ = st.selectbox(
            "Tipo CIV",
            ["perimembranosa", "muscular", "de entrada", "subpulmonar", "subaórtica"],
            key="tipo_civ"
        )
        diam_civ = st.text_input("Diámetro CIV (mm)", key="diam_civ")
        shunt_civ = st.selectbox(
            "Shunt CIV",
            ["izquierda a derecha", "bidireccional", "derecha a izquierda"],
            key="shunt_civ"
        )
        gradiente_civ = st.text_input("Gradiente CIV (mmHg)", key="grad_civ")

        if tipo_civ == "perimembranosa":
            aneurisma_civ = st.selectbox(
                "Aneurisma valva septal tricúspide",
                ["No", "Sí"],
                key="aneurisma_civ"
            )
        else:
            aneurisma_civ = ""
    else:
        tipo_civ = ""
        diam_civ = ""
        shunt_civ = ""
        gradiente_civ = ""
        aneurisma_civ = ""

# ------------------ PCA ------------------
with tab3:
    pca = st.selectbox("Conducto arterioso", ["No", "Sí"], key="pca")

    if pca == "Sí":
        pca_pulm = st.text_input("Diámetro extremo pulmonar (mm)", key="pca_pulm")
        pca_aortico = st.text_input("Diámetro extremo aórtico (mm)", key="pca_aortico")
        pca_longitud = st.text_input("Longitud del ductus (mm)", key="pca_longitud")
        pca_shunt = st.selectbox(
            "Shunt PCA",
            ["izquierda a derecha", "bidireccional", "derecha a izquierda"],
            key="pca_shunt"
        )
        pca_gradiente = st.text_input("Gradiente PCA (mmHg)", key="pca_grad")
    else:
        pca_pulm = ""
        pca_aortico = ""
        pca_longitud = ""
        pca_shunt = ""
        pca_gradiente = ""

st.divider()

# =========================================================
# MEDIDAS ESTRUCTURALES PHN
# =========================================================
st.subheader("Medidas estructurales cardíacas (PHN)")

tab_m1, tab_m2, tab_m3, tab_m4 = st.tabs([
    "Aorta y grandes vasos",
    "Pulmonares y válvulas",
    "Ventrículo izquierdo",
    "Coronarias"
])

with tab_m1:
    col_a1, col_a2 = st.columns(2)

    with col_a1:
        ANN = st.text_input("Diámetro del anillo aórtico (ANN) - mm", key="ANN")
        ROOT = st.text_input("Diámetro de la raíz aórtica (ROOT) - mm", key="ROOT")
        STJ = st.text_input("Diámetro de la unión sinotubular (STJ) - mm", key="STJ")
        AAO = st.text_input("Diámetro de aorta ascendente (AAO) - mm", key="AAO")

    with col_a2:
        ARCHPROX = st.text_input("Diámetro del arco aórtico proximal (ARCHPROX) - mm", key="ARCHPROX")
        ARCHDIST = st.text_input("Diámetro del arco aórtico distal (ARCHDIST) - mm", key="ARCHDIST")
        ISTH = st.text_input("Diámetro del istmo aórtico (ISTH) - mm", key="ISTH")

with tab_m2:
    col_p1, col_p2 = st.columns(2)

    with col_p1:
        MPA = st.text_input("Diámetro del tronco pulmonar (MPA) - mm", key="MPA")
        RPA = st.text_input("Diámetro de la arteria pulmonar derecha (RPA) - mm", key="RPA")
        LPA = st.text_input("Diámetro de la arteria pulmonar izquierda (LPA) - mm", key="LPA")
        MVAP = st.text_input("Diámetro anteroposterior mitral (MVAP) - mm", key="MVAP")
        MVLAT = st.text_input("Diámetro lateral mitral (MVLAT) - mm", key="MVLAT")

    with col_p2:
        TVAP = st.text_input("Diámetro anteroposterior tricuspídeo (TVAP) - mm", key="TVAP")
        TVLAT = st.text_input("Diámetro lateral tricuspídeo (TVLAT) - mm", key="TVLAT")
        PVLAX = st.text_input("Diámetro anular pulmonar eje largo (PVLAX) - mm", key="PVLAX")
        PVSAX = st.text_input("Diámetro anular pulmonar eje corto (PVSAX) - mm", key="PVSAX")

with tab_m3:
    col_vi1, col_vi2 = st.columns(2)

    with col_vi1:
        LVEDD = st.text_input("Diámetro telediastólico endocárdico del ventrículo izquierdo (LVEDD) - mm", key="LVEDD")
        agregar_medida("Diámetro telesistólico endocárdico del ventrículo izquierdo", "LVESD", LVESD)
        LVESD = st.text_input("Diámetro telesistólico endocárdico del ventrículo izquierdo (LVESD) - mm", key="LVESD")
        LVPWT = st.text_input("Espesor de la pared posterior del VI en diástole (LVPWT) - mm", key="LVPWT")

    with col_vi2:
        LVST = st.text_input("Espesor septal del VI en diástole (LVST) - mm", key="LVST")
        fevi_teicholz = calcular_fevi_teicholz(LVEDD, LVESD)
        fevi_teicholz_texto = f"{fevi_teicholz} %" if fevi_teicholz != "" else ""
        st.text_input("FEVI calculada por Teichholz (%)", value=fevi_teicholz_texto, disabled=True, key="fevi_teicholz")

with tab_m4:
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        LMCA = st.text_input("Diámetro de la coronaria izquierda principal (LMCA) - mm", key="LMCA")
        LAD = st.text_input("Diámetro de la descendente anterior proximal (LAD) - mm", key="LAD")

    with col_c2:
        RCA = st.text_input("Diámetro de la coronaria derecha proximal (RCA) - mm", key="RCA")

st.divider()

# =========================================================
# FUNCIONES TEXTO
# =========================================================
def texto_cia():
    if sia != "con defecto":
        return "Septum interauricular íntegro."

    texto = f"Comunicación interauricular tipo {tipo_cia}"

    if diam_cia:
        texto += f" de {diam_cia} mm de diámetro"

    if shunt_cia:
        texto += f", con cortocircuito de {shunt_cia}"

    if gradiente_cia:
        texto += f", con gradiente de {gradiente_cia} mmHg"

    texto += "."

    if tipo_cia == "Ostium Secundum":
        bordes = []

        if borde_vci:
            bordes.append(f"Borde de vena cava inferior: {borde_vci} mm")
        if borde_vcs:
            bordes.append(f"Borde de vena cava superior: {borde_vcs} mm")
        if borde_vp:
            bordes.append(f"Borde de venas pulmonares: {borde_vp} mm")
        if borde_aortico:
            bordes.append(f"Borde aórtico: {borde_aortico} mm")
        if borde_contraaortico:
            bordes.append(f"Borde contraaórtico: {borde_contraaortico} mm")
        if borde_valvas_av:
            bordes.append(f"Borde de válvulas AV: {borde_valvas_av} mm")

        if bordes:
            texto += " " + ". ".join(bordes) + "."

    return texto


def texto_civ():
    if siv != "con defecto":
        return "Septum interventricular íntegro."

    texto = f"Comunicación interventricular {tipo_civ}"

    if diam_civ:
        texto += f" de {diam_civ} mm"

    if shunt_civ:
        texto += f", con cortocircuito de {shunt_civ}"

    if gradiente_civ:
        texto += f", con gradiente de {gradiente_civ} mmHg"

    texto += "."

    if tipo_civ == "perimembranosa" and aneurisma_civ == "Sí":
        texto += " Se observa aneurisma formado por la valva septal de la tricúspide."

    return texto


def texto_pca():
    if pca != "Sí":
        return "Sin conducto arterioso."

    texto = "Ductus arterioso persistente"

    if pca_pulm:
        texto += f" de {pca_pulm} mm de diámetro en su extremo pulmonar"

    if pca_aortico:
        texto += f", {pca_aortico} mm en su extremo aórtico"

    if pca_longitud:
        texto += f" y {pca_longitud} mm de longitud"

    if pca_shunt:
        texto += f", con cortocircuito de {pca_shunt}"

    if pca_gradiente:
        texto += f", con gradiente de {pca_gradiente} mmHg"

    texto += "."

    return texto


# =========================================================
# HALLAZGOS
# =========================================================
if modo_normal:
    texto_vi = "13. Ventrículo izquierdo de paredes lisas y tamaño normal. Contractilidad global y segmentaria conservada. Tracto de salida del ventrículo izquierdo libre."
    
    if fevi_teicholz != "":
        texto_vi += f" FEVI por método de Teichholz: {fevi_teicholz} %."

    hallazgos = f"""1. Situs solitus auricular.
2. Levocardia – Levoapex.
3. Conexión de venas sistémicas normal a la aurícula derecha.
4. Conexión de venas pulmonares normal a la aurícula izquierda.
5. Aurícula izquierda de tamaño y función normal.
6. Aurícula derecha de tamaño y función normal.
7. Concordancia auriculoventricular y ventriculoarterial.
8. Septum interauricular íntegro.
9. Válvula tricúspide de morfología, implantación y función normal, con insuficiencia ligera.
10. Válvula mitral de morfología, implantación y función normal, sin estenosis ni insuficiencia.
11. Septum auriculoventricular indemne.
12. Septum interventricular íntegro.
{texto_vi}
14. Ventrículo derecho de tamaño normal, trabeculado, tripartito, con función conservada. Tracto de salida del ventrículo derecho libre.
15. Válvula aórtica trivalva, con apertura y cierre adecuados. Origen de arterias coronarias de ostium independientes, trayecto proximal normal.
16. Válvula pulmonar de características normales. Tronco y ramas pulmonares de adecuado calibre.
17. Sin evidencia de conducto arterioso persistente.
18. Arco aórtico izquierdo con vasos supraaórticos de origen y trayecto normal. No se evidencian signos de coartación. Flujo pulsátil en aorta abdominal sin corrida diastólica.
19. Sin derrame pericárdico. Sin vegetaciones. No se observan trombos intracavitarios."""
    
    if vp_vel:
        hallazgos += f"\n7. Válvula pulmonar: velocidad {vp_vel} m/s, gradiente máximo {vp_grad} mmHg."

    if vao_vel:
        hallazgos += f"\n8. Válvula aórtica: velocidad {vao_vel} m/s, gradiente máximo {vao_grad} mmHg."

    if aorta_vel:
        hallazgos += f"\n9. Aorta descendente: velocidad {aorta_vel} m/s, gradiente máximo {aorta_grad} mmHg."
else:
    hallazgos = f"""1. Situs {situs}
2. {cardia} - {apex}
3. {concordancia}
4. {texto_cia()}
5. {texto_civ()}
6. {texto_pca()}"""

# =========================================================
# CONCLUSIONES
# =========================================================
conclusiones = []

if sia == "con defecto":
    conclusiones.append(texto_cia())

if siv == "con defecto":
    conclusiones.append(texto_civ())

if pca == "Sí":
    conclusiones.append(texto_pca())

if not conclusiones:
    conclusiones.append("Corazón sin lesiones anatómicas o estructurales")

if psap_normal:
    conclusiones.append(f"PSAP {psap_normal} mmHg")

hap = clasificar_hap(psap_normal)
if hap:
    conclusiones.append(hap)

if fevi:
    conclusiones.append(f"Función sistólica y diastólica biventricular conservada. FEVI {fevi} %")

conclusiones_txt = "\n".join([f"{i+1}. {c}" for i, c in enumerate(conclusiones)])

# =========================================================
# TABLA DE MEDIDAS PHN
# =========================================================
z_scores = {
    "ANN": calcular_zscore_phn("ANN", ANN, superficie_corporal),
    "ROOT": calcular_zscore_phn("ROOT", ROOT, superficie_corporal),
    "STJ": calcular_zscore_phn("STJ", STJ, superficie_corporal),
    "AAO": calcular_zscore_phn("AAO", AAO, superficie_corporal),
    "ARCHPROX": calcular_zscore_phn("ARCHPROX", ARCHPROX, superficie_corporal),
    "ARCHDIST": calcular_zscore_phn("ARCHDIST", ARCHDIST, superficie_corporal),
    "ISTH": calcular_zscore_phn("ISTH", ISTH, superficie_corporal),
    "MPA": calcular_zscore_phn("MPA", MPA, superficie_corporal),
    "RPA": calcular_zscore_phn("RPA", RPA, superficie_corporal),
    "LPA": calcular_zscore_phn("LPA", LPA, superficie_corporal),
    "MVAP": calcular_zscore_phn("MVAP", MVAP, superficie_corporal),
    "MVLAT": calcular_zscore_phn("MVLAT", MVLAT, superficie_corporal),
    "TVAP": calcular_zscore_phn("TVAP", TVAP, superficie_corporal),
    "TVLAT": calcular_zscore_phn("TVLAT", TVLAT, superficie_corporal),
    "PVLAX": calcular_zscore_phn("PVLAX", PVLAX, superficie_corporal),
    "PVSAX": calcular_zscore_phn("PVSAX", PVSAX, superficie_corporal),
    "LVEDD": calcular_zscore_phn("LVEDD", LVEDD, superficie_corporal),
    "LVPWT": calcular_zscore_phn("LVPWT", LVPWT, superficie_corporal),
    "LVST": calcular_zscore_phn("LVST", LVST, superficie_corporal),
    "LMCA": calcular_zscore_phn("LMCA", LMCA, superficie_corporal),
    "LAD": calcular_zscore_phn("LAD", LAD, superficie_corporal),
    "RCA": calcular_zscore_phn("RCA", RCA, superficie_corporal),
}

medidas_phn = []

def agregar_medida(nombre, abrev, valor):
    if valor != "":
        medidas_phn.append({
            "estructura": f"{nombre} ({abrev})",
            "mm": valor,
            "zscore": z_scores.get(abrev, "")
        })

agregar_medida("Diámetro del anillo aórtico", "ANN", ANN)
agregar_medida("Diámetro de la raíz aórtica", "ROOT", ROOT)
agregar_medida("Diámetro de la unión sinotubular", "STJ", STJ)
agregar_medida("Diámetro de aorta ascendente", "AAO", AAO)
agregar_medida("Diámetro del arco aórtico proximal", "ARCHPROX", ARCHPROX)
agregar_medida("Diámetro del arco aórtico distal", "ARCHDIST", ARCHDIST)
agregar_medida("Diámetro del istmo aórtico", "ISTH", ISTH)

agregar_medida("Diámetro del tronco pulmonar", "MPA", MPA)
agregar_medida("Diámetro de la arteria pulmonar derecha", "RPA", RPA)
agregar_medida("Diámetro de la arteria pulmonar izquierda", "LPA", LPA)

agregar_medida("Diámetro anteroposterior mitral", "MVAP", MVAP)
agregar_medida("Diámetro lateral mitral", "MVLAT", MVLAT)
agregar_medida("Diámetro anteroposterior tricuspídeo", "TVAP", TVAP)
agregar_medida("Diámetro lateral tricuspídeo", "TVLAT", TVLAT)

agregar_medida("Diámetro anular pulmonar eje largo", "PVLAX", PVLAX)
agregar_medida("Diámetro anular pulmonar eje corto", "PVSAX", PVSAX)

agregar_medida("Diámetro telediastólico endocárdico del VI", "LVEDD", LVEDD)
agregar_medida("Diámetro telesistólico endocárdico del VI", "LVESD", LVESD)
agregar_medida("Espesor de la pared posterior del VI en diástole", "LVPWT", LVPWT)
agregar_medida("Espesor septal del VI en diástole", "LVST", LVST)

agregar_medida("Diámetro de la coronaria izquierda principal", "LMCA", LMCA)
agregar_medida("Diámetro de la descendente anterior proximal", "LAD", LAD)
agregar_medida("Diámetro de la coronaria derecha proximal", "RCA", RCA)

medidas_txt = ""
if medidas_phn:
    medidas_txt = "MEDIDAS ESTRUCTURALES PHN:\n"
    for fila in medidas_phn:
        ztxt = f" | Z-score: {fila['zscore']}" if fila["zscore"] != "" else ""
        medidas_txt += f"- {fila['estructura']}: {fila['mm']} mm{ztxt}\n"
        
# =========================================================
# REPORTE
# =========================================================
reporte = f"""
REPORTE ECO

Paciente: {nombre}
Edad: {edad_numero} {edad_unidad}
Peso: {peso} kg
Talla: {talla} cm
SC: {sc_texto}
Institución: {institucion}
Tipo de documento: {tipo_documento}
Documento: {numero_documento}
EPS: {eps}
Fecha: {fecha}

Ventana acústica: {ventana_acustica}

HALLAZGOS:
{hallazgos}

{medidas_txt}DOPPLER CUANTITATIVO:
Válvula pulmonar: velocidad {vp_vel} m/s, gradiente máximo {vp_grad} mmHg.
Válvula aórtica: velocidad {vao_vel} m/s, gradiente máximo {vao_grad} mmHg.
Aorta descendente: velocidad {aorta_vel} m/s, gradiente máximo {aorta_grad} mmHg.

CONCLUSIONES:
{conclusiones_txt}
"""

archivo = crear_word(reporte)

st.text_area("Reporte", reporte, height=500)

st.download_button("Descargar Word", archivo, "reporte.docx")
