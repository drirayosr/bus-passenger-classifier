# LaTeX Report - Bus Passenger Classification MLOps Project

This folder contains **two versions** of the technical report:

1. **Full Report** (`main.tex`) - 40-45 pages comprehensive documentation
2. **Short Report** (`report_short.tex`) - 5 pages concise version

## 📄 Report Versions

### 🔹 Short Report (5 pages) - **RECOMMENDED FOR QUICK READ**

**File:** `report_short.tex`

**Content:**
- Abstract with project overview
- Brief introduction and problem statement
- **Methodology:** Feature engineering, PCA, HDBSCAN clustering
- **Implementation:** All 7 phases (pipeline, DVC, MLflow, API, dashboard, Docker, CI/CD)
- Results: Performance metrics, hyperparameters, system performance
- Conclusion: Key achievements, lessons learned, future work

**Compile:**
```bash
# Windows
compile_short.bat

# Linux/Mac
pdflatex report_short.tex
pdflatex report_short.tex
```

**Output:** `report_short.pdf` (~5 pages)

---

### 🔹 Full Report (40-45 pages) - **COMPREHENSIVE VERSION**

**File:** `main.tex`

**Content:**
- Introduction (motivation, problem, scope, contributions)
- Background (MLOps principles, tools, related work)
- Methodology (detailed feature engineering, algorithms)
- Implementation (code examples, all 7 phases in detail)
- Results (confusion matrix, experiments, error analysis)
- Deployment (architecture, Docker, CI/CD, monitoring, scalability)
- Conclusion (lessons, limitations, future work)
- Appendices (code samples, configs, metrics)
- Bibliography

**Compile:**
```bash
# Windows
compile.bat

# Linux/Mac
make
```

**Output:** `main.pdf` (~40-45 pages)

## 📁 Structure

```
report/
├── report_short.tex      # SHORT: 5-page concise report ⭐
├── main.tex              # FULL: 40-page comprehensive report
├── references.bib        # Bibliography (for full report)
├── compile_short.bat     # Compile short report (Windows)
├── compile.bat           # Compile full report (Windows)
├── Makefile              # Compile full report (Linux/Mac)
├── sections/             # Full report sections
│   ├── 01_introduction.tex
│   ├── 02_background.tex
│   ├── 03_methodology.tex
│   ├── 04_implementation.tex
│   ├── 05_results.tex
│   ├── 06_deployment.tex
│   ├── 07_conclusion.tex
│   └── appendix.tex
├── figures/              # Images and diagrams
└── README.md             # This file
```

## 🔧 Prerequisites

### Option 1: Local LaTeX Installation

**Windows:**
- Install [MiKTeX](https://miktex.org/download) or [TeX Live](https://www.tug.org/texlive/)

**macOS:**
- Install [MacTeX](https://www.tug.org/mactex/)
```bash
brew install --cask mactex
```

**Linux:**
```bash
sudo apt-get install texlive-full  # Ubuntu/Debian
sudo dnf install texlive-scheme-full  # Fedora
```

### Option 2: Online LaTeX Editor

Upload the entire `report/` folder to:
- [Overleaf](https://www.overleaf.com/) (recommended)
- [ShareLaTeX](https://www.sharelatex.com/)

## 📝 Compiling the Reports

### Quick Start - Short Report (5 pages)

**Windows:**
```bash
cd report
compile_short.bat
```

**Linux/Mac:**
```bash
cd report
pdflatex report_short.tex
pdflatex report_short.tex  # Run twice for references
```

### Full Report (40 pages)

**Windows:**
```bash
cd report
compile.bat
```

**Linux/Mac:**
```bash
cd report
make
```

### Alternative Methods

```bash
cd report/

# Compile main document
pdflatex main.tex

# Generate bibliography
bibtex main

# Compile again (2x) for references
pdflatex main.tex
pdflatex main.tex
```

### Method 2: Using latexmk (automated)

```bash
cd report/
latexmk -pdf main.tex
```

### Method 3: Using VS Code

1. Install extension: [LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop)
2. Open `main.tex`
3. Press `Ctrl+Alt+B` (Windows/Linux) or `Cmd+Option+B` (macOS)

### Method 4: Makefile (if you have `make`)

```bash
cd report/
make          # Compile PDF
make clean    # Remove auxiliary files
make view     # Open PDF viewer
```

## 📊 Adding Figures

Place image files in the `figures/` folder, then reference them in LaTeX:

```latex
\begin{figure}[h]
\centering
\includegraphics[width=0.8\textwidth]{figures/my_plot.png}
\caption{Description of the figure}
\label{fig:my_label}
\end{figure}
```

Supported formats: PNG, JPG, PDF (vector graphics recommended)

## 📖 Report Sections

1. **Introduction** (5 pages)
   - Motivation, problem statement, project scope, contributions

2. **Background** (4 pages)
   - MLOps principles, tools (DVC, MLflow, FastAPI, Docker), related work

3. **Methodology** (6 pages)
   - Data description, feature engineering, PCA, HDBSCAN clustering

4. **Implementation** (8 pages)
   - 7-phase MLOps pipeline, code organization, testing strategy

5. **Results** (6 pages)
   - Model performance (F1=0.596), confusion matrix, hyperparameter tuning

6. **Deployment** (6 pages)
   - Architecture, Docker, CI/CD, monitoring, scalability

7. **Conclusion** (5 pages)
   - Lessons learned, limitations, future work

**Appendices** (6 pages)
- Code examples, configuration files, project metrics

**Total: ~40-45 pages**

## ✏️ Customization

### Update Author Information

Edit `main.tex`, lines 63-68:

```latex
\author{
    Your Name \\
    \textit{Your University} \\
    \texttt{your.email@example.com}
}
```

### Change Document Style

Modify packages and settings in `main.tex`, lines 1-50.

### Add/Remove Sections

Comment out sections in `main.tex`:

```latex
% \input{sections/06_deployment}  % Skip this section
```

## 📚 LaTeX Resources

- [Overleaf Documentation](https://www.overleaf.com/learn)
- [LaTeX Wikibook](https://en.wikibooks.org/wiki/LaTeX)
- [CTAN Package Repository](https://ctan.org/)

## 🐛 Troubleshooting

### Missing Packages

```bash
# MiKTeX (Windows)
mpm --install=<package-name>

# TeX Live (Linux/Mac)
tlmgr install <package-name>
```

### Bibliography Not Showing

Ensure you run the full compilation sequence:
```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Figures Not Appearing

- Check file path: `figures/image.png` (case-sensitive on Linux/Mac)
- Ensure image file exists
- Try PDF format for vector graphics

## 📤 Export Options

### PDF (default)
```bash
pdflatex main.tex
```

### Word Document (via pandoc)
```bash
pandoc main.tex -o report.docx --bibliography=references.bib
```

### HTML
```bash
htlatex main.tex
```

## 📄 License

This report template is part of the Bus Passenger Classification MLOps project.
For educational purposes.

## 📧 Contact

For questions about the report content or LaTeX compilation, refer to the main project README or contact the project team.
