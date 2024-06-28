from htmltools import TagList, tags

def custom_section():
    return TagList(
        tags.section(
            tags.br(),
            tags.div(
                tags.h1("Python el futuro de la programación"),
                tags.p(
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do "
                    "eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut "
                    "enim ad minim veniam, quis nostrud exercitation ullamco laboris "
                    "nisi ut aliquip ex ea commodo consequat."
                ),
                style=(
                "text-align: justify; "
                "word-break: break-word; "
                "hyphens: auto;"
                ),
            ),
            tags.br(),
            tags.div(
                tags.iframe(
                    width="355",
                    height="240",
                    src="https://www.youtube.com/embed/r3I9TLnFIqU?si=TqO0PGKqvyJbthdO",
                    title="YouTube video player",
                    frameborder="0",
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture",
                    allowfullscreen=True
                ),
                style=(
                "text-align: justify; "
                "word-break: break-word; "
                "hyphens: auto;"
                ),
            ),
            tags.hr(),
        )
    )

def respiratory_diseases_app():
    return TagList(
        custom_section(),
        tags.strong(tags.h4("Problem Statement")),
        tags.p(
            (
                "Air Pollution has always been a problem for the world and over "
                "the years, especially with the pandemic, the ambient air pollution "
                "seems to be a slow burn for the entire population of the planet. "
                "Through this app, we wish to explore the relationship between "
                "the PM2.5 particulate metric and the Death Rate "
                "(defined as deaths per 100,000) from respiratory "
                "illnesses over the world over the years."
            ),
            style=(
                "text-align: justify; "
                "word-break: break-word; "
                "hyphens: auto;"
            ),
        )
    )


