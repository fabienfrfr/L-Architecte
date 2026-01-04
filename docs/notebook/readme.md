# 🏗️ TheArchitect: Notebooks

This directory contains the R&D playground for **TheArchitect**.

### ⚡ Interactive Format

We use the **Python Interactive Script** format (`# %%`).

* **Persistent Memory**: Loads **Gemma 3 270m** once; stays in RAM for all cells.
* **Clean Repo**: No `.ipynb` or `.html` junk. Just pure `.py` files.
* **Doc**: Markdown comments are rendered live in the VS Code sidebar.

### 🔍 Journey to this format

We moved away from other tools to maintain a "Zero Pollution" policy:

* **Runme**: No memory between cells.
* **Jupyter (.ipynb)**: Messy JSON for Git.
* **Quarto**: Generated too many unwanted cache files.

### ⚡ The Essential VSCODE Shortcuts

* **Single line / Selection:** Press `Ctrl` + `/`.
* **Block (Multi-line):** Press `Ctrl` + `Shift` + `A`.

---

### 🎨 Special Notebook Comments

Since you are using the **Interactive Python** format, these specific comments act as "commands":

* **`# %%`**: Creates a new **executable cell**.
* **`# %% [markdown]`**: Creates a **documentation cell** that renders as clean text in the sidebar.
* **`# TODO:`**: Highlighted by most themes to track pending tasks in your agents.