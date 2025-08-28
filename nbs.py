import streamlit as st
import pandas as pd
import re
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Conversor e Depurador de CSV", layout="wide")
st.title("🗺️ Conversor de Códigos de Serviço para NBS")

# --- 2. BARRA LATERAL COM MODO DE DEPURAÇÃO ---
st.sidebar.header("⚙️ Ferramentas")
debug_mode = st.sidebar.toggle("Ativar Modo de Depuração", value=True)
st.sidebar.info("Se ocorrer um erro, ative o modo de depuração, faça o upload dos arquivos e envie um print da tela.")

# --- 3. INTERFACE DE UPLOAD ---
st.header("📤 1. Faça o Upload dos Arquivos")
col1, col2 = st.columns(2)
with col1:
    arquivo_municipal = st.file_uploader("Selecione o arquivo Municipal (ex: São Paulo)", type=['csv'])
with col2:
    st.markdown("Se não tiver a tabela NBS, baixe-a [aqui](https://www.gov.br/mdic/pt-br/images/REPOSITORIO/scs/decos/NBS/NBSa_2-0.csv).")
    arquivo_nbs = st.file_uploader("Selecione o arquivo da Tabela NBS", type=['csv'])

# --- 4. LÓGICA PRINCIPAL ---
if debug_mode:
    st.subheader("🕵️‍♀️ MODO DE DEPURAÇÃO ATIVADO 🕵️‍♀️")
    st.warning("O aplicativo irá analisar os arquivos enviados e parar. O botão de mapeamento está desativado.")

    if arquivo_municipal:
        with st.expander("Análise do Arquivo Municipal", expanded=True):
            try:
                st.write("**Conteúdo Bruto (primeiras 10 linhas):**")
                file_content_bytes = arquivo_municipal.getvalue()
                file_content_str = file_content_bytes.decode('latin1')
                st.code('\n'.join(file_content_str.splitlines()[:10]))

                st.write("**Tentativa de Leitura:**")
                arquivo_municipal.seek(0)
                df_test = pd.read_csv(arquivo_municipal, sep=';', encoding='latin1', header=7)
                st.success("Arquivo Municipal lido com sucesso!")
                st.write("Colunas encontradas:", df_test.columns.tolist())
                st.dataframe(df_test.head(3))
            except Exception as e:
                st.error("Falha ao ler o Arquivo Municipal!")
                st.exception(e)

    if arquivo_nbs:
        with st.expander("Análise do Arquivo NBS", expanded=True):
            try:
                st.write("**Conteúdo Bruto (primeiras 10 linhas):**")
                file_content_bytes = arquivo_nbs.getvalue()
                file_content_str = file_content_bytes.decode('latin1')
                st.code('\n'.join(file_content_str.splitlines()[:10]))

                st.write("**Tentativa de Leitura:**")
                arquivo_nbs.seek(0)
                df_test = pd.read_csv(arquivo_nbs, sep='|', encoding='latin1', header=0)
                st.success("Arquivo NBS lido com sucesso!")
                st.write("Colunas encontradas:", df_test.columns.tolist())
                st.dataframe(df_test.head(3))
            except Exception as e:
                st.error("Falha ao ler o Arquivo NBS!")
                st.exception(e)

else:
    # --- MODO DE PRODUÇÃO (CÓDIGO ORIGINAL) ---
    # Só continua se os dois arquivos forem enviados
    if arquivo_municipal and arquivo_nbs:
        st.header("▶️ 2. Inicie o Mapeamento")
        if st.button("Mapear Códigos de Serviço para NBS"):
            
            with st.spinner("Mágica em andamento..."):
                # (Aqui entraria toda a sua lógica de processamento original)
                # Como o erro está na leitura, vamos focar no modo de depuração.
                # O código de processamento completo será usado após a depuração.
                try:
                    # Leitura do arquivo municipal
                    df_municipal = pd.read_csv(arquivo_municipal, sep=';', encoding='latin1', header=7)
                    # Leitura da tabela NBS
                    df_nbs = pd.read_csv(arquivo_nbs, sep='|', encoding='latin1', header=0)
                    
                    # Se chegou aqui, a leitura funcionou e o resto do script pode ser adicionado
                    st.success("Leitura dos arquivos bem-sucedida, o problema pode estar na lógica de transformação.")
                    # ... (resto do código de transformação)

                except Exception as e:
                    st.error("O erro de leitura persistiu mesmo no modo de produção.")
                    st.exception(e)

### Como Usar a Ferramenta de Depuração

1.  **Salve o novo código** e rode o aplicativo.
2.  **Ative o "Modo de Depuração"**: Na barra lateral à esquerda, a chave "Ativar Modo de Depuração" já virá ligada. Mantenha assim.
3.  **Faça o Upload dos dois arquivos** como antes (o municipal e o NBS).
4.  **Analise o Resultado na Tela**: O aplicativo não vai mostrar o botão de mapeamento. Em vez disso, ele vai exibir uma análise detalhada para **cada arquivo**:
    * O conteúdo bruto das primeiras linhas.
    * Uma tentativa de ler o arquivo e o resultado: ou uma mensagem de **sucesso** com a prévia da tabela, ou uma mensagem de **erro em vermelho** com todos os detalhes técnicos.

### Sua Próxima Ação

Por favor, **me envie um print da tela inteira** do aplicativo depois de fazer o upload dos arquivos com o modo de depuração ativado.

A informação que aparecerá lá, especialmente a mensagem de erro em vermelho, nos dará a resposta final e definitiva sobre como corrigir o script. Com essa abordagem, não haverá mais adivinhação.
