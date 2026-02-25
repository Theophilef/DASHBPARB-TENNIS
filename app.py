import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import binom

st.set_page_config(layout="wide", page_title="Tennis Strategic Suite v9", page_icon="📊")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stMetric { border: 1px solid #e2e8f0; padding: 15px; border-radius: 12px; background: #ffffff; }
    .main { background-color: #f8fafc; }
    .report-box { padding: 20px; border-radius: 10px; border-left: 5px solid #1e3a8a; background: white; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎾 Tennis Strategic Intelligence Suite - Full Control Edition")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuration")
    mode = st.selectbox("Format Global", [
        "Grand Chelem (127)", 
        "Masters 1000 (63)", 
        "1er Tour de GC (64)", 
        "2ème Tour de GC (32)", 
        "ATP 500 (31)"
    ])
    
    match_map = {"127": 127, "63": 63, "64": 64, "32": 32, "31": 31}
    n_matchs = next(v for k, v in match_map.items() if k in mode)
    
    st.divider()
    n_joueurs = st.number_input("Volume de Joueurs", value=1000000, step=100000)
    prix_ticket = st.number_input("Prix du Ticket (€)", value=2.0, step=0.5)
    precision = st.slider("Précision des Experts (%)", 50, 95, 75) / 100
    
    st.divider()
    st.subheader("🏦 Part Entreprise (Marge Brute)")
    pct_entreprise = st.slider("% Conservé par l'Entreprise", 5, 40, 20)
    pct_joueurs_total = 100 - pct_entreprise
    
    st.divider()
    st.subheader(f"⚖️ Répartition des {pct_joueurs_total}% Joueurs")
    pct_gains_consolation = st.slider(f"% Gains Immédiats (sur les {pct_joueurs_total}%)", 0, pct_joueurs_total, int(pct_joueurs_total*0.75))
    pct_jackpot_next = pct_joueurs_total - pct_gains_consolation
    
    st.divider()
    st.subheader("💹 Charges & Taxes")
    frais_fixes = st.number_input("Frais fixes / tournoi (€)", value=25000)
    pct_taxes_sur_marge = st.slider("Impôts & Frais Bancaires (sur part entreprise)", 0, 70, 45) / 100

# --- CALCULS FINANCIERS ---
ca_tournoi = n_joueurs * prix_ticket
part_entreprise_brute = ca_tournoi * (pct_entreprise / 100)
impots_frais = part_entreprise_brute * pct_taxes_sur_marge
benefice_net_unitaire = part_entreprise_brute - impots_frais - frais_fixes
cac_max = max(0.0, benefice_net_unitaire / n_joueurs) if n_joueurs > 0 else 0

pot_consolation = ca_tournoi * (pct_gains_consolation / 100)
apport_jackpot = ca_tournoi * (pct_jackpot_next / 100)

# --- NAVIGATION ---
tabs = st.tabs(["💰 Finance & CAC", "🎯 Probabilités", "⏳ Évolution Jackpot", "🗓️ Simulation Saison", "⚖️ Comparateur", "📋 Audit & Synthèse"])

# --- ONGLET 1 : FINANCE & CAC ---
with tabs[0]:
    st.subheader("Structure de Revenus & Potentiel Marketing")
    c1, c2 = st.columns([2, 1])
    with c1:
        fig_water = go.Figure(go.Waterfall(
            orientation = "v", x = ["CA Brut", f"Part Joueurs ({pct_joueurs_total}%)", "Impôts & Frais", "Frais Fixes", "Bénéfice Net"],
            y = [ca_tournoi, -ca_tournoi*(pct_joueurs_total/100), -impots_frais, -frais_fixes, 0],
            text = [f"+{ca_tournoi:,.0f}", f"-{ca_tournoi*(pct_joueurs_total/100):,.0f}", f"-{impots_frais:,.0f}", f"-{frais_fixes:,.0f}", f"{benefice_net_unitaire:,.0f}"],
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
    fig_j = go.Figure(go.Scatter(x=np.arange(nb_t_j+1), y=[apport_jackpot*i for i in range(nb_t_j+1)], fill='tozeroy', line_color='#fbbf24'))
    st.plotly_chart(fig_j, use_container_width=True)

# --- ONGLET 4 : SAISON INTERACTIF ---
with tabs[3]:
    st.subheader("Planification de Saison Interactive")
    sc1, sc2, sc3 = st.columns([1, 1, 2])
    nb_gc = sc1.number_input("Nombre de Grands Chelems", value=4, min_value=0)
    nb_m1000 = sc2.number_input("Nombre de Masters 1000 / ATP", value=9, min_value=0)
    view_option = sc3.selectbox("Visualiser l'évolution de :", 
                                ["Bénéfice Net Cumulé", "Impôts & Frais Cumulés", f"Gains reversés aux joueurs ({pct_joueurs_total}%)"])
    
    total_t = nb_gc + nb_m1000
    indices = np.arange(1, total_t + 1)
    
    if view_option == "Bénéfice Net Cumulé":
        data_y, color_y = benefice_net_unitaire * indices, '#059669'
    elif view_option == "Impôts & Frais Cumulés":
        data_y, color_y = impots_frais * indices, '#ef4444'
    else:
        data_y, color_y = (ca_tournoi * (pct_joueurs_total/100)) * indices, '#3b82f6'
        
    fig_season = go.Figure(go.Scatter(x=indices, y=data_y, name=view_option, fill='tozeroy', line=dict(color=color_y, width=4)))
    st.plotly_chart(fig_season, use_container_width=True)

# --- ONGLET 5 : COMPARATEUR ---
with tabs[4]:
    st.subheader("⚖️ Comparateur de Scénarios")
    cmp1, cmp2 = st.columns(2)
    with cmp1:
        st.markdown("**Scénario A**")
        ja, ta = st.number_input("Joueurs A", value=1000000, key="ja"), st.number_input("Ticket A", value=2.0, key="ta")
        ba = (ja * ta * (pct_entreprise/100) * (1-pct_taxes_sur_marge)) - frais_fixes
        st.metric("Profit A", f"{ba:,.0f} €")
    with cmp2:
        st.markdown("**Scénario B**")
        jb, tb = st.number_input("Joueurs B", value=500000, key="jb"), st.number_input("Ticket B", value=5.0, key="tb")
        bb = (jb * tb * (pct_entreprise/100) * (1-pct_taxes_sur_marge)) - frais_fixes
        st.metric("Profit B", f"{bb:,.0f} €")
    fig_c = go.Figure(data=[go.Bar(name='A', x=['Profit'], y=[ba]), go.Bar(name='B', x=['Profit'], y=[bb])])
    st.plotly_chart(fig_c, use_container_width=True)

# --- ONGLET 6 : AUDIT & SYNTHÈSE ---
with tabs[5]:
    st.header("📋 Audit Stratégique & Recommandations")
    a1, a2, a3, a4, a5 = st.columns(5)
    a1.metric("CA Annuel", f"{ca_tournoi * total_t:,.0f} €")
    a2.metric("Marge Nette Totale", f"{(benefice_net_unitaire*total_t):,.0f} €")
    a3.metric("Budget Pub Max", f"{cac_max:.2f} €")
    a4.metric("Part Entreprise", f"{pct_entreprise}%")
    a5.metric("Seuil Rentabilité", f"{int(frais_fixes / ((prix_ticket*(pct_entreprise/100))*(1-pct_taxes_sur_marge))):,} J")

    st.divider()
    col_aud1, col_aud2 = st.columns([1, 1])
    with col_aud1:
        aud_labels = ['Bénéfice Net', 'Impôts & État', 'Frais Fixes', f'Gains Joueurs ({pct_joueurs_total}%)']
        aud_values = [benefice_net_unitaire, impots_frais, frais_fixes, ca_tournoi * (pct_joueurs_total/100)]
        fig_aud = go.Figure(data=[go.Pie(labels=aud_labels, values=aud_values, hole=.5, marker_colors=['#059669', '#ef4444', '#94a3b8', '#3b82f6'])])
        st.plotly_chart(fig_aud, use_container_width=True)
    with col_aud2:
        st.markdown("<div class='report-box'>", unsafe_allow_html=True)
        st.markdown(f"#### 📝 Analyse : Modèle à {pct_entreprise}%")
        st.write(f"En conservant **{pct_entreprise}%** du CA, vous générez **{part_entreprise_brute:,.0f} €** de marge brute.")
        st.write(f"Cela vous permet d'offrir un pot total de **{ca_tournoi*(pct_joueurs_total/100):,.0f} €** aux joueurs, ce qui est très compétitif.")
        st.markdown("</div>", unsafe_allow_html=True)
