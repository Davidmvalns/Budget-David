import streamlit as st
import pandas as pd
import os
import calendar
import json
import altair as alt
from datetime import datetime

# Désactiver la limite de 5000 lignes pour les graphiques Altair
alt.data_transformers.disable_max_rows()

# ==========================================
# 1. GESTION DES DONNÉES (Fichiers CSV et TXT)
# ==========================================
CSV_FILE = "historique_budget.csv"
CATEGORIES_FILE = "categories.txt"
CHARGES_FILE = "mes_charges_fixes.csv"
EPARGNES_FILE = "epargnes_fixes.csv"
PARAMETRES_FILE = "parametres.json"

# Les catégories par défaut lors du premier lancement
CATEGORIES_DEFAUT = [
    "Essence", "Courses", "Jeux", "Resto", "Amazon", "Bricolage", 
    "Livre", "Médicale", "Cash", "Électricité", "Cadeaux", "fdj / paris", 
    "Perisco", "Couteaux", "Film", "Divers", "Tristan", "Epargnes"
]

# Les charges fixes issues de ta copie d'écran
CHARGES_DEFAUT = [
    {"nom": "Assurances (maison/ voitures/ accident de la vie)", "montant": 133.35},
    {"nom": "Sfr (box / tel val)", "montant": 41.98},
    {"nom": "Free", "montant": 14.99},
    {"nom": "Credit maison", "montant": 848.81},
    {"nom": "Credit 208", "montant": 178.53},
    {"nom": "Électricité", "montant": 110.00},
    {"nom": "Eau", "montant": 40.00},
    {"nom": "Frais bancaire", "montant": 17.50},
    {"nom": "Canal +", "montant": 22.90},
    {"nom": "Netflix", "montant": 13.49},
    {"nom": "Apple", "montant": 0.99},
    {"nom": "Spotify", "montant": 14.99},
    {"nom": "Frais cantine val", "montant": 70.00},
    {"nom": "Impôts", "montant": 125.00}
]

# Les épargnes fixes par défaut
EPARGNES_DEFAUT = [
    {"nom": "Livret A", "montant": 100.00},
    {"nom": "Assurance Vie", "montant": 50.00}
]

# Liste des mois en français
MOIS_FR = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
]

def charger_categories():
    if not os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
            for c in CATEGORIES_DEFAUT:
                f.write(c + "\n")
    with open(CATEGORIES_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def ajouter_categorie(nouvelle_cat):
    cats = charger_categories()
    if nouvelle_cat not in cats:
        with open(CATEGORIES_FILE, "a", encoding="utf-8") as f:
            f.write(nouvelle_cat + "\n")

def init_db():
    charger_categories()
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["id", "date_transaction", "mois", "semaine", "categorie", "montant", "description"])
        df.to_csv(CSV_FILE, index=False)
    else:
        df = pd.read_csv(CSV_FILE)
        if "mois" not in df.columns:
            df.insert(2, "mois", "Mars 2024") 
            df.to_csv(CSV_FILE, index=False)
            
    if not os.path.exists(CHARGES_FILE):
        df_charges = pd.DataFrame(CHARGES_DEFAUT)
        df_charges.to_csv(CHARGES_FILE, index=False)

    if not os.path.exists(EPARGNES_FILE):
        df_epargnes = pd.DataFrame(EPARGNES_DEFAUT)
        df_epargnes.to_csv(EPARGNES_FILE, index=False)

# --- FONCTIONS LECTURE ROBUSTE ---
def _lire_csv_securise(chemin_fichier):
    if not os.path.exists(chemin_fichier):
        return pd.DataFrame()
    df = pd.read_csv(chemin_fichier)
    if not df.empty and "montant" in df.columns:
        if df['montant'].dtype == object:
            df['montant'] = df['montant'].astype(str).str.replace(',', '.')
        df['montant'] = pd.to_numeric(df['montant'], errors='coerce').fillna(0.0)
    return df

def get_all_transactions(): return _lire_csv_securise(CSV_FILE)
def get_all_charges(): return _lire_csv_securise(CHARGES_FILE)
def get_all_epargnes(): return _lire_csv_securise(EPARGNES_FILE)

def add_transaction(mois, semaine, categorie, montant, description):
    df = get_all_transactions()
    new_id = 1 if df.empty else df["id"].max() + 1
    date_jour = datetime.now().strftime("%d/%m/%Y %H:%M")
    nouvelle_ligne = pd.DataFrame([{"id": new_id, "date_transaction": date_jour, "mois": mois, "semaine": semaine, "categorie": categorie, "montant": float(montant), "description": description}])
    df = pd.concat([df, nouvelle_ligne], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def delete_transaction(transaction_id):
    df = get_all_transactions()
    df = df[df["id"] != transaction_id]
    df.to_csv(CSV_FILE, index=False)

def add_charge(nom, montant):
    df = get_all_charges()
    nouvelle_ligne = pd.DataFrame([{"nom": nom, "montant": float(montant)}])
    df = pd.concat([df, nouvelle_ligne], ignore_index=True)
    df.to_csv(CHARGES_FILE, index=False)

def update_charge(old_nom, new_nom, new_montant):
    df = get_all_charges()
    if old_nom in df['nom'].values:
        idx = df[df['nom'] == old_nom].index
        df.loc[idx, 'nom'] = new_nom
        df.loc[idx, 'montant'] = float(new_montant)
        df.to_csv(CHARGES_FILE, index=False)

def delete_charge(nom):
    df = get_all_charges()
    df = df[df["nom"] != nom]
    df.to_csv(CHARGES_FILE, index=False)

def add_epargne(nom, montant):
    df = get_all_epargnes()
    nouvelle_ligne = pd.DataFrame([{"nom": nom, "montant": float(montant)}])
    df = pd.concat([df, nouvelle_ligne], ignore_index=True)
    df.to_csv(EPARGNES_FILE, index=False)

def update_epargne(old_nom, new_nom, new_montant):
    df = get_all_epargnes()
    if old_nom in df['nom'].values:
        idx = df[df['nom'] == old_nom].index
        df.loc[idx, 'nom'] = new_nom
        df.loc[idx, 'montant'] = float(new_montant)
        df.to_csv(EPARGNES_FILE, index=False)

def delete_epargne(nom):
    df = get_all_epargnes()
    df = df[df["nom"] != nom]
    df.to_csv(EPARGNES_FILE, index=False)

def charger_parametres():
    if not os.path.exists(PARAMETRES_FILE):
        return {}
    with open(PARAMETRES_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {}

def sauvegarder_parametres(params):
    with open(PARAMETRES_FILE, "w", encoding="utf-8") as f:
        json.dump(params, f, indent=4)


# ==========================================
# 2. INTERFACE & MOTEUR DE CALCUL
# ==========================================

st.set_page_config(page_title="Mon Budget", page_icon="💰", layout="wide")
init_db()

st.title("💰 Suivi de mon Budget")

# --- GESTION DES PARAMÈTRES ---
st.sidebar.header("⚙️ Paramètres du mois")
annee_actuelle = datetime.now().year
annees_disponibles = list(range(2024, annee_actuelle + 5))

col1, col2 = st.sidebar.columns(2)
with col1: mois_selectionne = st.selectbox("Mois", MOIS_FR, index=datetime.now().month - 1)
with col2: 
    index_annee = annees_disponibles.index(annee_actuelle) if annee_actuelle in annees_disponibles else 0
    annee_selectionnee = st.selectbox("Année", annees_disponibles, index=index_annee)
mois_choisi = f"{mois_selectionne} {annee_selectionnee}"

st.sidebar.markdown("---")
st.sidebar.header("💰 Revenus & Budgets")
params_globaux = charger_parametres()
params_mois = params_globaux.get(mois_choisi, {})

if "revenus" not in params_mois and params_globaux:
    dernier_mois = list(params_globaux.keys())[-1]
    revenus_defaut = params_globaux[dernier_mois].get("revenus", 2434.0)
else:
    revenus_defaut = params_mois.get("revenus", 2434.0)

REVENUS = st.sidebar.number_input("Revenus du mois (€)", min_value=0.0, value=float(revenus_defaut), step=100.0)

mois_int = MOIS_FR.index(mois_selectionne) + 1
cal = calendar.monthcalendar(annee_selectionnee, mois_int)
nbr_mercredis = sum(1 for week in cal if week[2] != 0)
semaines_auto = max(4, min(nbr_mercredis, 5))

NOMBRE_SEMAINES = st.sidebar.slider("Nombre de semaines ce mois-ci", 4, 5, semaines_auto)
st.sidebar.caption(f"🤖 {semaines_auto} semaines détectées pour {mois_selectionne}.")

st.sidebar.markdown("#### 🎯 Budgets et Épargne par semaine")
budgets_hebdo = {}
choix_restes = {}
budget_mensuel_total = 0.0

for i in range(1, NOMBRE_SEMAINES + 1):
    nom_semaine = f"S {i}"
    b_defaut = params_mois.get("budgets_hebdo", {}).get(nom_semaine, 200.0)
    b = st.sidebar.number_input(f"Budget {nom_semaine} (€)", min_value=0.0, value=float(b_defaut), step=10.0, key=f"budget_{nom_semaine}")
    c_defaut = params_mois.get("choix_restes", {}).get(nom_semaine, "Reporter")
    index_choix = 0 if c_defaut == "Reporter" else 1
    choix = st.sidebar.radio(f"Si reste positif fin {nom_semaine} :", ["Reporter", "Épargner"], index=index_choix, key=f"choix_reste_{nom_semaine}", horizontal=True)
    
    budgets_hebdo[nom_semaine] = b
    choix_restes[nom_semaine] = choix
    budget_mensuel_total += b
    st.sidebar.markdown("---")

params_globaux[mois_choisi] = {"revenus": REVENUS, "budgets_hebdo": budgets_hebdo, "choix_restes": choix_restes}
sauvegarder_parametres(params_globaux)
BUDGET_MENSUEL = budget_mensuel_total
st.sidebar.info(f"💡 Budget Mensuel Alloué : **{BUDGET_MENSUEL:.2f} €**")

# --- ZONE DE SAISIE ---
st.sidebar.header("➕ Nouvelle Dépense")
with st.sidebar.form("ajout_depense", clear_on_submit=True):
    semaine_choisie = st.selectbox("Semaine", [f"S {i}" for i in range(1, NOMBRE_SEMAINES + 1)])
    liste_categories = charger_categories()
    categorie_choisie = st.selectbox("Catégorie existante", liste_categories)
    nouvelle_categorie = st.text_input("➕ Ou créer une catégorie :", placeholder="Ex: Vêtements")
    montant_saisi = st.number_input("Montant (€)", min_value=0.01, format="%.2f", step=1.0)
    desc_saisie = st.text_input("Description (Optionnel)")
    if st.form_submit_button("Ajouter"):
        cat_finale = nouvelle_categorie.strip().capitalize() if nouvelle_categorie.strip() else categorie_choisie
        if nouvelle_categorie.strip(): ajouter_categorie(cat_finale)
        add_transaction(mois_choisi, semaine_choisie, cat_finale, montant_saisi, desc_saisie)
        st.success(f"{montant_saisi}€ ajoutés dans {cat_finale} ({semaine_choisie})")
        st.rerun()

# ==========================================
# 3. MOTEUR DE CALCUL (Avant affichage)
# ==========================================
df_charges = get_all_charges()
total_charges_fixes = df_charges['montant'].sum() if not df_charges.empty else 0.0

df_epargnes = get_all_epargnes()
total_epargnes_fixes = df_epargnes['montant'].sum() if not df_epargnes.empty else 0.0

df_transactions = get_all_transactions()
if not df_transactions.empty: df_transactions['montant'] = pd.to_numeric(df_transactions['montant'], errors='coerce')
df_mois = df_transactions[df_transactions["mois"] == mois_choisi] if not df_transactions.empty else pd.DataFrame()

semaines_possibles = [f"S {i}" for i in range(1, NOMBRE_SEMAINES + 1)]
reports = pd.Series(0.0, index=semaines_possibles)
epargnes_semaine = pd.Series(0.0, index=semaines_possibles)
restes = pd.Series(0.0, index=semaines_possibles)

if not df_mois.empty:
    tableau_recap = pd.pivot_table(df_mois, values='montant', index=['categorie'], columns=['semaine'], aggfunc='sum', fill_value=0)
    for s in semaines_possibles:
        if s not in tableau_recap.columns: tableau_recap[s] = 0.0
    tableau_recap = tableau_recap[semaines_possibles]
    totaux_semaine = tableau_recap.sum()
else:
    totaux_semaine = pd.Series(0.0, index=semaines_possibles)

report_actuel = 0.0
for s in semaines_possibles:
    reports[s] = report_actuel
    budget_total_semaine = budgets_hebdo.get(s, 200.0) + report_actuel
    reste_brut = budget_total_semaine - totaux_semaine[s]
    
    if reste_brut > 0 and choix_restes.get(s) == "Épargner":
        epargnes_semaine[s] = reste_brut
        restes[s] = 0.0
        report_actuel = 0.0
    else:
        epargnes_semaine[s] = 0.0
        restes[s] = reste_brut
        report_actuel = reste_brut

depense_mensuelle = df_mois['montant'].sum() if not df_mois.empty else 0
total_epargne_ponctuelle = epargnes_semaine.sum()
total_epargne_global = total_epargnes_fixes + total_epargne_ponctuelle
marge_non_allouee = REVENUS - total_charges_fixes - total_epargnes_fixes - BUDGET_MENSUEL
reste_mensuel = BUDGET_MENSUEL - depense_mensuelle - total_epargne_ponctuelle

# ==========================================
# 4. AFFICHAGE DES ÉLÉMENTS UI
# ==========================================
col_exp_1, col_exp_2 = st.columns(2)

with col_exp_1:
    with st.expander(f"🏠 Voir et modifier mes Charges Fixes ({total_charges_fixes:.2f} €)", expanded=False):
        col_c1, col_c2 = st.columns([1.2, 1])
        with col_c1: st.dataframe(df_charges.style.format({"montant": "{:.2f} €"}), use_container_width=True, hide_index=True)
        with col_c2:
            tc1, tc2, tc3 = st.tabs(["➕", "✏️", "🗑️"])
            with tc1:
                with st.form("ajout_charge"):
                    nc = st.text_input("Nom")
                    mc = st.number_input("Montant (€)", min_value=0.01, step=1.0)
                    if st.form_submit_button("Ajouter") and nc: add_charge(nc, mc); st.rerun()
            with tc2:
                cam = st.selectbox("Modifier :", df_charges['nom'].tolist() if not df_charges.empty else [])
                if cam:
                    cac = df_charges[df_charges['nom'] == cam]['montant'].values[0]
                    nnc = st.text_input("Nom", value=cam)
                    nmc = st.number_input("Montant (€)", value=float(cac), step=1.0)
                    if st.button("Enregistrer", key="bs_c"): update_charge(cam, nnc, nmc); st.rerun()
            with tc3:
                cas = st.selectbox("Supprimer :", df_charges['nom'].tolist() if not df_charges.empty else [])
                if st.button("Confirmer", key="bd_c") and cas: delete_charge(cas); st.rerun()

with col_exp_2:
    with st.expander(f"🏦 Voir et modifier mes Épargnes Fixes ({total_epargnes_fixes:.2f} €)", expanded=False):
        col_e1, col_e2 = st.columns([1.2, 1])
        with col_e1: st.dataframe(df_epargnes.style.format({"montant": "{:.2f} €"}), use_container_width=True, hide_index=True)
        with col_e2:
            te1, te2, te3 = st.tabs(["➕", "✏️", "🗑️"])
            with te1:
                with st.form("ajout_epargne"):
                    ne = st.text_input("Nom")
                    me = st.number_input("Montant (€)", min_value=0.01, step=1.0)
                    if st.form_submit_button("Ajouter") and ne: add_epargne(ne, me); st.rerun()
            with te2:
                eam = st.selectbox("Modifier :", df_epargnes['nom'].tolist() if not df_epargnes.empty else [])
                if eam:
                    cae = df_epargnes[df_epargnes['nom'] == eam]['montant'].values[0]
                    nne = st.text_input("Nom", value=eam)
                    nme = st.number_input("Montant (€)", value=float(cae), step=1.0)
                    if st.button("Enregistrer", key="bs_e"): update_epargne(eam, nne, nme); st.rerun()
            with te3:
                eas = st.selectbox("Supprimer :", df_epargnes['nom'].tolist() if not df_epargnes.empty else [])
                if st.button("Confirmer", key="bd_e") and eas: delete_epargne(eas); st.rerun()

# --- MODULE STATISTIQUES & ANALYSES EXPERT ---
with st.expander("📈 Voir mes Statistiques et Analyses (Inclus Projections Épargne)", expanded=False):
    if df_transactions.empty:
        st.info("Aucune donnée enregistrée pour le moment. Reviens plus tard !")
    else:
        tab_mois, tab_global, tab_evo, tab_epargne, tab_sante = st.tabs([
            "📅 Ce mois-ci", "🏆 Catégories", "📈 Évolution", "🏦 Épargnes & Projections", "⚖️ Santé Financière"
        ])
        
        # --- TAB 1 : CE MOIS-CI ---
        with tab_mois:
            if df_mois.empty: st.info("Pas de dépenses ce mois.")
            else:
                sem_data = df_mois.groupby("semaine")["montant"].sum().reset_index()
                sem_data['label'] = sem_data['montant'].apply(lambda x: f"{x:.0f} €")
                cat_data_mois = df_mois.groupby("categorie")["montant"].sum().reset_index()
                cat_data_mois['label'] = cat_data_mois['montant'].apply(lambda x: f"{x:.0f} €")
                
                c_stat1, c_stat2 = st.columns(2)
                with c_stat1:
                    st.markdown("<h6 style='text-align: center;'>Dépenses par Semaine</h6>", unsafe_allow_html=True)
                    bars_sem = alt.Chart(sem_data).mark_bar(color="#3b82f6", cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
                        x=alt.X("semaine", title=None, sort=None, axis=alt.Axis(labelAngle=0)),
                        y=alt.Y("montant", title=None, axis=alt.Axis(grid=False, labels=False)),
                        tooltip=["semaine", "montant"]
                    )
                    text_sem = bars_sem.mark_text(align='center', baseline='bottom', dy=-5, fontSize=13, fontWeight='bold', color='gray').encode(text='label')
                    st.altair_chart((bars_sem + text_sem).properties(height=300).configure_view(strokeWidth=0), use_container_width=True)
                
                with c_stat2:
                    st.markdown("<h6 style='text-align: center;'>Répartition par Catégorie</h6>", unsafe_allow_html=True)
                    base_donut = alt.Chart(cat_data_mois).encode(
                        theta=alt.Theta("montant:Q"),
                        color=alt.Color("categorie:N", scale=alt.Scale(scheme='tableau20'), legend=alt.Legend(title=None, orient="bottom")),
                        tooltip=["categorie", "montant"]
                    )
                    arc_donut = base_donut.mark_arc(innerRadius=60, stroke="#fff", strokeWidth=2)
                    text_donut = base_donut.mark_text(radius=95, fontSize=12, fontWeight='bold').encode(text='label')
                    st.altair_chart((arc_donut + text_donut).properties(height=320).configure_view(strokeWidth=0), use_container_width=True)

        # --- TAB 2 : GLOBAL ---
        with tab_global:
            cat_global = df_transactions.groupby("categorie")["montant"].sum().reset_index().sort_values(by="montant", ascending=False)
            cat_global['label'] = cat_global['montant'].apply(lambda x: f"{x:.0f} €")
            st.markdown(f"<div style='text-align: center; color: gray;'>Total historique : <b>{cat_global['montant'].sum():.2f} €</b></div><br>", unsafe_allow_html=True)

            bars_glob = alt.Chart(cat_global).mark_bar(color="#10b981", cornerRadiusEnd=5).encode(
                x=alt.X("montant", title=None, axis=alt.Axis(grid=False, labels=False)), 
                y=alt.Y("categorie", sort="-x", title=None, axis=alt.Axis(labelFontSize=12)),
                tooltip=["categorie", "montant"]
            )
            text_glob = bars_glob.mark_text(align='left', baseline='middle', dx=5, fontSize=13, fontWeight='bold', color='gray').encode(text='label')
            st.altair_chart((bars_glob + text_glob).properties(width='container', height=max(300, len(cat_global)*35)).configure_view(strokeWidth=0), use_container_width=True)

        # --- TAB 3 : ÉVOLUTION ---
        with tab_evo:
            def parse_to_date(m_str):
                try:
                    m, y = str(m_str).split(" ")
                    return f"{y}-{MOIS_FR.index(m)+1:02d}-01"
                except: return "2000-01-01"
            df_evo = df_transactions.copy()
            df_evo['date_tri'] = df_evo['mois'].apply(parse_to_date)
            evo_data = df_evo.groupby(["date_tri", "mois"])["montant"].sum().reset_index().sort_values("date_tri")
            evo_data['label'] = evo_data['montant'].apply(lambda x: f"{x:.0f} €")
            
            base_evo = alt.Chart(evo_data).encode(
                x=alt.X("mois", sort=alt.EncodingSortField(field="date_tri", order="ascending"), title=None, axis=alt.Axis(labelAngle=-45, grid=False)),
                y=alt.Y("montant", title=None, axis=alt.Axis(grid=True, gridColor="#f3f4f6", labels=False)),
                tooltip=["mois", "montant"]
            )
            area_evo = base_evo.mark_area(color=alt.Gradient(gradient='linear', stops=[alt.GradientStop(color='rgba(239, 68, 68, 0.5)', offset=0), alt.GradientStop(color='rgba(239, 68, 68, 0.0)', offset=1)], x1=1, y1=1, x2=1, y2=0))
            line_evo = base_evo.mark_line(color="#ef4444", strokeWidth=3)
            points_evo = base_evo.mark_circle(size=80, color="#ef4444", opacity=1)
            text_evo = base_evo.mark_text(align='center', baseline='bottom', dy=-10, fontSize=13, fontWeight='bold', color='gray').encode(text='label')
            st.altair_chart((area_evo + line_evo + points_evo + text_evo).properties(height=350).configure_view(strokeWidth=0), use_container_width=True)

        # --- TAB 4 : EPARGNES ET PROJECTIONS (NOUVEAU) ---
        with tab_epargne:
            st.markdown("<h5 style='text-align: center;'>La Magie des Intérêts Composés 🪄</h5>", unsafe_allow_html=True)
            st.write(f"Ce mois-ci, tu as réussi à mettre de côté **{total_epargne_global:.2f} €** ({total_epargnes_fixes:.2f} € en fixe et {total_epargne_ponctuelle:.2f} € via tes restes de semaines).")
            
            epargne_annuelle = total_epargne_global * 12
            taux_interet = 0.03 # Taux moyen Livret A / LDDS
            
            proj_data = []
            capital_simple = 0
            capital_compose = 0
            for annee in range(0, 11):
                if annee == 0:
                    proj_data.append({"Année": annee, "Type": "Sans intérêts (Compte Courant)", "Montant": 0})
                    proj_data.append({"Année": annee, "Type": "Placé à 3% (Livret A, etc.)", "Montant": 0})
                else:
                    capital_simple += epargne_annuelle
                    capital_compose = (capital_compose + epargne_annuelle) * (1 + taux_interet)
                    proj_data.append({"Année": annee, "Type": "Sans intérêts (Compte Courant)", "Montant": capital_simple})
                    proj_data.append({"Année": annee, "Type": "Placé à 3% (Livret A, etc.)", "Montant": capital_compose})
                    
            df_proj = pd.DataFrame(proj_data)
            
            c_p1, c_p2, c_p3 = st.columns(3)
            val_1an = df_proj[(df_proj['Année'] == 1) & (df_proj['Type'] == 'Placé à 3% (Livret A, etc.)')]['Montant'].values[0]
            val_5ans = df_proj[(df_proj['Année'] == 5) & (df_proj['Type'] == 'Placé à 3% (Livret A, etc.)')]['Montant'].values[0]
            val_10ans = df_proj[(df_proj['Année'] == 10) & (df_proj['Type'] == 'Placé à 3% (Livret A, etc.)')]['Montant'].values[0]
            
            c_p1.metric("Projection 1 an", f"{val_1an:,.0f} €".replace(',', ' '))
            c_p2.metric("Projection 5 ans", f"{val_5ans:,.0f} €".replace(',', ' '))
            c_p3.metric("Projection 10 ans", f"{val_10ans:,.0f} €".replace(',', ' '))
            
            st.markdown("<br><h6 style='text-align: center;'>Projection de ton capital sur 10 ans</h6>", unsafe_allow_html=True)
            chart_proj = alt.Chart(df_proj).mark_line(point=True, strokeWidth=3).encode(
                x=alt.X("Année:O", title="Années"),
                y=alt.Y("Montant:Q", title="Capital cumulé (€)"),
                color=alt.Color("Type:N", legend=alt.Legend(title="Stratégie", orient="top-left")),
                tooltip=[alt.Tooltip("Année", title="Dans X années"), alt.Tooltip("Type", title="Stratégie"), alt.Tooltip("Montant", title="Capital (€)", format=",.0f")]
            ).properties(height=350).configure_view(strokeWidth=0)
            st.altair_chart(chart_proj, use_container_width=True)

        # --- TAB 5 : SANTE FINANCIERE (NOUVEAU) ---
        with tab_sante:
            st.markdown("<h5 style='text-align: center;'>Analyse de ta Règle 50 / 30 / 20 ⚖️</h5>", unsafe_allow_html=True)
            st.write("Les experts financiers recommandent de diviser son budget ainsi : 50% pour les Besoins (Charges), 30% pour les Envies (Variables), et 20% pour l'Épargne. Voici où tu te situes ce mois-ci :")
            
            if REVENUS > 0:
                pct_charges = (total_charges_fixes / REVENUS) * 100
                pct_variables = (depense_mensuelle / REVENUS) * 100
                pct_epargne = (total_epargne_global / REVENUS) * 100
                
                col_s1, col_s2, col_s3 = st.columns(3)
                
                # Jauge Charges
                color_c = "green" if pct_charges <= 50 else "red"
                col_s1.markdown(f"<div style='text-align: center; padding: 15px; border-radius: 10px; background-color: #f3f4f6;'><b>Charges Fixes</b><br><span style='font-size: 24px; color: {color_c};'>{pct_charges:.1f}%</span><br><small>Recommandé : < 50%</small></div>", unsafe_allow_html=True)
                
                # Jauge Variables
                color_v = "green" if pct_variables <= 30 else "orange"
                col_s2.markdown(f"<div style='text-align: center; padding: 15px; border-radius: 10px; background-color: #f3f4f6;'><b>Dépenses Variables</b><br><span style='font-size: 24px; color: {color_v};'>{pct_variables:.1f}%</span><br><small>Recommandé : < 30%</small></div>", unsafe_allow_html=True)
                
                # Jauge Epargne
                color_e = "green" if pct_epargne >= 20 else "orange"
                col_s3.markdown(f"<div style='text-align: center; padding: 15px; border-radius: 10px; background-color: #f3f4f6;'><b>Taux d'Épargne</b><br><span style='font-size: 24px; color: {color_e};'>{pct_epargne:.1f}%</span><br><small>Recommandé : > 20%</small></div>", unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if pct_epargne >= 20:
                    st.success("🎉 Félicitations ! Ton taux d'épargne est excellent.")
                elif pct_epargne > 0:
                    st.info("👍 C'est un bon début ! Essaie d'optimiser tes dépenses variables pour épargner un peu plus.")
                else:
                    st.warning("⚠️ Attention, tu n'as pas généré d'épargne ce mois-ci par rapport à tes revenus.")
            else:
                st.info("Renseigne tes revenus dans le menu de gauche pour débloquer cette analyse.")

# --- ENCARTS RÉSUMÉ MENSUEL ---
st.markdown("##### 🏦 Vue Globale Financière")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Revenus", f"{REVENUS:.2f} €")
c2.metric("Charges Fixes", f"{total_charges_fixes:.2f} €")
c3.metric("Épargnes Fixes", f"{total_epargnes_fixes:.2f} €")
c4.metric("Épargnes Ponctuelles", f"{total_epargne_ponctuelle:.2f} €")
c5.metric("Budget Alloué (Semaines)", f"{BUDGET_MENSUEL:.2f} €")
c6.metric("Surplus du mois", f"{marge_non_allouee:.2f} €", delta=f"{marge_non_allouee:.2f} €", delta_color="normal")

st.markdown("---")

# --- AFFICHAGE DU TABLEAU DÉTAILLÉ ---
if not df_mois.empty:
    tableau_affichage = tableau_recap.copy()
    
    tableau_affichage.loc['📥 REPORT (De la sem. préc.)'] = reports
    tableau_affichage.loc['🛒 TOTAL DES DÉPENSES'] = totaux_semaine
    tableau_affichage.loc['🏦 MIS EN ÉPARGNE PONCTUELLE'] = epargnes_semaine
    tableau_affichage.loc['🏁 RESTE (Pour la sem. suiv.)'] = restes
    
    nouveaux_noms = {s: f"{s} ({budgets_hebdo.get(s, 0):g} €)" for s in semaines_possibles}
    tableau_affichage = tableau_affichage.rename(columns=nouveaux_noms)
    
    def colorer_tableau(data):
        styles = pd.DataFrame('', index=data.index, columns=data.columns)
        ligne_reste = '🏁 RESTE (Pour la sem. suiv.)'
        ligne_epargne = '🏦 MIS EN ÉPARGNE PONCTUELLE'
        
        for col in data.columns:
            if ligne_reste in data.index:
                val = data.at[ligne_reste, col]
                if isinstance(val, (int, float)):
                    if val >= 0: styles.at[ligne_reste, col] = 'color: #15803d; font-weight: bold;'
                    else: styles.at[ligne_reste, col] = 'color: #b91c1c; font-weight: bold;'
                    
            if ligne_epargne in data.index:
                val_epargne = data.at[ligne_epargne, col]
                if isinstance(val_epargne, (int, float)) and val_epargne > 0:
                    styles.at[ligne_epargne, col] = 'color: #0369a1; font-weight: bold;'
                    
        return styles

    st.dataframe(tableau_affichage.style.format("{:.2f} €").apply(colorer_tableau, axis=None), use_container_width=True)

else:
    st.info("Aucune transaction enregistrée pour ce mois. Ajoute ta première dépense depuis le menu !")

# --- HISTORIQUE DES ACTIONS ---
st.markdown("---")
st.header(f"📝 Historique détaillé ({mois_choisi})")

if not df_mois.empty:
    st.dataframe(df_mois.sort_values(by="id", ascending=False).drop(columns=['id', 'mois']), use_container_width=True, hide_index=True)
    st.markdown("### 🗑️ Supprimer une erreur")
    options_suppression = {row['id']: f"{row['categorie']} | {row['montant']:.2f} € | {row['semaine']} | {row['date_transaction']}" for _, row in df_mois.sort_values(by="id", ascending=False).iterrows()}
    id_a_supprimer = st.selectbox("Sélectionne la transaction à annuler :", options=list(options_suppression.keys()), format_func=lambda x: options_suppression[x])
    if st.button("Supprimer cette transaction"): delete_transaction(id_a_supprimer); st.rerun()