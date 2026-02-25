import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import binom

st.set_page_config(layout="wide", page_title="Tennis Strategy Master Suite", page_icon="🎾")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stMetric { border: 1px solid #e2e8f0; padding: 15px; border-radius: 12px; background: #ffffff; }
    .main { background-color: #f8fafc; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎾 Tennis Strategic Master Suite (Fusion v5)")
st.markdown("---")

# --- BARRE LATÉRALE : PARAMÈTRES ---
with st.sidebar:
    st.header("⚙️ Configuration")
    mode = st.selectbox("Format du Tournoi", ["Grand Chelem (127)", "Masters 1000 (63)", "1er Tour Express (64)"])
    n_matchs = 127 if "127" in mode else 63 if "63" in mode else 64
    
    st.divider()
    n_joueurs = st.number_input("Volume de Joueurs", value=1000000, step=100000)
    prix_ticket = st.number_input("Prix du Ticket (€)", value=2.0, step=0.5)
    precision = st.slider("Précision des Experts (%)", 50, 95, 75) / 100
    
    st.divider()
    st.subheader("⚖️ Répartition des 80% Joueurs")
    pct_gains_consolation = st.slider("% Gains Immédiats (Consolation)", 0, 80, 60)
    pct_jackpot_next = 80 - pct_gains_consolation
    
    st.divider()
    st.subheader("🏦 Charges Entreprise")
    frais_fixes = st.number_input("Frais fixes / tournoi (€)", value=25000)
    pct_taxes_sur_marge = st.slider("Impôts & Frais Bancaires (sur les 20%)", 0, 70, 45) / 100

# --- CALCULS FINANCIERS ---
ca_total = n_joueurs * prix_ticket
part_entreprise_brute = ca_total * 0.20
impots_frais = part_entreprise_brute * pct_taxes_sur_marge
benefice_net_unitaire = part_entreprise_brute - impots_frais - frais_fixes

pot_consolation = ca_total * (pct_gains_consolation / 100)
apport_jackpot = ca_total * (pct_jackpot_next / 100)

# --- ONGLET 1 : FINANCE DÉTAILLÉE ---
t1, t2, t3, t4, t5 = st.tabs(["💰 Finance & Marge", "🎯 Probabilités Précises", "⏳ Évolution Jackpot", "📅 Saison Complète", "📋 Synthèse Audit"])

with t1:
    st.subheader("Répartition et Flux de Trésorerie")
    col1, col2 = st.columns([2, 1])
    with col1:
        # Waterfall Chart pour le détail
        fig_water = go.Figure(go.Waterfall(
            orientation = "v",
            measure = ["relative", "relative", "relative", "relative", "total"],
            x = ["CA Brut", "Part Joueurs (80%)", "Impôts & Frais (sur 20%)", "Frais Fixes", "Bénéfice Net"],
            textposition = "outside",
            text = [f"+{ca_total:,.0f}", f"-{ca_total*0.8:,.0f}", f"-{impots_frais:,.0f}", f"-{frais_fixes:,.0f}", f"{benefice_net_unitaire:,.0f}"],
            y = [ca_total, -ca_total*0.8, -impots_frais, -frais_fixes, 0],
            connector = {"line":{"color":"#cbd5e1"}},
        ))
        st.plotly_chart(fig_water, use_container_width=True)
    
    with col2:
        st.write("### 🍰 Répartition CA (%)")
        labels = ['Part Entreprise (Marge)', 'Impôts & Banques', 'Gains Joueurs', 'Provision Jackpot']
        values = [benefice_net_unitaire + frais_fixes, impots_frais, pot_consolation, apport_jackpot]
        fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4)])
        st.plotly_chart(fig_pie, use_container_width=True)

# --- ONGLET 2 : PROBABILITÉS HAUTE PRÉCISION ---
with t2:
    st.subheader("Analyse de Risque Mathématique")
    st.write("Probabilité qu'au moins un joueur réussisse le palier (Précision complète) :")
    
    err_list = [0, 1, 2, 3, 4, 5]
    for e in err_list:
        p_indiv = binom.pmf(n_matchs - e, n_matchs, precision)
        p_collectif = 1 - (1 - p_indiv)**n_joueurs
        n_gagnants = n_joueurs * p_indiv
        
        c_a, c_b, c_c = st.columns([1, 2, 1])
        c_a.write(f"**{e} Erreur(s)**")
        # Affichage avec 12 décimales pour la précision demandée
        c_b.code(f"{p_collectif*100:.12f} % de chance")
        c_c.write(f"~{int(n_gagnants)} gagnants")

# --- ONGLET 3 : ÉVOLUTION JACKPOT ---
with t3:
    st.subheader("Projection de croissance du Jackpot")
    nb_tournois = st.slider("Tournois successifs sans 0 faute", 1, 20, 10)
    steps = np.arange(nb_tournois + 1)
    evol = [apport_jackpot * i for i in steps]
    
    fig_line = go.Figure(go.Scatter(x=steps, y=evol, mode='lines+markers', line=dict(color='#fbbf24', width=4)))
    fig_line.update_layout(xaxis_title="Nombre de tournois", yaxis_title="Cagnotte cumulée (€)")
    st.plotly_chart(fig_line, use_container_width=True)

# --- ONGLET 4 : SAISON COMPLÈTE ---
with t4:
    st.subheader("Simulation Financière Annuelle")
    # 4 GC + 9 Masters 1000
    benef_annuel = benefice_net_unitaire * 13
    ca_annuel = ca_total * 13
    
    st.metric("Bénéfice Net Annuel Estimé", f"{benef_annuel:,.0f} €")
    
    labels_an = ['Bénéfice Net Annuel', 'Taxes & Frais Annuels', 'Coûts Fixes Annuels', 'Reversement Joueurs']
    values_an = [benef_annuel, impots_frais*13, frais_fixes*13, (pot_consolation + apport_jackpot)*13]
    fig_an = go.Figure(go.Bar(x=labels_an, y=values_an, marker_color='#1e3a8a'))
    st.plotly_chart(fig_an, use_container_width=True)

# --- ONGLET 5 : SYNTHÈSE AUDIT ---
with t5:
    st.subheader("📋 Rapport de Viabilité")
    col_syn1, col_syn2 = st.columns(2)
    with col_syn1:
        st.info(f"""
        **Données Entreprise :**
        - **Marge brute :** 20% fixes ({part_entreprise_brute:,.0f} €)
        - **Impôts & Frais bancaires :** {impots_frais:,.0f} €
        - **Bénéfice Net / Tournoi :** {benefice_net_unitaire:,.0f} €
        - **Seuil de rentabilité :** {int(frais_fixes / (prix_ticket*0.2*(1-pct_taxes_sur_marge)))} joueurs.
        """)
    with col_syn2:
        st.warning(f"""
        **Données Joueurs :**
        - **Gains Immédiats (Consolation) :** {pot_consolation:,.0f} € ({pct_gains_consolation}%)
        - **Jackpot Épargné :** {apport_jackpot:,.0f} € ({pct_jackpot_next}%)
        - **Risque de Rupture Jackpot :** Extrêmement faible sur {n_matchs} matchs.
        """)
