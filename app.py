import streamlit as st
import os
import requests

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

def consultar_certidao(nome, url, params):
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
                    st.markdown(f"[📄 Clique aqui para baixar a certidão]({link_pdf})")
                else:
                    st.warning("⚠️ PDF ainda não disponível ou não localizado.")
            else:
                st.warning("⚠️ Nenhum dado encontrado na resposta.")
        else:
            st.error("❌ Resposta inesperada. Conteúdo não é JSON.")
            st.code(response.text[:600])
    except Exception as e:
        st.error(f"Erro ao consultar {nome}: {e}")

st.set_page_config(page_title="Certidões PDF - Versão Final", layout="centered")
st.title("📑 Sistema Infosimples com Download Automático de Certidões")

cnpj = st.text_input("Digite o CNPJ:", value="15347020000100", max_chars=14)
token = os.getenv("infosimples_token")

if st.button("Emitir Certidões com PDF"):
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