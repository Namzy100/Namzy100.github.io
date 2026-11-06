---
permalink: /projects/hw5_ufo_sightings/
name: UFO Sightings — Time and Place
tools: [Python, Altair, Vega-Lite]
description: Two views of reported UFO sightings, including an interactive filter by reported shape.
custom_js:
  - vega.min
  - vega-lite.min
  - vega-embed.min
  - justcharts
---

# UFO sightings: When and where do people report them?

I used the UFO sightings dataset from the IS 445 course repository to look at two questions: when do reports tend to happen, and which US states have the most reports for different reported shapes? These are records of **reported sightings**, not proof of unusual objects in the sky.

## Plot 1 — Month and hour

<vegachart schema-url="{{ site.baseurl }}/assets/json/hw5_ufo_hour_month.json" style="width: 100%"></vegachart>

The first visualization is a heatmap showing how many sightings were reported in each combination of **month** and **hour of the day**. The x-axis uses hour as an **ordinal** category, and the y-axis uses month as an **ordinal** category. The number of reports is **quantitative** and controls cell color. I chose the sequential **viridis** scale because darker and brighter cells make differences in counts easier to see without implying that one month or hour belongs to a separate category. In Python, I extracted month and hour from the original date/time strings, discarded rows with unusable times, counted reports for each combination, and filled missing combinations with zero. I chose a heatmap instead of a line chart because my main question is about patterns within the day as well as across the calendar.

## Plot 2 — US states and reported shapes

<vegachart schema-url="{{ site.baseurl }}/assets/json/hw5_ufo_shape_states.json" style="width: 100%"></vegachart>

The second visualization is a bar chart comparing the number of reported sightings across **15 US states**. State is a **nominal** category on the y-axis, while the number of reports is a **quantitative** value on the x-axis. I also use a sequential **blues** color scale for the counts: darker bars correspond to larger totals, so color reinforces the numerical comparison rather than introducing another category. To prepare the data, I standardized country, state, and shape labels, kept US reports with two-letter state codes, selected the 15 states with the most reports overall and the 10 most commonly reported shapes, and grouped the data by state and shape. These are raw report totals, not population-adjusted rates, so a larger number should not be interpreted as a higher likelihood of a sighting.

The **Reported shape** dropdown is the interactive part of the second plot. Changing it updates the bars to show only reports with the selected shape, while keeping the same states visible. That makes it easier to compare how the geographic pattern changes for different descriptions. Hovering over a cell or bar also reveals the underlying count. I think the combination is useful because the first view highlights the timing of reports, while the second allows a more focused look at *where* people report particular kinds of sightings.

## Data and analysis

<div class="left">
{% include elements/button.html link="https://raw.githubusercontent.com/UIUC-iSchool-DataViz/is445_data/main/ufo-scrubbed-geocoded-time-standardized-00.csv" text="The Data" %}
</div>
<div class="right">
{% include elements/button.html link="https://github.com/Namzy100/Namzy100.github.io/blob/main/python_notebooks/HW5_UFO_Sightings.ipynb" text="The Analysis" %}
</div>

*Data source: [UIUC IS 445 course data repository](https://github.com/UIUC-iSchool-DataViz/is445_data). Source records are based on [NUFORC reports organized by the ufo-reports project](https://zenodo.org/records/1205624).*
