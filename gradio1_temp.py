import gradio as gr
import os
import tempfile
from datetime import datetime
from generate_pitch_deck_ppt import get_structured_content, create_pdf

# Initialize API keys from environment variables (will be overridden by UI inputs)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")

def generate_pitch_deck(idea, openrouter_key, unsplash_key, progress=gr.Progress()):
    """
    Wrapper function for the pitch deck generator that works with Gradio
    Returns the path to the generated PDF and JSON files
    """
    try:
        # Update API keys from UI inputs
        if openrouter_key:
            os.environ["OPENROUTER_API_KEY"] = openrouter_key
        if unsplash_key:
            os.environ["UNSPLASH_ACCESS_KEY"] = unsplash_key
            
        # Validate we have required API keys
        if not os.environ.get("OPENROUTER_API_KEY"):
            raise ValueError("OpenRouter API key is required")
        
        progress(0.1, "Initializing...")
            
        # Generate structured content
        progress(0.2, "Generating content with GPT-4o...")
        structured = get_structured_content(idea)
        
        progress(0.6, "Creating PDF presentation...")
        # Create PDF
        pdf_path = create_pdf(structured, idea)
        
        # Get the corresponding JSON path
        json_path = pdf_path.replace(".pdf", ".json")
        
        progress(1.0, "Complete!")
        return pdf_path, json_path, f"✅ Successfully generated pitch deck for: '{idea}'"
    except Exception as e:
        return None, None, f"❌ Error: {str(e)}"

def main():
    """
    Create and launch the Gradio interface with improved design
    """
    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .gr-prose h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        background: linear-gradient(90deg, #4285F4, #0F9D58);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }
    .gr-prose h2 {
        font-size: 1.25rem !important;
        font-weight: 500 !important;
        color: #5A5A5A !important;
        margin-bottom: 1.5rem !important;
    }
    .footer {
        margin-top: 2rem;
        text-align: center;
        font-size: 0.85rem;
        color: #666;
    }
    .container {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background: white;
    }
    .features {
        display: flex;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    .feature-card {
        flex: 1;
        padding: 1rem;
        border-radius: 8px;
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
    }
    .feature-title {
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #4285F4;
    }
    .accordion .label {
        font-weight: 600 !important;
    }
    """
    
    with gr.Blocks(title="AI Pitch Deck Generator", theme=gr.themes.Soft(primary_hue="blue"), css=custom_css) as demo:
        gr.Markdown("# 🚀 AI-Powered Pitch Deck Generator")
        gr.Markdown("## Transform your startup idea into a professional pitch deck in seconds using GPT-4o")
        
        with gr.Row():
            with gr.Column(scale=2):
                # Features section
                with gr.Group(elem_classes="container"):
                    gr.Markdown("### How It Works")
                    
                    with gr.Row(elem_classes="features"):
                        with gr.Column(elem_classes="feature-card"):
                            gr.Markdown("""
                            <div class="feature-title">1. Enter Your Idea</div>
                            Describe your startup concept in a few sentences
                            """)
                        
                        with gr.Column(elem_classes="feature-card"):
                            gr.Markdown("""
                            <div class="feature-title">2. AI Generation</div>
                            GPT-4o creates structured content for your pitch
                            """)
                        
                        with gr.Column(elem_classes="feature-card"):
                            gr.Markdown("""
                            <div class="feature-title">3. Get Your Deck</div>
                            Download a professional PDF with relevant images
                            """)
                
                # Input section
                with gr.Group(elem_classes="container"):
                    gr.Markdown("### Your Startup Idea")
                    idea_input = gr.Textbox(
                        label="",
                        placeholder="Describe your startup idea in 1-2 sentences...",
                        lines=4,
                        elem_id="idea-input"
                    )
                    
                    # API key inputs in accordion
                    with gr.Accordion("API Keys (Required)", open=True, elem_classes="accordion"):
                        with gr.Row():
                            with gr.Column():
                                openrouter_key = gr.Textbox(
                                    label="OpenRouter API Key",
                                    type="password",
                                    placeholder="Enter your OpenRouter API key",
                                    value=OPENROUTER_API_KEY,
                                    info="Get your key at openrouter.ai"
                                )
                            with gr.Column():
                                unsplash_key = gr.Textbox(
                                    label="Unsplash Access Key",
                                    type="password",
                                    placeholder="Enter your Unsplash Access Key",
                                    value=UNSPLASH_ACCESS_KEY,
                                    info="Get your key at unsplash.com/developers"
                                )
                    
                    # Examples
                    gr.Markdown("### Example Ideas")
                    examples = gr.Examples(
                        examples=[
                            "An AI-powered platform that helps small businesses optimize their social media marketing strategies with minimal effort.",
                            "A mobile app that uses gamification to teach financial literacy and investment basics to teenagers through fun challenges.",
                            "A SaaS platform that automates inventory management for e-commerce businesses using predictive analytics and machine learning.",
                            "A sustainable food delivery service that connects local farmers directly with urban consumers to reduce food waste."
                        ],
                        inputs=[idea_input],
                        label=""
                    )
                    
                    # Generate button
                    submit_btn = gr.Button("Generate Pitch Deck", variant="primary", size="lg")
            
            # Output section
            with gr.Column(scale=1):
                with gr.Group(elem_classes="container"):
                    gr.Markdown("### Your Generated Pitch Deck")
                    
                    # Status output
                    status = gr.Textbox(
                        label="Status",
                        placeholder="Waiting for generation...",
                        interactive=False
                    )
                    
                    # Outputs
                    pdf_output = gr.File(label="Download PDF Presentation")
                    json_output = gr.File(label="Download JSON Content")
                    
                    # Information box
                    with gr.Accordion("About This Tool", open=False):
                        gr.Markdown("""
                        This tool generates professional pitch decks using GPT-4o through OpenRouter.
                        
                        **What's included in your pitch deck:**
                        - Problem & Solution
                        - Market Analysis
                        - Competition Overview
                        - Unique Selling Proposition
                        - Business Model
                        - Financial Projections
                        - Team Overview
                        - Call to Action
                        
                        Images are sourced from Unsplash based on each section's content.
                        """)
        
        # Footer
        gr.Markdown(
            f"""<div class="footer">
            Last updated: 2025-06-21 | 
            Created by m01ali | 
            Powered by OpenRouter and Unsplash
            </div>""",
            elem_classes="footer"
        )
                
        # Set up button click handler with all inputs
        submit_btn.click(
            fn=generate_pitch_deck,
            inputs=[idea_input, openrouter_key, unsplash_key],
            outputs=[pdf_output, json_output, status]
        )
    
    # Launch with a larger default height
    demo.launch(height=800)

if __name__ == "__main__":
    main()