# Domain Checker - Production Ready Security Tool

A comprehensive domain security analysis tool that helps identify potentially suspicious or fraudulent websites. Built with Python and Tkinter, featuring advanced security checks, caching, and a modern user interface.

## 🚀 Quick Start for Users

**1. Download:**
-  [DomainChecker-Package.zip](./DomainChecker-Package.zip) (20MB)

**2. Extract:**
- Unzip the file to any folder (e.g., your Desktop)

**3. Install:**
- Open the extracted `Distribution` folder
- **Right-click** `install.bat` and select **"Run as administrator"**
- Follow the prompts (a desktop icon will be created)

**4. Use:**
- Double-click the "Domain Checker" desktop icon to launch the app

---

## 🚀 Features

### Core Security Checks
- **WHOIS Information**: Complete domain registration details
- **DNS Resolution**: IP address and domain resolution status
- **SSL Certificate Validation**: Certificate validity and expiration
- **Domain Age Analysis**: Registration date and age calculation
- **Suspicious Indicators**: Pattern detection and risk assessment
- **Blacklist Checking**: Integration with AbuseIPDB
- **Malware Detection**: VirusTotal integration
- **Social Media Presence**: Cross-platform verification

### User Experience
- **Modern GUI**: Clean, intuitive interface with dark/light mode
- **Real-time Progress**: Loading indicators during checks
- **History Management**: Track previously checked domains
- **Export Options**: CSV and PDF export functionality
- **Copy to Clipboard**: Easy result sharing
- **Summary/Detailed Views**: Toggle between concise and comprehensive results
- **Settings Panel**: Configure API keys and preferences

### Production Features
- **Secure Configuration**: Encrypted API key storage
- **Comprehensive Logging**: Debug, error, and analytics logging
- **Caching System**: Performance optimization with file and memory cache
- **Rate Limiting**: API call management to prevent abuse
- **Error Handling**: Graceful failure recovery
- **Input Validation**: Robust domain format checking

## 📋 Requirements

- Windows 10/11
- No Python installation required
- Internet connection for API calls

## 🛠️ Installation (Advanced/Developers)

If you want to run from source or build your own executable, see below for advanced instructions.

### Option 1: Run from Source

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/domain-checker.git
   cd domain-checker
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys** (optional but recommended):
   ```bash
   cp config.env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

### Option 2: Standalone Executable

1. **Build the executable**:
   ```bash
   python build.py
   ```

2. **Run the installer** (Windows):
   ```bash
   install.bat
   ```

3. **Or run directly**:
   ```bash
   ./dist/DomainChecker.exe
   ```

## 🔑 API Key Setup

For full functionality, obtain API keys from these services:

### Required APIs
- **VirusTotal**: [Get API Key](https://www.virustotal.com/gui/join-us)
- **AbuseIPDB**: [Get API Key](https://www.abuseipdb.com/api)

### Optional APIs
- **DNS Tracking**: Your preferred DNS tracking service

### Configuration
1. Open the application
2. Click "Settings"
3. Enter your API keys
4. Click "Save"

## 📖 Usage

### Basic Usage
1. **Enter Domain**: Type a domain name (e.g., `example.com`)
2. **Check Domain**: Click "Check Domain" or press Enter
3. **View Results**: Review the comprehensive security analysis
4. **Export/Share**: Use export buttons or copy to clipboard

### Advanced Features
- **History**: Click on any domain in the history list to re-check
- **View Modes**: Toggle between summary and detailed views
- **Settings**: Configure API keys and preferences
- **Dark Mode**: Enable in settings for better eye comfort

### Understanding Results

#### Risk Score (0-100)
- **0-20**: Safe - Low risk domain
- **21-40**: Low - Minor concerns
- **41-60**: Medium - Moderate risk indicators
- **61-80**: High - Multiple suspicious factors
- **81-100**: Critical - High risk, avoid

#### Key Indicators
- **Domain Age**: Newer domains (< 30 days) are higher risk
- **SSL Certificate**: Invalid or expired certificates increase risk
- **Suspicious Patterns**: Unusual domain names or registrars
- **Blacklist Status**: Presence in security databases
- **Malware Detection**: Positive scans from antivirus engines

## 🏗️ Architecture

```
domain-checker/
├── main.py                 # Main application entry point
├── build.py               # PyInstaller build script
├── requirements.txt       # Python dependencies
├── config.env.example     # Configuration template
├── services/
│   └── domain_checker.py  # Core domain checking logic
├── utils/
│   ├── config.py          # Configuration management
│   ├── logger.py          # Logging system
│   ├── validators.py      # Input validation
│   └── cache.py           # Caching and rate limiting
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables
```bash
# API Keys
DNS_TRACKING_API_KEY=your_key_here
VIRUSTOTAL_API_KEY=your_key_here
ABUSEIPDB_API_KEY=your_key_here

# Application Settings
ENABLE_ANALYTICS=false
ENABLE_CRASH_REPORTING=false
DARK_MODE=false
AUTO_UPDATE=true
```

### Settings Panel
Access via the "Settings" button in the main interface:
- **API Keys**: Configure external service keys
- **Preferences**: Toggle features and appearance
- **Dark Mode**: Switch between light and dark themes

## 📊 Logging

Logs are stored in `~/.domain_checker/logs/`:
- `app.log`: General application logs
- `errors.log`: Error and exception logs
- `analytics.log`: Usage analytics (if enabled)

## 🚀 Performance

- **Caching**: Results cached for 1 hour by default
- **Rate Limiting**: Prevents API abuse
- **Background Processing**: Non-blocking UI during checks
- **Memory Management**: Automatic cleanup of old cache entries

## 🔒 Security

- **Encrypted Storage**: API keys encrypted using Fernet
- **Local Data**: All data stored locally, no cloud dependencies
- **Input Sanitization**: Robust domain validation
- **Error Handling**: Secure error messages without data leakage

## 🐛 Troubleshooting

### Common Issues

**"API key not configured"**
- Open Settings and enter your API keys
- Some features work without API keys

**"Domain check failed"**
- Check your internet connection
- Verify domain format (e.g., `example.com`, not `http://example.com`)
- Check logs in `~/.domain_checker/logs/`

**"Build failed"**
- Ensure PyInstaller is installed: `pip install pyinstaller`
- Check Python version compatibility

### Log Files
Check log files for detailed error information:
```bash
# View recent errors
tail -f ~/.domain_checker/logs/errors.log

# View application logs
tail -f ~/.domain_checker/logs/app.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [python-whois](https://github.com/richardpenman/whois) for WHOIS lookups
- [VirusTotal](https://www.virustotal.com/) for malware detection
- [AbuseIPDB](https://www.abuseipdb.com/) for blacklist checking
- [PyInstaller](https://pyinstaller.org/) for executable packaging

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/domain-checker/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/domain-checker/wiki)
- **Email**: support@domainchecker.com

---

**⚠️ Disclaimer**: This tool is for educational and security research purposes. Always verify results independently and use responsibly.
