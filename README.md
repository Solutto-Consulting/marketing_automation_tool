# Marketing Automation Tool for Odoo 18.0

## 📋 Overview

The Marketing Automation Tool is a comprehensive content management module for Odoo 18.0 that centralizes and simplifies marketing and content management tasks. This module integrates with external automation tools like n8n to provide semi-automated workflows for content translation and other marketing operations.

## 🚀 Features

### Version 1.0
- **Automation Service Configuration**: Centralized configuration panel for n8n API integration
- **Blog Post Translation Workflow**: Semi-automated translation process with status tracking
- **External Service Integration**: Secure communication with n8n automation hub
- **Translation Status Management**: Complete lifecycle tracking of translation requests
- **Multi-language Support**: Built-in Spanish translation (100% coverage)

## 🏗️ Architecture

### Models
- **Blog Post Extension**: Adds translation status tracking to `blog.post`
- **Configuration Settings**: Extends `res.config.settings` for automation service setup
- **Translation Wizard**: Transient model for language selection and batch operations

### Controllers
- **Translation Callback Endpoint**: Secure HTTP endpoint for receiving translations from n8n
- **Authentication**: Token-based security for external service communication

### Views
- **Enhanced Blog Post Views**: Added translation status columns and action buttons
- **Configuration Interface**: User-friendly setup in General Settings
- **Translation Wizard**: Intuitive interface for initiating translations

## 📱 User Interface

### Blog Post Management
- **Status Column**: Visual indicators for translation progress
- **Action Button**: "Send to Translate" option in list and form views
- **Filtering**: Search and group by translation status
- **Status Badge**: Color-coded translation status indicators

### Configuration
- **Settings Panel**: Located in Settings > General Settings > Marketing Automation
- **Secure Fields**: Password-protected token storage
- **Validation**: Real-time configuration validation

## 🔒 Security

### Access Control
- **Role-based Access**: Restricted to Website Designers and System Administrators
- **Secure Endpoints**: Token-based authentication for external communications
- **Data Validation**: Comprehensive input validation and sanitization

### Groups and Permissions
- `website.group_website_designer`: Access to translation features
- `base.group_system`: Full administrative access

## 🔧 Technical Implementation

### Translation Workflow
1. **User Selection**: Select blog posts and target language via wizard
2. **Validation**: Check for ongoing translations and language conflicts  
3. **API Request**: Send structured JSON to n8n with authentication
4. **Status Tracking**: Update translation status to "In Progress"
5. **Callback Processing**: Receive and store translations via secure endpoint
6. **Translation Storage**: Utilize Odoo's `ir.translation` mechanism

### API Integration
- **Outbound**: Secure POST requests to n8n with Bearer token authentication
- **Inbound**: Protected callback endpoint with token validation
- **Error Handling**: Comprehensive error management and logging

### Data Structure
```json
{
  "post_id": 123,
  "source_lang": "es_ES",
  "target_lang": "en_US",
  "callback_url": "https://domain.com/marketing_tool/translation_callback",
  "content_to_translate": {
    "name": "Article Title",
    "subtitle": "Article Subtitle", 
    "content": "<h1>HTML Content</h1>",
    "website_meta_title": "SEO Title",
    "website_meta_description": "SEO Description",
    "website_meta_keywords": "keyword1, keyword2"
  }
}
```

## ⚙️ Configuration

### Initial Setup
1. **Install Module**: Install from Apps menu
2. **Configure Automation Service**: 
   - Navigate to Settings > General Settings
   - Find "Marketing Automation" section
   - Set n8n Hub URL and Authentication Token
3. **Set Permissions**: Ensure users have appropriate access rights

### n8n Integration
- **Endpoint URL**: Configure your n8n webhook endpoint
- **Authentication**: Generate and configure Bearer token
- **Callback URL**: Ensure Odoo instance is accessible from n8n

## 📊 Translation Status Workflow

```
Not Translated → In Progress → Translated
                      ↓
                   Failed
```

### Status Descriptions
- **Not Translated**: Default state for new blog posts
- **In Progress**: Article sent to translation service
- **Translated**: Translation completed and stored
- **Failed**: Error occurred during translation process

## 🌐 Multi-language Support

### Supported Languages
- **English**: Primary development language
- **Spanish (es_ES)**: Complete translation (100% coverage)

### Translation Fields
- Article title and subtitle
- Content (HTML)
- SEO meta title, description, and keywords

## 🔍 Usage Examples

### Single Article Translation
1. Open blog post in form view
2. Click "Send to Translate" button
3. Select target language
4. Monitor status in status badge

### Batch Translation
1. Navigate to blog post list view
2. Select multiple articles
3. Actions > "Send to Translate"
4. Choose target language
5. Track progress via status column

## 🛠️ Technical Requirements

### Dependencies
- `base`: Core Odoo functionality
- `website`: Website management features
- `website_blog`: Blog post functionality

### External Dependencies
- **requests**: HTTP client for API communication
- **json**: JSON data processing

### Odoo Version
- **Odoo 18.0**: Fully compatible with latest version
- **Breaking Changes**: Uses `<list>` tags (not `<tree>`)

## 📈 Performance Considerations

### Optimization Features
- **Batch Processing**: Handle multiple articles efficiently
- **Async Communication**: Non-blocking external API calls
- **Error Recovery**: Robust error handling and status management
- **Database Efficiency**: Optimized queries and minimal database impact

### Scalability
- **Queue Support**: Ready for future queued job implementation
- **Rate Limiting**: Built-in protection against API abuse
- **Resource Management**: Efficient memory and CPU usage

## 🔧 Development Guidelines

### Code Standards
- **Language**: All code and comments in English
- **Documentation**: Comprehensive docstrings and inline documentation
- **Testing**: Built-in error handling and validation
- **Logging**: Detailed logging for debugging and monitoring

### Attribution
- **Company**: Solutto Consulting LLC
- **Developer**: Gilson Rincón (gilson.rincon@soluttoconsulting.com)
- **Role**: CEO and Founder

## 📋 Complete Documentation

### Quick Access by Role:
- **👤 [User Guide](docs/functional/user_guide.md)** - Complete step-by-step user manual
- **👔 [Business Processes](docs/functional/business_processes.md)** - Standard operating procedures  
- **👨‍💻 [Development Guide](docs/technical/development_guide.md)** - Technical development patterns
- **🔒 [Security & Roles](docs/functional/roles_permissions.md)** - Access control and permissions
- **📊 [Reports Guide](docs/functional/reports_guide.md)** - Analytics and reporting
- **🔧 [API Reference](docs/technical/api_reference.md)** - Complete API documentation

## 🆘 Support

### Getting Help
- **Documentation**: Comprehensive guides for all user types
- **Support Contact**: Solutto Consulting LLC
- **Developer**: gilson.rincon@soluttoconsulting.com

### Common Issues
- **Configuration**: Verify n8n URL and token settings
- **Permissions**: Ensure proper user group assignments
- **Connectivity**: Check network connectivity to n8n instance
- **Status Stuck**: Review error logs for detailed troubleshooting

## 📄 License

This module is licensed under LGPL-3.

---

**Developed with ❤️ by Solutto Consulting LLC**
