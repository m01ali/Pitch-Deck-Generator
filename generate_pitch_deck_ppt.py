import json
import requests
import os
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from PIL import Image
from io import BytesIO

# === CONFIGURATION ===
# Check if API keys are set or prompt user to enter them
NOVITA_API_KEY = os.environ.get("NOVITA_API_KEY", None)
if not NOVITA_API_KEY or NOVITA_API_KEY == "YOUR_NOVITA_API_KEY":
    NOVITA_API_KEY = input("Enter your Novita AI API key: ")
    # Save to environment variable for future use
    os.environ["NOVITA_API_KEY"] = NOVITA_API_KEY

# For Unsplash, we need the Access Key (not the Secret Key)
# The Access Key is used as the Client-ID in API requests
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", None)
if not UNSPLASH_ACCESS_KEY or UNSPLASH_ACCESS_KEY == "YOUR_UNSPLASH_API_KEY":
    print("\nFor Unsplash images, you need to provide your Access Key (not Secret Key)")
    print("You can find your Access Key at: https://unsplash.com/oauth/applications")
    UNSPLASH_ACCESS_KEY = input("Enter your Unsplash Access Key: ")
    # Save to environment variable for future use
    os.environ["UNSPLASH_ACCESS_KEY"] = UNSPLASH_ACCESS_KEY

MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct-fp8"

client = OpenAI(
    base_url="https://api.novita.ai/v3/openai",
    api_key=NOVITA_API_KEY,
)

slide_order = [
    "Problem", "Solution", "Market Analysis", "Competitors",
    "Unique Selling Proposition (USP)", "Business Model",
    "Financial Projections", "Team Overview", "Call to Action"
]

def get_structured_content(idea):
    # Check if we have a valid API key
    if not NOVITA_API_KEY or NOVITA_API_KEY == "YOUR_NOVITA_API_KEY":
        raise ValueError("Novita AI API key is not set. Please set a valid API key.")
    
    prompt = f"""
    Generate a JSON object for a startup pitch deck based on the idea: '{idea}'.
    Include keys: Problem, Solution, Market Analysis, Competitors,
    Unique Selling Proposition (USP), Business Model, Financial Projections,
    Team Overview, Call to Action.
    Make sure the output is strictly valid JSON without any markdown formatting or explanatory text.
    The response should be a valid JSON object that can be parsed directly.
    """

    try:
        print("🔄 Generating content with LLaMA 4 Maverick...")  
        res = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that responds with valid JSON only. Do not include any explanatory text, markdown formatting, or code blocks in your response."},
                {"role": "user", "content": prompt}
            ],
            stream=False,
            max_tokens=4096,
            temperature=0.7,
            top_p=1,
            presence_penalty=0,
            frequency_penalty=0,
            response_format={"type": "json_object"},
            extra_body={"top_k": 50, "repetition_penalty": 1, "min_p": 0}
        )

        content = res.choices[0].message.content
        print("\n--- Raw Model Output ---\n", content)
        
        # Parse the JSON
        structured_content = json.loads(content)
        print("✅ Content generated successfully!")
        return structured_content
    
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        # Create a basic structure if parsing fails
        return {
            "Problem": "Failed to generate content. Please try again.",
            "Solution": "Failed to generate content. Please try again.",
            "Market Analysis": "Failed to generate content. Please try again.",
            "Competitors": "Failed to generate content. Please try again.",
            "Unique Selling Proposition (USP)": "Failed to generate content. Please try again.",
            "Business Model": "Failed to generate content. Please try again.",
            "Financial Projections": "Failed to generate content. Please try again.",
            "Team Overview": "Failed to generate content. Please try again.",
            "Call to Action": "Failed to generate content. Please try again."
        }
    
    except openai.AuthenticationError as e:
        print(f"❌ Authentication error: {e}")
        raise ValueError("Invalid API key. Please check your Novita AI API key and try again.")
    
    except openai.RateLimitError as e:
        print(f"❌ Rate limit exceeded: {e}")
        raise ValueError("API rate limit exceeded. Please try again later.")
    
    except openai.APIError as e:
        print(f"❌ API error: {e}")
        raise ValueError("An error occurred with the Novita AI API. Please try again later.")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise ValueError(f"An unexpected error occurred: {str(e)}. Please try again.")

def fetch_unsplash_image(query):
    # Check if we have a valid API key
    if not UNSPLASH_ACCESS_KEY or UNSPLASH_ACCESS_KEY == "YOUR_UNSPLASH_API_KEY":
        print(f"⚠️ Unsplash API key not set. Skipping image for '{query}'")
        return None
        
    # For Unsplash API, we need to use the Access Key as the Client-ID
    # The secret key is only used for server-side OAuth authentication
    url = f"https://api.unsplash.com/search/photos?query={query}&per_page=1"
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    
    try:
        print(f"🔍 Searching for image related to '{query}'...")
        response = requests.get(url, headers=headers)
        
        # Check for API errors
        if response.status_code != 200:
            print(f"⚠️ Unsplash API error: {response.status_code} - {response.text}")
            print("ℹ️ Make sure you're using your Unsplash Access Key, not the Secret key.")
            return None
            
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            image_url = data["results"][0]["urls"]["regular"]
            print(f"✅ Found image for '{query}', downloading...")
            image_response = requests.get(image_url)
            
            if image_response.status_code == 200:
                return BytesIO(image_response.content)
        
        print(f"❌ No image found for '{query}' or API limit reached")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error fetching image: {e}")
        return None
    except ValueError as e:
        print(f"❌ Invalid JSON response from Unsplash: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error fetching image: {e}")
        return None

def create_pdf(structured_content, title):
    # Define styles for our PDF document
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1F497D'),  # Dark blue
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#4472C4'),  # Medium blue
        spaceAfter=15,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1F497D'),  # Dark blue
        spaceAfter=15,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#323232'),  # Dark gray
        spaceAfter=10
    )
    
    highlight_style = ParagraphStyle(
        'Highlight',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#4472C4'),  # Medium blue
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    key_style = ParagraphStyle(
        'Key',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#4472C4'),  # Medium blue
        spaceAfter=5,
        fontName='Helvetica-Bold'
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#323232'),  # Dark gray
        leftIndent=20,
        spaceAfter=5,
        bulletIndent=10,
        bulletText='•'
    )
    
    # Create a safe filename by limiting length and removing invalid characters
    safe_title = title.lower()
    # Replace invalid filename characters
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        safe_title = safe_title.replace(char, '-')
    # Limit length to avoid path too long errors
    safe_title = safe_title[:50]  # Limit to 50 characters
    
    file_name = safe_title.replace(" ", "_") + "_pitch_deck.pdf"
    
    # Create the PDF document
    doc = SimpleDocTemplate(file_name, pagesize=letter)
    story = []  # This will hold all the elements of our document
    
    # Add title page
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph("Pitch Deck Generated with LLaMA 4 Maverick (Novita AI)", subtitle_style))
    story.append(Spacer(1, 1*inch))
    
    # Add each section
    for section in slide_order:
        # Add a page break before each section (except the first one)
        if section != slide_order[0]:
            story.append(Spacer(1, 0.5*inch))
        
        # Add section title
        story.append(Paragraph(section, section_title_style))
        story.append(Spacer(1, 0.25*inch))
        
        # Try to get an image for this section
        img_io = fetch_unsplash_image(section)
        if img_io:
            # Process the image for PDF
            try:
                with Image.open(img_io) as img:
                    # Save as temporary file
                    temp_img_path = f"temp_{section.lower().replace(' ', '_')}.jpg"
                    img.save(temp_img_path, format='JPEG')
                    
                    # Add image to the document
                    img = RLImage(temp_img_path, width=4*inch, height=3*inch)
                    story.append(img)
                    story.append(Spacer(1, 0.25*inch))
            except Exception as e:
                print(f"❌ Error processing image for {section}: {e}")
        
        # Handle different JSON structures
        content = structured_content.get(section, "")
        
        # If content is a string, split by periods
        if isinstance(content, str):
            for i, line in enumerate(content.split(". ")):
                if line.strip():
                    if i == 0:  # First paragraph is highlighted
                        story.append(Paragraph(line.strip(), highlight_style))
                    else:
                        story.append(Paragraph(line.strip(), normal_style))
        
        # If content is a dict, extract values
        elif isinstance(content, dict):
            # Add description if available
            if "Description" in content:
                story.append(Paragraph(content["Description"], highlight_style))
                story.append(Spacer(1, 0.1*inch))
            
            # Add other key-value pairs
            for key, value in content.items():
                if key != "Description":
                    # Handle nested lists
                    if isinstance(value, list):
                        story.append(Paragraph(f"{key}:", key_style))
                        
                        for item in value:
                            story.append(Paragraph(f"• {item}", bullet_style))
                    
                    # Handle nested dicts
                    elif isinstance(value, dict):
                        story.append(Paragraph(f"{key}:", key_style))
                        
                        for sub_key, sub_value in value.items():
                            story.append(Paragraph(f"• <b>{sub_key}:</b> {sub_value}", bullet_style))
                    
                    # Handle simple values
                    else:
                        story.append(Paragraph(f"<b>{key}:</b> {value}", normal_style))
        
        # If content is a list, add each item as a bullet point
        elif isinstance(content, list):
            story.append(Paragraph("Key Points:", key_style))
            
            for item in content:
                story.append(Paragraph(f"• {item}", bullet_style))
    
    # Build the PDF document
    doc.build(story)
    print(f"✅ Saved PDF as {file_name}")
    
    # Clean up temporary image files
    for section in slide_order:
        temp_img_path = f"temp_{section.lower().replace(' ', '_')}.jpg"
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
    
    # Save JSON
    json_name = safe_title.replace(" ", "_") + "_pitch_deck.json"
    with open(json_name, "w") as f:
        json.dump(structured_content, f, indent=4)
    print(f"✅ Saved structured content as {json_name}")
    
    # Return the full path to the PDF file
    return os.path.abspath(file_name)

if __name__ == "__main__":
    try:
        print("📊 Pitch Deck Generator - PDF Edition 📊")
        print("===========================================\n")
        
        idea = input("Enter your startup idea: ")
        if not idea.strip():
            print("❌ Error: Please enter a valid startup idea.")
            exit(1)
            
        print("\n🚀 Generating your pitch deck...\n")
        
        # Generate content
        structured = get_structured_content(idea)
        
        # Create PDF
        file_path = create_pdf(structured, idea)
        
        print("\n✨ All done! Your pitch deck has been created successfully.")
        print(f"📄 You can find your PDF at: {file_path}")
        
    except ValueError as e:
        print(f"\n❌ Error: {str(e)}")
        exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user.")
        exit(1)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")
        print("Please try again or report this issue.")
        exit(1)