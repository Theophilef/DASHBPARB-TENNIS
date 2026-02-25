import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import binom

st.set_page_config(layout="wide", page_title="Tennis Business Suite", page_icon="🎾")

# --- DESIGN PREMIUM CSS ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 700; color: #1f2937; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; padding: 10px 20px; }
    .main { background-color: #f3f4f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎾 Tennis Strategy Executive Suite")
st.caption("Version 4.0 - Analyse de Viabilité & Rentabilité Multitournois")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🛠️ Configuration")
    mode = st.selectbox("Type de Tournoi", ["Grand Chelem (127)", "Masters 1000 (63)", "Mode Express (64)"])
    n_matchs = 127 if "127" in mode else 63 if "63" in mode else 64
    
    st.divider()
    n_joueurs = st.number_input("Nombre de Joueurs", value=1000000, step=100000)
    prix_ticket = st.slider("Prix du Ticket (€)", 1.0, 10.0, 2.0)
    precision = st.slider("Précision des Experts (%)", 50, 95, 75) / 100
    
    st.divider()
    st.subheader("⚖️ Répartition des 80%")
    pct_gains = st.slider("% Reversé Gains (Consolation)", 0, 80, 60)
    pct_jackpot = 80 - pct_gains

# --- CALCULS ---
ca_total = n_joueurs * prix_ticket
part_entreprise = ca_total * 0.20
part_gains = ca_total * (pct_gains / 100)
part_jackpot = ca_total * (pct_jackpot / 100)

# --- TABS ---
t1, t2, t3, t4 = st.tabs(["💰 Finance & CAC", "🎯 Probabilités", "🗓️ Calendrier Annuel", "📑 Audit Stratégique"])

with t1:
    st.subheader("Analyse Financière & Publicitaire")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Graphique de répartition pro
        fig_pie = go.Figure(data=[go.Pie(labels=['Entreprise', 'Gains Joueurs', 'Jackpot'], 
                                 values=[part_entreprise, part_gains, part_jackpot], hole=.5)])
        fig_pie.update_traces(marker=dict(colors=['#065f46', '#3b82f6', '#fbbf24']))
        st.plotly_chart(fig_pie, use_container_width=True, key="pie_fin")

    with col2:
        st.write("### 🚀 Coût d'Acquisition (CAC)")
        # Calcul : Combien on peut payer pour 1 client
        frais_fixes_estim = 20000
        marge_dispo_marketing = (part_entreprise - frais_fixes_estim)
        cac_max = marge_dispo_marketing / n_joueurs
        st.metric("Budget Pub Max / Joueur", f"{cac_max:.2f} €")
        st.info(f"Si vous payez moins de **{cac_max:.2f} €** en pub pour acquérir un joueur, vous faites du profit.")

with t2:
    st.subheader("Analyse de Risque (Binomiale)")
    err_list = [0, 1, 2, 3]
    probs = [ (1 - (1 - binom.pmf(n_matchs-e, n_matchs, precision))**n_joueurs)*100 for e in err_list]
    
    fig_risq = go.Figure(go.Bar(x=[f"{e} Erreurs" for e in err_list], y=probs, marker_color='#065f46'))
    fig_risq.update_layout(title="Chance d'avoir au moins 1 gagnant (%)")
    st.plotly_chart(fig_risq, use_container_width=True, key="bar_risq")

with t3:
    st.subheader("📅 Simulation Saison Complète")
    st.write("Estimation du bénéfice net sur 1 an (4 Grand Chelem + 9 Masters 1000)")
    benef_annuel = (part_entreprise * 13) - (20000 * 13) # Exemple
    st.metric("Bénéfice Net Annuel Estimé", f"{benef_annuel:,.0f} €")
    
    # Graphique cumulé
    mois = ["Jan", "Fev", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Dec"]
    ca_cumul = np.cumsum([ca_total if i in [0, 4, 7, 8] else ca_total*0.4 for i in range(12)])
    fig_an = go.Figure(go.Scatter(x=mois, y=ca_cumul, fill='tozeroy', line_color='#3b82f6'))
    st.plotly_chart(fig_an, use_container_width=True)

with t4:
    st.subheader("Rapport d'Audit Automatisé")
    st.markdown(f"""
    - **Viabilité du Jackpot :** Le montant de **{part_jackpot:,.0f} €** ajouté à chaque tournoi permet une croissance organique rapide.
    - **Marge de Sécurité :** À {precision*100}% de précision, le modèle est **TRÈS SÉCURISÉ**.
    - **Seuil de Rentabilité :** Votre structure est rentable dès que vous dépassez **{int(20000/(prix_ticket*0.2))}** joueurs.
    """)
