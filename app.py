import streamlit as st
import os
import requests

def consultar_certidao(nome, url, params):
    try:
        response = requests.get(url, params=params)
        st.subheader(f"🔎 {nome}")
        st.write("Status Code:", response.status_code)
        st.write("Content-Type:", response.headers.get("Content-Type", "N/A"))
        if 'application/pdf' in response.headers.get("Content-Type", ""):
            st.success("✅ Certidão gerada com sucesso.")
            return response.content
        else:
            st.error("❌ Não é um PDF. Resposta:")
            st.code(response.text[:600])
            return None
    except Exception as e:
        st.error(f"Erro ao consultar {nome}: {e}")
        return None

st.set_page_config(page_title="CNDs Corrigidas", layout="centered")
st.title("📄 Consulta de Certidões Infosimples (EndPoints Corrigidos)")

cnpj = st.text_input("Digite o CNPJ:", value="15347020000100", max_chars=14)
token = os.getenv("infosimples_token")

if st.button("Emitir Certidões Corrigidas"):
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

        consultar_certidao("Receita Federal (PGFN)", f"{base}/receita-federal/pgfn", parametros)
        consultar_certidao("SEFAZ Amapá", f"{base}/sefaz/ap/certidao-debitos", parametros)
        consultar_certidao("FGTS / Caixa", f"{base}/caixa/regularidade", parametros)
        consultar_certidao("CNDT / Justiça do Trabalho", f"{base}/tribunal/tst/cndt", parametros)