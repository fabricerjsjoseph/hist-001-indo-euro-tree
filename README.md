# 🌳 Indo-European Language Family Tree

Une application Streamlit interactive pour visualiser l'arbre généalogique des langues indo-européennes à travers un dendrogramme élégant et informatif. L'interface a été pensée avec un regard d'historien : filtres chronologiques, statuts d'attestation, zones géographiques et annotations contextuelles.

## 📦 Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Note** : Graphviz doit également être installé sur votre système :
- **Ubuntu/Debian** : `sudo apt-get install graphviz`
- **macOS** : `brew install graphviz`
- **Windows** : Télécharger depuis [graphviz.org](https://graphviz.org/download/)

## 🚀 Lancer l'application

```bash
streamlit run indo_european_tree_streamlit.py
```

L'application sera accessible à l'adresse `http://localhost:8501`

## ✨ Fonctionnalités principales

### Visualisation

- **Dendrogramme interactif** : Visualisation hiérarchique claire et esthétique des relations linguistiques
- **Design moderne** : Interface épurée avec des couleurs et une typographie optimisées pour la lisibilité
- **Légendes visuelles** : Symboles Unicode distinctifs pour chaque statut d'attestation

### Filtres intelligents

- **Profondeur de l'arbre** : Contrôle du nombre de niveaux hiérarchiques affichés
- **Statuts historiques** : Filtrage par attestation (attesté ●, reconstruit ○, éteint ✖, débattu ≈)
- **Régions culturelles** : Sélection par zone géographique d'attestation
- **Période chronologique** : Slider temporel de -4500 à aujourd'hui
- **Recherche textuelle** : Recherche dans les noms, exemples et notes historiques

### Données et export

- **Tableau détaillé** : Vue tabulaire avec toutes les métadonnées linguistiques
- **Export CSV** : Téléchargement des branches filtrées pour analyse externe
- **Métriques en temps réel** : Statistiques sur les branches affichées
- **Documentation complète** : Onglet méthodologie avec sources et interprétation

## 📊 Données

Les périodes correspondent à des plages d'attestation approximatives :
- Premières traces écrites documentées
- Reconstructions linguistiques basées sur la méthode comparative
- Continuités vernaculaires pour les langues vivantes

Les zones culturelles servent d'indication géohistorique et ne sont pas exclusives.

## 🎨 Caractéristiques visuelles

- **Palette de couleurs** : Différenciation claire par statut d'attestation
- **Symboles Unicode** : Badges visuels pour une identification rapide
- **Mise en page responsive** : Adaptation automatique à différentes tailles d'écran
- **Informations contextuelles** : Périodes et exemples affichables sur demande

## 📚 Licences et sources

Les regroupements suivent les synthèses universitaires standard en linguistique historique comparative :
- Beekes (2011) - *Comparative Indo-European Linguistics*
- Fortson (2018) - *Indo-European Language and Culture*
- Mallory & Adams (2006) - *The Oxford Introduction to Proto-Indo-European*

Les éventuelles reconstitutions relèvent de l'état de l'art et peuvent varier selon les écoles de pensée.
