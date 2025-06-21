# Pitch Deck Generator

A Python tool that automatically generates professional pitch decks for startup ideas using GPT4o and Unsplash images.

## Features

- **AI-Powered Content Generation**: Uses GPT4o to create structured content for your pitch deck
- **Professional PDF Format**: Generates beautifully formatted PDF documents with consistent styling
- **Relevant Images**: Automatically fetches relevant images from Unsplash for each section
- **Comprehensive Structure**: Includes all essential pitch deck sections:
  - Problem
  - Solution
  - Market Analysis
  - Competitors
  - Unique Selling Proposition (USP)
  - Business Model
  - Financial Projections
  - Team Overview
  - Call to Action
- **Error Handling**: Robust error handling for API issues, network problems, and user interruptions
- **JSON Export**: Saves the structured content as a JSON file for further use or editing

## Requirements

- Python 3.8+
- Required Python packages (see Installation)
- OpenRouter API key (for GPT-4o access)
- Unsplash API Access Key (for images)

## Installation

1. Clone this repository or download the script

2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
.\venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux
```

3. Install the required packages:

```bash
pip install openai reportlab pillow requests PyMuPDF
```


## API Keys Setup

### OpenRouter API Key

1. Sign up for an OpenRouter account at [https://openrouter.ai](https://openrouter.ai)
2. Navigate to your account settings to find your API key
3. Set it as an environment variable or enter it when prompted by the script

### Unsplash API Key

1. Create a developer account at [https://unsplash.com/developers](https://unsplash.com/developers)
2. Create a new application to get your Access Key
3. Use your **Access Key** (not Secret Key) when prompted by the script

## Usage

1. Run the script (CLI):

```bash
python generate_pitch_deck_ppt.py
```

* For interface: 

```bash
python gradio_app.py
```

2. Enter your startup idea when prompted

3. The script will:
   - Generate structured content 
   - Fetch relevant images from Unsplash
   - Create a professionally formatted PDF
   - Save both the PDF and the structured JSON content


## Output Files

The script generates two files:

1. **PDF Pitch Deck**: A professionally formatted presentation with all sections and images
2. **JSON Content File**: The structured content that can be used for other purposes or edited manually

## Troubleshooting

### API Authentication Errors

- For Novita AI: Ensure you're using the correct API key from your account
- For Unsplash: Make sure you're using the Access Key (not the Secret Key) as prompted

### Image Fetching Issues

- Check your internet connection
- Verify your Unsplash API key is correct
- Unsplash has rate limits for free accounts; you might hit these limits with frequent use

## License

MIT

## Acknowledgements

- [Unsplash](https://unsplash.com) for the image API
- [ReportLab](https://www.reportlab.com/) for PDF generation
- [OpenAI](https://openai.com) for the client library structure