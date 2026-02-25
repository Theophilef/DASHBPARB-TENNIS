import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import binom

st.set_page_config(layout="wide", page_title="Tennis Strategic Suite v8", page_icon="📊")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stMetric { border: 1px solid #e2e8f0; padding: 15px; border-radius: 12px; background: #ffffff; }
    .main { background-color: #f8fafc; }
    .report-box { padding: 20px; border-radius: 10px; border-left: 5px solid #1e3a8a; background: white; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎾 Tennis Strategic Intelligence Suite - Expert Edition")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuration")
    # Ajout des nouveaux formats demandés
    mode = st.selectbox("Format Global", [
        "Grand Chelem (127)", 
        "Masters 1000 (63)", 
        "1er Tour de GC (64)", 
        "2ème Tour de GC (32)", 
        "ATP 500 (31)"
    ])
    
    # Mapping du nombre de matchs selon le format
    match_map = {"127": 127, "63": 63, "64": 64, "32": 32, "31": 31}
    n_matchs = next(v for k, v in match_map.items() if k in mode)
    
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
    pct_taxes_sur_marge = st.slider("Impôts & Frais Bancaires (sur marge %)", 0, 70, 45) / 100

# --- CALCULS FINANCIERS ---
ca_tournoi = n_joueurs * prix_ticket
part_entreprise_brute = ca_tournoi * 0.20
impots_frais = part_entreprise_brute * pct_taxes_sur_marge
benefice_net_unitaire = part_entreprise_brute - impots_frais - frais_fixes
cac_max = max(0.0, benefice_net_unitaire / n_joueurs) if n_joueurs > 0 else 0

# --- NAVIGATION ---
tabs = st.tabs(["💰 Finance & CAC", "🎯 Probabilités", "⏳ Évolution Jackpot", "🗓️ Simulation Saison", "⚖️ Comparateur", "📋 Audit & Synthèse"])

# --- ONGLET 1 : FINANCE & CAC ---
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
        st.plotly_chart(fig_water, use_container_width=True, key="fin_water")
    with c2:
        st.metric("Bénéfice Net / Tournoi", f"{benefice_net_unitaire:,.0f} €")
        st.metric("Coût d'Acquisition Max (CAC)", f"{cac_max:.3f} € / ticket")

# --- ONGLET 2 : PROBABILITÉS ---
with tabs[1]:
    st.subheader(f"Analyse de Risque : {mode}")
    err_list = [0, 1, 2, 3, 4, 5]
    for e in err_list:
        p_indiv = binom.pmf(n_matchs - e, n_matchs, precision)
        p_collectif = (1 - (1 - p_indiv)**n_joueurs) * 100
        ca, cb, cc = st.columns([1, 2, 1])
        ca.write(f"**{e} Erreur(s)**")
        cb.code(f"{p_collectif:.12f} %")
        cc.write(f"~{int(n_joueurs * p_indiv)} gagnants")

# --- ONGLET 3 : JACKPOT ---
with tabs[2]:
    st.subheader("Croissance de la Réserve")
    nb_t_j = st.slider("Tournois sans 0 faute", 1, 20, 10)
    apport_j = ca_tournoi * (pct_jackpot_next / 100)
    fig_j = go.Figure(go.Scatter(x=np.arange(nb_t_j+1), y=[apport_j*i for i in range(nb_t_j+1)], fill='tozeroy', line_color='#fbbf24'))
    st.plotly_chart(fig_j, use_container_width=True)

# --- ONGLET 4 : SAISON (GRAPHIQUE INTERACTIF DEMANDÉ) ---
with tabs[3]:
    st.subheader("Planification de Saison Interactive")
    sc1, sc2, sc3 = st.columns([1, 1, 2])
    nb_gc = sc1.number_input("Nombre de Grands Chelems", value=4, min_value=0)
    nb_m1000 = sc2.number_input("Nombre de Masters 1000 / ATP", value=9, min_value=0)
    
    # Liste déroulante pour choisir l'indicateur
    view_option = sc3.selectbox("Visualiser l'évolution de :", 
                                ["Bénéfice Net Cumulé", "Impôts & Frais Cumulés", "Gains reversés aux joueurs (80%)"])
    
    total_t = nb_gc + nb_m1000
    indices = np.arange(1, total_t + 1)
    
    # Mapping des données selon le choix
    if view_option == "Bénéfice Net Cumulé":
        data_y = benefice_net_unitaire * indices
        color_y = '#059669'
    elif view_option == "Impôts & Frais Cumulés":
        data_y = impots_frais * indices
        color_y = '#ef4444'
    else:
        data_y = (ca_tournoi * 0.8) * indices
        color_y = '#3b82f6'
        
    fig_season = go.Figure(go.Scatter(x=indices, y=data_y, name=view_option, fill='tozeroy', line=dict(color=color_y, width=4)))
    fig_season.update_layout(xaxis_title="Nombre de Tournois", yaxis_title="Montant Cumulé (€)")
    st.plotly_chart(fig_season, use_container_width=True)

# --- ONGLET 5 : COMPARATEUR ---
with tabs[4]:
    st.subheader("⚖️ Comparaison de Scénarios")
    cmp1, cmp2 = st.columns(2)
    with cmp1:
        st.markdown("**Scénario A**")
        ja = st.number_input("Joueurs A", value=1000000, key="ja")
        ta = st.number_input("Ticket A", value=2.0, key="ta")
        ba = (ja * ta * 0.2 * (1-pct_taxes_sur_marge)) - frais_fixes
        st.metric("Profit A", f"{ba:,.0f} €")
    with cmp2:
        st.markdown("**Scénario B**")
        jb = st.number_input("Joueurs B", value=500000, key="jb")
        tb = st.number_input("Ticket B", value=5.0, key="tb")
        bb = (jb * tb * 0.2 * (1-pct_taxes_sur_marge)) - frais_fixes
        st.metric("Profit B", f"{bb:,.0f} €")
    fig_c = go.Figure(data=[go.Bar(name='A', x=['Profit'], y=[ba]), go.Bar(name='B', x=['Profit'], y=[bb])])
    st.plotly_chart(fig_c, use_container_width=True)

# --- ONGLET 6 : AUDIT & SYNTHÈSE ---
with tabs[5]:
    st.header("📋 Audit Stratégique & Recommandations")
    a1, a2, a3, a4, a5 = st.columns(5)
    a1.metric("CA Annuel Estimé", f"{ca_tournoi * total_t:,.0f} €")
    a2.metric("Marge Nette Totale", f"{(benefice_net_unitaire*total_t):,.0f} €")
    a3.metric("Budget Pub Max / J", f"{cac_max:.2f} €")
    a4.metric("Format", f"{n_matchs} Matchs")
    a5.metric("Seuil Rentabilité", f"{int(frais_fixes / (prix_ticket*0.2*(1-pct_taxes_sur_marge))):,} J")

    st.divider()
    col_aud1, col_aud2 = st.columns([1, 1])
    with col_aud1:
        aud_labels = ['Bénéfice Net', 'Impôts & État', 'Frais Fixes', 'Gains Joueurs (80%)']
        aud_values = [benefice_net_unitaire, impots_frais, frais_fixes, ca_tournoi * 0.8]
        fig_aud = go.Figure(data=[go.Pie(labels=aud_labels, values=aud_values, hole=.5, marker_colors=['#059669', '#ef4444', '#94a3b8', '#3b82f6'])])
        st.plotly_chart(fig_aud, use_container_width=True)
    with col_aud2:
        st.markdown("<div class='report-box'>", unsafe_allow_html=True)
        st.markdown(f"#### 📝 Interprétation : {mode}")
        if n_matchs < 40:
            st.write("🎯 **Format Attractif :** Avec peu de matchs, la probabilité de gagnants à 0 erreur augmente. Idéal pour faire le buzz et acquérir des clients rapidement.")
        else:
            st.write("🛡️ **Format Sécurisé :** Le risque de vider le jackpot est quasi nul. Parfait pour accumuler une réserve massive.")
        st.write(f"📈 **Levier :** Votre CAC Max est de **{cac_max:.2f}€**. C'est votre arme principale pour la croissance.")
        st.markdown("</div>", unsafe_allow_html=True)
