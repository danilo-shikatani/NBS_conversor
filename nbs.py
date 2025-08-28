import streamlit as st
import pandas as pd
import re
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Conversor de Códigos de Serviço para NBS", layout="wide")
st.title("🗺️ Conversor de Códigos de Serviço Municipal para NBS")
st.markdown("Faça o upload dos dois arquivos abaixo para iniciar a conversão.")

# --- 2. FUNÇÕES DE PROCESSAMENTO ---
def clean_text(text):
    """Limpa o texto para uma melhor comparação."""
    if not isinstance(text, str):
        return ''
    text = text.lower()
    text = re.sub(r'[^a-z0-9\sà-ú]', '', text)
    return text

def find_best_match(description, nbs_df):
    """Encontra a melhor correspondência na tabela NBS com base na similaridade de texto."""
    best_score = 0
    best_code = None
    best_desc = None
    desc_words = set(description.split())
    if not desc_words:
        return None, None, 0
    
    for _, nbs_row in nbs_df.iterrows():
        nbs_words = set(nbs_row['descricao_limpa'].split())
        if not nbs_words:
            continue
        score = len(desc_words.intersection(nbs_words)) / len(desc_words.union(nbs_words))
        if score > best_score:
            best_score = score
            best_code = nbs_row['codigo_nbs']
            best_desc = nbs_row['descricao_nbs']
    return best_code, best_desc, best_score

# --- 3. INTERFACE DE UPLOAD ---
st.header("📤 Passo 1: Faça o Upload do Arquivo Municipal")
arquivo_municipal = st.file_uploader(
    "Selecione o arquivo da sua prefeitura (ex: anexo de São Paulo)",
    type=['csv']
)

st.header("📤 Passo 2: Faça o Upload da Tabela NBS")
st.markdown("Se você não tem este arquivo, baixe-o [aqui](https://www.gov.br/mdic/pt-br/images/REPOSITORIO/scs/decos/NBS/NBSa_2-0.csv).")
arquivo_nbs = st.file_uploader(
    "Selecione o arquivo 'NBSa_2-0.csv'",
    type=['csv']
)

# --- 4. PROCESSAMENTO ---
if arquivo_municipal and arquivo_nbs:
    st.header("▶️ Passo 3: Inicie o Mapeamento")
    if st.button("Mapear Códigos de Serviço para NBS"):
        with st.spinner("Processando os arquivos... Isso pode levar alguns minutos."):
            # --- Arquivo Municipal ---
            try:
                df_municipal = pd.read_csv(arquivo_municipal, sep=';', encoding='latin1', header=7)
                df_municipal = df_municipal.iloc[:, [0, 2]].copy()
                df_municipal.columns = ['codigo_servico_sp', 'descricao_servico_sp']
                df_municipal.dropna(subset=['descricao_servico_sp'], inplace=True)
                df_municipal = df_municipal[~df_municipal['descricao_servico_sp'].str.contains(r'^\d+\.\s', regex=True)]
            except Exception as e:
                st.error(f"Erro ao ler o arquivo municipal: {e}")
                st.stop()
            
            # --- Arquivo NBS ---
            try:
                df_nbs = pd.read_csv(
                    arquivo_nbs,
                    sep=';',
                    encoding='latin1',
                    engine='python',
                    on_bad_lines='skip'
                )
                df_nbs = df_nbs.iloc[:, :2]  # pegar apenas as duas primeiras colunas
                df_nbs.columns = ['codigo_nbs', 'descricao_nbs']
            except Exception as e:
                st.error(f"Erro ao ler o arquivo NBS: {e}")
                st.stop()
            
            st.success("Arquivos carregados com sucesso. Iniciando comparação...")

            # Limpeza de descrições
            df_municipal['descricao_limpa'] = df_municipal['descricao_servico_sp'].apply(clean_text)
            df_nbs['descricao_limpa'] = df_nbs['descricao_nbs'].apply(clean_text)

            # Mapeamento
            mapeamento_results = df_municipal['descricao_limpa'].apply(lambda x: find_best_match(x, df_nbs))
            df_municipal['codigo_nbs_sugerido'] = [res[0] for res in mapeamento_results]
            df_municipal['descricao_nbs_sugerida'] = [res[1] for res in mapeamento_results]
            df_municipal['pontuacao_confianca'] = [res[2] for res in mapeamento_results]

            st.session_state['df_resultado'] = df_municipal[[
                'codigo_servico_sp', 'descricao_servico_sp', 
                'codigo_nbs_sugerido', 'descricao_nbs_sugerida', 'pontuacao_confianca'
            ]]
        
        st.balloons()
        st.success("Mapeamento concluído com sucesso!")

# --- 5. EXIBIÇÃO E DOWNLOAD ---
if 'df_resultado' in st.session_state:
    st.header("📊 4. Resultado do Mapeamento")
    df_resultado_final = st.session_state['df_resultado']
    st.info(f"Foram processados {len(df_resultado_final)} serviços. A 'pontuação de confiança' (0 a 1) indica similaridade entre descrições.")
    st.dataframe(df_resultado_final)

    # Download CSV
    @st.cache_data
    def converter_df_para_csv(df):
        return df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8')
    csv_final = converter_df_para_csv(df_resultado_final)
    st.download_button(
        label="📥 Baixar Resultado em CSV",
        data=csv_final,
        file_name="mapeamento_servicos_para_nbs.csv",
        mime="text/csv",
    )

    # Download Excel
   @st.cache_data
def converter_df_para_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Mapeamento')
    return output.getvalue()
    
    excel_final = converter_df_para_excel(df_resultado_final)
    st.download_button(
        label="📥 Baixar Resultado em Excel",
        data=excel_final,
        file_name="mapeamento_servicos_para_nbs.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


