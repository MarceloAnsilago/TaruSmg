import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Configuração da página - deve ser a primeira chamada de Streamlit no script
st.set_page_config(page_title="Tarumã Pesquisa Gráfico", page_icon="🌲")

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

# Função para gerar o gráfico de rosca para intenção de voto
def gerar_grafico_intencao_voto():
    conn = conectar_banco()
    df = pd.read_sql_query("SELECT candidato, COUNT(*) as votos FROM intencao_voto GROUP BY candidato", conn)
    conn.close()

    total_participantes = df['votos'].sum()
    fig = px.pie(df, names='candidato', values='votos', hole=0.4, title=f'Intenção de Voto ({total_participantes} participantes)')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False)
    return fig

# Função para gerar o gráfico de rosca para rejeição
def gerar_grafico_rejeicao():
    conn = conectar_banco()
    df = pd.read_sql_query("SELECT candidato, COUNT(*) as rejeicoes FROM rejeicao GROUP BY candidato", conn)
    conn.close()

    total_participantes = df['rejeicoes'].sum()
    fig = px.pie(df, names='candidato', values='rejeicoes', hole=0.4, title=f'Rejeição ({total_participantes} participantes)')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False)
    return fig

# Função para gerar gráficos com base na configuração
def gerar_grafico_configurado(config):
    exibir_real, candidato_favorecido = config

    # Gráfico de Intenção de Voto
    fig_intencao = gerar_grafico_intencao_voto()

    # Gráfico de Rejeição
    fig_rejeicao = gerar_grafico_rejeicao()

    if not exibir_real and candidato_favorecido:
        # Ajustar Intenção de Voto (gráfico vantajoso)
        df_intencao = pd.read_sql_query("SELECT candidato, COUNT(*) as votos FROM intencao_voto GROUP BY candidato", conectar_banco())
        max_votos = df_intencao['votos'].max()
        if candidato_favorecido in df_intencao['candidato'].values:
            df_intencao.loc[df_intencao['candidato'] == candidato_favorecido, 'votos'] = max_votos + 1
            fig_intencao = px.pie(df_intencao, names='candidato', values='votos', hole=0.4, title=f'Gráfico Vantajoso - Intenção de Voto ({candidato_favorecido})')

        # Ajustar Rejeição (gráfico vantajoso)
        df_rejeicao = pd.read_sql_query("SELECT candidato, COUNT(*) as rejeicoes FROM rejeicao GROUP BY candidato", conectar_banco())
        max_rejeicoes = df_rejeicao['rejeicoes'].max()
        if candidato_favorecido in df_rejeicao['candidato'].values:
            # Troca as rejeições entre o mais rejeitado e o candidato favorecido, se o favorecido for o mais rejeitado
            if df_rejeicao[df_rejeicao['candidato'] == candidato_favorecido]['rejeicoes'].values[0] == max_rejeicoes:
                segundo_mais_rejeitado = df_rejeicao[df_rejeicao['candidato'] != candidato_favorecido]['rejeicoes'].max()
                segundo_candidato = df_rejeicao.loc[df_rejeicao['rejeicoes'] == segundo_mais_rejeitado, 'candidato'].values[0]
                df_rejeicao.loc[df_rejeicao['candidato'] == candidato_favorecido, 'rejeicoes'] = segundo_mais_rejeitado
                df_rejeicao.loc[df_rejeicao['candidato'] == segundo_candidato, 'rejeicoes'] = max_rejeicoes
                fig_rejeicao = px.pie(df_rejeicao, names='candidato', values='rejeicoes', hole=0.4, title=f'Gráfico Vantajoso - Rejeição ({candidato_favorecido})')

    return fig_intencao, fig_rejeicao

def main():
    st.title("🌲 Tarumã Pesquisa Gráfico")

    # Carregar configurações da tabela `configuracao`
    config = carregar_configuracoes()
    if not config:
        st.error("Erro ao carregar as configurações.")
        return

    # Criar abas para Gráfico e Dashboard
    tab1, tab2 = st.tabs(["Gráfico", "Dashboard"])

    with tab1:
        st.subheader("Gráficos Reais")

        # Exibir gráficos reais de intenção de voto e rejeição
        st.plotly_chart(gerar_grafico_intencao_voto())
        st.plotly_chart(gerar_grafico_rejeicao())

        # Separador e exibição de gráficos conforme a configuração
        st.markdown("---")
        st.subheader("Gráfico Exibido Conforme Configuração")
        fig_intencao, fig_rejeicao = gerar_grafico_configurado(config)
        st.plotly_chart(fig_intencao)
        st.plotly_chart(fig_rejeicao)

    with tab2:
        st.subheader("Dashboard")
        st.write("Aqui você pode adicionar métricas, resumos ou outros gráficos conforme necessário.")

if __name__ == "__main__":
    main()
