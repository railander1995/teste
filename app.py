import streamlit as st
import os
import requests

def testar_endpoint(nome, url, cnpj, token):
    params = {
        "cnpj": cnpj,
        "token": token,
        "timeout": 300,
        "resposta_tipo": "arquivo"
    }
    try:
        response = requests.get(url, params=params)
        st.subheader(f"🔎 {nome}")
        st.write("Status Code:", response.status_code)
        st.write("Content-Type:", response.headers.get("Content-Type", "N/A"))
        if 'application/pdf' in response.headers.get("Content-Type", ""):
            st.success("✅ Certidão gerada com sucesso (PDF detectado).")
        else:
            st.error("❌ Não é um PDF. Resposta:")
            st.code(response.text[:500])
    except Exception as e:
        st.error(f"Erro ao consultar {nome}: {e}")

st.set_page_config(page_title="Diagnóstico Infosimples", layout="centered")
st.title("🧪 Diagnóstico das Certidões - Infosimples")

cnpj = st.text_input("Digite o CNPJ (somente números):", value="33000167000101", max_chars=14)
token = os.getenv("infosimples_token")

if st.button("Testar Endpoints"):
    if not token:
        st.error("❌ Token não encontrado no secrets. Configure em Settings > Secrets.")
    elif not cnpj or len(cnpj) != 14:
        st.warning("⚠️ Digite um CNPJ válido com 14 dígitos.")
    else:
        st.info("🔄 Testando comunicação com as APIs da Infosimples...")
        testar_endpoint("Receita Federal (PGFN)",
                        "https://api.infosimples.com/api/v2/receita-federal/pgfn/",
                        cnpj, token)
        testar_endpoint("SEFAZ Amapá",
                        "https://api.infosimples.com/api/v2/sefaz/ap/certidao-debitos/",
                        cnpj, token)
        testar_endpoint("FGTS / Caixa",
                        "https://api.infosimples.com/api/v2/caixa/regularidade/",
                        cnpj, token)
        testar_endpoint("CNDT / Justiça do Trabalho",
                        "https://api.infosimples.com/api/v2/tribunal/tst/cndt/",
                        cnpj, token)