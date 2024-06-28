from shiny.ui import modal_show, modal, modal_button
from htmltools import TagList, tags

def info_modal(show_modal):
    if show_modal:
        modal_show(
            modal(
                tags.strong(tags.h3("Respiratory Diseases App")),
                tags.p("Exploring Relationships between PM2.5 & Respiratory Diseases"),
                tags.hr(),
                tags.strong(tags.h4("Problem Statement")),
                tags.p(
                    """
                    Air Pollution has always been a problem for the world and over
                    the years, especially with the pandemic, the ambient air pollution
                    seems to be a slow burn for the entire population of the planet.
                    Through this app, we wish to explore the relationship between
                    the PM2.5 particulate metric and the Death Rate
                    (defined as deaths per 100,000) from respiratory
                    illnesses over the world over the years.
                    """,
                    style="""
                    text-align: justify;
                    word-break: break-word;
                    hyphens: auto;
                    """,
                ),
                size="l",
                easy_close=True,
                footer=modal_button("Close"),
            )
        )
