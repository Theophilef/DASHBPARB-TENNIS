import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import binom

st.set_page_config(layout="wide", page_title="Tennis Business Suite v3", page_icon="📈")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f8f9fa; border-radius: 5px; }
    .stMetric { border: 1px solid #e2e8f0; padding: 15px; border-radius: 12px; background: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Tennis Strategic Intelligence - Executive Suite")

# --- SIDEBAR CONTROL ---
with st.sidebar:
    st.header("⚙️ Configuration Globale")
    mode = st.selectbox("Format", ["Grand Chelem (127)", "Masters 1000 (63)", "1er Tour (64)"])
    n_matchs = 127 if "127" in mode else 63 if "63" in mode else 64
    
    st.divider()
    n_joueurs = st.number_input("Nombre de Joueurs", value=1000000, step=100000)
    prix_ticket = st.number_input("Prix du Ticket (€)", value=2.0, step=0.5)
    precision = st.slider("Précision des Experts (%)", 50, 95, 75) / 100
    
    st.divider()
    st.subheader("⚖️ Répartition des 80% Joueurs")
    st.info("Les 20% entreprise sont fixes. Réglez ici le reste :")
    pct_gains_directs = st.slider("% Reversé en Gains (Consolation)", 0, 80, 60)
    pct_jackpot_next = 80 - pct_gains_directs
    st.warning(f"Répartition : {pct_gains_directs}% Gains / {pct_jackpot_next}% Réinvestissement")

# --- CALCULS ---
ca_total = n_joueurs * prix_ticket
part_entreprise = ca_total * 0.20
part_gains = ca_total * (pct_gains_directs / 100)
part_jackpot = ca_total * (pct_jackpot_next / 100)

# --- TABS ---
t1, t2, t3, t4 = st.tabs(["💰 Structure Financière", "🎯 Analyse de Probabilités", "⏳ Évolution Temporelle", "📋 Synthèse Exécutive"])

with t1:
    st.subheader("Répartition du Chiffre d'Affaires")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        labels = ['Part Entreprise (20%)', f'Gains Joueurs ({pct_gains_directs}%)', f'Réinvestissement Jackpot ({pct_jackpot_next}%)']
        values = [part_entreprise, part_gains, part_jackpot]
        colors = ['#1e3a8a', '#3b82f6', '#fbbf24']
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, marker_colors=colors)])
        fig.update_traces(textinfo='percent+label+value', texttemplate='%{label}<br>%{percent}<br>%{value:,.0f} €')
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2))
        st.plotly_chart(fig, use_container_width=True, key="finance_pie")

    with col2:
        st.markdown("### Analyse de Marge")
        st.metric("Total Encaissé", f"{ca_total:,.0f} €")
        st.write("---")
        st.write(f"- **Revenu Entreprise :** {part_entreprise:,.0f} € (20%)")
        st.write(f"- **Reversement Immédiat :** {part_gains:,.0f} € ({pct_gains_directs}%)")
        st.write(f"- **Provision Jackpot :** {part_jackpot:,.0f} € ({pct_jackpot_next}%)")

with t2:
    st.subheader("Probabilités & Payout")
    err_list = [0, 1, 2, 3]
    stats = []
    for e in err_list:
        p_indiv = binom.pmf(n_matchs - e, n_matchs, precision)
        n_gagnants = max(1, n_joueurs * p_indiv)
        stats.append({"err": e, "p": (1-(1-p_indiv)**n_joueurs)*100, "win": n_gagnants})

    c_p1, c_p2 = st.columns(2)
    with c_p1:
        fig_bar = go.Figure(go.Bar(x=[f"{s['err']} Err" for s in stats], y=[s['p'] for s in stats], 
                                   marker_color='#3b82f6', text=[f"{s['p']:.2f}%" for s in stats], textposition='auto'))
        fig_bar.update_layout(title="Chance d'avoir au moins 1 gagnant")
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_p2:
        st.write("### Gains par Gagnant (si pas de 0 faute)")
        for s in stats:
            gain_u = part_gains / s['win']
            st.info(f"🏆 **{s['err']} Erreur(s)** : {int(s['win']):,} gagnants espérés | Gain : **{gain_u:,.2f} €** / pers.")

with t3:
    st.subheader("Évolution Chronologique du Jackpot")
    nb_t = st.slider("Simuler sur nombre de tournois", 1, 15, 8)
    historique = [part_jackpot * i for i in range(nb_t + 1)]
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=list(range(nb_t + 1)), y=historique, mode='lines+markers+text', 
                                  name="Jackpot Cumulé", line=dict(color='#fbbf24', width=4)))
    fig_line.update_layout(xaxis_title="Numéro du Tournoi", yaxis_title="Valeur du Jackpot (€)", 
                          title=f"Croissance de la Réserve ({pct_jackpot_next}% par tournoi)")
    st.plotly_chart(fig_line, use_container_width=True)

with t4:
    st.subheader("Synthèse Stratégique")
    st.success(f"""
    **Rapport de Synthèse - {mode}**
    
    1. **Rentabilité Fixe** : L'entreprise génère **{part_entreprise:,.0f} €** de revenus bruts par tournoi, quel que soit le résultat sportif.
    2. **Stratégie de Rétention** : En redistribuant **{pct_gains_directs}%** ({part_gains:,.0f} €), vous assurez une satisfaction immédiate des joueurs.
    3. **Stratégie de Virilité (Jackpot)** : Vous épargnez **{part_jackpot:,.0f} €** par tournoi. Après {nb_t} tournois sans sans-faute, le jackpot affiché sera de **{part_jackpot * nb_t:,.0f} €**, créant un appel marketing massif.
    4. **Sécurité** : La probabilité qu'un joueur vide le jackpot (0 faute) sur ce format est de seulement **{stats[0]['p']:.6f}%**.
    """)
