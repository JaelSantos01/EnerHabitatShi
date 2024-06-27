from pathlib import Path
from shiny import App, ui, reactive, Session

from utils.helper_text import info_modal

page_dependencies = ui.tags.head(
    ui.tags.link(rel="stylesheet", type="text/css", href="layout.css"),
    ui.tags.link(rel="stylesheet", type="text/css", href="style.css"),
    ui.tags.script(src="index.js"),

    # PWA Support
    ui.tags.script("""

        async function delayManifest() {
            let retries = 100;
            let statusCode = 404;
            let response;

            while (statusCode === 404 && --retries > 0) {
                response = await fetch("pwa/manifest.json");
                statusCode = response.statusCode;
            }

            if (response.statusCode === 404) throw new Error('max retries reached');

            $('head').append('<link rel="manifest" href="pwa/manifest.json"/>');

            return response;
        }
        delayManifest();

        if('serviceWorker' in navigator) {
        navigator.serviceWorker
            .register('/respiratory_disease_pyshiny/pwa-service-worker.js', { scope: '/respiratory_disease_pyshiny/' })
            .then(function() { console.log('Service Worker Registered'); });
        }
    """),
    ui.tags.link(rel="apple-touch-icon", href="pwa/icon.png"),

    ui.tags.meta(name="description", content="Respiratory Disease PyShiny"),
    ui.tags.meta(name="theme-color", content="#000000"),
    ui.tags.meta(name="apple-mobile-web-app-status-bar-style", content="#000000"),
    ui.tags.meta(name="apple-mobile-web-app-capable", content="yes"),
    ui.tags.meta(name="viewport", content="width=device-width, initial-scale=1"),
)



app_ui = ui.page_fluid(
    page_dependencies,
    title="Respiratory Disease App",
)


def server(input, output, session: Session):

    info_modal()




www_dir = Path(__file__).parent / "www"
app = App(app_ui, server, static_assets=www_dir)