import streamlit as st
from datetime import date
from docx import Document
from io import BytesIO

st.set_page_config(page_title="Eco Pediátrico", layout="wide")

st.title("🫀 Generador de Ecocardiograma Pediátrico")

# =========================================================
# FUNCIÓN SUPERFICIE CORPORAL
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
    tipo_documento = st.selectbox(
        "Tipo documento",
        ["CC", "TI", "RC", "CE"]
    )
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
    concordancia = st.selectbox("Concordancia", ["Normal", "Alterada"])

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

# =========================================================
# DEFECTOS
# =========================================================
st.subheader("Defectos estructurales")

tab1, tab2, tab3 = st.tabs(["CIA", "CIV", "PCA"])

with tab1:
    sia = st.selectbox("Septum interauricular", ["íntegro", "con defecto"])
    if sia == "con defecto":
        tipo_cia = st.selectbox("Tipo CIA", ["Ostium Secundum", "Ostium Primum"], key="tipo_cia")
        diam_cia = st.text_input("Diámetro CIA (mm)", key="diam_cia")
        gradiente_cia = st.text_input("Gradiente CIA (mmHg)", key="grad_cia")
    else:
        tipo_cia = diam_cia = gradiente_cia = ""

with tab2:
    siv = st.selectbox("Septum interventricular", ["íntegro", "con defecto"])
    if siv == "con defecto":
        tipo_civ = st.selectbox("Tipo CIV", ["perimembranosa", "muscular"], key="tipo_civ")
        diam_civ = st.text_input("Diámetro CIV (mm)", key="diam_civ")
        gradiente_civ = st.text_input("Gradiente CIV (mmHg)", key="grad_civ")
    else:
        tipo_civ = diam_civ = gradiente_civ = ""

with tab3:
    pca = st.selectbox("PCA", ["No", "Sí"])
    if pca == "Sí":
        pca_diam = st.text_input("Diámetro PCA (mm)", key="diam_pca")
    else:
        pca_diam = ""

# =========================================================
# TEXTO
# =========================================================
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
def texto_cia():
    if sia != "con defecto":
        return "Septum interauricular íntegro."
    return f"CIA {tipo_cia} de {diam_cia} mm, gradiente {gradiente_cia} mmHg."

def texto_civ():
    if siv != "con defecto":
        return "Septum interventricular íntegro."
    return f"CIV {tipo_civ} de {diam_civ} mm, gradiente {gradiente_civ} mmHg."

def texto_pca():
    if pca != "Sí":
        return "Sin PCA."
    return f"PCA de {pca_diam} mm."

def crear_word(reporte):
    doc = Document()

    # ======================
    # TÍTULO
    # ======================
    titulo = doc.add_paragraph()
    run = titulo.add_run("REPORTE DE ECOCARDIOGRAMA PEDIÁTRICO")
    run.bold = True
    titulo.alignment = 1  # centrado

    doc.add_paragraph("")  # espacio

    # ======================
    # FILIACIÓN
    # ======================
    doc.add_paragraph("DATOS DEL PACIENTE", style='Heading 2')

    doc.add_paragraph(f"Nombre: {nombre}")
    doc.add_paragraph(f"Edad: {edad_numero} {edad_unidad}")
    doc.add_paragraph(f"Peso: {peso} kg")
    doc.add_paragraph(f"Talla: {talla} cm")
    doc.add_paragraph(f"Superficie corporal: {sc_texto}")
    doc.add_paragraph(f"Institución: {institucion}")
    doc.add_paragraph(f"Documento: {numero_documento}")
    doc.add_paragraph(f"Fecha: {fecha}")

    doc.add_paragraph("")

    # ======================
    # HALLAZGOS
    # ======================
    doc.add_paragraph("HALLAZGOS", style='Heading 2')

    for linea in hallazgos.split("\n"):
        if linea.strip():
            doc.add_paragraph(linea)

    doc.add_paragraph("")

    # ======================
    # DOPPLER
    # ======================
    doc.add_paragraph("DOPPLER CUANTITATIVO", style='Heading 2')

    doc.add_paragraph(f"Válvula pulmonar: velocidad {vp_vel} m/s, gradiente máximo {vp_grad} mmHg")
    doc.add_paragraph(f"Válvula aórtica: velocidad {vao_vel} m/s, gradiente máximo {vao_grad} mmHg")

    doc.add_paragraph("")

    # ======================
    # CONCLUSIONES
    # ======================
    doc.add_paragraph("CONCLUSIONES", style='Heading 2')

    for linea in conclusiones_txt.split("\n"):
        if linea.strip():
            doc.add_paragraph(linea)

    doc.add_paragraph("")
    doc.add_paragraph("__________________________________")
    doc.add_paragraph("Dr. Guillermo Aristizabal Villa")
    doc.add_paragraph("Cardiólogo Pediatra - Hemodinamista")

    # Guardar
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# =========================================================
# HALLAZGOS
# =========================================================
if modo_normal:
    hallazgos = f"""1. Situs solitus auricular.
2. Levocardia - Levoapex.
3. Concordancia AV y VA.
4. Septum interauricular íntegro.
5. Septum interventricular íntegro.
6. Sin conducto arterioso."""
    
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

HALLAZGOS:
{hallazgos}

DOPPLER CUANTITATIVO:
Válvula pulmonar: velocidad {vp_vel} m/s, gradiente máximo {vp_grad} mmHg.
Válvula aórtica: velocidad {vao_vel} m/s, gradiente máximo {vao_grad} mmHg.
Aorta descendente: velocidad {aorta_vel} m/s, gradiente máximo {aorta_grad} mmHg.

CONCLUSIONES:
{conclusiones_txt}
"""

archivo = crear_word(reporte)

st.text_area("Reporte", reporte, height=400)

st.download_button("Descargar Word", archivo, "reporte.docx")
