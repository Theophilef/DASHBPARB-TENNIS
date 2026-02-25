import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import binom

st.set_page_config(layout="wide", page_title="Tennis Prediction Pro", page_icon="🎾")

st.title("🎾 Dashboard Stratégique Pro : Pari Mutuel Tennis")
st.markdown("Modèle d'affaires : **20% fixes pour l'entreprise**. Si 0 faute : **80% aux gagnants**. Sinon : **60% en consolation et 20% au Jackpot**.")

# --- ONGLETS POUR LES FORMATS ---
tab_gc, tab_m1000, tab_express = st.tabs(["🏆 Grand Chelem (127)", "🎾 Masters 1000 (63)", "⚡ 1er Tour de GC (64)"])

def render_dashboard(n_matchs, nom_format):
    st.header(f"Analyse Stratégique : {nom_format}")
    
    # --- CURSEURS DE PARAMÉTRAGE ---
    st.subheader("⚙️ Paramètres de la simulation")
    c_input1, c_input2, c_input3, c_input4 = st.columns(4)
    n_joueurs = c_input1.number_input(f"Nombre de Joueurs", min_value=1000, value=1000000, step=50000, key=f"j_{n_matchs}")
    prix_ticket = c_input2.number_input(f"Prix du Ticket (€)", min_value=1.0, value=2.0, step=0.5, key=f"t_{n_matchs}")
    precision = c_input3.slider(f"Précision moyenne (%)", 50, 95, 75, key=f"p_{n_matchs}") / 100
    
    c_frais1, c_frais2 = st.columns(2)
    frais_fixes = c_frais1.number_input("Frais fixes (€) (Salaires, Marketing...)", value=25000, step=5000, key=f"f_{n_matchs}")
    pct_taxes = c_frais2.slider("Impôts/Frais (en % des 20% entreprise)", 0, 80, 45, key=f"tax_{n_matchs}") / 100

    # --- CALCULS FINANCIERS ---
    ca_total = n_joueurs * prix_ticket
    part_entreprise_brute = ca_total * 0.20
    montant_taxes_frais = part_entreprise_brute * pct_taxes
    benefice_net = part_entreprise_brute - montant_taxes_frais - frais_fixes
    
    pot_0_faute = ca_total * 0.80
    pot_consolation = ca_total * 0.60
    pot_jackpot = ca_total * 0.20

    marge_nette_par_ticket = prix_ticket * 0.20 * (1 - pct_taxes)
    seuil_joueurs = frais_fixes / marge_nette_par_ticket if marge_nette_par_ticket > 0 else 0

    # --- CALCULS DES PROBABILITÉS ---
    erreurs_cibles = [0, 1, 2, 3]
    probs_au_moins_un = []
    esperance_gagnants = []
    
    for k in erreurs_cibles:
        p_indiv = binom.pmf(n_matchs - k, n_matchs, precision)
        p_au_moins_un = 1 - (1 - p_indiv)**n_joueurs
        probs_au_moins_un.append(p_au_moins_un)
        esperance_gagnants.append(n_joueurs * p_indiv)

    proba_0_faute = probs_au_moins_un[0]
    if proba_0_faute > 0.5:
        scenario_actuel = "Scénario A (0 Erreur trouvée : Distribution 80%)"
    else:
        scenario_actuel = "Scénario B (Aucun 0 Erreur : Consolation 60% + Jackpot 20%)"

    # --- AFFICHAGE DES KPIS ---
    st.markdown("---")
    st.markdown(f"### 💰 Chiffres Clés de l'Entreprise")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Chiffre d'Affaires (CA)", f"{ca_total:,.0f} €")
    kpi2.metric("Part Entreprise Brute (20%)", f"{part_entreprise_brute:,.0f} €")
    kpi3.metric("Bénéfice Net", f"{benefice_net:,.0f} €", delta=f"{benefice_net/ca_total*100:.1f}% Marge Nette")
    kpi4.metric("Seuil Rentabilité (Joueurs)", f"{int(seuil_joueurs):,} joueurs", delta="Pour être à 0€ de perte", delta_color="off")

    # --- AFFICHAGE DES GRAPHIQUES ---
    st.markdown("---")
    c_graph1, c_graph2 = st.columns(2)

    with c_graph1:
        st.markdown("### 🎯 Focus : Probabilité d'avoir des gagnants")
        fig_prob = go.Figure()
        fig_prob.add_trace(go.Bar(
            x=[f"{e} erreur(s)" for e in erreurs_cibles], 
            y=[p * 100 for p in probs_au_moins_un],
            text=[f"{p*100:.2f}%<br>({int(esp)} gagnants espérés)" for p, esp in zip(probs_au_moins_un, esperance_gagnants)],
            textposition='auto',
            marker_color=['#27ae60', '#f1c40f', '#e67e22', '#e74c3c']
        ))
        fig_prob.update_layout(yaxis_title="% de chance", showlegend=False)
        # LA CORRECTION EST ICI (ajout du key)
        st.plotly_chart(fig_prob, use_container_width=True, key=f"bar_{n_matchs}")

    with c_graph2:
        st.markdown(f"### 🍰 Répartition Réelle de l'Argent")
        st.write(f"Scénario actuel : **{scenario_actuel}**")
        
        if proba_0_faute > 0.05:
            labels = ['Gagnants 0 Faute (80%)', 'Taxes & Frais', 'Bénéfice Net']
            values = [pot_0_faute, montant_taxes_frais + frais_fixes, benefice_net]
            colors = ['#3498db', '#95a5a6', '#2ecc71']
        else:
            labels = ['Joueurs Consolation (60%)', 'Jackpot Futur (20%)', 'Taxes & Frais', 'Bénéfice Net']
            values = [pot_consolation, pot_jackpot, montant_taxes_frais + frais_fixes, benefice_net]
            colors = ['#9b59b6', '#f1c40f', '#95a5a6', '#2ecc71']

        fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4, marker_colors=colors)])
        # LA CORRECTION EST ICI (ajout du key)
        st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_{n_matchs}")

    st.success(f"**Payout & Rentabilité :** Sur {ca_total:,.0f} €, l'entreprise prend **{part_entreprise_brute:,.0f} €**. "
             f"Après {montant_taxes_frais:,.0f} € de taxes et {frais_fixes:,.0f} € de coûts fixes, "
             f"le bénéfice net est de **{benefice_net:,.0f} €**. "
             f"Si 0 faute : **{pot_0_faute:,.0f} €** au vainqueur. Sinon : consolation de **{pot_consolation:,.0f} €** et jackpot de **{pot_jackpot:,.0f} €** épargné.")

with tab_gc: render_dashboard(127, "Tableau Complet Grand Chelem (127 matchs)")
with tab_m1000: render_dashboard(63, "Tableau Complet Masters 1000 (63 matchs)")
with tab_express: render_dashboard(64, "Prédictions des 1ers Tours (64 matchs)")
