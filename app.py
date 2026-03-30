"""
Streamlit Web Interface for Chess Board Analyzer
Interactive web app for uploading and analyzing chess positions
"""

import streamlit as st
import json
import os
from pathlib import Path

from enhanced_pipeline import EnhancedChessBoardAnalyzerPipeline


def configure_streamlit():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Chess Board Analyzer",
        page_icon="♟️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def load_pipeline():
    """Load the analysis pipeline (cached)"""
    return EnhancedChessBoardAnalyzerPipeline(
        board_size=512,
        upload_dir=os.path.join(os.path.expanduser("~"), ".chess_analyzer_uploads")
    )


def display_board_visualization(board_matrix):
    """Display chess board with pieces"""
    if not board_matrix:
        return
    
    piece_symbols = {
        'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
        'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
    }
    
    board_html = "<div style='display: grid; grid-template-columns: repeat(8, 50px); gap: 0; border: 3px solid #333;'>"
    
    for i, row in enumerate(board_matrix):
        for j, piece in enumerate(row):
            is_light = (i + j) % 2 == 0
            bg_color = "#f0d9b5" if is_light else "#b58863"
            piece_display = piece_symbols.get(piece, '')
            
            board_html += f"""
            <div style='
                width: 50px;
                height: 50px;
                background-color: {bg_color};
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 30px;
                font-weight: bold;
                border: 1px solid #999;
            '>{piece_display}</div>
            """
    
    board_html += "</div>"
    st.markdown(board_html, unsafe_allow_html=True)


def display_evaluation_bar(eval_bar):
    """Display chess.com-style evaluation bar"""
    if not eval_bar:
        return
    
    white_pct = eval_bar.get('white_percentage', 50)
    black_pct = eval_bar.get('black_percentage', 50)
    score = eval_bar.get('numeric_display', '0.0')
    
    # Create horizontal bar
    bar_html = f"""
    <div style='display: flex; height: 40px; border: 2px solid #333; border-radius: 4px; overflow: hidden; margin: 1rem 0;'>
        <div style='background-color: #f0f0f0; width: {white_pct}%; display: flex; align-items: center; justify-content: flex-start; padding-left: 10px; font-weight: bold;'>
            {score}
        </div>
        <div style='background-color: #2c2c2c; width: {black_pct}%; display: flex; align-items: center; justify-content: flex-end; padding-right: 10px; color: white; font-weight: bold;'>
        </div>
    </div>
    <div style='display: flex; justify-content: space-between; font-size: 12px; margin-top: 5px;'>
        <span>White: {white_pct:.1f}%</span>
        <span>Black: {black_pct:.1f}%</span>
    </div>
    """
    st.markdown(bar_html, unsafe_allow_html=True)


def main():
    """Main Streamlit app"""
    configure_streamlit()
    
    # Header
    st.markdown("<h1 style='text-align: center;'>♟️ Chess Board Analyzer 2.0</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>AI-Powered Chess Position Analysis</p>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        white_to_move = st.radio(
            "Who's to move?",
            ["White", "Black"],
            help="Assume white or black to move"
        ) == "White"
        
        save_json = st.checkbox("Save JSON output", value=True)
        
        st.divider()
        st.markdown("### About")
        st.info("""
        Upload a chess board image (screenshot or photo) to analyze:
        - Board detection
        - Piece classification
        - Position evaluation
        - Chess.com-style analysis
        """)
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📤 Analyze", "📊 Results", "📋 Help"])
    
    with tab1:
        st.header("Upload Chess Board Image")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Supported Formats")
            st.write("• PNG\n• JPG/JPEG\n• BMP\n• TIFF")
            st.markdown("### Size Requirements")
            st.write("• Min: 200×200 px\n• Max: 4096×4096 px\n• Max file: 10 MB")
        
        with col2:
            uploaded_file = st.file_uploader(
                "Choose chess board image",
                type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
                help="Upload a clear image of a chess board"
            )
        
        if uploaded_file is not None:
            st.divider()
            
            # Show uploaded image
            st.subheader("Uploaded Image")
            image_data = uploaded_file.read()
            st.image(image_data, use_column_width=True)
            
            # Save uploaded file temporarily
            temp_path = f"/tmp/{uploaded_file.name}"
            with open(temp_path, 'wb') as f:
                f.write(image_data)
            
            # Analyze button
            if st.button("🔍 Analyze Position", key="analyze_btn", use_container_width=True):
                with st.spinner("🔄 Analyzing position... This may take a minute..."):
                    try:
                        # Load pipeline
                        pipeline = load_pipeline()
                        
                        # Analyze
                        json_path = f"/tmp/{uploaded_file.name.split('.')[0]}_analysis.json" if save_json else None
                        output = pipeline.analyze_uploaded_image(
                            temp_path,
                            white_to_move=white_to_move,
                            save_json=json_path
                        )
                        
                        # Store in session
                        st.session_state.analysis_output = output
                        st.session_state.json_path = json_path
                        
                        # Success message
                        st.success("✅ Analysis complete!")
                        
                        # Show results summary
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Board Detect", f"{output.board_confidence:.1%}")
                        with col2:
                            st.metric("Evaluation", f"{output.total_score:+.1f}p")
                        with col3:
                            st.metric("Best Side", output.best_side.title())
                        with col4:
                            st.metric("Time", f"{output.processing_time:.1f}s")
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
                        st.exception(e)
    
    with tab2:
        if 'analysis_output' in st.session_state and st.session_state.analysis_output.success:
            output = st.session_state.analysis_output
            
            st.header("Analysis Results")
            
            # Position section
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("📋 Position")
                if output.board_matrix:
                    display_board_visualization(output.board_matrix)
            
            with col2:
                st.subheader("📊 Evaluation")
                
                if output.eval_bar:
                    st.markdown("### Position Evaluation")
                    display_evaluation_bar(output.eval_bar)
                    
                    st.markdown(f"**{output.eval_bar['explanation']}**")
                
                # FEN
                st.markdown("### FEN Notation")
                st.code(output.fen, language="text")
                
                # Metrics
                st.markdown("### Evaluation Breakdown")
                col1, col2, col3 = st.columns(3)
                with col1:
                    material = output.evaluation_scores.get('material_score', 0)
                    st.metric("Material", f"{material:+.2f}p")
                with col2:
                    mobility = output.evaluation_scores.get('mobility_score', 0)
                    st.metric("Mobility", f"{mobility:+.2f}p")
                with col3:
                    king_safety = output.evaluation_scores.get('king_safety_score', 0)
                    st.metric("King Safety", f"{king_safety:+.2f}p")
            
            st.divider()
            
            # Analysis section
            st.subheader("🧠 Analysis")
            st.write(output.analysis_summary)
            
            col1, col2 = st.columns(2)
            with col1:
                if output.strengths:
                    st.markdown("**✅ Strengths:**")
                    for strength in output.strengths:
                        st.write(f"• {strength}")
                if output.weaknesses:
                    st.markdown("**⚠️ Weaknesses:**")
                    for weakness in output.weaknesses:
                        st.write(f"• {weakness}")
            
            with col2:
                if output.key_highlights:
                    st.markdown("**🎯 Key Highlights:**")
                    for highlight in output.key_highlights:
                        st.write(f"• {highlight}")
            
            st.divider()
            
            # JSON Output
            st.subheader("📄 JSON Export")
            json_str = json.dumps(output.json_output, indent=2)
            st.code(json_str, language="json")
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name="analysis.json",
                    mime="application/json"
                )
            with col2:
                if 'json_path' in st.session_state and st.session_state.json_path:
                    try:
                        with open(st.session_state.json_path, 'r') as f:
                            st.download_button(
                                label="📥 Download Full Report",
                                data=f.read(),
                                file_name="chess_analysis_report.json",
                                mime="application/json"
                            )
                    except:
                        pass
        else:
            st.info("📤 Upload an image in the 'Analyze' tab to see results here")
    
    with tab3:
        st.header("How to Use")
        
        st.subheader("1️⃣ Upload Image")
        st.write("""
        - Take a clear screenshot or photo of your chess board
        - Make sure the board is well-lit and clearly visible
        - Supported formats: PNG, JPG, BMP, TIFF
        """)
        
        st.subheader("2️⃣ Configure Settings")
        st.write("""
        - Select whose turn it is in the sidebar
        - Choose whether to save JSON output
        """)
        
        st.subheader("3️⃣ Analyze")
        st.write("""
        - Click the "Analyze Position" button
        - The AI will:
          - Detect the chess board
          - Recognize all pieces using CNN
          - Convert to FEN notation
          - Evaluate the position
          - Generate a chess.com-style analysis bar
        """)
        
        st.subheader("4️⃣ Review Results")
        st.write("""
        - See the board visualization
        - Check the evaluation score and bar
        - Read the detailed analysis
        - Download the results as JSON
        """)
        
        st.divider()
        
        st.subheader("About the AI")
        st.info("""
        **Chess Board Analyzer 2.0** uses:
        - **CNN**: ResNet18 fine-tuned for chess piece recognition
        - **Evaluation**: 6-feature engine (material, mobility, king safety, pawn structure, center control, piece-square tables)
        - **Analysis**: Human-readable summaries similar to chess.com
        """)


if __name__ == "__main__":
    main()
