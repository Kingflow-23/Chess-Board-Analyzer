# Chess Board Analyzer - Setup & Usage

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Python Path
**Windows PowerShell:**
```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path
```

**Windows (CMD):**
```cmd
for /f %i in ('cd') do set PYTHONPATH=%i\src
```

**Linux/Mac:**
```bash
export PYTHONPATH="$(pwd)/src"
```

### 3. Run Applications

**Web App (Recommended):**
```bash
streamlit run app.py
```
Visit: http://localhost:8501

**Lightweight Demo:**
```bash
python demo_lightweight.py
```

**Run Tests:**
```bash
python tests/test_evaluation.py
```

---

## 📁 Project Structure

```
Chess-Board-Analyzer/
├── app.py                          # Production web interface
├── demo_lightweight.py             # Demo (no PyTorch needed)
├── requirements.txt                # Dependencies
├── README.md                       # Full documentation
├── ARCHITECTURE.md                 # Technical architecture
├── src/
│   ├── enhanced_pipeline.py        # Main pipeline orchestrator
│   ├── upload_handler.py           # Image validation
│   ├── output_formatter.py         # JSON output
│   ├── cv_module/
│   │   ├── board_detection.py      # Chess board detection
│   │   ├── cnn_classifier.py       # Neural network classifier
│   │   └── preprocessing.py        # Image preprocessing
│   ├── evaluation_engine/
│   │   ├── evaluator.py            # 6-feature evaluation
│   │   ├── features.py             # Feature extraction
│   │   └── weights.py              # Evaluation weights
│   ├── position_module/
│   │   └── fen_converter.py        # FEN conversions
│   ├── explanation_layer/
│   │   └── __init__.py             # Analysis generation
│   └── visualization/
│       └── eval_bar.py             # Evaluation bars
├── tests/
│   ├── test_evaluation.py          # 17 unit tests
│   └── test_fen_conversion.py      # FEN tests
└── data/
    ├── models/
    └── test_images/
```

---

## 💻 How to Use

### Option 1: Web App (Recommended)
```bash
streamlit run app.py
```
- Upload chess board images
- Get instant analysis
- Download results as JSON

### Option 2: Demo Script
```bash
python demo_lightweight.py
```
Shows core functionality without image processing.

### Option 3: Python Code
```python
from enhanced_pipeline import EnhancedChessBoardAnalyzerPipeline

# Initialize
pipeline = EnhancedChessBoardAnalyzerPipeline()

# Analyze image
result = pipeline.analyze_uploaded_image("chess.jpg", white_to_move=True)

# Access results
print(result.fen)              # Chess notation
print(result.total_score)      # Evaluation score
print(result.best_side)        # Who is winning
print(result.json_output)      # Complete JSON
```

---

## 🧪 Running Tests

```bash
# Run all tests
python tests/test_evaluation.py

# Or with pytest
pytest tests/
```

Tests cover:
- ✅ Evaluation engine (7 tests)
- ✅ Evaluation bars (5 tests)  
- ✅ JSON output (2 tests)
- ✅ Upload handling (2 tests)
- ✅ Integration tests (1 test)

---

## 🔧 Technical Details

### Evaluation Features
1. **Material Balance** - Piece values
2. **Mobility** - Legal moves available
3. **King Safety** - Pawn shield protection
4. **Pawn Structure** - Pawn quality
5. **Center Control** - Control of d4, e4, d5, e5
6. **Piece-Square Tables** - Positional bonuses

### Output Format
```json
{
  "status": "success",
  "position": {
    "fen": "...",
    "board_matrix": [...],
    "whose_turn": "white"
  },
  "evaluation": {
    "total_score": 0.5,
    "features": {...}
  },
  "bar": {
    "white_percentage": 55.0,
    "black_percentage": 45.0,
    "centipawn_score": 50
  },
  "analysis": {
    "summary": "...",
    "strengths": [...],
    "weaknesses": [...]
  }
}
```

---

## ⚠️ Troubleshooting

### Import Error: `ModuleNotFoundError`
**Solution**: Set PYTHONPATH
```powershell
$env:PYTHONPATH = "$env:PYTHONPATH;$(Get-Location)\src"
python your_script.py
```

### PyTorch Not Found
**Solution**: Use lightweight demo or install PyTorch
```bash
# Use demo without PyTorch:
python demo_lightweight.py

# Or install PyTorch:
pip install torch torchvision
```

### Streamlit Port in Use
**Solution**: Use different port
```bash
streamlit run app.py --server.port 8502
```

---

## 📚 Full Documentation
See **README.md** for complete technical details.
See **ARCHITECTURE.md** for system design.

---

**Status**: ✅ Production Ready
