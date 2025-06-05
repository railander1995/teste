import streamlit as st
import os
import requests
import tempfile
from PyPDF2 import PdfMerger

st.set_page_config(page_title="📑 Emissor de Certidões", layout="wide")

st.markdown("""
<style>
body {
    background-color: #f0f8ff;
    color: #003366;
}
.certidao-card {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
}
.certidao-title {
    font-size: 18px;
    font-weight: bold;
    color: #003366;
}
.download-link {
    color: #0056b3;
    font-weight: 600;
    margin-top: 10px;
}
.unify-button {
    background-color: #0056b3;
    color: white;
    font-weight: bold;
    border-radius: 6px;
    padding: 10px;
    margin-top: 20px;
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

base_url = "https://api.infosimples.com/api/v2/consultas"

servicos = {
    "Receita Federal (PGFN)": "receita-federal/pgfn",
    "SEFAZ Amapá": "sefaz/ap/certidao-debitos",
    "FGTS / Caixa": "caixa/regularidade",
    "CNDT / Justiça do Trabalho": "tribunal/tst/cndt"
}

def extrair_link_pdf(data_item):
    if isinstance(data_item, str) and data_item.startswith("http") and data_item.endswith(".pdf"):
        return data_item
    if isinstance(data_item, dict):
        for val in data_item.values():
            link = extrair_link_pdf(val)
            if link:
                return link
    return None

def consultar_servico(nome, rota, parametros, arquivos_pdf):
    st.markdown(f"<div class='certidao-card'><div class='certidao-title'>{nome}</div>", unsafe_allow_html=True)
    try:
        r = requests.get(f"{base_url}/{rota}", params=parametros)
        if "application/json" in r.headers.get("Content-Type", ""):
            dados = r.json().get("data", [{}])[0]
            link = extrair_link_pdf(dados)
            if link:
                st.markdown(f"<a class='download-link' href='{link}' target='_blank'>📄 Clique aqui para baixar</a>", unsafe_allow_html=True)
                r_pdf = requests.get(link)
                if r_pdf.status_code == 200:
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    temp_file.write(r_pdf.content)
                    temp_file.close()
                    arquivos_pdf.append(temp_file.name)
            else:
                st.warning("⚠️ PDF não encontrado.")
        else:
            st.error("❌ Resposta inválida.")
    except Exception as e:
        st.error(f"Erro: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

def consultar_cnpj_e_incluir(parametros, arquivos_pdf):
    st.markdown("<div class='certidao-card'><div class='certidao-title'>📑 Cadastro Nacional da Pessoa Jurídica (PDF)</div>", unsafe_allow_html=True)
    try:
        url = f"{base_url}/receita-federal/cnpj"
        r = requests.get(url, params=parametros)
        if "application/json" in r.headers.get("Content-Type", ""):
            dados = r.json().get("data", [{}])[0]
            for k, v in dados.items():
                st.write(f"**{k.replace('_', ' ').title()}**: {v}")
            link = extrair_link_pdf(dados)
            if link:
                st.markdown(f"<a class='download-link' href='{link}' target='_blank'>📄 Clique aqui para baixar PDF do CNPJ</a>", unsafe_allow_html=True)
                r_pdf = requests.get(link)
                if r_pdf.status_code == 200:
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    temp_file.write(r_pdf.content)
                    temp_file.close()
                    arquivos_pdf.append(temp_file.name)
        else:
            st.warning("⚠️ Não foi possível consultar dados do CNPJ.")
    except Exception as e:
        st.error(f"Erro CNPJ: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

def unificar_pdfs(lista, nome_saida="certidoes_unificadas.pdf"):
    if not lista:
        return None
    merger = PdfMerger()
    for arquivo in lista:
        merger.append(arquivo)
    caminho_final = os.path.join(tempfile.gettempdir(), nome_saida)
    merger.write(caminho_final)
    merger.close()
    return caminho_final

arquivos = []

if st.button("🚀 Emitir Certidões Automáticas"):
    if not cnpj or not token:
        st.warning("Informe CNPJ e token.")
    else:
        parametros = {
            "cnpj": cnpj,
            "token": token,
            "timeout": 600,
            "ignore_site_receipt": 0,
            "preferencia_emissao": "2via"
        }

        st.markdown("### 📋 Resultados das Certidões")
        for nome, rota in servicos.items():
            consultar_servico(nome, rota, parametros, arquivos)

        consultar_cnpj_e_incluir(parametros, arquivos)

if arquivos:
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    if st.button("📥 Unificar Todas as Certidões em PDF", key="unify"):
        pdf_final = unificar_pdfs(arquivos)
        with open(pdf_final, "rb") as f:
            st.download_button("📎 Baixar Certidões Unificadas", f, file_name="certidoes_unificadas.pdf")
    st.markdown("</div>", unsafe_allow_html=True)
