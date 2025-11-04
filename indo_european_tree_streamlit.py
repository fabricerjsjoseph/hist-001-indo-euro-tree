"""Streamlit app for exploring the Indo-European language family.

This module provides an interactive dendrogram visualization using Graphviz,
together with historian-friendly filters such as period range, attestation
status and geographic spheres of influence.
"""

from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd
import streamlit as st

try:
    from graphviz import Digraph

    _HAS_GRAPHVIZ = True
except Exception:  # pragma: no cover - Graphviz optional
    _HAS_GRAPHVIZ = False


st.set_page_config(
    page_title="Indo-European Family Tree • Dendrogram",
    layout="wide",
    page_icon="🌳",
    initial_sidebar_state="expanded",
)

CURRENT_YEAR = _dt.date.today().year


@dataclass(frozen=True)
class Branch:
    """Representation of a node in the linguistic tree."""

    label: str
    parent: str
    status: str
    examples: str
    region: str
    period_start: int
    period_end: Optional[int]
    notes: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {
            "label": self.label,
            "parent": self.parent,
            "status": self.status,
            "examples": self.examples,
            "region": self.region,
            "period_start": self.period_start,
            "period_end": self.period_end if self.period_end is not None else CURRENT_YEAR,
            "notes": self.notes,
        }


RAW_DATA: Sequence[Branch] = (
    Branch(
        label="Indo-European",
        parent="",
        status="reconstructed",
        examples="Proto-Indo-European lexicon",
        region="Pontic-Caspian steppe",
        period_start=-4500,
        period_end=CURRENT_YEAR,
        notes="Most reconstructions place the homeland north of the Black Sea.",
    ),
    Branch(
        label="Anatolian",
        parent="Indo-European",
        status="extinct",
        examples="Hittite, Luwian, Lycian",
        region="Anatolia",
        period_start=-1900,
        period_end=-400,
        notes="Earliest attested branch; cuneiform archives at Hattusa.",
    ),
    Branch(
        label="Hittite",
        parent="Anatolian",
        status="extinct",
        examples="Hittite royal archives",
        region="Central Anatolia",
        period_start=-1700,
        period_end=-1100,
        notes="Documented in the Old Hittite Empire and subsequent New Kingdom.",
    ),
    Branch(
        label="Luwic",
        parent="Anatolian",
        status="extinct",
        examples="Luwian, Lycian, Carian",
        region="Western & Southern Anatolia",
        period_start=-1600,
        period_end=-200,
        notes="Includes the hieroglyphic inscriptions from Anatolia and northern Syria.",
    ),
    Branch(
        label="Tocharian",
        parent="Indo-European",
        status="extinct",
        examples="Tocharian A (Agnean), Tocharian B (Kuchean)",
        region="Tarim Basin",
        period_start=400,
        period_end=900,
        notes="Manuscripts uncovered along the Silk Road; Buddhist translations.",
    ),
    Branch(
        label="Italo-Celtic",
        parent="Indo-European",
        status="debated",
        examples="Shared innovations in morphology",
        region="Western & Central Europe",
        period_start=-1800,
        period_end=-500,
        notes="Hypothetical grouping linking early Italic and Celtic languages.",
    ),
    Branch(
        label="Italic",
        parent="Italo-Celtic",
        status="attested",
        examples="Latin, Oscan, Umbrian",
        region="Italian Peninsula",
        period_start=-700,
        period_end=CURRENT_YEAR,
        notes="Latin develops into the Romance continuum after the Roman Empire.",
    ),
    Branch(
        label="Romance",
        parent="Italic",
        status="attested",
        examples="Spanish, French, Italian, Romanian",
        region="Southern & Western Europe",
        period_start=200,
        period_end=CURRENT_YEAR,
        notes="Diverse vernaculars evolving from Vulgar Latin following Roman expansion.",
    ),
    Branch(
        label="Celtic",
        parent="Italo-Celtic",
        status="attested",
        examples="Irish, Welsh, Breton",
        region="Atlantic Europe",
        period_start=-600,
        period_end=CURRENT_YEAR,
        notes="Includes Insular and Continental traditions; Goidelic vs Brythonic split.",
    ),
    Branch(
        label="Germanic",
        parent="Indo-European",
        status="attested",
        examples="English, German, Norse",
        region="Northern Europe",
        period_start=-500,
        period_end=CURRENT_YEAR,
        notes="Marked by Grimm's and Verner's laws; attested from the 1st century CE.",
    ),
    Branch(
        label="North Germanic",
        parent="Germanic",
        status="attested",
        examples="Swedish, Danish, Icelandic",
        region="Scandinavia",
        period_start=700,
        period_end=CURRENT_YEAR,
        notes="Old Norse textual corpus includes the sagas and skaldic poetry.",
    ),
    Branch(
        label="West Germanic",
        parent="Germanic",
        status="attested",
        examples="English, German, Dutch",
        region="North Sea basin",
        period_start=400,
        period_end=CURRENT_YEAR,
        notes="Successive sound shifts lead to Anglo-Frisian and High German outcomes.",
    ),
    Branch(
        label="East Germanic",
        parent="Germanic",
        status="extinct",
        examples="Gothic, Vandalic",
        region="Central & Eastern Europe",
        period_start=0,
        period_end=600,
        notes="Gothic Bible (Wulfila) is a cornerstone for Germanic comparative studies.",
    ),
    Branch(
        label="Balto-Slavic",
        parent="Indo-European",
        status="attested",
        examples="Baltic and Slavic languages",
        region="Eastern Europe",
        period_start=-1200,
        period_end=CURRENT_YEAR,
        notes="Shared accentual innovations underpin the Balto-Slavic hypothesis.",
    ),
    Branch(
        label="Baltic",
        parent="Balto-Slavic",
        status="attested",
        examples="Lithuanian, Latvian",
        region="Eastern Baltic",
        period_start=1200,
        period_end=CURRENT_YEAR,
        notes="Lithuanian preserves archaic features valuable to reconstruction.",
    ),
    Branch(
        label="Slavic",
        parent="Balto-Slavic",
        status="attested",
        examples="Russian, Polish, Serbo-Croatian",
        region="Slavic Europe",
        period_start=500,
        period_end=CURRENT_YEAR,
        notes="Split into West, East and South Slavic; Glagolitic and Cyrillic scripts.",
    ),
    Branch(
        label="Hellenic",
        parent="Indo-European",
        status="attested",
        examples="Greek",
        region="Aegean basin",
        period_start=-1400,
        period_end=CURRENT_YEAR,
        notes="Linear B tablets attest Mycenaean Greek in the Late Bronze Age.",
    ),
    Branch(
        label="Indo-Iranian",
        parent="Indo-European",
        status="attested",
        examples="Sanskrit, Avestan, Persian",
        region="Iranian Plateau & South Asia",
        period_start=-1800,
        period_end=CURRENT_YEAR,
        notes="Includes Indo-Aryan, Iranian and Nuristani; Vedic hymns are earliest.",
    ),
    Branch(
        label="Indo-Aryan",
        parent="Indo-Iranian",
        status="attested",
        examples="Hindi, Bengali, Marathi",
        region="South Asia",
        period_start=-1500,
        period_end=CURRENT_YEAR,
        notes="Rigvedic Sanskrit provides a window onto Indo-Aryan migrations.",
    ),
    Branch(
        label="Iranian",
        parent="Indo-Iranian",
        status="attested",
        examples="Persian, Kurdish, Pashto",
        region="Iran & Central Asia",
        period_start=-1000,
        period_end=CURRENT_YEAR,
        notes="Avestan, Old Persian inscriptions and Middle Iranian literatures.",
    ),
    Branch(
        label="Nuristani",
        parent="Indo-Iranian",
        status="attested",
        examples="Waigali, Ashkun",
        region="Hindu Kush",
        period_start=500,
        period_end=CURRENT_YEAR,
        notes="Remote mountain communities preserve distinctive phonology.",
    ),
    Branch(
        label="Albanian",
        parent="Indo-European",
        status="attested",
        examples="Gheg, Tosk",
        region="Western Balkans",
        period_start=1200,
        period_end=CURRENT_YEAR,
        notes="Earliest texts from the 15th century; debated Illyrian connections.",
    ),
    Branch(
        label="Armenian",
        parent="Indo-European",
        status="attested",
        examples="Classical Armenian, Modern Armenian",
        region="Armenian Highlands",
        period_start=-500,
        period_end=CURRENT_YEAR,
        notes="Unique script devised in the 5th century by Mesrop Mashtots.",
    ),
    Branch(
        label="Thracian-Dacian",
        parent="Indo-European",
        status="extinct",
        examples="Thracian, Dacian",
        region="Lower Danube",
        period_start=-1200,
        period_end=600,
        notes="Known from glosses and onomastics; limited textual attestation.",
    ),
    Branch(
        label="Phrygian",
        parent="Indo-European",
        status="extinct",
        examples="Phrygian inscriptions",
        region="Central Anatolia",
        period_start=-800,
        period_end=400,
        notes="Shares similarities with Greek; inscriptions in Greek alphabet.",
    ),
    Branch(
        label="Illyrian-Messapic",
        parent="Indo-European",
        status="debated",
        examples="Illyrian, Messapic",
        region="Western Balkans & Apulia",
        period_start=-900,
        period_end=600,
        notes="Sparse inscriptions; debated relationship to Albanian.",
    ),
)


STATUS_COLOR = {
    "attested": "#3fb8af",
    "reconstructed": "#4fc3f7",
    "extinct": "#ef5350",
    "debated": "#ffb300",
}

# Status badges for visual distinction in the dendrogram
STATUS_BADGES = {
    "attested": "●",
    "reconstructed": "○",
    "extinct": "✖",
    "debated": "≈",
}


@st.cache_data
def load_dataframe() -> pd.DataFrame:
    """Create the DataFrame from the raw dataclass list."""

    df = pd.DataFrame([branch.to_dict() for branch in RAW_DATA])
    df["period_end"].fillna(CURRENT_YEAR, inplace=True)

    levels: Dict[str, int] = {}

    def node_level(node: str) -> int:
        if node in levels:
            return levels[node]
        parent = df.loc[df["label"] == node, "parent"]
        if parent.empty or parent.iloc[0] == "":
            levels[node] = 0
        else:
            levels[node] = 1 + node_level(parent.iloc[0])
        return levels[node]

    for node in df["label"].tolist():
        node_level(node)
    df["level"] = df["label"].map(levels)

    def period_label(row: pd.Series) -> str:
        start = format_year(row["period_start"])
        end = format_year(row["period_end"])
        if row["period_end"] >= CURRENT_YEAR:
            end = "présent"
        return f"{start} – {end}"

    df["period_label"] = df.apply(period_label, axis=1)
    return df


def format_year(value: int) -> str:
    """Format integer years into historian-friendly strings."""

    if value < 0:
        return f"{-value} av. n.è."
    if value == 0:
        return "an 0"
    return f"{value} apr. n.è."


DF = load_dataframe()


def lighten(color: str, factor: float = 0.2) -> str:
    """Return a lighter tint of a hex colour for better legibility."""

    color = color.lstrip("#")
    r, g, b = (int(color[i : i + 2], 16) for i in (0, 2, 4))
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def filter_by_time(df: pd.DataFrame, period: Tuple[int, int]) -> pd.Series:
    start, end = period
    return (df["period_start"] <= end) & (df["period_end"] >= start)


# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------
st.sidebar.header("🌳 Paramètres d'exploration")
st.sidebar.markdown("---")
max_depth = st.sidebar.slider(
    "📊 Profondeur de l'arbre",
    1,
    int(DF["level"].max() + 1),
    4,
    help="Contrôle le nombre de niveaux hiérarchiques affichés dans le dendrogramme"
)
status_options = list(STATUS_COLOR)
status_selection = st.sidebar.multiselect(
    "🏛️ Statuts historiques",
    status_options,
    default=status_options,
    help="Filtrer par statut d'attestation linguistique"
)
regions = sorted(DF["region"].unique())
region_selection = st.sidebar.multiselect(
    "🗺️ Régions culturelles",
    regions,
    default=regions,
    help="Filtrer par zone géographique d'attestation"
)
st.sidebar.markdown("---")
min_year, max_year = int(DF["period_start"].min()), int(DF["period_end"].max())
time_range = st.sidebar.slider(
    "📅 Période représentée",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=50,
    format="%d",
    help="Filtrer par période chronologique"
)
st.sidebar.markdown("---")
query = st.sidebar.text_input(
    "🔍 Recherche",
    placeholder="ex. Gothic, Iran, Vulgar Latin…",
    help="Recherche dans les noms, exemples et notes"
)
st.sidebar.markdown("---")
st.sidebar.markdown("**Affichage**")
show_examples = st.sidebar.checkbox("Afficher les exemples", True)
show_notes = st.sidebar.checkbox("Afficher les périodes", True)

st.sidebar.markdown("---")
st.sidebar.caption(
    "💡 Les données chronologiques sont indicatives et expriment des fourchettes de mise en contact ou d'attestation."
)


# ---------------------------------------------------------------------------
# Filtering logic
# ---------------------------------------------------------------------------
def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    base = df.copy()
    base = base[base["level"] < max_depth]

    mask_time = filter_by_time(base, time_range)
    mask_status = base["status"].isin(status_selection) if status_selection else True
    mask_region = base["region"].isin(region_selection) if region_selection else True

    combined_mask = mask_time & mask_status & mask_region
    candidate = base[combined_mask]

    if query.strip():
        pattern = re.compile(re.escape(query.strip()), re.IGNORECASE)
        mask_query = (
            base["label"].str.contains(pattern)
            | base["examples"].str.contains(pattern)
            | base["notes"].str.contains(pattern)
        )
        candidate = candidate[candidate["label"].isin(base[mask_query]["label"])]
    else:
        mask_query = pd.Series([False] * len(base), index=base.index)

    keep: set[str] = set(candidate["label"].tolist())

    parent_map = {row.label: row.parent for row in df.itertuples()}
    for label in list(keep):
        current = parent_map.get(label, "")
        while current:
            keep.add(current)
            current = parent_map.get(current, "")

    if query.strip():
        children_map: Dict[str, List[str]] = {}
        for row in df.itertuples():
            children_map.setdefault(row.parent, []).append(row.label)
        for label in base[mask_query]["label"]:
            stack = [label]
            while stack:
                node = stack.pop()
                if node in keep:
                    continue
                keep.add(node)
                stack.extend(children_map.get(node, []))

    filtered = df[df["label"].isin(keep)].copy()
    filtered["visible"] = filtered["label"].isin(candidate["label"])
    return filtered


VISIBLE_DF = apply_filters(DF)


def node_label(row: pd.Series) -> str:
    base = row["label"]
    if show_examples and row["examples"]:
        base = f"{base} — {row['examples']}"
    return base


VISIBLE_DF["text"] = VISIBLE_DF.apply(node_label, axis=1)
VISIBLE_DF.sort_values(["level", "label"], inplace=True)

opacity_map = {
    row.label: (1.0 if row.visible else 0.3)
    for row in VISIBLE_DF.itertuples()
}


# ---------------------------------------------------------------------------
# Enhanced Dendrogram Visualization
# ---------------------------------------------------------------------------
def render_dendrogram() -> None:
    """Render an enhanced dendrogram visualization with improved aesthetics."""
    if not _HAS_GRAPHVIZ:
        st.error("⚠️ Graphviz n'est pas disponible dans cet environnement.")
        st.info("Veuillez installer Graphviz pour afficher le dendrogramme.")
        return

    # Create enhanced graph with better styling
    g = Digraph("indo_european_tree", format="svg")
    
    # Graph-level attributes for better aesthetics
    g.attr(
        rankdir="LR",
        bgcolor="#0a0e1a",
        splines="ortho",  # Orthogonal edges for cleaner look
        nodesep="0.6",
        ranksep="1.2",
        dpi="300",
    )
    
    # Enhanced node styling with modern design
    g.attr(
        "node",
        shape="box",
        style="rounded,filled",
        color="#2d3748",
        fontcolor="#f7fafc",
        fillcolor="#1a202c",
        penwidth="2",
        fontsize="11",
        fontname="Arial",
        margin="0.3,0.15",
    )
    
    # Enhanced edge styling with gradient-like appearance
    # Note: Gradient syntax (color1:color2) requires Graphviz >= 2.40
    # Falls back to single color if not supported
    g.attr(
        "edge",
        color="#4299e1:#667eea",  # Gradient from blue to purple (Graphviz 2.40+)
        penwidth="2.5",
        arrowsize="0.8",
    )

    allowed = set(VISIBLE_DF["label"])
    
    # Render nodes with enhanced visual distinction
    for row in VISIBLE_DF.itertuples(index=False):
        # Calculate fill color with better visibility
        base_color = STATUS_COLOR[row.status]
        if row.visible:
            fill = lighten(base_color, factor=0.25)
            border_color = base_color
            penwidth = "2.5"
        else:
            fill = lighten(base_color, factor=0.65)
            border_color = lighten(base_color, factor=0.5)
            penwidth = "1.5"
        
        # Get status badge from module constant
        badge = STATUS_BADGES.get(row.status, "")
        
        # Build label with optional information
        label_parts = [f"{badge}  {row.text}"]
        if show_notes and row.period_label:
            label_parts.append(f"📅 {row.period_label}")
        
        label_text = "\n".join(label_parts)
        
        # Add node with enhanced styling
        g.node(
            row.label,
            label_text,
            fillcolor=fill,
            color=border_color,
            penwidth=penwidth,
            style="rounded,filled",
            fontcolor="#f7fafc" if row.visible else "#a0aec0",
        )

    # Create edges with proper hierarchy
    for row in VISIBLE_DF.itertuples(index=False):
        if row.parent and row.parent in allowed:
            edge_color = "#4299e1:#667eea" if row.visible else "#4a5568"
            edge_width = "2.5" if row.visible else "1.5"
            g.edge(
                row.parent,
                row.label,
                color=edge_color,
                penwidth=edge_width,
            )

    st.graphviz_chart(g, use_container_width=True)


# ---------------------------------------------------------------------------
# Header and metrics
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style='text-align: center; padding: 1rem 0;'>
        <h1 style='color: #4299e1; font-size: 2.5rem; margin-bottom: 0.5rem;'>
            🌳 Arbre Généalogique Indo-Européen
        </h1>
        <p style='color: #a0aec0; font-size: 1.1rem; font-style: italic;'>
            Exploration interactive des branches linguistiques et de leur évolution historique
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# Legend in an expander for cleaner interface
with st.expander("📖 Légende des symboles", expanded=False):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**● Attesté**  \nLangues avec sources écrites")
    with col2:
        st.markdown("**○ Reconstruit**  \nProto-langues reconstituées")
    with col3:
        st.markdown("**✖ Éteint**  \nLangues disparues")
    with col4:
        st.markdown("**≈ Débattu**  \nRegroupements hypothétiques")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🌿 Branches affichées", len(VISIBLE_DF))
with col2:
    st.metric("● Attestées", int((VISIBLE_DF["status"] == "attested").sum()))
with col3:
    st.metric("✖ Éteintes", int((VISIBLE_DF["status"] == "extinct").sum()))
with col4:
    st.metric("○ Reconstruites", int((VISIBLE_DF["status"] == "reconstructed").sum()))

st.markdown("---")


# ---------------------------------------------------------------------------
# Main dendrogram visualization
# ---------------------------------------------------------------------------
st.markdown("### 🌳 Dendrogramme de la famille indo-européenne")
st.markdown(
    """
    <p style='color: #a0aec0; margin-bottom: 1.5rem;'>
    Visualisation hiérarchique des relations linguistiques entre les branches de la famille indo-européenne.
    Les couleurs représentent les statuts d'attestation, et les liens montrent les relations de parenté.
    </p>
    """,
    unsafe_allow_html=True
)

render_dendrogram()

st.markdown("---")

# ---------------------------------------------------------------------------
# Data table and context
# ---------------------------------------------------------------------------
table_tab, context_tab = st.tabs(["📊 Tableau détaillé", "📚 Méthodologie"])

with table_tab:
    st.markdown("### Détails des branches affichées")
    display_columns = [
        "label",
        "parent",
        "status",
        "region",
        "period_label",
        "examples",
        "notes",
    ]
    
    # Display styled dataframe
    styled_df = VISIBLE_DF[display_columns].rename(
        columns={
            "label": "🌿 Branche",
            "parent": "⬆️ Parent",
            "status": "📋 Statut",
            "region": "🗺️ Région",
            "period_label": "📅 Chronologie",
            "examples": "📝 Exemples",
            "notes": "📖 Notes historiques",
        }
    )
    
    st.dataframe(
        styled_df,
        hide_index=True,
        use_container_width=True,
        height=400,
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        download_csv = VISIBLE_DF[display_columns].to_csv(index=False)
        st.download_button(
            "⬇️ Télécharger (CSV)",
            download_csv,
            file_name="indo_european_branches.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col2:
        st.caption(
            f"💡 {len(VISIBLE_DF)} branches affichées • "
            "Les notes synthétisent les apports principaux de chaque branche dans une perspective diachronique."
        )

with context_tab:
    st.markdown("### Crédits et méthodologie")
    
    st.markdown("""
    #### 📚 Sources principales
    
    Les données présentées dans ce dendrogramme s'appuient sur les travaux de référence en linguistique 
    historique indo-européenne :
    
    - **Manuels de référence** : Introduction à la linguistique historique comparative
    - **Atlas linguistiques** : Atlas des langues indo-européennes et de leur distribution géographique
    - **Corpus épigraphiques** : Collections de textes anciens et inscriptions
    
    #### ⏱️ Chronologie et datation
    
    Les périodes mentionnées correspondent à des **plages d'attestation approximatives** :
    - Premières traces écrites documentées
    - Reconstitutions linguistiques basées sur la méthode comparative
    - Continuités vernaculaires pour les langues vivantes
    
    #### 🔍 Utilisation de l'outil
    
    Cette visualisation interactive permet de :
    - **Filtrer** les branches par époque, région ou statut d'attestation
    - **Explorer** les relations hiérarchiques entre les langues
    - **Rechercher** des branches spécifiques via la barre de recherche
    - **Télécharger** les données filtrées pour une analyse approfondie
    
    #### 📊 Interprétation des symboles
    
    - **● Attesté** : Langues documentées par des sources écrites directes
    - **○ Reconstruit** : Proto-langues déduites par la méthode comparative
    - **✖ Éteint** : Langues qui ne sont plus parlées
    - **≈ Débattu** : Regroupements dont la validité fait débat dans la communauté scientifique
    
    #### ⚠️ Note importante
    
    Les regroupements linguistiques présentés reflètent l'état actuel des connaissances et peuvent varier 
    selon les écoles de pensée. Les hypothèses de parenté linguistique, notamment pour les branches les 
    plus anciennes, restent sujettes à révision à mesure que de nouvelles données deviennent disponibles.
    """)
    
    st.markdown("---")
    st.caption("Visualisation créée avec Streamlit et Graphviz • Données compilées à partir de sources académiques")
