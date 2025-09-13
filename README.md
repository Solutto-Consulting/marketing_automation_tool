# Content Management Tool for Odoo (sc_marketing_automation_tool)

[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-blue.svg)](https://odoo.com)
[![Version](https://img.shields.io/badge/Version-18.0.1.0.1-green.svg)](https://github.com/Solutto-Consulting/marketing_automation_tool)
[![License](https://img.shields.io/badge/License-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

## Overview

The **Content Management Tool for Odoo v18.0.1.0.1** introduces powerful **agent-based content strategy** capabilities, transforming from a translation-focused tool into a comprehensive AI-powered content management platform. This version features specialized AI agents for content research, generation, and enhanced translation workflows.

## Key Features (v18.0.1.0.1)

### 🤖 **Agent-Based Content Strategy** (NEW)
- **Content Research Agent**: AI-powered topic discovery using web search capabilities
- **Content Generation Agent**: Complete blog post creation from research ideas
- **AI-Powered Image Generation**: Professional blog cover images using gpt-image-1 model
- **Enhanced Translation Agent**: Improved translation capabilities with OpenAI Agents SDK

### 📊 **Usage Monitoring & Optimization** (ENHANCED)
- **Comprehensive Usage Tracking**: Unified monitoring for text and image generation
- **Advanced Usage Dashboard**: Interactive dashboard with daily breakdown and trends
- **Cost Optimization**: Token usage breakdown and image generation cost tracking
- **Persistent Data Storage**: Enhanced data retention and historical analysis

### ⚙️ **Centralized Configuration** (ENHANCED)
- **Marketing Automation Settings**: Dedicated configuration section for all AI agents
- **Image Generation Configuration**: Comprehensive settings for size, quality, format
- **Agent-Specific Configuration**: Specialized settings for each AI agent type
- **Enhanced Security**: Improved credential management and access controls

### 🔄 **Multi-Agent Background Processing** (ENHANCED)
- **Specialized Cron Jobs**: Independent processing for research, generation, and translation
- **Enhanced Task Management**: Comprehensive status tracking across all agent types
- **Improved Error Handling**: Agent-specific error patterns and recovery mechanisms

## Version Features Matrix

### ✅ Included in v18.0.1.0.1 (September 2025)

#### **Content Strategy Features**
- **Content Research Agent**: WebSearchTool integration for topic discovery
- **Content Generation Agent**: Complete blog post drafting from research ideas
- **AI-Powered Image Generation**: Professional blog cover images using gpt-image-1 model
- **Advanced Usage Monitoring**: Enhanced dashboard with daily breakdown and persistent data
- **Centralized Settings Architecture**: Dedicated Marketing Automation configuration section
- **Multi-Agent Workflow**: End-to-end content pipeline from research to publication

#### **Enhanced Technical Features**
- **OpenAI Agents SDK Integration**: Upgrade to >=0.2.9 with WebSearchTool support
- **gpt-image-1 Direct Images API**: Latest image generation model with advanced features
- **Static File Management**: Web-accessible image storage with proper URL generation
- **Structured AI Responses**: JSON-based content generation with defined schemas
- **Enhanced Usage Monitoring**: Persistent data storage with daily breakdown analysis
- **Placeholder Processing**: Dynamic content replacement ({today} support)
- **Enhanced Background Processing**: Separate cron jobs for each agent type
- **Improved Error Handling**: Agent-specific error patterns and recovery

#### **User Interface Enhancements**
- **Marketing Automation Menu**: Centralized navigation for all content features
- **Agent Configuration Wizards**: User-friendly interfaces for research and generation
- **Usage Monitoring Views**: Dashboard with graphs and historical data
- **Enhanced Task Management**: Color-coded status tracking across all agents

### 🔧 Technical Architecture (v18.0.1.0.1)
- **Multi-Agent Architecture**: Specialized AI agents with dedicated configurations
- **Direct Images API Integration**: Native gpt-image-1 support with advanced parameters
- **Static File Management**: Module-based image storage with web accessibility
- **Enhanced Data Models**: New models for content ideas, generation tasks, image metadata, and usage tracking
- **Settings Migration**: Automatic migration from General Settings to Marketing Automation
- **Backward Compatibility**: All existing translation functionality preserved and enhanced
- **Enhanced Security Model**: Agent-specific access controls and credential management

### ⚠️ Features Not Included in v18.0.1.0.1
- **Advanced Analytics**: Comprehensive content performance metrics (planned for v18.0.1.1.0+)
- **Multi-Provider Support**: Support for additional AI providers beyond OpenAI (planned for v18.0.2.0.0+)
- **Webhook Integration**: External webhook notifications (planned for v18.0.1.2.0+)
- **Custom Agent Training**: User-defined agent training and fine-tuning (enterprise feature)

**Migration Path**: Seamless upgrade from v18.0.1.0.0 with automatic settings migration and data preservation.

## Technical Specifications

### Dependencies
- **Odoo Modules**: base, website, website_blog, mail
- **External Library**: openai-agents (Python SDK for OpenAI integration)
- **Python Version**: 3.9+ (required by openai-agents)

### Core Models
- **sc.translation.task**: Tracks translation requests and their status
- **blog.post** (extended): Enhanced with translation tracking capabilities
- **res.config.settings** (extended): OpenAI configuration management

## Installation

1. **Install External Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Module**:
   - Place the module in your Odoo addons path
   - Update the apps list in Odoo
   - Install the "Content Management Tool" module

3. **Configuration**:
   - Navigate to Settings > General Settings > AI Marketing Tools
   - Configure your OpenAI API credentials
   - Select the desired AI model for translations

## Usage

1. **Configure OpenAI Settings**:
   - Go to Settings > General Settings
   - Scroll to "AI Marketing Tools" section
   - Enter your OpenAI API Key and Organization ID
   - Select your preferred OpenAI model

2. **Translate Blog Posts**:
   - Navigate to Website > Blog > Blog Posts
   - Select one or more blog posts
   - Click Action > "Translate with AI"
   - Choose target language and provide optional instructions
   - Monitor translation progress in Marketing Automation > Translation Tasks

3. **Monitor Translation Tasks**:
   - Access Marketing Automation > Content Translation > Translation Tasks
   - View status, manage errors, and reset failed tasks
   - Track translation history for each blog post

## Documentation

### Language Navigation
- **English Documentation**: This file (README.md)
- **Documentación en Español**: [README.es.md](README.es.md)

### Detailed Guides (v18.0.1.0.0)
- **Functional Guide EN**: [docs/functional/guide.en.md](docs/functional/guide.en.md)
- **Functional Guide ES**: [docs/functional/guide.es.md](docs/functional/guide.es.md)
- **Technical Guide EN**: [docs/technical/guide.en.md](docs/technical/guide.en.md)
- **Technical Guide ES**: [docs/technical/guide.es.md](docs/technical/guide.es.md)
- **Implementation Plan**: [docs/plan/PLAN.md](docs/plan/PLAN.md)
- **Changelog**: [docs/CHANGELOG.md](docs/CHANGELOG.md)

## Developer Information

**Author**: Gilson Rincón, CEO & Founder  
**Company**: Solutto Consulting LLC  
**Email**: support@soluttoconsulting.com  
**Website**: https://soluttoconsulting.com

## Support

For technical support, feature requests, or bug reports, please contact:
- **Email**: support@soluttoconsulting.com
- **Website**: https://soluttoconsulting.com

## License

This module is licensed under the GNU Lesser General Public License v3.0 (LGPL-3).  
See [LICENSE](LICENSE) for more details.

## Version Information

- **Module Version**: 18.0.1.0.0
- **Odoo Version**: 18.0 Community
- **Last Updated**: September 2025

---

*This module follows Solutto Consulting's development standards and best practices for Odoo 18.0.*
