import streamlit as st
import pandas as pd
import re
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Conversor de Códigos de Serviço para NBS", layout="wide")
st.title("🗺️ Conversor de Códigos de Serviço Municipal para NBS")
st.markdown("Faça o upload do seu arquivo de códigos de serviço (ex: anexo da prefeitura de São Paulo) para encontrar os códigos NBS correspondentes.")


# --- 2. FUNÇÕES DE PROCESSAMENTO E CACHE ---

@st.cache_data
def carregar_dados_nbs():
    """Baixa e carrega a tabela oficial NBS em um DataFrame, guardando em cache."""
    try:
        url_nbs = 'https://www.gov.br/mdic/pt-br/images/REPOSITORIO/scs/decos/NBS/NBSa_2-0.csv'
        
        # --- ESTA É A LINHA QUE RESOLVE O PROBLEMA ---
        # Adicionamos engine='python' para usar o leitor mais flexível,
        # que consegue lidar com arquivos mal formatados.
        df = pd.read_csv(
            url_nbs,
            sep=';',
            encoding='latin1',
            header=0,
            engine='python'
        )
        # -------------------------------------------
        
        df.columns = ['codigo_nbs', 'descricao_nbs']
        return df
    except Exception as e:
        st.error(f"Não foi possível carregar a tabela NBS do governo. Erro: {e}")
        return None

def clean_text(text):
    if not isinstance(text, str): return ''
    text = text.lower()
    text = re.sub(r'[^a-z0-9\sà-ú]', '', text)
    return text

def find_best_match(description, nbs_df):
    best_score = 0
    best_code = None
    best_desc = None
    desc_words = set(description.split())
    if not desc_words: return None, None, 0
    
    for _, nbs_row in nbs_df.iterrows():
        nbs_words = set(nbs_row['descricao_limpa'].split())
        if not nbs_words: continue
        
        score = len(desc_words.intersection(nbs_words)) / len(desc_words.union(nbs_words))
        
        if score > best_score:
            best_score = score
            best_code = nbs_row['codigo_nbs']
            best_desc = nbs_row['descricao_nbs']
    return best_code, best_desc, best_score


# --- 3. INTERFACE DO APLICATIVO ---
df_nbs = carregar_dados_nbs()

if df_nbs is not None:
    st.header("📤 1. Faça o Upload do seu Arquivo")
    uploaded_file = st.file_uploader(
        "Selecione o arquivo CSV com os códigos de serviço municipais",
        type=['csv']
    )

    if uploaded_file:
        st.header("▶️ 2. Inicie o Mapeamento")
        if st.button("Mapear Códigos de Serviço para NBS"):
            with st.spinner("Mágica em andamento... Lendo seu arquivo e comparando com a tabela NBS. Isso pode levar alguns minutos."):
                df_municipal = pd.read_csv(uploaded_file, sep=';', encoding='latin1', header=7)
                df_municipal = df_municipal.iloc[:, [0, 2]].copy()
                df_municipal.columns = ['codigo_servico_sp', 'descricao_servico_sp']
                df_municipal.dropna(subset=['descricao_servico_sp'], inplace=True)
                df_municipal = df_municipal[~df_municipal['descricao_servico_sp'].str.contains(r'^\d+\.\s', regex=True)]
                
                df_municipal['descricao_limpa'] = df_municipal['descricao_servico_sp'].apply(clean_text)
                df_nbs['descricao_limpa'] = df_nbs['descricao_nbs'].apply(clean_text)

                mapeamento_results = df_municipal['descricao_limpa'].apply(lambda x: find_best_match(x, df_nbs))

                df_municipal['codigo_nbs_sugerido'] = [res[0] for res in mapeamento_results]
                df_municipal['descricao_nbs_sugerida'] = [res[1] for res in mapeamento_results]
                df_municipal['pontuacao_confianca'] = [res[2] for res in mapeamento_results]

                st.session_state['df_resultado'] = df_municipal[[
                    'codigo_servico_sp', 'descricao_servico_sp', 'codigo_nbs_sugerido', 
                    'descricao_nbs_sugerida', 'pontuacao_confianca'
                ]]
            st.balloons()
            st.success("Mapeamento concluído com sucesso!")

# --- 4. EXIBIÇÃO DO RESULTADO E DOWNLOAD ---
if 'df_resultado' in st.session_state:
    st.header("📊 3. Resultado do Mapeamento")
    df_resultado_final = st.session_state['df_resultado']
    st.info(f"Foram processados {len(df_resultado_final)} serviços. A 'pontuação de confiança' (de 0 a 1) indica a similaridade entre as descrições.")
    st.dataframe(df_resultado_final)

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
