# LinkedIn Email Extractor (Improved)

A Python tool to extract email addresses from LinkedIn profile URLs. This improved version can take a specific LinkedIn profile URL and attempt to extract the email address from that profile.

## Features

- **Direct URL Processing**: Input a LinkedIn profile URL and get the email
- **Multiple Extraction Methods**: Uses various techniques to find emails
- **Advanced Web Scraping**: Includes Selenium support for dynamic content
- **Email Validation**: Filters out invalid or test email addresses
- **User-Friendly Interface**: Simple interactive script for easy use

## Installation

1. **Clone or download the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **For Selenium support (optional but recommended)**:
   - Install Chrome browser
   - Download ChromeDriver from: https://chromedriver.chromium.org/
   - Add ChromeDriver to your PATH or place it in the same directory

## Usage

### Method 1: Interactive Script (Recommended)
```bash
python3 extract_email.py
```
Then enter the LinkedIn profile URL when prompted.

### Method 2: Command Line
```bash
# Basic version
python3 linkedin_email_extractor.py "https://www.linkedin.com/in/johndoe/"

# Advanced version (with Selenium)
python3 linkedin_email_extractor_advanced.py "https://www.linkedin.com/in/johndoe/"
```

### Method 3: As a Python Module
```python
from linkedin_email_extractor_advanced import LinkedInEmailExtractorAdvanced

extractor = LinkedInEmailExtractorAdvanced()
result = extractor.extract_email_from_linkedin_url("https://www.linkedin.com/in/johndoe/")

if "error" not in result:
    print(f"Email: {result['email']}")
    print(f"Method: {result['method']}")
else:
    print(f"Error: {result['error']}")
```

## How It Works

The tool uses multiple methods to extract emails:

1. **Selenium WebDriver**: Loads the page in a browser and searches for email patterns
2. **Direct Scraping**: Downloads the page HTML and searches for email patterns
3. **Contact Info Section**: Attempts to access the contact information overlay
4. **Profile Data**: Searches through JSON data embedded in the page
5. **About Section**: Checks the about section for email information

## Email Patterns Detected

The tool can find emails in various formats:
- Standard: `user@domain.com`
- Obfuscated: `user[at]domain[dot]com`
- Spaced: `user @ domain . com`
- Text-based: `user at domain dot com`

## Limitations

- **Profile Privacy**: Only works with public LinkedIn profiles
- **Email Visibility**: The email must be publicly visible on the profile
- **Rate Limiting**: LinkedIn may block requests if too many are made
- **Dynamic Content**: Some profiles use JavaScript to load content dynamically

## Troubleshooting

### "No email found" Error
- Make sure the LinkedIn profile is public
- The email might not be publicly visible
- Try a different LinkedIn profile

### Selenium Errors
- Install Chrome browser
- Download and install ChromeDriver
- Make sure ChromeDriver is in your PATH

### Import Errors
- Install all dependencies: `pip install -r requirements.txt`
- Make sure you're using Python 3.6+

## Files Description

- `extract_email.py` - Interactive script for easy use
- `linkedin_email_extractor.py` - Basic version using requests
- `linkedin_email_extractor_advanced.py` - Advanced version with Selenium
- `requirements.txt` - Python dependencies
- `lee.py` - Original script (uses Google API)

## Legal and Ethical Considerations

⚠️ **Important**: This tool is for educational purposes only. Please:

- Respect LinkedIn's Terms of Service
- Only extract emails from profiles where the information is publicly available
- Use the extracted emails responsibly and in compliance with applicable laws
- Don't use for spam or unsolicited communications
- Consider reaching out through LinkedIn's messaging system first

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details. 