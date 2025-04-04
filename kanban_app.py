
import pandas as pd
import streamlit as st
from datetime import datetime

ARQUIVO = "kanban_tarefas.csv"

def carregar_tarefas():
    try:
        return pd.read_csv(ARQUIVO, parse_dates=["Data de Início", "Prazo"], dayfirst=True)
    except:
        return pd.DataFrame(columns=["Feature", "Responsável", "Data de Início", "Prazo", "Status", "Prioridade", "Tags"])

def salvar_tarefas(df):
    df.to_csv(ARQUIVO, index=False)

def mostrar_kanban(df):
    status_list = ["A fazer", "Em andamento", "Concluído"]
    for status in status_list:
        with st.expander(f"{status} ({(df['Status'] == status).sum()})"):
            for _, row in df[df["Status"] == status].iterrows():
                atrasado = "🔥" if datetime.now() > row["Prazo"] else ""
                st.markdown(f"**{row['Feature']}** {atrasado}")
                st.text(f"Responsável: {row['Responsável']} | Prazo: {row['Prazo'].date()} | Prioridade: {row.get('Prioridade', '')} | Tags: {row.get('Tags', '')}")
                st.markdown("---")

st.title("📋 Bee Cam - Kanban de Tarefas")
df = carregar_tarefas()

aba = st.sidebar.radio("Menu", ["📊 Quadro", "➕ Nova Tarefa", "✏️ Editar", "🗑️ Excluir", "📤 Exportar"])

if aba == "📊 Quadro":
    mostrar_kanban(df)

elif aba == "➕ Nova Tarefa":
    with st.form("nova_tarefa"):
        feature = st.text_input("Feature")
        responsavel = st.text_input("Responsável")
        data_inicio = st.date_input("Data de Início", datetime.today())
        prazo = st.date_input("Prazo")
        status = st.selectbox("Status", ["A fazer", "Em andamento", "Concluído"])
        prioridade = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])
        tags = st.text_input("Tags")
        submitted = st.form_submit_button("Salvar")
        if submitted:
            nova = {
                "Feature": feature,
                "Responsável": responsavel,
                "Data de Início": pd.to_datetime(data_inicio),
                "Prazo": pd.to_datetime(prazo),
                "Status": status,
                "Prioridade": prioridade,
                "Tags": tags
            }
            df = pd.concat([df, pd.DataFrame([nova])], ignore_index=True)
            salvar_tarefas(df)
            st.success("Tarefa adicionada!")

elif aba == "✏️ Editar":
    if len(df) > 0:
        tarefa_alvo = st.selectbox("Selecione a tarefa", df["Feature"].tolist())
        if tarefa_alvo:
            idx = df[df["Feature"] == tarefa_alvo].index[0]
            novo_status = st.selectbox("Novo status", ["A fazer", "Em andamento", "Concluído"])
            novo_prazo = st.date_input("Novo prazo", df.loc[idx, "Prazo"])
            if st.button("Atualizar"):
                df.at[idx, "Status"] = novo_status
                df.at[idx, "Prazo"] = pd.to_datetime(novo_prazo)
                salvar_tarefas(df)
                st.success("Tarefa atualizada!")

elif aba == "🗑️ Excluir":
    if len(df) > 0:
        tarefa_excluir = st.selectbox("Tarefa a excluir", df["Feature"].tolist())
        if st.button("Excluir tarefa", type="primary"):
            df = df[df["Feature"] != tarefa_excluir]
            salvar_tarefas(df)
            st.warning("Tarefa excluída.")

elif aba == "📤 Exportar":
    nome = st.text_input("Nome do arquivo", "relatorio_tarefas.xlsx")
    if st.button("Exportar para Excel"):
        df.to_excel(nome, index=False)
        st.success(f"Exportado como {nome}")
