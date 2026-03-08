import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

st.set_page_config(
    page_title="Demo de Verificação de Assinaturas",
    page_icon="✍️",
    layout="wide",
)

# =========================
# Estilo
# =========================
st.markdown("""
<style>
    .main {
        background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .hero-box {
        background: rgba(255,255,255,0.80);
        border: 1px solid rgba(255,255,255,0.5);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 24px 28px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        margin-bottom: 1.2rem;
    }

    .kpi-card {
        background: white;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.07);
        border: 1px solid #e5e7eb;
        text-align: center;
        min-height: 120px;
    }

    .section-card {
        background: white;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.07);
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }

    .result-ok {
        background: linear-gradient(135deg, #dcfce7, #bbf7d0);
        border: 1px solid #86efac;
        color: #14532d;
        padding: 16px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 18px;
        text-align: center;
    }

    .result-bad {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        border: 1px solid #fca5a5;
        color: #7f1d1d;
        padding: 16px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 18px;
        text-align: center;
    }

    .small-muted {
        color: #6b7280;
        font-size: 0.95rem;
    }

    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3rem;
        font-weight: 600;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# =========================
# Funções auxiliares
# =========================
def decodificar_imagem_base64(b64_string: str):
    image_bytes = base64.b64decode(b64_string)
    return Image.open(BytesIO(image_bytes))


def pil_para_bytes_download(img: Image.Image):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


def chamar_predict(api_url, arquivo1, arquivo2):
    files = {
        "signature1": (arquivo1.name, arquivo1.getvalue(), arquivo1.type or "image/png"),
        "signature2": (arquivo2.name, arquivo2.getvalue(), arquivo2.type or "image/png"),
    }
    response = requests.post(f"{api_url}/predict", files=files, timeout=120)
    response.raise_for_status()
    return response.json()


def chamar_compare(api_url, arquivo1, arquivo2):
    files = {
        "signature1": (arquivo1.name, arquivo1.getvalue(), arquivo1.type or "image/png"),
        "signature2": (arquivo2.name, arquivo2.getvalue(), arquivo2.type or "image/png"),
    }
    response = requests.post(f"{api_url}/compare", files=files, timeout=180)
    response.raise_for_status()
    return response.json()


# =========================
# Barra lateral
# =========================
with st.sidebar:
    st.title("Configurações")
    api_url = st.text_input("URL da API Backend", value="http://194.163.172.45")
    threshold = st.slider("Limiar de decisão", min_value=0.0, max_value=2.0, value=0.50, step=0.01)

    st.markdown("---")
    st.markdown("### Observações da demo")
    st.write("Use este limiar para automatizar a regra de decisão mostrada na demonstração.")
    st.caption("Exemplo: distância ≤ 0.50 → provável correspondência")

    st.markdown("---")
    st.markdown("### Endpoints esperados")
    st.code("/predict\n/compare")


# =========================
# Cabeçalho
# =========================
st.markdown("""
<div class="hero-box">
    <h1 style="margin-bottom:0.3rem;">✍️ Plataforma de Verificação de Assinaturas</h1>
    <p class="small-muted" style="margin-bottom:0;">
        Demo comercial para comparação de assinaturas utilizando embeddings de deep learning e análise visual.
    </p>
</div>
""", unsafe_allow_html=True)


# =========================
# Upload
# =========================
coluna_esquerda, coluna_direita = st.columns(2)

with coluna_esquerda:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Assinatura de Referência")
    arquivo1 = st.file_uploader(
        "Envie a primeira assinatura",
        type=["png", "jpg", "jpeg"],
        key="sig1"
    )
    if arquivo1:
        img1 = Image.open(arquivo1).convert("RGB")
        st.image(img1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with coluna_direita:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Assinatura de Consulta")
    arquivo2 = st.file_uploader(
        "Envie a segunda assinatura",
        type=["png", "jpg", "jpeg"],
        key="sig2"
    )
    if arquivo2:
        img2 = Image.open(arquivo2).convert("RGB")
        st.image(img2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# Ação principal
# =========================
analisar = st.button("Executar Análise de Assinatura")

if analisar:
    if not arquivo1 or not arquivo2:
        st.warning("Por favor, envie as duas imagens de assinatura antes de executar a análise.")
    else:
        try:
            with st.spinner("Calculando a distância entre embeddings e gerando as visualizações de comparação..."):
                predict_json = chamar_predict(api_url, arquivo1, arquivo2)
                compare_json = chamar_compare(api_url, arquivo1, arquivo2)

            distancia = float(predict_json["distance"])
            eh_correspondencia = distancia <= threshold

            # KPIs
            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown(
                    f"""
                    <div class="kpi-card">
                        <div style="font-size:14px;color:#6b7280;">Distância entre Embeddings</div>
                        <div style="font-size:34px;font-weight:700;margin-top:8px;">{distancia:.4f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with c2:
                st.markdown(
                    f"""
                    <div class="kpi-card">
                        <div style="font-size:14px;color:#6b7280;">Limiar</div>
                        <div style="font-size:34px;font-weight:700;margin-top:8px;">{threshold:.2f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with c3:
                veredito = "Provável Correspondência" if eh_correspondencia else "Provável Diferença"
                st.markdown(
                    f"""
                    <div class="kpi-card">
                        <div style="font-size:14px;color:#6b7280;">Decisão Automatizada</div>
                        <div style="font-size:28px;font-weight:700;margin-top:12px;">{veredito}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.write("")

            if eh_correspondencia:
                st.markdown(
                    f'<div class="result-ok">✅ Decisão: provável assinatura genuína (distância ≤ {threshold:.2f})</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="result-bad">⚠️ Decisão: provável divergência / risco de falsificação (distância > {threshold:.2f})</div>',
                    unsafe_allow_html=True
                )

            st.write("")

            # Decodificar imagens
            imagem_jaccard = decodificar_imagem_base64(compare_json["jaccard_image"])
            imagem_pressao = decodificar_imagem_base64(compare_json["pressure_comparison"])
            imagem_vetor = decodificar_imagem_base64(compare_json["vector_comparison"])

            st.markdown("## Resultados Visuais da Comparação")

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.subheader("Sobreposição de Jaccard")
                st.image(imagem_jaccard, use_container_width=True)
                st.download_button(
                    label="Baixar Imagem de Jaccard",
                    data=pil_para_bytes_download(imagem_jaccard),
                    file_name="comparacao_jaccard.png",
                    mime="image/png",
                    key="download_jaccard"
                )
                st.markdown('</div>', unsafe_allow_html=True)

            with col_b:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.subheader("Comparação de Pressão")
                st.image(imagem_pressao, use_container_width=True)
                st.download_button(
                    label="Baixar Imagem de Pressão",
                    data=pil_para_bytes_download(imagem_pressao),
                    file_name="comparacao_pressao.png",
                    mime="image/png",
                    key="download_pressure"
                )
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Comparação de Fluxo Vetorial")
            st.image(imagem_vetor, use_container_width=True)
            st.download_button(
                label="Baixar Imagem Vetorial",
                data=pil_para_bytes_download(imagem_vetor),
                file_name="comparacao_vetorial.png",
                mime="image/png",
                key="download_vector"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        except requests.exceptions.ConnectionError:
            st.error("Não foi possível conectar à API backend. Verifique se o servidor Flask está em execução e se a URL está correta.")
        except requests.exceptions.HTTPError as e:
            try:
                erro_json = e.response.json()
                st.error(f"Erro da API: {erro_json}")
            except Exception:
                st.error(f"Erro HTTP: {e}")
        except Exception as e:
            st.error(f"Erro inesperado: {str(e)}")


# =========================
# Rodapé
# =========================
st.markdown("---")
st.caption("Interface demonstrativa para verificação de assinaturas e outputs explicáveis de comparação.")