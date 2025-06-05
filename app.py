import streamlit as st
import os
import requests
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="📑 Consulta de Certidões", layout="wide")

st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .certidao-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }
    .certidao-title {
        font-size: 18px;
        font-weight: bold;
    }
    .pdf-link {
        color: #4A90E2;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("📄 Emissor Inteligente de Certidões Negativas")
st.caption("Sistema automatizado via Infosimples API")

col1, col2 = st.columns([1, 2])
with col1:
    cnpj = st.text_input("Digite o CNPJ da empresa:", value="15347020000100", max_chars=14)

with col2:
    token = os.getenv("infosimples_token")
    if not token:
        token = st.text_input("Token Infosimples:", type="password")

st.markdown("---")

servicos = {
    "Receita Federal (PGFN)": "receita-federal/pgfn",
    "SEFAZ Amapá": "sefaz/ap/certidao-debitos",
    "FGTS / Caixa": "caixa/regularidade",
    "CNDT / Justiça do Trabalho": "tribunal/tst/cndt"
}

base_url = "https://api.infosimples.com/api/v2/consultas"

@st.cache_data(show_spinner=False)
def consultar(certidao, rota, parametros):
    try:
        response = requests.get(f"{base_url}/{rota}", params=parametros)
        if 'application/json' in response.headers.get("Content-Type", ""):
            data = response.json().get("data", [{}])[0]
            return extrair_link_pdf(data)
        return None
    except Exception as e:
        return None

def extrair_link_pdf(data_item):
    if isinstance(data_item, str) and data_item.startswith("http"):
        return data_item
    if isinstance(data_item, dict):
        for v in data_item.values():
            if isinstance(v, str) and v.startswith("http"):
                return v
            elif isinstance(v, dict):
                res = extrair_link_pdf(v)
                if res:
                    return res
    return None

if st.button("🚀 Emitir Certidões Automáticas"):
    if not token or not cnpj:
        st.warning("Informe o CNPJ e o token para continuar.")
    else:
        parametros = {
            "cnpj": cnpj,
            "token": token,
            "timeout": 600,
            "ignore_site_receipt": 0,
            "preferencia_emissao": "2via"
        }

        st.markdown("### 📋 Resultados das Consultas")
        for nome, rota in servicos.items():
            with st.container():
                st.markdown("<div class='certidao-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='certidao-title'>{nome}</div>", unsafe_allow_html=True)
                pdf_link = consultar(nome, rota, parametros)
                if pdf_link:
                    st.markdown(f"<a class='pdf-link' href='{pdf_link}' target='_blank'>📄 Clique aqui para baixar</a>", unsafe_allow_html=True)
                else:
                    st.warning("PDF não disponível ou certidão negativa não emitida.")
                st.markdown("</div>", unsafe_allow_html=True)