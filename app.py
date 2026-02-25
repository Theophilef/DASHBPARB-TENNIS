import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import binom

st.set_page_config(layout="wide", page_title="Tennis Strategy Master Suite Pro", page_icon="📊")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stMetric { border: 1px solid #e2e8f0; padding: 15px; border-radius: 12px; background: #ffffff; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .main { background-color: #f8fafc; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Tennis Strategic Intelligence - v6.0")

# --- SIDEBAR : PARAMÈTRES GÉNÉRAUX ---
with st.sidebar:
    st.header("⚙️ Paramètres de Base")
    mode = st.selectbox("Format Global", ["Grand Chelem (127)", "Masters 1000 (63)", "1er Tour Express (64)"])
    n_matchs = 127 if "127" in mode else 63 if "63" in mode else 64
    
    st.divider()
    n_joueurs = st.number_input("Volume de Joueurs", value=1000000, step=100000)
    prix_ticket = st.number_input("Prix du Ticket (€)", value=2.0, step=0.5)
    precision = st.slider("Précision des Experts (%)", 50, 95, 75) / 100
    
    st.divider()
    st.subheader("⚖️ Répartition des 80% Joueurs")
    pct_gains_consolation = st.slider("% Gains Immédiats", 0, 80, 60)
    pct_jackpot_next = 80 - pct_gains_consolation
    
    st.divider()
    st.subheader("🏦 Charges & Taxes")
    frais_fixes = st.number_input("Frais fixes / tournoi (€)", value=25000)
    pct_taxes_sur_marge = st.slider("Impôts & Frais Bancaires (sur marge)", 0, 70, 45) / 100

# --- CALCULS FINANCIERS UNITAIRES ---
ca_tournoi = n_joueurs * prix_ticket
part_entreprise_brute = ca_tournoi * 0.20
impots_frais = part_entreprise_brute * pct_taxes_sur_marge
benefice_net_unitaire = part_entreprise_brute - impots_frais - frais_fixes
# Marketing : Budget max par ticket avant perte
budget_marketing_max_total = benefice_net_unitaire if benefice_net_unitaire > 0 else 0
cac_max = budget_marketing_max_total / n_joueurs if n_joueurs > 0 else 0

# --- ONGLET ---
tabs = st.tabs(["💰 Finance & Marketing", "🎯 Probabilités", "⏳ Évolution Jackpot", "🗓️ Simulation Saison", "⚖️ Comparateur de Scénarios", "📋 Synthèse Audit"])

# --- ONGLET 1 : FINANCE & MARKETING ---
with tabs[0]:
    st.subheader("Structure de Revenus & Potentiel Marketing")
    c1, c2 = st.columns([2, 1])
    with c1:
        fig_water = go.Figure(go.Waterfall(
            orientation = "v", x = ["CA Brut", "Part Joueurs (80%)", "Impôts & Frais", "Frais Fixes", "Bénéfice Net"],
            y = [ca_tournoi, -ca_tournoi*0.8, -impots_frais, -frais_fixes, 0],
            text = [f"+{ca_tournoi:,.0f}", f"-{ca_tournoi*0.8:,.0f}", f"-{impots_frais:,.0f}", f"-{frais_fixes:,.0f}", f"{benefice_net_unitaire:,.0f}"],
            textposition = "outside", connector = {"line":{"color":"#cbd5e1"}}
        ))
        st.plotly_chart(fig_water, use_container_width=True)
    
    with c2:
        st.write("### 🚀 Analyse Marketing (CAC)")
        st.metric("Bénéfice Net / Tournoi", f"{benefice_net_unitaire:,.0f} €")
        st.metric("Coût d'Acquisition Max (CAC)", f"{cac_max:.3f} € / ticket")
        st.help("Il s'agit de la somme maximale que vous pouvez dépenser en publicité par joueur pour rester à l'équilibre (0 € de profit).")

# --- ONGLET 2 : PROBABILITÉS ---
with tabs[1]:
    st.subheader("Analyse de Risque Mathématique")
    err_list = [0, 1, 2, 3, 4, 5]
    for e in err_list:
        p_indiv = binom.pmf(n_matchs - e, n_matchs, precision)
        p_collectif = 1 - (1 - p_indiv)**n_joueurs
        c_a, c_b, c_c = st.columns([1, 2, 1])
        c_a.write(f"**{e} Erreur(s)**")
        c_b.code(f"{p_collectif*100:.12f} % de chance")
        c_c.write(f"~{int(n_joueurs * p_indiv)} gagnants")

# --- ONGLET 3 : JACKPOT ---
with tabs[2]:
    st.subheader("Croissance de la Réserve")
    nb_t_jackpot = st.slider("Tournois sans gagnant à 0 faute", 1, 20, 10, key="slider_jackpot")
    apport_j = ca_tournoi * (pct_jackpot_next / 100)
    fig_j = go.Figure(go.Scatter(x=np.arange(nb_t_jackpot+1), y=[apport_j*i for i in range(nb_t_jackpot+1)], mode='lines+markers', line_color='#fbbf24'))
    st.plotly_chart(fig_j, use_container_width=True)

# --- ONGLET 4 : SAISON (MODULABLE) ---
with tabs[3]:
    st.subheader("Planification de Saison Personnalisée")
    sc1, sc2 = st.columns(2)
    nb_gc = sc1.number_input("Nombre de Grands Chelems", value=4, min_value=0)
    nb_m1000 = sc2.number_input("Nombre de Masters 1000", value=9, min_value=0)
    
    total_tournois = nb_gc + nb_m1000
    benef_saison = benefice_net_unitaire * total_tournois
    ca_saison = ca_tournoi * total_tournois
    
    st.metric("Bénéfice Net Total sur la Période", f"{benef_saison:,.0f} €", delta=f"{total_tournois} tournois")
    
    # Graphique d'évolution temporelle
    tournois_labels = [f"T{i+1}" for i in range(total_tournois)]
    evol_benef = [benefice_net_unitaire * (i+1) for i in range(total_tournois)]
    fig_season = go.Figure(go.Scatter(x=tournois_labels, y=evol_benef, fill='tozeroy', name="Bénéfice Cumulé", line_color='#059669'))
    st.plotly_chart(fig_season, use_container_width=True)

# --- ONGLET 5 : COMPARATEUR ---
with tabs[4]:
    st.subheader("⚖️ Comparaison de deux Scénarios")
    comp1, comp2 = st.columns(2)
    
    with comp1:
        st.markdown("**Scénario A**")
        j_a = st.number_input("Joueurs (A)", value=1000000, key="ja")
        t_a = st.number_input("Ticket (A)", value=2.0, key="ta")
        benef_a = (j_a * t_a * 0.2 * (1-pct_taxes_sur_marge)) - frais_fixes
        st.metric("Profit (A)", f"{benef_a:,.0f} €")

    with comp2:
        st.markdown("**Scénario B**")
        j_b = st.number_input("Joueurs (B)", value=500000, key="jb")
        t_b = st.number_input("Ticket (B)", value=5.0, key="tb")
        benef_b = (j_b * t_b * 0.2 * (1-pct_taxes_sur_marge)) - frais_fixes
        st.metric("Profit (B)", f"{benef_b:,.0f} €")
    
    fig_comp = go.Figure(data=[go.Bar(name='Scénario A', x=['Profit Net'], y=[benef_a]), go.Bar(name='Scénario B', x=['Profit Net'], y=[benef_b])])
    st.plotly_chart(fig_comp, use_container_width=True)

# --- ONGLET 6 : SYNTHÈSE ---
with tabs[5]:
    st.subheader("📋 Audit Stratégique Global")
    st.info(f"Le CA par tournoi est de **{ca_tournoi:,.0f} €**. Votre point mort est atteint à **{int(frais_fixes / marge_nette_par_ticket) if 'marge_nette_par_ticket' in locals() else '---'}** joueurs.")
    st.success("Modèle robuste : Le profit net annuel avec votre configuration est estimé à **" + f"{benef_saison:,.0f} €**.")
