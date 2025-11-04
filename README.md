# Indo-European Language Family Explorer

Une application Streamlit interactive pour visualiser l'arbre des langues indo-européennes avec plusieurs vues (sunburst, icicle, treemap et dendrogramme Graphviz). L'interface a été pensée avec un regard d'historien : filtres chronologiques, statuts d'attestation, zones géographiques et annotations contextuelles.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancer l'application

```bash
streamlit run indo_european_tree_streamlit.py
```

## Fonctionnalités principales

- **Vues multiples** : sunburst, icicle, treemap et dendrogramme pour explorer les relations.
- **Filtres experts** : sélection par période, statut historique (attesté, reconstruit, éteint, débattu) et région culturelle.
- **Recherche plein texte** : sur les noms de branches, exemples et notes historiques.
- **Badges et notes** : infobulles enrichies, badges de statut et téléchargement CSV de la sélection.
- **Tableau contextuel** : onglet dédié avec détails chronologiques et synthèses historiographiques.

## Données

Les périodes correspondent à des plages d'attestation approximatives (premières traces écrites, reconstructions ou continuités vernaculaires). Les zones culturelles servent d'indication géohistorique et ne sont pas exclusives.

## Licences et sources

Les regroupements suivent les synthèses universitaires standard (Beekes 2011, Fortson 2018, Mallory & Adams 2006). Les éventuelles reconstitutions relèvent de l'état de l'art et peuvent varier selon les écoles.
