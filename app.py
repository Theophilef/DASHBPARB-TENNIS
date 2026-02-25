import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import binom

# Configuration Pro
st.set_page_config(layout="wide", page_title="Tennis Prediction Strategic Suite", page_icon="📊")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { border: 1px solid #d1d5db; padding: 10px; border-radius: 5px; background: white; }
    h1, h2, h3 { color: #1e3a8a; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Tennis Strategic Intelligence Suite")
st.markdown("---")

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3233/3233850.png", width=80)
    st.header("🎛️ Centre de Contrôle")
    mode = st.selectbox("Format du Tournoi", ["Grand Chelem (127)", "Masters 1000 (63)", "1er Tour Express (64)"])
    n_matchs = 127 if "127" in mode else 63 if "63" in mode else 64
    
    st.divider()
    n_joueurs = st.number_input("Volume de Joueurs", value=1000000, step=100000)
    prix_ticket = st.slider("Prix du Ticket (€)", 1.0, 10.0, 2.0)
    precision = st.slider("Précision des experts (%)", 50, 95, 75) / 100
    
    st.divider()
    st.subheader("🏦 Paramètres Business")
    frais_fixes = st.number_input("Frais fixes / tournoi (€)", value=20000)
    pct_taxes_entreprise = st.slider("Taxes & Frais bancaires (sur marge %)", 0, 70, 40) / 100

# --- CALCULS DE BASE ---
ca_total = n_joueurs * prix_ticket
part_entreprise_brute = ca_total * 0.20
taxes_et_frais = part_entreprise_brute * pct_taxes_entreprise
benefice_net = part_entreprise_brute - taxes_et_frais - frais_fixes

# --- NAVIGATION PAR SOUS-ONGLETS ---
st.subheader(f"📍 Analyse Focus : {mode}")
tab1, tab2, tab3, tab4 = st.tabs(["💰 Finance & Marge", "🎯 Probabilités & Gains", "📈 Évolution Jackpot", "📋 Rapport Exécutif"])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.write("### Décomposition du Revenu")
        # Graphique Waterfall
        fig_water = go.Figure(go.Waterfall(
            name = "Finance", orientation = "v",
            measure = ["relative", "relative", "relative", "relative", "total"],
            x = ["Mises Totales", "Part Joueurs (80%)", "Taxes & Frais", "Frais Fixes", "Bénéfice Net"],
            textposition = "outside",
            text = [f"+{ca_total:,.0f}", f"-{ca_total*0.8:,.0f}", f"-{taxes_et_frais:,.0f}", f"-{frais_fixes:,.0f}", f"{benefice_net:,.0f}"],
            y = [ca_total, -ca_total*0.8, -taxes_et_frais, -frais_fixes, 0],
            connector = {"line":{"color":"rgb(63, 63, 63)"}},
        ))
        fig_water.update_layout(height=450)
        st.plotly_chart(fig_water, use_container_width=True)
    
    with col2:
        st.write("### Rentabilité Réelle")
        marge_nette_pct = (benefice_net / ca_total) * 100 if ca_total > 0 else 0
        st.metric("Marge Nette sur CA", f"{marge_nette_pct:.2f}%")
        st.progress(max(0.0, min(marge_nette_pct / 20.0, 1.0)))
        st.write(f"Pour chaque ticket de {prix_ticket}€, il reste **{benefice_net/n_joueurs:.2f}€** dans votre poche.")

with tab2:
    st.write("### Analyse des Gains Joueurs")
    c_a, c_b = st.columns(2)
    
    erreurs = [0, 1, 2, 3]
    stats = []
    for e in erreurs:
        p_i = binom.pmf(n_matchs - e, n_matchs, precision)
        n_gagnants = max(1, n_joueurs * p_i)
        stats.append({"err": e, "proba": (1-(1-p_i)**n_joueurs)*100, "nb": n_gagnants})
    
    with c_a:
        fig_bar = go.Figure(go.Bar(
            x=[f"{s['err']} Erreur(s)" for s in stats],
            y=[s['proba'] for s in stats],
            marker_color='#1e3a8a',
            text=[f"{s['proba']:.1f}%" for s in stats], textposition='auto'
        ))
        fig_bar.update_layout(title="Probabilité d'avoir au moins 1 gagnant")
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_b:
        st.write("### Estimation des gains par tête")
        pot_dispo = ca_total * 0.80
        for s in stats:
            gain_u = pot_dispo / s['nb']
            st.write(f"**{s['err']} Erreur(s)** : ~{int(s['nb'])} gagnants | Gain : **{gain_u:,.2f} €** / pers.")

with tab3:
    st.write("### Projection sur la Saison")
    nb_t = st.slider("Nombre de tournois cumulés sans 0 faute", 1, 15, 5)
    apport_mensuel = ca_total * 0.20 # On suppose 20% réinvestis
    cumul = [apport_mensuel * i for i in range(nb_t + 1)]
    
    fig_evol = go.Figure(go.Scatter(x=list(range(nb_t+1)), y=cumul, fill='tozeroy', line_color='#059669'))
    fig_evol.update_layout(title="Croissance de la Réserve Jackpot", xaxis_title="Nombre de tournois", yaxis_title="Euros (€)")
    st.plotly_chart(fig_evol, use_container_width=True)

with tab4:
    st.write("### Résumé de la Stratégie")
    st.info(f"""
    **Modèle Économique :**
    - **Sécurité :** Sur ce format ({n_matchs} matchs), votre risque de payer le jackpot de rang 0 est de **{(1-stats[0]['proba']/100)*100:.6f}%**.
    - **Point Mort :** Il vous faut au minimum **{int(frais_fixes / (prix_ticket*0.2*(1-pct_taxes_entreprise)))} joueurs** pour être rentable.
    - **Conseil Marketing :** Le pot de consolation (1 à 2 erreurs) est de **{ca_total*0.6:,.0f}€**, c'est votre argument de vente principal.
    """)
