import gradio as gr
import os
import tempfile
import json
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
        
        # Create a simple preview by extracting a few sections from the structured content
        preview_html = create_content_preview(structured, idea)
        
        progress(1.0, "Complete!")
        return pdf_path, json_path, preview_html, f"✅ Successfully generated pitch deck for: '{idea}'"
    except Exception as e:
        return None, None, "<div class='error-preview'>Error generating content</div>", f"❌ Error: {str(e)}"

def create_content_preview(structured_content, idea):
    """
    Creates an HTML preview of the content without needing to render the PDF
    """
    try:
        # Create a preview of up to 3 sections
        sections_to_preview = ["Problem", "Solution", "Market Analysis"]
        
        html = "<div class='content-preview'>"
        html += f"<div class='preview-title'>{idea}</div>"
        
        # Add each section
        for section in sections_to_preview:
            if section in structured_content:
                html += f"<div class='preview-section'>"
                html += f"<div class='section-title'>{section}</div>"
                
                content = structured_content.get(section, "")
                
                # Handle different content types
                if isinstance(content, str):
                    # Split by periods for better readability
                    paragraphs = content.split(". ")
                    for para in paragraphs:
                        if para.strip():
                            html += f"<p>{para.strip()}</p>"
                
                elif isinstance(content, dict):
                    # Add description if available
                    if "Description" in content:
                        html += f"<p class='highlight'>{content['Description']}</p>"
                    
                    # Add other key-value pairs
                    for key, value in content.items():
                        if key != "Description":
                            if isinstance(value, list):
                                html += f"<div class='key-label'>{key}:</div>"
                                html += "<ul>"
                                for item in value[:3]:  # Limit to first 3 items
                                    html += f"<li>{item}</li>"
                                if len(value) > 3:
                                    html += "<li>...</li>"
                                html += "</ul>"
                            elif isinstance(value, dict):
                                html += f"<div class='key-label'>{key}:</div>"
                                html += "<ul>"
                                for sub_key, sub_value in list(value.items())[:3]:  # Limit to first 3 items
                                    html += f"<li><b>{sub_key}:</b> {sub_value}</li>"
                                if len(value) > 3:
                                    html += "<li>...</li>"
                                html += "</ul>"
                            else:
                                html += f"<p><b>{key}:</b> {value}</p>"
                
                elif isinstance(content, list):
                    html += "<ul>"
                    for item in content[:5]:  # Limit to first 5 items
                        html += f"<li>{item}</li>"
                    if len(content) > 5:
                        html += "<li>...</li>"
                    html += "</ul>"
                
                html += "</div>"  # Close section
        
        html += "<div class='preview-footer'>Download the PDF to view the complete presentation with images</div>"
        html += "</div>"  # Close preview
        
        return html
    except Exception as e:
        print(f"Error creating content preview: {e}")
        return f"<div class='error-preview'>Error creating content preview: {str(e)}</div>"

def main():
    """
    Create and launch the Gradio interface with improved design
    """
    # Custom CSS for better styling with enhanced colors
    custom_css = """
    body {
        background-color: #F3F4F6;
    }
    
    .gradio-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .gr-prose h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        background: linear-gradient(90deg, #6366F1, #10B981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }
    
    .gr-prose h2 {
        font-size: 1.25rem !important;
        font-weight: 500 !important;
        color: #6B7280 !important;
        margin-bottom: 1.5rem !important;
    }
    
    .gr-prose h3 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: #4F46E5 !important;
        margin-bottom: 1rem !important;
    }
    
    .footer {
        margin-top: 2rem;
        text-align: center;
        font-size: 0.85rem;
        color: #6B7280;
        padding: 1rem;
        background-color: white;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
    }
    
    .container {
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .features {
        display: flex;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .feature-card {
        flex: 1;
        padding: 1.25rem;
        border-radius: 8px;
        background: #F3F4F6;
        border: 1px solid #E5E7EB;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.05);
    }
    
    .feature-title {
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: #6366F1;
        font-size: 1.1rem;
    }
    
    /* Content Preview Styling */
    .content-preview {
        display: flex;
        flex-direction: column;
        gap: 15px;
        padding: 20px;
        border-radius: 8px;
        background-color: white;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
    }
    
    .preview-title {
        font-weight: 700;
        color: #4F46E5;
        font-size: 1.5rem;
        text-align: center;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #E5E7EB;
    }
    
    .preview-section {
        padding: 15px;
        border-radius: 8px;
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
        margin-bottom: 10px;
    }
    
    .section-title {
        font-weight: 600;
        color: white;
        background-color: #6366F1;
        padding: 8px 15px;
        border-radius: 6px;
        margin-bottom: 12px;
        display: inline-block;
    }
    
    .content-preview p {
        margin-bottom: 10px;
        line-height: 1.5;
    }
    
    .content-preview .highlight {
        color: #4F46E5;
        font-weight: 500;
    }
    
    .content-preview ul {
        margin-left: 20px;
        margin-bottom: 10px;
    }
    
    .content-preview li {
        margin-bottom: 5px;
    }
    
    .key-label {
        font-weight: 600;
        color: #4F46E5;
        margin-top: 10px;
        margin-bottom: 5px;
    }
    
    .preview-footer {
        color: #6B7280;
        text-align: center;
        font-style: italic;
        margin-top: 15px;
        padding-top: 10px;
        border-top: 1px solid #E5E7EB;
    }
    
    .error-preview {
        color: #EF4444;
        text-align: center;
        padding: 20px;
        border: 1px solid #FCA5A5;
        border-radius: 8px;
        background-color: #FEF2F2;
    }
    
    /* Override button styling */
    button.primary {
        background-color: #6366F1 !important;
        color: white !important;
    }
    
    button.primary:hover {
        background-color: #4F46E5 !important;
    }
    """
    
    with gr.Blocks(title="AI Pitch Deck Generator", theme=gr.themes.Soft(), css=custom_css) as demo:
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
                            <div class="feature-title">📝 1. Enter Your Idea</div>
                            Describe your startup concept in a few sentences
                            """)
                        
                        with gr.Column(elem_classes="feature-card"):
                            gr.Markdown("""
                            <div class="feature-title">🧠 2. AI Generation</div>
                            GPT-4o creates structured content for your pitch
                            """)
                        
                        with gr.Column(elem_classes="feature-card"):
                            gr.Markdown("""
                            <div class="feature-title">📊 3. Get Your Deck</div>
                            Preview and download your professional pitch deck
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
                    with gr.Accordion("API Keys (Required)", open=True):
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
                    submit_btn = gr.Button("Generate Pitch Deck", variant="primary", elem_classes="primary")
            
            # Output section
            with gr.Column(scale=2):
                with gr.Group(elem_classes="container"):
                    gr.Markdown("### Your Generated Pitch Deck")
                    
                    # Status output
                    status = gr.Textbox(
                        label="Status",
                        placeholder="Waiting for generation...",
                        interactive=False
                    )
                    
                    # Preview HTML
                    preview = gr.HTML(label="Content Preview", elem_classes="preview-container")
                    
                    # Outputs
                    with gr.Row():
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
            """<div class="footer">
            Last updated: 2025-06-21 22:42:12 | 
            Created by m01ali | 
            Powered by OpenRouter and Unsplash
            </div>""",
            elem_classes="footer"
        )
                
        # Set up button click handler with all inputs
        submit_btn.click(
            fn=generate_pitch_deck,
            inputs=[idea_input, openrouter_key, unsplash_key],
            outputs=[pdf_output, json_output, preview, status]
        )
    
    # Launch with a larger default height
    demo.launch(height=800)

if __name__ == "__main__":
    main()