import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 1. Configuração da Página Web
st.set_page_config(
    page_title="Gestão Escolar SEDUC-SP | Produtividade Docente",
    page_icon="🏫",
    layout="wide"
)

NOME_ARQUIVO_DADOS = "dados_semanais_seduc.csv"

# 2. Função para Inicializar / Carregar o Banco de Dados (CSV)
def carregar_ou_criar_banco():
    colunas = [
        "Semana", "Data_Registro", "Professor", "Disciplina",
        "Meta_Prova_Paulista", "Qualidade_TarefaSP", "Plataforma_Especifica",
        "Execucao_Planejamento", "Registro_Aula", "Formacao_EFAPE", "Indice_Produtividade"
    ]
    if not os.path.exists(NOME_ARQUIVO_DADOS):
        df_vazio = pd.DataFrame(columns=colunas)
        df_vazio.to_csv(NOME_ARQUIVO_DADOS, index=False, encoding="utf-8-sig")
        return df_vazio
    else:
        return pd.read_csv(NOME_ARQUIVO_DADOS)

# 3. Função para Calcular o Índice Dinâmico com base nos Pesos Escolhidos
def recalcular_indice_dataframe(df, p_meta, p_tarefa, p_plat, p_plan, p_reg, p_efape):
    if df.empty:
        return df
    
    # Cálculo vetorizado usando os pesos definidos pelo usuário
    df["Indice_Produtividade"] = (
        (df["Meta_Prova_Paulista"] * (p_meta / 100.0)) +
        (df["Qualidade_TarefaSP"] * (p_tarefa / 100.0)) +
        (df["Plataforma_Especifica"] * (p_plat / 100.0)) +
        (df["Execucao_Planejamento"] * (p_plan / 100.0)) +
        (df["Registro_Aula"] * (p_reg / 100.0)) +
        (df["Formacao_EFAPE"] * (p_efape / 100.0))
    ).round(1)
    
    return df

def calcular_indice_unitario(meta, tarefa, plat, plan, reg, efape, p_meta, p_tarefa, p_plat, p_plan, p_reg, p_efape):
    return round(
        (meta * (p_meta / 100.0)) +
        (tarefa * (p_tarefa / 100.0)) +
        (plat * (p_plat / 100.0)) +
        (plan * (p_plan / 100.0)) +
        (reg * (p_reg / 100.0)) +
        (efape * (p_efape / 100.0)), 1
    )

# ==============================================================================
# MENU LATERAL & PAINEL DE PESOS
# ==============================================================================
st.sidebar.image("https://www.educacao.sp.gov.br/wp-content/uploads/2019/02/logo-seduc-sp.png", width=180)
st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Ir para:", ["📊 Dashboard de Produtividade", "📝 Entrada e Gestão de Dados"])

st.sidebar.divider()

# CONFIGURAÇÃO DE PESOS DINÂMICOS
with st.sidebar.expander("⚙️️ Personalizar Pesos do Índice (%)", expanded=False):
    st.caption("Ajuste a importância de cada indicador no cálculo do Índice Global de Produtividade.")
    
    p_meta = st.number_input("Meta Prova Paulista (%)", min_value=0, max_value=100, value=25, step=5)
    p_tarefa = st.number_input("Qualidade TarefaSP (%)", min_value=0, max_value=100, value=20, step=5)
    p_plat = st.number_input("Plataforma Específica (%)", min_value=0, max_value=100, value=15, step=5)
    p_plan = st.number_input("Execução Planejamento (%)", min_value=0, max_value=100, value=15, step=5)
    p_reg = st.number_input("Registro de Aula (%):", min_value=0, max_value=100, value=15, step=5)
    p_efape = st.number_input("Formação EFAPE (%)", min_value=0, max_value=100, value=10, step=5)
    
    soma_pesos = p_meta + p_tarefa + p_plat + p_plan + p_reg + p_efape
    
    if soma_pesos != 100:
        st.error(f"⚠️ A soma dos pesos deve ser exatamente **100%**! Soma atual: **{soma_pesos}%**")
    else:
        st.success("✅ Soma dos pesos igual a 100%!")

# ==============================================================================
# PÁGINA 1: ENTRADA E GESTÃO DE DADOS (CADASTRAR, EDITAR, EXCLUIR)
# ==============================================================================
if pagina == "📝 Entrada e Gestão de Dados":
    st.title("📝 Gestão de Registros Semanais")
    st.markdown("Cadastre novos lançamentos, edite informações digitadas incorretamente ou exclua registros.")

    tab_cadastrar, tab_gerenciar = st.tabs(["➕ Novo Registro", "✏️ Editar ou Excluir Registro"])

    # --------------------------------------------------------------------------
    # SUB-ABA 1: CADASTRAR NOVO REGISTRO
    # --------------------------------------------------------------------------
    with tab_cadastrar:
        st.subheader("Cadastrar Novo Lançamento Semanal")
        df_banco = carregar_ou_criar_banco()

        with st.form("form_registro_semanal", clear_on_submit=False):
            c_semana, c_prof, c_disc = st.columns(3)
            
            with c_semana:
                semana = st.selectbox(
                    "Semana de Referência:",
                    [f"Semana {i}" for i in range(1, 53)]
                )
            
            with c_prof:
                professor = st.text_input("Nome do Professor:", placeholder="Ex: Ana Silva")
                
            with c_disc:
                disciplina = st.selectbox(
                    "Disciplina Responsável:",
                    ["Matemática", "Língua Portuguesa", "História", "Geografia", "Ciências / Biologia", "Física / Química", "Inglês", "Educação Física", "Artes", "Outra"]
                )

            st.divider()
            st.subheader("📊 Indicadores da SEDUC-SP (%)")

            col1, col2 = st.columns(2)

            with col1:
                meta_prova = st.number_input("1. % Média Notas Prova Paulista / Meta:", min_value=0.0, max_value=150.0, value=80.0, step=1.0, key="cad_meta")
                qualidade_tarefa = st.number_input("2. Índice de Qualidade do TarefaSP (%):", min_value=0.0, max_value=100.0, value=85.0, step=1.0, key="cad_tarefa")
                plat_especifica = st.number_input("3. Índice da Plataforma do Professor (%):", min_value=0.0, max_value=100.0, value=75.0, step=1.0, key="cad_plat")

            with col2:
                planejamento = st.number_input("4. Conclusão e Execução de Planejamento (%):", min_value=0.0, max_value=100.0, value=90.0, step=1.0, key="cad_plan")
                registro = st.number_input("5. Registro de Aula / Diário de Classe (%):", min_value=0.0, max_value=100.0, value=95.0, step=1.0, key="cad_reg")
                efape = st.number_input("6. Realização de Formação EFAPE (%):", min_value=0.0, max_value=100.0, value=100.0, step=1.0, key="cad_efape")

            btn_salvar = st.form_submit_button("💾 Salvar Registro Semanal")

        if btn_salvar:
            if not professor.strip():
                st.error("⚠️️ Por favor, informe o nome do professor antes de salvar.")
            elif soma_pesos != 100:
                st.error("⚠️ Não é possível salvar enquanto a soma dos pesos na barra lateral for diferente de 100%.")
            else:
                indice_final = calcular_indice_unitario(
                    meta_prova, qualidade_tarefa, plat_especifica, planejamento, registro, efape,
                    p_meta, p_tarefa, p_plat, p_plan, p_reg, p_efape
                )
                data_atual = datetime.now().strftime("%d/%m/%Y")

                novo_registro = pd.DataFrame([{
                    "Semana": semana,
                    "Data_Registro": data_atual,
                    "Professor": professor.strip(),
                    "Disciplina": disciplina,
                    "Meta_Prova_Paulista": meta_prova,
                    "Qualidade_TarefaSP": qualidade_tarefa,
                    "Plataforma_Especifica": plat_especifica,
                    "Execucao_Planejamento": planejamento,
                    "Registro_Aula": registro,
                    "Formacao_EFAPE": efape,
                    "Indice_Produtividade": indice_final
                }])

                df_atualizado = pd.concat([df_banco, novo_registro], ignore_index=True)
                df_atualizado.to_csv(NOME_ARQUIVO_DADOS, index=False, encoding="utf-8-sig")

                st.success(f"✅ Dados de **{professor}** para a **{semana}** salvos com sucesso! Índice Calculado: **{indice_final} pts**")
                st.rerun()

    # --------------------------------------------------------------------------
    # SUB-ABA 2: EDITAR OU EXCLUIR REGISTRO
    # --------------------------------------------------------------------------
    with tab_gerenciar:
        st.subheader("Gerenciar Registros Salvos")
        df_banco = carregar_ou_criar_banco()

        if df_banco.empty:
            st.info("Nenhum registro cadastrado no banco de dados para editar ou excluir.")
        else:
            opcoes_registro = [
                f"ID {idx} | {row['Semana']} | {row['Professor']} ({row['Disciplina']}) - Data: {row['Data_Registro']}"
                for idx, row in df_banco.iterrows()
            ]

            registro_selecionado = st.selectbox("Selecione o registro que deseja alterar ou apagar:", opcoes_registro)
            
            idx_linha = int(registro_selecionado.split(" | ")[0].replace("ID ", ""))
            dados_linha = df_banco.loc[idx_linha]

            acao = st.radio("Escolha a ação desejada:", ["✏️ Editar Dados", "🗑️ Excluir Registro Completo"], horizontal=True)

            if acao == "✏️️ Editar Dados":
                st.info(f"Editando registro ID {idx_linha} do professor **{dados_linha['Professor']}** ({dados_linha['Semana']}).")
                
                with st.form("form_editar_registro"):
                    c_sem_ed, c_prof_ed, c_disc_ed = st.columns(3)
                    
                    lista_semanas = [f"Semana {i}" for i in range(1, 53)]
                    idx_sem = lista_semanas.index(dados_linha["Semana"]) if dados_linha["Semana"] in lista_semanas else 0
                    
                    semana_ed = c_sem_ed.selectbox("Semana:", lista_semanas, index=idx_sem)
                    professor_ed = c_prof_ed.text_input("Professor:", value=dados_linha["Professor"])
                    
                    lista_discs = ["Matemática", "Língua Portuguesa", "História", "Geografia", "Ciências / Biologia", "Física / Química", "Inglês", "Educação Física", "Artes", "Outra"]
                    idx_disc = lista_discs.index(dados_linha["Disciplina"]) if dados_linha["Disciplina"] in lista_discs else 0
                    disciplina_ed = c_disc_ed.selectbox("Disciplina:", lista_discs, index=idx_disc)

                    st.divider()
                    col_ed1, col_ed2 = st.columns(2)

                    with col_ed1:
                        meta_ed = col_ed1.number_input("Meta Prova Paulista (%):", value=float(dados_linha["Meta_Prova_Paulista"]))
                        tarefa_ed = col_ed1.number_input("Qualidade TarefaSP (%):", value=float(dados_linha["Qualidade_TarefaSP"]))
                        plat_ed = col_ed1.number_input("Plataforma Específica (%):", value=float(dados_linha["Plataforma_Especifica"]))

                    with col_ed2:
                        plan_ed = col_ed2.number_input("Execução Planejamento (%):", value=float(dados_linha["Execucao_Planejamento"]))
                        reg_ed = col_ed2.number_input("Registro de Aula (%):", value=float(dados_linha["Registro_Aula"]))
                        efape_ed = col_ed2.number_input("Formação EFAPE (%):", value=float(dados_linha["Formacao_EFAPE"]))

                    btn_atualizar = st.form_submit_button("🔄 Atualizar Registro")

                if btn_atualizar:
                    novo_indice = calcular_indice_unitario(meta_ed, tarefa_ed, plat_ed, plan_ed, reg_ed, efape_ed, p_meta, p_tarefa, p_plat, p_plan, p_reg, p_efape)
                    
                    df_banco.at[idx_linha, "Semana"] = semana_ed
                    df_banco.at[idx_linha, "Professor"] = professor_ed.strip()
                    df_banco.at[idx_linha, "Disciplina"] = disciplina_ed
                    df_banco.at[idx_linha, "Meta_Prova_Paulista"] = meta_ed
                    df_banco.at[idx_linha, "Qualidade_TarefaSP"] = tarefa_ed
                    df_banco.at[idx_linha, "Plataforma_Especifica"] = plat_ed
                    df_banco.at[idx_linha, "Execucao_Planejamento"] = plan_ed
                    df_banco.at[idx_linha, "Registro_Aula"] = reg_ed
                    df_banco.at[idx_linha, "Formacao_EFAPE"] = efape_ed
                    df_banco.at[idx_linha, "Indice_Produtividade"] = novo_indice

                    df_banco.to_csv(NOME_ARQUIVO_DADOS, index=False, encoding="utf-8-sig")
                    st.success(f"✅ Registro do professor **{professor_ed}** atualizado com sucesso!")
                    st.rerun()

            elif acao == "🗑️ Excluir Registro Completo":
                st.warning(f"⚠️ **Atenção:** Você está prestes a excluir permanentemente o registro de **{dados_linha['Professor']}** referente à **{dados_linha['Semana']}**.")
                
                col_del1, col_del2 = st.columns([1, 4])
                with col_del1:
                    btn_confirmar_exclusao = st.button("🚨 Confirmar Exclusão", type="primary")

                if btn_confirmar_exclusao:
                    df_banco = df_banco.drop(index=idx_linha).reset_index(drop=True)
                    df_banco.to_csv(NOME_ARQUIVO_DADOS, index=False, encoding="utf-8-sig")
                    st.success("🗑️ Registro excluído com sucesso!")
                    st.rerun()

    st.divider()
    st.subheader("📋 Visão Geral de Todos os Registros do Banco")
    df_historico = carregar_ou_criar_banco()
    if not df_historico.empty:
        # Recalcular índice na tabela exibida com base nos pesos ativos
        df_historico = recalcular_indice_dataframe(df_historico, p_meta, p_tarefa, p_plat, p_plan, p_reg, p_efape)
        st.dataframe(df_historico, use_container_width=True, hide_index=False)

# ==============================================================================
# PÁGINA 2: DASHBOARD INTERATIVO
# ==============================================================================
else:
    st.title("📊 Painel de Produtividade e Rendimento Docente")
    st.markdown("Acompanhamento contínuo baseado nas alimentações semanais da gestão escolar.")

    df_banco = carregar_ou_criar_banco()

    if df_banco.empty:
        st.warning("⚠️ O banco de dados está vazio! Acesse a aba **'📝 Entrada e Gestão de Dados'** no menu lateral para realizar os primeiros lançamentos.")
    else:
        # Recalcula o Índice de TODO o banco em tempo real usando os pesos atuais da barra lateral
        df_banco = recalcular_indice_dataframe(df_banco, p_meta, p_tarefa, p_plat, p_plan, p_reg, p_efape)

        # Filtros no Menu Lateral
        st.sidebar.divider()
        st.sidebar.subheader("Filtros do Dashboard")
        
        semanas_disponiveis = sorted(df_banco["Semana"].unique())
        semana_sel = st.sidebar.multiselect("Filtrar por Semana:", opções:=semanas_disponiveis, default=semanas_disponiveis)
        
        disciplinas_disponiveis = sorted(df_banco["Disciplina"].unique())
        disciplina_sel = st.sidebar.multiselect("Filtrar por Disciplina:", opções:=disciplinas_disponiveis, default=disciplinas_disponiveis)

        df_filtrado = df_banco[
            (df_banco["Semana"].isin(semana_sel)) &
            (df_banco["Disciplina"].isin(disciplina_sel))
        ].copy()

        if df_filtrado.empty:
            st.info("Nenhum dado encontrado para os filtros selecionados.")
        else:
            # Agrupar por Professor (Média do período selecionado)
            df_resumo = df_filtrado.groupby(["Professor", "Disciplina"], as_index=False).agg({
                "Indice_Produtividade": "mean",
                "Meta_Prova_Paulista": "mean",
                "Qualidade_TarefaSP": "mean",
                "Plataforma_Especifica": "mean",
                "Execucao_Planejamento": "mean",
                "Registro_Aula": "mean",
                "Formacao_EFAPE": "mean"
            }).round(1)

            df_resumo = df_resumo.sort_values(by="Indice_Produtividade", ascending=False)
            df_resumo["Posição"] = range(1, len(df_resumo) + 1)

            # KPIs Principais
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Média Geral Escola", f"{df_resumo['Indice_Produtividade'].mean():.1f} pts")
            col2.metric("Meta Prova Paulista", f"{df_resumo['Meta_Prova_Paulista'].mean():.1f}%")
            col3.metric("Qualidade TarefaSP", f"{df_resumo['Qualidade_TarefaSP'].mean():.1f}%")
            col4.metric("Execução Planejamento", f"{df_resumo['Execucao_Planejamento'].mean():.1f}%")
            col5.metric("Formação EFAPE", f"{df_resumo['Formacao_EFAPE'].mean():.1f}%")

            st.divider()

            # SEÇÃO 1 DE GRÁFICOS
            c_graf1, c_graf2 = st.columns([3, 2])

            with c_graf1:
                st.subheader("🏆 Ranking de Professores por Índice de Produtividade")
                fig_bar = px.bar(
                    df_resumo.head(10),
                    x="Indice_Produtividade",
                    y="Professor",
                    orientation="h",
                    color="Indice_Produtividade",
                    color_continuous_scale="Blues",
                    text="Indice_Produtividade",
                    labels={"Indice_Produtividade": "Índice (0-100)", "Professor": ""}
                )
                fig_bar.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)

            with c_graf2:
                st.subheader("🎯 TarefaSP vs. Meta Prova Paulista")
                fig_scatter1 = px.scatter(
                    df_resumo,
                    x="Qualidade_TarefaSP",
                    y="Meta_Prova_Paulista",
                    size="Indice_Produtividade",
                    color="Disciplina",
                    hover_name="Professor",
                    labels={
                        "Qualidade_TarefaSP": "Qualidade TarefaSP (%)",
                        "Meta_Prova_Paulista": "Atingimento Prova Paulista (%)"
                    }
                )
                st.plotly_chart(fig_scatter1, use_container_width=True)

            st.divider()

            # SEÇÃO 2 DE GRÁFICOS
            st.subheader("📈 Relação: Índice de Produtividade vs. Meta Prova Paulista")
            st.caption(f"Pesos atuais em uso: Prova Paulista ({p_meta}%), TarefaSP ({p_tarefa}%), Plataformas ({p_plat}%), Planejamento ({p_plan}%), Registro ({p_reg}%), EFAPE ({p_efape}%).")

            fig_scatter2 = px.scatter(
                df_resumo,
                x="Meta_Prova_Paulista",
                y="Indice_Produtividade",
                color="Disciplina",
                size="Execucao_Planejamento",
                text="Professor",
                hover_data=["Qualidade_TarefaSP", "Registro_Aula", "Formacao_EFAPE"],
                labels={
                    "Meta_Prova_Paulista": "Atingimento Meta Prova Paulista (%)",
                    "Indice_Produtividade": "Índice de Produtividade Global (0-100 pts)"
                }
            )
            fig_scatter2.update_traces(textposition="top center")
            fig_scatter2.update_layout(height=450)
            st.plotly_chart(fig_scatter2, use_container_width=True)

            st.divider()

            # Tabela Completa
            st.subheader("📋 Tabela Detalhada de Rendimento Docente")
            cols_exibir = [
                "Posição", "Professor", "Disciplina", "Indice_Produtividade",
                "Meta_Prova_Paulista", "Qualidade_TarefaSP", "Plataforma_Especifica",
                "Execucao_Planejamento", "Registro_Aula", "Formacao_EFAPE"
            ]
            
            st.dataframe(
                df_resumo[cols_exibir],
                column_config={
                    "Indice_Produtividade": st.column_config.ProgressColumn(
                        "Índice Global", format="%.1f", min_value=0, max_value=100
                    ),
                    "Meta_Prova_Paulista": st.column_config.NumberColumn("Meta Prova Paulista %", format="%.1f%%"),
                    "Qualidade_TarefaSP": st.column_config.NumberColumn("TarefaSP %", format="%.1f%%"),
                    "Plataforma_Especifica": st.column_config.NumberColumn("Plat. Específica %", format="%.1f%%"),
                    "Execucao_Planejamento": st.column_config.NumberColumn("Planejamento %", format="%.1f%%"),
                    "Registro_Aula": st.column_config.NumberColumn("Registro Aula %", format="%.1f%%"),
                    "Formacao_EFAPE": st.column_config.NumberColumn("EFAPE %", format="%.1f%%"),
                },
                hide_index=True,
                use_container_width=True
            )

            # Detalhamento do Professor
            st.divider()
            st.subheader("🔍 Ficha de Avaliação Detalhada")
            prof_selecionado = st.selectbox("Selecione o Professor para ver o histórico semanal:", df_resumo["Professor"].unique())
            
            df_prof = df_filtrado[df_filtrado["Professor"] == prof_selecionado]
            st.markdown(f"**Histórico de Lançamentos de {prof_selecionado}:**")
            st.dataframe(
                df_prof[["Semana", "Data_Registro", "Indice_Produtividade", "Meta_Prova_Paulista", "Qualidade_TarefaSP", "Plataforma_Especifica", "Execucao_Planejamento", "Registro_Aula", "Formacao_EFAPE"]], 
                use_container_width=True, 
                hide_index=True
            )