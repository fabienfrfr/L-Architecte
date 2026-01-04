from nicegui import ui
from typing import Callable, Dict, Any


class ArchitectLayout:
    def __init__(self, on_start: Callable):
        # This allows NiceGUI to use the 'github' icon name
        ui.add_head_html(
            '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">'
        )

        self.on_start = on_start

        # Header setup
        with ui.header().classes(
            "items-center justify-between bg-white border-b px-4 py-2"
        ):
            ui.label("TheArchitect").classes("text-xl font-bold text-black")
            # We use an explicit FontAwesome class for GitHub
            with ui.link(
                target="https://github.com/fabienfrfr/AgenticArchitect", new_tab=True
            ):
                ui.element("i").classes(
                    "fa-brands fa-github text-3xl text-black hover:text-gray-600"
                )

        self.container = ui.column().classes("w-full items-center")
        self.setup_ui()

    def setup_ui(self):
        with self.container:
            # 1. Main Input Section (Requirements first)
            with ui.card().classes(
                "w-2/3 q-pa-md mt-10 shadow-lg border-t-4 border-black"
            ):
                ui.label("Agentic Requirements Analysis").classes("text-h4 mb-4")

                self.req_input = ui.textarea(
                    label="Project Requirements",
                    placeholder="Describe your project here...",
                ).classes("w-full")

                ui.button(
                    "START AGENTIC WORKFLOW",
                    on_click=lambda: self.on_start(self.req_input.value),
                ).classes("w-full mt-4 bg-black text-white")

                self.spinner = ui.spinner(size="lg").classes("mt-4")
                self.spinner.set_visibility(False)

                self.results_area = ui.column().classes("w-full mt-6")

            # 2. System Architecture Section (Graph second)
            with ui.card().classes("w-2/3 q-pa-md mt-5 shadow-2xl"):
                ui.label("System Architecture").classes("text-h6 mb-2")
                self.graph_card = ui.column().classes("w-full items-center")

    def update_graph(self, compiled_graph):
        """
        Updates the UI with the actual Mermaid diagram from LangGraph
        """
        self.graph_card.clear()
        with self.graph_card:
            try:
                # Fix: draw_mermaid() for text output doesn't need draw_method
                # It returns the Mermaid string directly
                mermaid_code = compiled_graph.get_graph().draw_mermaid()
                mermaid_code = mermaid_code.replace("graph TD", "graph LR").replace(
                    "graph TB", "graph LR"
                )
                ui.mermaid(mermaid_code).classes("w-full")
            except Exception as e:
                # Fallback if Mermaid fails: display as ASCII
                try:
                    ascii_graph = compiled_graph.get_graph().draw_ascii()
                    ui.pre(ascii_graph).classes("text-xs")
                except:
                    ui.label(f"Error loading graph: {str(e)}").classes("text-red")

    def toggle_loader(self, visible: bool):
        self.spinner.set_visibility(visible)

    def display_results(self, result: Dict[str, Any]):
        self.results_area.clear()
        with self.results_area:
            ui.label("Analysis Results").classes("text-h6 border-b w-full mb-2")
            ui.json_editor({"content": {"json": result}}).classes("w-full")
