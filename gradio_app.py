import gradio as gr
import os
import tempfile
from generate_pitch_deck_ppt import get_structured_content, create_pdf

# Initialize API keys from environment variables (will be overridden by UI inputs)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")

def generate_pitch_deck(idea, openrouter_key, unsplash_key):
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
            
        # Generate structured content
        structured = get_structured_content(idea)
        
        # Create PDF
        pdf_path = create_pdf(structured, idea)
        
        # Get the corresponding JSON path
        json_path = pdf_path.replace(".pdf", ".json")
        
        return pdf_path, json_path
    except Exception as e:
        raise gr.Error(f"An error occurred: {str(e)}")

def main():
    """
    Create and launch the Gradio interface
    """
    with gr.Blocks(title="Pitch Deck Generator", theme="soft") as demo:
        gr.Markdown("# 🚀 AI-Powered Pitch Deck Generator")
        gr.Markdown("Generate professional pitch decks for your startup ideas using GPT-4o")
        
        with gr.Row():
            with gr.Column():
                idea_input = gr.Textbox(
                    label="Your Startup Idea",
                    placeholder="Describe your startup idea in 1-2 sentences...",
                    lines=3
                )
                submit_btn = gr.Button("Generate Pitch Deck", variant="primary")
                
                # API key inputs
                with gr.Accordion("API Keys (Optional)", open=False):
                    openrouter_key = gr.Textbox(
                        label="OpenRouter API Key",
                        type="password",
                        placeholder="Leave blank to use environment variable or be prompted"
                    )
                    unsplash_key = gr.Textbox(
                        label="Unsplash Access Key",
                        type="password",
                        placeholder="Leave blank to use environment variable or be prompted"
                    )
                
            with gr.Column():
                # Outputs
                pdf_output = gr.File(label="Generated PDF")
                json_output = gr.File(label="Structured Content (JSON)")
                
                # Status output
                status = gr.Textbox(label="Status", interactive=False)
                
        # Set up button click handler with all inputs
        submit_btn.click(
            fn=generate_pitch_deck,
            inputs=[idea_input, openrouter_key, unsplash_key],
            outputs=[pdf_output, json_output]
        )
        
        # Add some examples
        gr.Examples(
            examples=[
                "An AI-powered platform that helps small businesses optimize their social media marketing",
                "A mobile app that uses gamification to teach financial literacy to teenagers",
                "A SaaS platform that automates inventory management for e-commerce businesses"
            ],
            inputs=[idea_input]
        )
        
    # Launch immediately with share=False for local use
    # When deploying to HuggingFace, it will automatically handle the launch
    demo.launch(share=False)

if __name__ == "__main__":
    # Skip the main() function and launch directly
    with gr.Blocks(title="Pitch Deck Generator", theme="soft") as demo:
        gr.Markdown("# 🚀 AI-Powered Pitch Deck Generator")
        gr.Markdown("Generate professional pitch decks for your startup ideas using GPT-4o")
        
        with gr.Row():
            with gr.Column():
                idea_input = gr.Textbox(
                    label="Your Startup Idea",
                    placeholder="Describe your startup idea in 1-2 sentences...",
                    lines=3
                )
                submit_btn = gr.Button("Generate Pitch Deck", variant="primary")
                
                # API key inputs (now required in the UI)
                with gr.Accordion("API Keys (Required)", open=True):
                    openrouter_key = gr.Textbox(
                        label="OpenRouter API Key",
                        type="password",
                        placeholder="Enter your OpenRouter API key",
                        value=OPENROUTER_API_KEY
                    )
                    unsplash_key = gr.Textbox(
                        label="Unsplash Access Key",
                        type="password",
                        placeholder="Enter your Unsplash Access Key",
                        value=UNSPLASH_ACCESS_KEY
                    )
                
            with gr.Column():
                # Outputs
                pdf_output = gr.File(label="Generated PDF")
                json_output = gr.File(label="Structured Content (JSON)")
                
                # Status output
                status = gr.Textbox(label="Status", interactive=False)
                
        # Set up button click handler with all inputs
        submit_btn.click(
            fn=generate_pitch_deck,
            inputs=[idea_input, openrouter_key, unsplash_key],
            outputs=[pdf_output, json_output]
        )
        
        # Add some examples
        gr.Examples(
            examples=[
                "An AI-powered platform that helps small businesses optimize their social media marketing",
                "A mobile app that uses gamification to teach financial literacy to teenagers",
                "A SaaS platform that automates inventory management for e-commerce businesses"
            ],
            inputs=[idea_input]
        )
    
    demo.launch()