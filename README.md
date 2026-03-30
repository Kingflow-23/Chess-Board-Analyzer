# Chess Board Analyzer 🏆

AI-powered system for analyzing chess positions from images. Upload a board photo and get instant evaluation with detailed analysis.

## 🎯 What It Does

- **📷 Image Recognition** - Detects chess boards and pieces from photos/screenshots
- **♟️ Position Analysis** - Converts board to FEN notation
- **⚙️ Smart Evaluation** - 6-feature evaluation engine rates positions
- **📊 Visual Feedback** - Chess.com-style evaluation bars
- **📝 JSON Export** - Complete analysis in machine-readable format

## 🚀 Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Run Web App
**Windows PowerShell:**
```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path
streamlit run app.py
```

**Windows (Alternative - one line):**
```powershell
$env:PYTHONPATH = "$((Resolve-Path .\src).Path)"; streamlit run app.py
```

**Linux/Mac:**
```bash
export PYTHONPATH="$(pwd)/src"
streamlit run app.py
```

### 3. Or Run Demo
```bash
python demo_lightweight.py
```

### 4. Or Run Tests
```bash
python tests/test_evaluation.py
```
✅ Result: 17/17 tests pass

## 📁 Project Files

```
Chess-Board-Analyzer/
├── app.py                          # Web interface (Streamlit)
├── demo_lightweight.py             # Quick demo
├── requirements.txt                # Dependencies
│
├── src/
│   ├── enhanced_pipeline.py        # Main orchestrator
│   ├── cv_module/                  # Board & piece detection
│   ├── evaluation_engine/          # Position evaluation
│   ├── position_module/            # FEN conversion  
│   ├── visualization/              # Eval bars
│   ├── output_formatter.py         # JSON output
│   └── upload_handler.py           # Image validation
│
└── tests/
    └── test_evaluation.py          # 17 unit tests

README.md          # This file
SETUP.md          # Detailed setup guide
ARCHITECTURE.md   # Technical details
```

## 💻 How to Use

### Web Interface (Recommended)
```bash
streamlit run app.py
```
- Upload chess board images (PNG, JPG, BMP, TIFF)
- Get instant analysis with evaluation bar
- Download results as JSON

### Python Code
```python
from enhanced_pipeline import EnhancedChessBoardAnalyzerPipeline

pipeline = EnhancedChessBoardAnalyzerPipeline()
result = pipeline.analyze_uploaded_image("chess.jpg", white_to_move=True)

print(result.fen)              # FEN notation
print(result.total_score)      # Evaluation score
print(result.best_side)        # Who's winning
print(result.json_output)      # Full JSON
```

## 🧪 Run Tests

```bash
python tests/test_evaluation.py
```

Tests include:
- ✅ Evaluation engine (7 tests)
- ✅ Evaluation bars (5 tests)
- ✅ JSON output (2 tests)
- ✅ Upload validation (2 tests)
- ✅ Integration tests (1 test)

**Result**: ✅ **17/17 PASSED**

## 📊 Evaluation Features

The engine analyzes 6 independent aspects:

1. **Material Balance** - Piece values (Pawn=1, Knight=3, etc.)
2. **Mobility** - Number of legal moves available
3. **King Safety** - Pawn shield, open lines, threats
4. **Pawn Structure** - Doubled, isolated, advanced pawns
5. **Center Control** - Control of d4, e4, d5, e5 squares
6. **Piece-Square Tables** - Positional bonuses

Total score combines all features into centipawns (100cp = 1 pawn worth advantage).

## 📋 JSON Output

```json
{
  "status": "success",
  "position": {
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "board_matrix": [[...]], 
    "whose_turn": "white"
  },
  "evaluation": {
    "total_score": 0.5,
    "best_side": "white",
    "features": {
      "material_balance": 0.0,
      "mobility": 0.5,
      "king_safety": 0.0,
      "pawn_structure": 0.0,
      "center_control": 0.0,
      "piece_square_tables": 0.0
    }
  },
  "bar": {
    "white_percentage": 55.2,
    "black_percentage": 44.8,
    "centipawn_score": 52,
    "evaluation_type": "white_slightly_better"
  },
  "analysis": {
    "summary": "Balanced position with slight white advantage",
    "strengths": ["Good piece coordination"],
    "weaknesses": ["Exposed king"],
    "key_highlights": ["Control center"]
  }
}
```

## ⚙️ Configuration

### Setting Python Path (Windows)
```powershell
$env:PYTHONPATH = "$env:PYTHONPATH;$(Get-Location)\src"
python app.py
```

### Or Linux/Mac
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python app.py
```

## 🔧 Troubleshooting

### Import Error
```
ModuleNotFoundError: No module named 'enhanced_pipeline'
```
**Solution**: Set PYTHONPATH (see Configuration section)

### PyTorch Error
**Solution**: Use demo without PyTorch:
```bash
python demo_lightweight.py
```

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup instructions
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture
- **[tests/](tests/)** - Example tests showing usage

## 📦 Dependencies

- `python-chess` - Chess notation and validation
- `opencv-python` - Image processing
- `numpy` - Numerical computation
- `torch` - Neural networks (optional, for CNN classifier)
- `streamlit` - Web interface (optional)

See [requirements.txt](requirements.txt) for versions.

## ✅ Project Status

- ✅ Core pipeline working
- ✅ Evaluation engine complete
- ✅ JSON output integrated
- ✅ Full test coverage (17 tests)
- ✅ Streamlit web app
- ✅ Demo scripts
- ✅ Production ready

---

**Last Updated**: March 30, 2026  
**Status**: ✅ **COMPLETE & TESTED**
