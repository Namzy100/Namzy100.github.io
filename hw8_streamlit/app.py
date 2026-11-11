"""IS 445 Homework 8: an original Streamlit exploration of reported UFO sightings."""
import altair as alt
import pandas as pd
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/UIUC-iSchool-DataViz/is445_data/main/ufo-scrubbed-geocoded-time-standardized-00.csv"
COLUMNS = [
    "date_sighted", "city", "state", "country", "shape",
    "duration_seconds", "duration_reported", "notes",
    "date_reported", "latitude", "longitude",
]
DURATION_LABELS = [
    "Under 10 sec", "10–30 sec", "30–60 sec", "1–5 min",
    "5–15 min", "15–60 min", "Over 1 hour",
]
DURATION_EDGES = [0, 10, 30, 60, 300, 900, 3600, 86400]


st.set_page_config(
    page_title="UFO Reports | Patterns in Time & Duration",
    page_icon="🛸",
    layout="wide",
)

st.title("🛸 UFO Reports: Patterns in Time & Duration")
st.caption("IS 445 · Homework 8 · An interactive Streamlit data story")
st.info(
    "These are unverified, self-reported sightings. Counts reflect reports, "
    "not confirmed events, and are not adjusted for population or changes in reporting."
)


@st.cache_data(ttl=3600, show_spinner="Loading reports from the course dataset…")
def load_data():
    data = pd.read_csv(
        DATA_URL,
        names=COLUMNS,
        header=None,
        dtype=str,
        on_bad_lines="skip",
        low_memory=False,
    )
    data = data[~data["date_sighted"].fillna("").str.lower().isin(
        ["datetime", "date_sighted"]
    )].copy()
    data["year"] = pd.to_numeric(
        data["date_sighted"].str.extract(
            r"^\s*\d{1,2}/\d{1,2}/(\d{4})", expand=False
        ),
        errors="coerce",
    )
    data["shape"] = data["shape"].fillna("").str.strip().str.lower()
    data["duration"] = pd.to_numeric(
        data["duration_seconds"].str.replace(",", "", regex=False),
        errors="coerce",
    )
    return data


try:
    reports = load_data()
except Exception as exc:
    st.error("The course data could not be loaded. Please try refreshing the app.")
    st.exception(exc)
    st.stop()

time_data = reports[
    reports["year"].between(1950, 2025)
    & reports["shape"].ne("")
].copy()
if time_data.empty:
    st.error("No usable dated reports were found in the source data.")
    st.stop()

shape_rank = time_data["shape"].value_counts()
top_shapes = shape_rank.head(8).index.tolist()
year_min, year_max = int(time_data["year"].min()), int(time_data["year"].max())

st.subheader("1 · How have reports changed across years?")
st.write(
    "Select descriptions and a year range to compare annual report trends. "
    "Lines represent counts of reports with each selected shape."
)
controls_a, controls_b = st.columns([3, 2])
with controls_a:
    shapes_for_trend = st.multiselect(
        "Reported shapes to compare",
        options=top_shapes,
        default=top_shapes[:3],
        key="trend_shapes",
    )
with controls_b:
    years = st.slider(
        "Sightings year range",
        min_value=year_min,
        max_value=year_max,
        value=(max(year_min, 1990), year_max),
        key="trend_years",
    )

if shapes_for_trend:
    counts = (
        time_data[
            time_data["shape"].isin(shapes_for_trend)
            & time_data["year"].between(*years)
        ]
        .groupby(["year", "shape"], as_index=False)
        .size()
        .rename(columns={"size": "Reports"})
    )
    trend = (
        alt.Chart(counts)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("year:Q", title="Year", axis=alt.Axis(format="d", tickMinStep=1)),
            y=alt.Y("Reports:Q", title="Number of reports"),
            color=alt.Color("shape:N", title="Reported shape"),
            tooltip=[
                alt.Tooltip("year:Q", format="d", title="Year"),
                alt.Tooltip("shape:N", title="Shape"),
                alt.Tooltip("Reports:Q", title="Reports", format=","),
            ],
        )
        .properties(height=370)
    )
    st.altair_chart(trend, width="stretch")
else:
    st.warning("Choose at least one shape to display the annual trend.")

st.markdown(
    "**Design and interpretation.** This line chart highlights how frequently different "
    "shapes were reported from year to year, rather than the hour/month patterns examined "
    "in my previous assignment. Year and report count are quantitative encodings; shape "
    "is nominal and mapped to distinct hues. Lines make changes over time and differences "
    "between descriptions easier to follow. I extracted years from sighting dates, "
    "standardized shape labels, removed unusable dates, and aggregated annual counts in "
    "Pandas. The multiselect and range slider let readers compare different descriptions "
    "without clutter from every possible shape. With more time, I would add an optional "
    "population-adjusted rate and annotate major changes in reporting practices."
)

st.divider()
st.subheader("2 · How long do sightings reportedly last?")
st.write(
    "Compare duration profiles as percentages within each reported shape. "
    "Each bar totals 100%, so shapes with different report counts remain comparable."
)
duration_data = reports[
    reports["shape"].isin(top_shapes)
    & reports["duration"].gt(0)
    & reports["duration"].le(86400)
].copy()
duration_data["duration_group"] = pd.cut(
    duration_data["duration"],
    bins=DURATION_EDGES,
    labels=DURATION_LABELS,
    include_lowest=True,
    right=True,
)

selected_duration_shapes = st.multiselect(
    "Shapes for duration comparison",
    options=top_shapes,
    default=top_shapes[:4],
    key="duration_shapes",
)
if selected_duration_shapes:
    subset = duration_data[
        duration_data["shape"].isin(selected_duration_shapes)
    ]
    summaries = (
        subset.groupby(["shape", "duration_group"], observed=True)
        .size()
        .reset_index(name="Reports")
    )
    summaries["Total"] = summaries.groupby("shape")["Reports"].transform("sum")
    summaries["Percent"] = (summaries["Reports"] / summaries["Total"] * 100)
    bars = (
        alt.Chart(summaries)
        .mark_bar()
        .encode(
            x=alt.X("sum(Percent):Q", title="Share of valid reports (%)",
                    scale=alt.Scale(domain=[0, 100])),
            y=alt.Y("shape:N", title="Reported shape",
                    sort=selected_duration_shapes),
            color=alt.Color(
                "duration_group:N",
                title="Reported duration",
                sort=DURATION_LABELS,
                scale=alt.Scale(scheme="tableau20"),
            ),
            order=alt.Order("duration_group:N", sort="ascending"),
            tooltip=[
                alt.Tooltip("shape:N", title="Shape"),
                alt.Tooltip("duration_group:N", title="Duration"),
                alt.Tooltip("Reports:Q", format=",", title="Reports in bin"),
                alt.Tooltip("Percent:Q", format=".1f", title="Share (%)"),
            ],
        )
        .properties(height=max(220, len(selected_duration_shapes) * 60))
    )
    st.altair_chart(bars, width="stretch")
    st.caption(
        "Only positive durations up to 24 hours are included. Longer or missing "
        "durations are excluded, and duration values are self-reported."
    )
else:
    st.warning("Choose at least one shape to compare duration distributions.")

st.markdown(
    "**Design and interpretation.** This 100% stacked-bar chart explores a different "
    "feature of the dataset: reported event duration. Shape and duration range are "
    "nominal categories, with duration represented by ordered color segments; the "
    "horizontal quantitative axis gives the percentage within each shape. Percentages "
    "are preferable to raw totals here because some descriptions occur far more "
    "often than others. I converted the duration field to numeric seconds, excluded "
    "invalid/nonpositive entries and values above 24 hours, grouped seconds into "
    "readable intervals, and calculated the share of each interval per shape. "
    "The shape selector keeps the comparison focused. With more time, I would "
    "investigate how sensitive the patterns are to implausible self-reported durations "
    "and add uncertainty or sample-size warnings."
)

st.divider()
st.subheader("Sources and relationship to Homework 5")
st.markdown(
    "Data: [UIUC IS 445 UFO sightings CSV](" + DATA_URL + "). "
    "Original records are reported sightings, not independently verified observations."
)
st.markdown(
    "**Originality note:** This homework reuses the **dataset** from my Homework 5, "
    "but **does not reuse either Homework 5 chart or any Homework 5 write-up text**. "
    "Homework 5 analyzed month by hour (heatmap) and state by reported shape "
    "(dropdown bar chart). This app instead analyzes annual shape trends (interactive "
    "line chart) and within-shape duration percentages (stacked bar chart). "
    "The cleaning approach follows the same dataset structure, but the questions, "
    "encodings, interactions, and written interpretations are new."
)
