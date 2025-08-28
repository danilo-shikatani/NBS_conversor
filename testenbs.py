import streamlit as st
import pandas as pd
import io

st.set_page_config(layout="wide")
st.title("🕵️ Ferramenta de Diagnóstico de Arquivos CSV")

st.info("Use esta ferramenta para descobrir os parâmetros corretos para ler arquivos CSV problemáticos.")

# 1. Upload do arquivo problemático
uploaded_file = st.file_uploader(
    "Faça o upload do arquivo CSV que está dando erro (ex: NBSa_2-0.csv)",
    type=['csv']
)

if uploaded_file:
    # 2. Mostra as primeiras linhas do arquivo como texto puro
    st.subheader("Conteúdo Bruto do Arquivo (Primeiras 10 linhas)")
    
    # Lê as primeiras linhas para inspeção visual
    file_content_bytes = uploaded_file.getvalue()
    try:
        # Tenta decodificar com latin1 primeiro
        file_content_str = file_content_bytes.decode('latin1')
    except UnicodeDecodeError:
        # Se falhar, tenta com utf-8
        file_content_str = file_content_bytes.decode('utf-8')

    st.code('\n'.join(file_content_str.splitlines()[:10]))
    st.markdown("---")

    # 3. Parâmetros de leitura interativos
    st.subheader("Parâmetros de Leitura")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        separador = st.selectbox("Separador (Delimitador)", [';', ',', '\t', '|'], index=0)
    with col2:
        encoding = st.selectbox("Codificação (Encoding)", ['latin1', 'utf-8', 'cp1252'], index=0)
    with col3:
        header_row = st.number_input("Linha do Cabeçalho (começando do 0)", value=0)

    # 4. Botão para tentar ler o arquivo
    if st.button("Tentar Ler o Arquivo com estes Parâmetros"):
        try:
            # Garante que o ponteiro do arquivo esteja no início
            uploaded_file.seek(0)
            
            df = pd.read_csv(
                uploaded_file,
                sep=separador,
                encoding=encoding,
                header=header_row,
                engine='python' # Usa o motor flexível
            )
            
            st.success("✅ Sucesso! O arquivo foi lido com esta configuração.")
            st.subheader("Pré-visualização da Tabela Lida:")
            st.dataframe(df.head())
            st.code(f"Parâmetros que funcionaram: sep='{separador}', encoding='{encoding}', header={header_row}")

        except Exception as e:
            st.error("❌ Falha na Leitura!")
            st.subheader("Mensagem de Erro Detalhada:")
            st.exception(e)