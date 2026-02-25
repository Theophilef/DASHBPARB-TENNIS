import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import binom

st.set_page_config(layout="wide", page_title="Tennis Prediction Pro", page_icon="🎾")

# --- STYLE PERSONNALISÉ ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🎾 Tennis Prediction Pro : Simulateur de Saison")
st.markdown("Structure : **20% fixes Entreprise** | Répartition du reste modulable.")

# --- ONGLETS ---
tab_gc, tab_m1000, tab_express = st.tabs(["🏆 Grand Chelem (127)", "🎾 Masters 1000 (63)", "⚡ 1er Tour de GC (64)"])

def render_dashboard(n_matchs, nom_format):
    # --- BARRE LATÉRALE DE CONTRÔLE GÉNÉRAL ---
    with st.sidebar:
        st.header(f"🕹️ Contrôles {nom_format}")
        n_joueurs = st.number_input(f"Nombre de Joueurs", min_value=1000, value=1000000, step=100000, key=f"j_{n_matchs}")
        prix_ticket = st.number_input(f"Prix du Ticket (€)", min_value=1.0, value=2.0, step=0.5, key=f"t_{n_matchs}")
        precision = st.slider(f"Précision des Joueurs (%)", 50, 95, 75, key=f"p_{n_matchs}") / 100
        
        st.divider()
        st.subheader("💰 Stratégie de Redistribution")
        st.caption("Si aucun gagnant à 0 faute :")
        pct_joueurs = st.slider("Part Consolation aux joueurs (%)", 0, 80, 60, key=f"pj_{n_matchs}")
        pct_jackpot_input = st.slider("Part Réinvestissement Jackpot (%)", 0, 80, 20, key=f"pjk_{n_matchs}")
        
        st.divider()
        st.subheader("📈 Paramètres de Croissance")
        jackpot_initial = st.number_input("Jackpot de départ (€)", value=0, key=f"ji_{n_matchs}")
        tournois_sim = st.slider("Simuler sur X tournois", 1, 20, 10, key=f"sim_{n_matchs}")

    # --- CALCULS ---
    ca_total = n_joueurs * prix_ticket
    part_entreprise_brute = ca_total * 0.20
    apport_jackpot_actuel = ca_total * (pct_jackpot_input / 100)
    pot_consolation = ca_total * (pct_joueurs / 100)
    
    # Proba 0 faute
    p_0 = binom.pmf(n_matchs, n_matchs, precision)
    chance_gagnant_0 = 1 - (1 - p_0)**n_joueurs

    # --- AFFICHAGE DES CHIFFRES CLÉS ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CA par Tournoi", f"{ca_total:,.0f} €")
    c2.metric("Marge Entreprise", f"{part_entreprise_brute:,.0f} €")
    c3.metric("Apport Jackpot/Tour", f"{apport_jackpot_actuel:,.0f} €")
    c4.metric("Sécurité Jackpot", f"{(1-chance_gagnant_0)*100:.4f}%")

    # --- GRAPHIQUE D'ÉVOLUTION DU JACKPOT ---
    st.subheader("📈 Projection de croissance du Jackpot")
    steps = np.arange(tournois_sim + 1)
    evol_jackpot = jackpot_initial + (apport_jackpot_actuel * steps)
    
    fig_evol = go.Figure()
    fig_evol.add_trace(go.Scatter(x=steps, y=evol_jackpot, mode='lines+markers', line=dict(color='#2ecc71', width=3), name="Jackpot cumulé"))
    fig_evol.update_layout(xaxis_title="Nombre de tournois sans gagnant 0 faute", yaxis_title="Montant du Jackpot (€)", height=400)
    st.plotly_chart(fig_evol, use_container_width=True, key=f"evol_{n_matchs}")

    # --- RÉPARTITION ET PROBABILITÉS ---
    st.divider()
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🎯 Probabilités de Gains")
        erreurs = [0, 1, 2, 3]
        probs = [(1 - (1 - binom.pmf(n_matchs - e, n_matchs, precision))**n_joueurs)*100 for e in erreurs]
        fig_bar = go.Figure(go.Bar(x=[f"{e} Erreurs" for e in erreurs], y=probs, marker_color='#3498db'))
        fig_bar.update_layout(yaxis_title="% de chance d'avoir un gagnant", height=350)
        st.plotly_chart(fig_bar, use_container_width=True, key=f"bar_{n_matchs}")

    with col_b:
        st.subheader("🍰 Répartition du Cash")
        labels = ['Part Entreprise', 'Part Joueurs (Consolation)', 'Réinvestissement Jackpot']
        values = [20, pct_joueurs, pct_jackpot_input]
        fig_pie = go.Figure(go.Pie(labels=labels, values=values, hole=.4))
        fig_pie.update_layout(height=350)
        st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_{n_matchs}")

# Rendu des onglets
with tab_gc: render_dashboard(127, "Grand Chelem")
with tab_m1000: render_dashboard(63, "Masters 1000")
with tab_express: render_dashboard(64, "1er Tour Express")
