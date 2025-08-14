# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Run the Tool
```bash
python3 extract_email.py
```

### 3. Enter LinkedIn URL
When prompted, paste a LinkedIn profile URL like:
```
https://www.linkedin.com/in/johndoe/
```

## 📋 Available Scripts

| Script | Description | Best For |
|--------|-------------|----------|
| `extract_email.py` | Interactive script | **Recommended** - Easiest to use |
| `linkedin_email_extractor_robust.py` | Advanced with anti-detection | When LinkedIn blocks requests |
| `linkedin_email_extractor_advanced.py` | Uses Selenium | Dynamic content |
| `linkedin_email_extractor.py` | Basic version | Simple cases |

## 🎯 Example Usage

```bash
# Interactive mode (recommended)
python3 extract_email.py

# Command line mode
python3 linkedin_email_extractor_robust.py "https://www.linkedin.com/in/johndoe/"
```

## ⚠️ Important Notes

- **Public Profiles Only**: Works only with public LinkedIn profiles
- **Email Visibility**: The email must be publicly visible on the profile
- **Rate Limiting**: LinkedIn may block requests if too many are made
- **Legal Use**: Only extract emails that are publicly available

## 🔧 Troubleshooting

### "No email found" Error
- Profile might be private
- Email not publicly visible
- LinkedIn blocking requests

### Selenium Errors
- Install Chrome browser
- Download ChromeDriver
- Add to PATH

### Import Errors
- Run: `pip3 install -r requirements.txt`
- Use Python 3.6+

## 📞 Support

If you encounter issues:
1. Check the profile is public
2. Try a different LinkedIn profile
3. Wait a few minutes and try again
4. Use the interactive script for better error handling 