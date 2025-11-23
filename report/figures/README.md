# Figures Directory

Place your figures and diagrams here.

## Recommended Figures

1. **cluster_visualization.png** - 2D PCA projection showing HDBSCAN clusters
2. **architecture_diagram.png** - System architecture diagram (Docker containers)
3. **confusion_matrix.png** - Model confusion matrix visualization
4. **feature_importance.png** - Feature importance plot
5. **mlflow_ui.png** - Screenshot of MLflow experiment tracking
6. **dashboard_screenshot.png** - Streamlit dashboard screenshot
7. **api_swagger.png** - FastAPI Swagger UI screenshot
8. **pipeline_flowchart.png** - ML pipeline flowchart

## Creating Figures

### From Python/Matplotlib

```python
import matplotlib.pyplot as plt

# Your plot code
fig, ax = plt.subplots(figsize=(10, 6))
# ... plotting ...

# Save with high DPI for LaTeX
plt.savefig('figures/my_plot.png', dpi=300, bbox_inches='tight')
```

### From Plotly

```python
import plotly.graph_objects as go

fig = go.Figure(...)
fig.write_image('figures/my_plot.png', width=1200, height=800)
```

### From Screenshots

- Use Snipping Tool (Windows) or Screenshot utility (Mac/Linux)
- Save as PNG or JPG
- Recommended resolution: 1920x1080 or higher

## Format Guidelines

- **Vector graphics**: PDF format preferred (matplotlib can save as PDF)
- **Raster graphics**: PNG format, minimum 300 DPI
- **File naming**: lowercase with underscores (e.g., `confusion_matrix.png`)
- **Size**: Keep images under 5 MB each

## Usage in LaTeX

```latex
\begin{figure}[h]
\centering
\includegraphics[width=0.8\textwidth]{figures/your_image.png}
\caption{Your caption here}
\label{fig:your_label}
\end{figure}
```

## Tools for Creating Diagrams

- **Architecture diagrams**: [draw.io](https://draw.io), [Lucidchart](https://www.lucidchart.com/)
- **Flowcharts**: [Mermaid](https://mermaid.js.org/), TikZ (LaTeX native)
- **Network diagrams**: Graphviz, Gephi
- **Data visualizations**: Python (Matplotlib, Plotly, Seaborn)
