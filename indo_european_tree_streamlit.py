"""Streamlit app for exploring the Indo-European language family.

This module provides several interactive views (sunburst, icicle, treemap and
Graphviz dendrogram) together with historian-friendly filters such as period
range, attestation status and geographic spheres of influence.
"""

from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    from graphviz import Digraph

    _HAS_GRAPHVIZ = True
except Exception:  # pragma: no cover - Graphviz optional
    _HAS_GRAPHVIZ = False


st.set_page_config(
    page_title="Indo-European Family • Interactive",
    layout="wide",
    page_icon="🌍",
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
st.sidebar.header("Paramètres d'exploration")
view = st.sidebar.radio(
    "Vue principale",
    ["Sunburst", "Icicle", "Treemap", "Dendrogramme"],
    index=0,
)
max_depth = st.sidebar.slider(
    "Profondeur de l'arbre",
    1,
    int(DF["level"].max() + 1),
    3,
)
status_options = list(STATUS_COLOR)
status_selection = st.sidebar.multiselect(
    "Statuts historiques",
    status_options,
    default=status_options,
)
regions = sorted(DF["region"].unique())
region_selection = st.sidebar.multiselect(
    "Régions culturelles",
    regions,
    default=regions,
)
min_year, max_year = int(DF["period_start"].min()), int(DF["period_end"].max())
time_range = st.sidebar.slider(
    "Période représentée",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=50,
    format="%d",
)
query = st.sidebar.text_input(
    "Recherche",
    placeholder="ex. Gothic, Iran, Vulgar Latin…",
)
show_examples = st.sidebar.checkbox("Afficher les exemples", True)
show_notes = st.sidebar.checkbox("Afficher les notes dans l'infobulle", False)

st.sidebar.caption(
    "Les données chronologiques sont indicatives et expriment des fourchettes de mise en contact ou d'attestation."
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
# Helper visualisations
# ---------------------------------------------------------------------------
def make_hovertemplate() -> str:
    lines = ["<b>%{customdata[0]}</b>"]
    lines.append("Statut : %{customdata[1]}")
    lines.append("Région : %{customdata[2]}")
    lines.append("Période : %{customdata[3]}")
    if show_examples:
        lines.append("Exemples : %{customdata[4]}")
    if show_notes:
        lines.append("Notes : %{customdata[5]}")
    return "<br>".join(lines)


def render_plotly(kind: str) -> Optional[go.Figure]:
    base = VISIBLE_DF.copy()
    base["value"] = 1
    custom = base[[
        "label",
        "status",
        "region",
        "period_label",
        "examples",
        "notes",
    ]].to_numpy()

    if kind == "Sunburst":
        fig = px.sunburst(
            base,
            names="text",
            parents="parent",
            values="value",
            color="status",
            color_discrete_map=STATUS_COLOR,
            branchvalues="total",
            custom_data=custom,
        )
    elif kind == "Icicle":
        fig = px.icicle(
            base,
            names="text",
            parents="parent",
            values="value",
            color="status",
            color_discrete_map=STATUS_COLOR,
            branchvalues="total",
            custom_data=custom,
            tiling=dict(orientation="v"),
        )
    elif kind == "Treemap":
        fig = px.treemap(
            base,
            names="text",
            parents="parent",
            values="value",
            color="status",
            color_discrete_map=STATUS_COLOR,
            branchvalues="total",
            custom_data=custom,
        )
    else:  # pragma: no cover - invalid kind routed elsewhere
        return None

    hovertemplate = make_hovertemplate()
    fig.update_traces(
        hovertemplate=hovertemplate,
        selector=dict(type="sunburst"),
        insidetextorientation="radial",
        root_color="#0f172a",
        marker=dict(line=dict(color="#0b1220", width=1)),
    )
    fig.update_traces(
        hovertemplate=hovertemplate,
        selector=dict(type="icicle"),
        marker=dict(line=dict(color="#0b1220", width=1)),
    )
    fig.update_traces(
        hovertemplate=hovertemplate,
        selector=dict(type="treemap"),
        marker=dict(line=dict(color="#0b1220", width=1)),
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor="#0b1220",
        plot_bgcolor="#0b1220",
        font=dict(size=14, color="#e5e7eb"),
        hoverlabel=dict(bgcolor="#111827"),
    )
    return fig


def render_graphviz() -> None:
    if not _HAS_GRAPHVIZ:
        st.info("Graphviz n'est pas disponible dans cet environnement.")
        return

    g = Digraph("indo_european", format="svg")
    g.attr(rankdir="LR", bgcolor="#0b1220")
    g.attr(
        "node",
        shape="box",
        style="rounded,filled",
        color="#1e293b",
        fontcolor="#e2e8f0",
        fillcolor="#111827",
        penwidth="1.1",
        fontsize="10",
    )
    g.attr("edge", color="#38bdf8", penwidth="1.0")

    allowed = set(VISIBLE_DF["label"])
    for row in VISIBLE_DF.itertuples(index=False):
        fill = lighten(
            STATUS_COLOR[row.status],
            factor=0.35 if row.visible else 0.7,
        )
        badge = {
            "attested": "●",
            "reconstructed": "○",
            "extinct": "✖",
            "debated": "~",
        }.get(row.status, "")
        note_line = f"\n{row.period_label}" if show_notes else ""
        g.node(
            row.label,
            f"{badge}  {row.text}{note_line}",
            fillcolor=fill,
            style="rounded,filled",
        )

    for row in VISIBLE_DF.itertuples(index=False):
        if row.parent and row.parent in allowed:
            g.edge(row.parent, row.label)

    st.graphviz_chart(g, use_container_width=True)


# ---------------------------------------------------------------------------
# Header and metrics
# ---------------------------------------------------------------------------
left_col, right_col = st.columns([0.7, 0.3])
with left_col:
    st.markdown(
        """
        # Indo-European Language Family
        _Lecture interactive des branches, statuts et périodes d'attestation._
        """
    )
with right_col:
    st.markdown(
        """
        **Légende**  
        ● attesté &nbsp;&nbsp; ○ reconstruit &nbsp;&nbsp; ✖ éteint &nbsp;&nbsp; ~ débattu
        """
    )

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Branches affichées", len(VISIBLE_DF))
with col2:
    st.metric("Attestées", int((VISIBLE_DF["status"] == "attested").sum()))
with col3:
    st.metric("Extinctes", int((VISIBLE_DF["status"] == "extinct").sum()))

status_count = (
    VISIBLE_DF.groupby("status")["label"].count().reindex(status_options).fillna(0).astype(int)
)
st.bar_chart(status_count, height=160)


# ---------------------------------------------------------------------------
# Tabs for visualisation & data
# ---------------------------------------------------------------------------
chart_tab, table_tab = st.tabs(["Visualisation", "Tableau & contexte"])

with chart_tab:
    if view in {"Sunburst", "Icicle", "Treemap"}:
        figure = render_plotly(view)
        if figure:
            st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
    else:
        render_graphviz()

with table_tab:
    st.markdown("### Détails des branches sélectionnées")
    display_columns = [
        "label",
        "parent",
        "status",
        "region",
        "period_label",
        "examples",
        "notes",
    ]
    st.dataframe(
        VISIBLE_DF[display_columns].rename(
            columns={
                "label": "Branche",
                "parent": "Parent",
                "status": "Statut",
                "region": "Région",
                "period_label": "Chronologie",
                "examples": "Exemples",
                "notes": "Notes historiques",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

    download_csv = VISIBLE_DF[display_columns].to_csv(index=False)
    st.download_button(
        "Télécharger la sélection (CSV)",
        download_csv,
        file_name="indo_european_branches.csv",
        mime="text/csv",
    )

    st.info(
        "Les notes synthétisent les apports principaux de chaque branche dans une perspective diachronique."
    )


with st.expander("Crédits et méthodologie"):
    st.markdown(
        """
        **Sources indicatives** : manuels d'introduction à la linguistique historique, atlas des langues
        indo-européennes, corpus épigraphiques. Les périodes correspondent à des plages d'attestation
        approximatives (premières traces écrites ou reconstitutions).  
        **Bonnes pratiques** : possibilités de filtrer par époque ou par aire culturelle, survols enrichis
        et téléchargement des données pour prolonger l'analyse.
        """
    )
