import marimo

__generated_with = "0.19.6"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🏗️ TheArchitect: Minimalist R&D Lab
    **Author:** Fabien Furfaro
    **Project:** [AgenticArchitect](https://github.com/fabienfrfr/AgenticArchitect)

    > **Methodology:** Functional Testing (Playground Mode)
    > **Goal:** Testing ETL.
    """)
    return


@app.cell
def _():
    import re
    import pypdfium2 as pdfium
    from fastembed import TextEmbedding
    import numpy as np

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Extraction with Pdfium
    """)
    return


@app.cell
def _():
    a = 1
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Transformation with FastEmbed
    """)
    return


@app.cell
def _():
    b = 2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Load with ArangoDB
    """)
    return


@app.cell
def _():
    c = 3
    return


if __name__ == "__main__":
    app.run()
