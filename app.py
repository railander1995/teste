import streamlit as st
import os
import requests
from PyPDF2 import PdfMerger
import tempfile

def extrair_link_pdf(data_item):
    if isinstance(data_item, str) and data_item.startswith("http"):
        return data_item
    if isinstance(data_item, dict):
        for chave in data_item:
            valor = data_item[chave]
            if isinstance(valor, str) and valor.startswith("http"):
                return valor
            elif isinstance(valor, dict):
                resultado = extrair_link_pdf(valor)
                if resultado:
                    return resultado
    return None

def consultar_certidao(nome, url, params, arquivos_pdf):
    try:
        response = requests.get(url, params=params)
        st.subheader(f"🔎 {nome}")
        st.write("Status Code:", response.status_code)
        st.write("Content-Type:", response.headers.get("Content-Type", "N/A"))

        if 'application/json' in response.headers.get("Content-Type", ""):
            dados = response.json()
            st.success("✅ Consulta realizada com sucesso.")
            if "data" in dados and isinstance(dados["data"], list) and len(dados["data"]) > 0:
                link_pdf = extrair_link_pdf(dados["data"][0])
                if link_pdf:
                    st.markdown(f"[📄 Clique aqui para baixar a certidão individual]({link_pdf})")
                    try:
                        r = requests.get(link_pdf)
                        if r.status_code == 200:
                            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                            temp_file.write(r.content)
                            temp_file.close()
                            arquivos_pdf.append(temp_file.name)
                        else:
                            st.warning(f"⚠️ Não foi possível baixar o PDF de {nome}.")
                    except Exception as e:
                        st.warning(f"⚠️ Erro ao baixar PDF: {e}")
                else:
                    st.warning("⚠️ PDF ainda não disponível ou não localizado.")
            else:
                st.warning("⚠️ Nenhum dado encontrado na resposta.")
        else:
            st.error("❌ Resposta inesperada. Conteúdo não é JSON.")
            st.code(response.text[:600])
    except Exception as e:
        st.error(f"Erro ao consultar {nome}: {e}")

def unificar_pdfs(caminhos):
    if not caminhos:
        return None
    merger = PdfMerger()
    for caminho in caminhos:
        merger.append(caminho)
    final_path = os.path.join(tempfile.gettempdir(), "certidoes_unificadas.pdf")
    merger.write(final_path)
    merger.close()
    return final_path

st.set_page_config(page_title="Certidões Unificadas", layout="centered")
st.title("📑 Sistema Infosimples - Certidões em PDF Unificadas")

cnpj = st.text_input("Digite o CNPJ:", value="15347020000100", max_chars=14)
token = os.getenv("infosimples_token")

if st.button("Emitir e Unificar Certidões"):
    if not token:
        st.error("⚠️ Token não encontrado. Configure nos Secrets.")
    elif not cnpj or len(cnpj) != 14:
        st.warning("⚠️ Digite um CNPJ válido com 14 dígitos.")
    else:
        base = "https://api.infosimples.com/api/v2/consultas"
        parametros = {
            "cnpj": cnpj,
            "cpf": "",
            "token": token,
            "timeout": 600,
            "ignore_site_receipt": 0,
            "preferencia_emissao": "2via"
        }

        arquivos = []
        consultar_certidao("Receita Federal (PGFN)", f"{base}/receita-federal/pgfn", parametros, arquivos)
        consultar_certidao("SEFAZ Amapá", f"{base}/sefaz/ap/certidao-debitos", parametros, arquivos)
        consultar_certidao("FGTS / Caixa", f"{base}/caixa/regularidade", parametros, arquivos)
        consultar_certidao("CNDT / Justiça do Trabalho", f"{base}/tribunal/tst/cndt", parametros, arquivos)

        if arquivos:
            unificado = unificar_pdfs(arquivos)
            if unificado:
                with open(unificado, "rb") as f:
                    st.download_button("📥 Baixar Certidões Unificadas", f, file_name="certidoes_unificadas.pdf")
            else:
                st.warning("⚠️ Nenhum PDF foi unificado.")
        else:
            st.warning("⚠️ Nenhum PDF disponível para unificação.")