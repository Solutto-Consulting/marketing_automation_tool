# SC Marketing Automation Tool

AI-powered content management and blog translation automation for Odoo 18.0

## 📋 Complete Documentation

**📚 [Complete Documentation Index](docs/INDEX.md)**

### Quick Access by Role:
- **👤 [User Guide](docs/functional/user-guide.md)** - Complete step-by-step user manual
- **👔 [Business Processes](docs/functional/business-processes.md)** - Standard operating procedures  
- **👨‍💻 [Development Guide](docs/technical/development-guide.md)** - Technical development patterns
- **🔒 [Security & Roles](docs/functional/roles-permissions.md)** - Access control and permissions
- **📊 [Reports Guide](docs/functional/reports-guide.md)** - Analytics and reporting
- **🔧 [API Reference](docs/technical/api-reference.md)** - Complete API documentation

### Getting Started:
1. **Read the [Installation Guide](docs/functional/installation-guide.md)** for setup instructions
2. **Configure user roles** using [Security & Roles](docs/functional/roles-permissions.md)
3. **Follow [Business Processes](docs/functional/business-processes.md)** for workflow setup
4. **Train your team** using the provided documentation

## ⚡ Quick Overview

SC Marketing Automation Tool revolutionizes blog content localization using OpenAI's Agent SDK for intelligent, context-aware translations. This Odoo 18.0 module provides automated background processing, comprehensive status tracking, and enterprise-grade multi-company support.

### 🎯 Key Features

- **🤖 AI-Powered Translation**: OpenAI Agent SDK integration for high-quality, context-aware translations
- **⚡ Asynchronous Processing**: Background cron jobs handle translation tasks without blocking the UI
- **📊 Complete Audit Trail**: Full chatter integration with status tracking and error management
- **🏢 Multi-Company Support**: Enterprise-ready with company isolation and security rules
- **🌍 Spanish Translation**: Complete i18n support with comprehensive Spanish translations
- **🔒 Security-First Design**: Granular permissions with User and Manager roles
- **📈 Scalable Architecture**: Handles bulk translations efficiently with intelligent batching

### 🛠️ Technical Stack

- **Framework**: Odoo 18.0 Community/Enterprise
- **AI Engine**: OpenAI Agent SDK (>=0.2.9)
- **Languages**: Python 3.8+, JavaScript ES6+
- **Database**: PostgreSQL 12+
- **Dependencies**: openai-agents, requests, httpx, asyncio-throttle

## 🚀 Installation

### Prerequisites

```bash
# Ensure Odoo 18.0 environment is ready
source ./odoo-env/bin/activate

# Install Python dependencies
pip install -r custom-addons/sc_marketing_automation_tool/requirements.txt
```

### Module Installation

1. **Add to addons path**: Ensure `custom-addons` is in your Odoo addons path
2. **Update apps list**: Go to Apps > Update Apps List
3. **Install module**: Search for "SC Marketing Automation Tool" and install
4. **Configure OpenAI**: Go to Settings > General Settings > SC Marketing Automation

### OpenAI Configuration

1. Obtain your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Navigate to Settings > General Settings > SC Marketing Automation
3. Enter your API key and organization ID (optional)
4. Select your preferred model (GPT-4o recommended)
5. Test the connection using the "Test OpenAI Connection" button

## 📚 Usage Guide

### Basic Workflow

1. **Create/Edit Blog Post**: Ensure your blog post is published
2. **Initiate Translation**: Click "New Translation" button on the blog post
3. **Configure Translation**: Select target language and add custom instructions
4. **Monitor Progress**: Track translation status in Translation Tasks menu
5. **Review Results**: Check translated content and apply as needed

### Bulk Translation

1. Go to Website > Blog > Posts
2. Select multiple published blog posts
3. Click Actions > Create Translation Tasks
4. Configure batch translation settings
5. Monitor progress in Translation Tasks dashboard

### Advanced Features

- **Custom AI Instructions**: Provide specific tone, style, or formatting guidelines
- **Cost Estimation**: Preview estimated costs before processing
- **Error Recovery**: Automatic retry logic with manual reset options
- **Multi-Company**: Isolated processing per company with shared configuration

## 🔧 Configuration

### User Roles

- **Marketing Automation User**: Can create and view translation tasks
- **Marketing Automation Manager**: Full access including system configuration

### System Settings

| Setting | Description | Default |
|---------|-------------|---------|
| OpenAI API Key | Your OpenAI API key | Required |
| OpenAI Model | AI model to use | gpt-4o |
| Organization ID | OpenAI organization | Optional |

### Cron Jobs

- **Process Translation Tasks**: Runs every 5 minutes to process pending translations
- **Cleanup Old Tasks**: Daily cleanup of completed tasks older than 30 days
- **Health Monitoring**: Hourly checks for stuck or failed translations

## 🛡️ Security

### Access Control

- **Company Isolation**: Translation tasks are isolated by company
- **User Permissions**: Granular access control based on user roles
- **API Key Security**: Encrypted storage of OpenAI credentials
- **Record Rules**: Multi-company record access rules

### Data Protection

- **Secure Storage**: Encrypted configuration parameters
- **Audit Trail**: Complete activity tracking via chatter
- **Error Handling**: Graceful failure with detailed error logging
- **Rate Limiting**: Built-in protection against API overuse

## 🧪 Testing

### Running Tests

```bash
# Activate environment
source ./odoo-env/bin/activate

# Run module tests
python3 odoo-src/odoo-bin -c config/solutto-consulting.conf \
  --test-enable --test-tags=sc_marketing_automation_tool \
  --stop-after-init -d test_database

# Run specific test class
python3 odoo-src/odoo-bin -c config/solutto-consulting.conf \
  --test-enable --test-tags=TestScTranslationTask \
  --stop-after-init -d test_database
```

### Test Coverage

- ✅ Translation task lifecycle
- ✅ Blog post integration
- ✅ Wizard functionality  
- ✅ Configuration settings
- ✅ Multi-company isolation
- ✅ Cron job processing
- ✅ Error handling
- ✅ Security rules

## 📊 Performance

### Optimization Features

- **Asynchronous Processing**: Non-blocking translation execution
- **Intelligent Batching**: Efficient handling of bulk requests
- **Resource Management**: Configurable concurrent translation limits
- **Caching**: Optimized database queries and API calls

### Monitoring

- **Translation Health**: Automatic monitoring of system performance
- **Error Rate Tracking**: Alerts for high error rates
- **Processing Metrics**: Duration and cost tracking per translation
- **System Notifications**: Admin alerts for critical issues

## 🤝 Contributing

### Development Setup

```bash
# Clone and setup development environment
git clone <repository-url>
cd odoo18/custom-addons/sc_marketing_automation_tool

# Install dependencies
pip install -r requirements.txt

# Run tests
python3 ../../odoo-src/odoo-bin --test-enable -i sc_marketing_automation_tool
```

### Code Standards

- Follow Odoo 18.0 development guidelines
- Maintain English-only codebase with Spanish translations
- Include comprehensive tests for new features
- Document all public APIs and methods

## 🆘 Support

### Getting Help

- **Documentation**: Check the complete documentation in `docs/`
- **Issues**: Report bugs via the issue tracker
- **Contact**: Reach out to Solutto Consulting for enterprise support

### Common Issues

| Issue | Solution |
|-------|----------|
| Translation not starting | Check OpenAI API key configuration |
| High error rate | Verify API credits and model availability |
| Slow processing | Review concurrent translation limits |
| Missing translations | Check target language configuration |

## 📝 License

This module is licensed under AGPL-3. See LICENSE file for full details.

## 👥 Credits

**Developed by**: [Solutto Consulting LLC](https://soluttoconsulting.com)  
**Author**: Gilson Rincón (gilson.rincon@soluttoconsulting.com)  
**Role**: CEO and Founder  

Solutto Consulting specializes in IT consulting, software development, AI adoption, and business process automation.

---

## 🔄 Changelog

### Version 18.0.1.0.0
- Initial release
- OpenAI Agent SDK integration
- Asynchronous translation processing
- Multi-company support
- Complete Spanish translations
- Comprehensive test suite
- Enterprise security features

---

*For detailed technical documentation, see [Technical Documentation](docs/technical/)*
*For user guides and workflows, see [Functional Documentation](docs/functional/)*
