from pathlib import Path
from shiny import App, ui, reactive, Session

from utils.helper_text import info_modal



app_ui = ui.page_fluid(
    title="Respiratory Disease App",
)


def server(input, output, session: Session):

    info_modal()




www_dir = Path(__file__).parent / "www"
app = App(app_ui, server, static_assets=www_dir)