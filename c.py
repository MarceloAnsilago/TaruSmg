import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO

# Configuração da página - deve ser a primeira chamada de Streamlit no script
st.set_page_config(page_title="Tarumã Pesquisa Conf", page_icon="🌲")

# Função para conectar ao banco de dados
def conectar_banco():
    return sqlite3.connect('enquete.db')

# Função para carregar as configurações atuais
def carregar_configuracoes():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('SELECT exibir_real, candidato_favorecido FROM configuracao WHERE id = 1')
    config = cursor.fetchone()
    conn.close()
    return config

# Função para salvar as configurações
def salvar_configuracoes(exibir_real, candidato_favorecido=None):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE configuracao SET 
        exibir_real = ?,
        candidato_favorecido = ?,
        data_hora = CURRENT_TIMESTAMP
        WHERE id = 1
    ''', (exibir_real, candidato_favorecido))
    conn.commit()
    conn.close()

# Função para exibir a tabela `configuracao` como dataframe
def exibir_dataframe_configuracao():
    conn = conectar_banco()
    df = pd.read_sql_query("SELECT * FROM configuracao", conn)
    conn.close()
    return df

# Função para exibir a tabela de tokens
def exibir_tokens():
    conn = conectar_banco()
    df = pd.read_sql_query("SELECT * FROM tokens", conn)
    conn.close()
    return df

# Função para exibir a tabela de intenção de votos
def exibir_tabela_intencao_votos():
    conn = conectar_banco()
    df = pd.read_sql_query("SELECT * FROM intencao_voto", conn)
    conn.close()
    return df

# Função para exibir a tabela de rejeição
def exibir_tabela_rejeicao():
    conn = conectar_banco()
    df = pd.read_sql_query("SELECT * FROM rejeicao", conn)
    conn.close()
    return df

# Função para zerar os tokens
def zerar_tokens():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('UPDATE tokens SET usado_intencao = FALSE, usado_rejeicao = FALSE')
    conn.commit()
    conn.close()

# Função para zerar a tabela de intenção de votos
def zerar_intencao_votos():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM intencao_voto')
    conn.commit()
    conn.close()

# Função para zerar a tabela de rejeição
def zerar_rejeicao():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM rejeicao')
    conn.commit()
    conn.close()

# Função para converter DataFrame para Excel e CSV para download
def converter_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def converter_para_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def main():
    st.title("Configurações")

    # Exibir opções de configuração
    st.subheader("Configurações dos Gráficos")
    
    config = carregar_configuracoes()

    if config:
        exibir_real, candidato_favorecido = config
    else:
        st.error("Erro ao carregar as configurações.")
        exibir_real = True  # Valor padrão se ocorrer erro ao carregar
        candidato_favorecido = None

    # Checkbox para exibir gráficos reais
    exibir_real = st.checkbox("Exibir gráficos reais", value=exibir_real)

    # Exibir combobox e dataframe se "Exibir gráficos reais" for desmarcado
    if not exibir_real:
        st.subheader("Seleção do Candidato Favorecido")
        candidato_favorecido = st.selectbox(
            "Escolha o candidato que deve ser favorecido:",
            ("Fabio de Paula", "Coronel Crispim", "Prof Eudes")
        )
        st.write("O candidato selecionado receberá a maior votação quando estiver em desvantagem e a menor rejeição quando ele não for o menos rejeitado.")

        # Exibir a tabela de configuração como dataframe
        st.subheader("Visualização da Tabela de Configuração")
        df = exibir_dataframe_configuracao()
        st.dataframe(df)

        # Adicionar legenda explicativa
        st.write("Legenda: **1** para 'Sim' (Exibir gráficos reais), **0** para 'Não' (Não exibir gráficos reais)")

    # Botão para salvar as configurações
    if st.button("Salvar Configurações"):
        salvar_configuracoes(exibir_real, candidato_favorecido)
        st.success("Configurações salvas com sucesso.")

    # Separador
    st.markdown("---")

    # Botões para download dos votos
    st.subheader("Download de Votos")

    df_intencao = exibir_tabela_intencao_votos()
    df_rejeicao = exibir_tabela_rejeicao()

    # Exibir tabelas de intenção de votos e rejeição com botões para atualizar
    st.subheader("Visualização da Tabela de Intenção de Votos")
    st.dataframe(df_intencao)
    if st.button("Atualizar Tabela de Intenção de Votos"):
        df_intencao = exibir_tabela_intencao_votos()
        st.dataframe(df_intencao)
        st.success("Tabela de Intenção de Votos atualizada.")

    st.subheader("Visualização da Tabela de Rejeição")
    st.dataframe(df_rejeicao)
    if st.button("Atualizar Tabela de Rejeição"):
        df_rejeicao = exibir_tabela_rejeicao()
        st.dataframe(df_rejeicao)
        st.success("Tabela de Rejeição atualizada.")

    # Separador acima do botão de download
    st.markdown("---")

    # Download de intenção de votos em Excel e CSV
    st.download_button(
        label="Baixar Intenção de Votos (Excel)",
        data=converter_para_excel(df_intencao),
        file_name="intencao_votos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.download_button(
        label="Baixar Intenção de Votos (CSV)",
        data=converter_para_csv(df_intencao),
        file_name="intencao_votos.csv",
        mime="text/csv"
    )

    # Download de rejeição em Excel e CSV
    st.download_button(
        label="Baixar Rejeição (Excel)",
        data=converter_para_excel(df_rejeicao),
        file_name="rejeicao.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.download_button(
        label="Baixar Rejeição (CSV)",
        data=converter_para_csv(df_rejeicao),
        file_name="rejeicao.csv",
        mime="text/csv"
    )

    # Separador para as opções de zerar tokens
    st.markdown("---")

    # Exibir tokens antes de zerá-los
    st.subheader("Visualização dos Tokens")
    df_tokens = exibir_tokens()
    st.dataframe(df_tokens)

    # Botões para download dos tokens em Excel e CSV
    st.download_button(
        label="Baixar Tokens (Excel)",
        data=converter_para_excel(df_tokens),
        file_name="tokens.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.download_button(
        label="Baixar Tokens (CSV)",
        data=converter_para_csv(df_tokens),
        file_name="tokens.csv",
        mime="text/csv"
    )

    # Separador para a opção de zerar banco de dados
    st.markdown("---")

    # Checkbox para zerar banco de dados
    if st.checkbox("Zerar banco de dados"):
        st.warning("Essa ação não pode ser desfeita. Selecione as opções abaixo para zerar:")

        # Botão para zerar tokens
        if st.button("Zerar Tokens"):
            zerar_tokens()
            st.success("Todos os tokens foram zerados com sucesso.")
            # Reexibir os tokens após zerar para verificar se deu certo
            df_tokens = exibir_tokens()
            st.dataframe(df_tokens)
        
        # Botão para zerar intenção de votos
        if st.button("Zerar Intenção de Votos"):
            zerar_intencao_votos()
            st.success("Todos os votos de intenção foram zerados com sucesso.")
            df_intencao = exibir_tabela_intencao_votos()
            st.dataframe(df_intencao)
        
        # Botão para zerar rejeição
        if st.button("Zerar Rejeição"):
            zerar_rejeicao()
            st.success("Todas as rejeições foram zeradas com sucesso.")
            df_rejeicao = exibir_tabela_rejeicao()
            st.dataframe(df_rejeicao)

if __name__ == "__main__":
    main()
