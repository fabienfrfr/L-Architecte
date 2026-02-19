#set page(paper: "a4", margin: (x: 2cm, y: 2.5cm))
#set text(font: "New Computer Modern", size: 10.5pt, lang: "en")
#import "@preview/cetz:0.4.2": canvas, draw, tree

#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import fletcher.shapes: diamond


#import "@preview/pintorita:0.1.4"
#show raw.where(lang: "pintora"): it => pintorita.render(it.text)

#import "@preview/oxdraw:0.1.0": *


// --- Header ---
#align(center)[
  #block(inset: 10pt, stroke: 1pt + gray, radius: 5pt)[
    #text(size: 24pt, weight: "bold")[AgenticArchitect] \
    #text(size: 14pt, style: "italic", fill: gray)[Technical Documentation & Architecture]
  ]
]

#v(1cm)

= Introduction
*AgenticArchitect* is a local-first multi-agent system designed to transform raw requirements into production-ready AI and Data solutions. It leverages state-graph orchestration to automate the Software Development Life Cycle (SDLC).

= Technical Stack
The infrastructure, managed via `devbox.json`, ensures high performance and data sovereignty:

- *Orchestration*: #raw("K3d / K3s") for local Kubernetes clusters.
- *Development*: #raw("Skaffold") for hot-reloading and #raw("UV") for Python management.
- *AI Framework*: #raw("Pydantic AI") for agent logic and #raw("Ollama") (Qwen 3:0.6B) for local inference.
- *Observability*: #raw("Arize Phoenix") for tracing agentic workflows.

= Agentic Workflow
The system operates through four specialized roles:

+ *Project Manager Agent*: Validates SMART criteria and identifies gaps.
+ *Data Analyst Agent*: Handles EDA (Exploratory Data Analysis) and synthetic data generation.
+ *Architect Agent*: Designs C4 Diagrams and Architecture Decision Records (ADR).
+ *Engineer Agent*: Implements SOLID-compliant code using TDD principles.


#canvas({
  import draw: *
  let encircle(i) = {
    std.box(baseline: 2pt, std.circle(stroke: .5pt, radius: .5em)[#move(dx: -0.36em, dy: -1.1em, $#i$)])
  }

  set-style(content: (padding: 0.5em))
  tree.tree(
    ([Expression #encircle($5$)], (
        [Expression #encircle($3$)],
        ([Expression #encircle($1$)], `Int(1)`),
        `Plus`,
        ([Expression #encircle($2$)], `Int(2)`),
      ),
      `Lt`,
      ([Expression #encircle($4$)], `Int(4)`),
    ))
})


#diagram(
	node-stroke: 1pt,
	node((0,0), [Start], corner-radius: 2pt, extrude: (0, 3)),
	edge("-|>"),
	node((0,1), align(center)[
		Hey, wait,\ this flowchart\ is a trap!
	], shape: diamond),
	edge("d,r,u,l", "-|>", [Yes], label-pos: 0.1)
)

```pintora
componentDiagram
  DataQuery -- [Component]
  B -- [C]
  [Component] ..> HTTP : use
```

#oxdraw(
```
graph TD
A[Input] --> B[Process]
B --> C[Output]
```,
  background: white,
  overrides: (
    node_styles: (
      A: (fill: "#4CAF50", stroke: "#2E7D32", text: "white"),
      B: (fill: "#2196F3", stroke: "#1976D2"),
      C: (fill: "#FF9800", stroke: "#F57C00")
    ),
    edge_styles: (
      "A --> B": (color: "#666", line: "dashed"),
      "B --> C": (color: "#E91E63", arrow: "both")
    )
  )
)

= Quick Start
To initialize the development environment:

```bash
# Install tools and deploy the cluster
make install && make cluster && make setup-dev

# Start the pipeline with hot-reload
skaffold dev

```

Key Service Endpoints:

* *Architect App* *: `http://localhost:8080`

* *Phoenix UI* *: `http://localhost:6006`

* *Ollama API* *: `http://localhost:11434`

= License
This project is licensed under the *GNU Affero General Public License v3.0 (AGPL-3.0)*.
