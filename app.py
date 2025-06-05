import streamlit as st
import os
import requests

def consultar_certidao(nome, url, params, chave_pdf=None):
    try:
        response = requests.get(url, params=params)
        st.subheader(f"🔎 {nome}")
        st.write("Status Code:", response.status_code)
        st.write("Content-Type:", response.headers.get("Content-Type", "N/A"))

        if 'application/json' in response.headers.get("Content-Type", ""):
            dados = response.json()
            st.success("✅ Consulta realizada com sucesso.")
            if chave_pdf:
                try:
                    pdf_url = dados["data"][0]
                    for key in chave_pdf.split("."):
                        pdf_url = pdf_url.get(key, {})
                    if isinstance(pdf_url, str) and pdf_url.startswith("http"):
                        st.markdown(f"[📄 Clique aqui para baixar a certidão]({pdf_url})")
                    else:
                        st.warning("⚠️ PDF ainda não disponível ou chave não encontrada.")
                except Exception as e:
                    st.error(f"Erro ao extrair o PDF: {e}")
            else:
                st.info("ℹ️ Nenhum PDF esperado para este serviço.")
        else:
            st.error("❌ Resposta inesperada. Conteúdo não é JSON.")
            st.code(response.text[:600])
    except Exception as e:
        st.error(f"Erro ao consultar {nome}: {e}")

st.set_page_config(page_title="Certidões com PDF", layout="centered")
st.title("📑 Sistema Infosimples com Download de Certidões (PDF)")

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

        consultar_certidao("Receita Federal (PGFN)", f"{base}/receita-federal/pgfn", parametros, chave_pdf="pdf")
        consultar_certidao("SEFAZ Amapá", f"{base}/sefaz/ap/certidao-debitos", parametros, chave_pdf="certidao.pdf")
        consultar_certidao("FGTS / Caixa", f"{base}/caixa/regularidade", parametros, chave_pdf="crf.pdf")
        consultar_certidao("CNDT / Justiça do Trabalho", f"{base}/tribunal/tst/cndt", parametros, chave_pdf="certidao.pdf")