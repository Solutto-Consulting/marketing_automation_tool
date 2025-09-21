# Content Management Tool for Odoo (sc_marketing_automation_tool)

[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-blue.svg)](https://odoo.com)
[![Version](https://img.shields.io/badge/Version-18.0.1.0.1-green.svg)](https://github.com/Solutto-Consulting/marketing_automation_tool)
[![License](https://img.shields.io/badge/License-OPL--1-red.svg)](LICENSE)

## 🏢 Commercial License

**This is a commercial module developed by Solutto Consulting LLC.**

- **Price**: $25 USD
- **License**: Odoo Proprietary License v1.0 (OPL-1) — see LICENSE
- **Support**: Professional support included (support@soluttoconsulting.com)
- **Refund policy**: Refunds within 30 days only if you cannot install/use the module and adequate support was not provided; no guarantee with conflicting third-party modules.

## Overview

The **Content Management Tool for Odoo v18.0.1.0.1** is a comprehensive **AI-powered content automation platform** featuring specialized AI agents for content research and generation. This tool streamlines the content creation workflow from ideation to publication.

**🌍 [Versión en Español](README.es.md) | 📚 [Documentación Completa](docs/)**

## Key Features (v18.0.1.0.1)

### 🤖 **Agent-Based Content Strategy**
- **Content Research Agent**: AI-powered topic discovery using web search capabilities
- **Content Generation Agent**: Complete blog post creation from research ideas  
- **AI-Powered Image Generation**: Professional blog cover images using gpt-image-1 model
- **Configurable Instructions**: Customizable system prompts for each agent type

### 📊 **Usage Monitoring & Analytics**
- **Comprehensive Usage Tracking**: Real-time monitoring for all OpenAI API operations
- **Interactive Usage Dashboard**: Visual analytics with daily breakdowns and cost tracking
- **Operation-Specific Monitoring**: Dedicated tracking for research, generation, and image creation
- **Cost Optimization Tools**: Token usage analysis and budget monitoring

### ⚙️ **Enterprise Configuration**
- **Centralized Settings**: Dedicated Marketing Automation configuration panel
- **Static Model Management**: Reliable model definitions independent of API availability
- **Security Framework**: Enhanced credential management and access controls
- **Multi-Company Support**: Company-dependent configurations and data isolation

### 🔄 **Background Processing**
- **Asynchronous Task Processing**: Non-blocking execution for all content operations
- **Intelligent Cron Jobs**: Separate processors for research and generation tasks
- **Error Recovery**: Comprehensive error handling with retry mechanisms
- **State Management**: Clear task states with audit trails

## Documentation

### 📖 User Guides
- **[Functional User Guide (English)](docs/functional/guide.en.md)**: End-user workflows and features
- **[Guía Funcional (Español)](docs/functional/guide.es.md)**: Flujos de trabajo y características para usuarios finales

### 🔧 Technical Documentation  
- **[Technical Developer Guide (English)](docs/technical/guide.en.md)**: Architecture, development patterns, and API integration
- **[Guía Técnica para Desarrolladores (Español)](docs/technical/guide.es.md)**: Arquitectura, patrones de desarrollo e integración de APIs

### 📋 Additional Resources
- **[Feature Coverage Matrix](docs/coverage-matrix.md)**: Complete mapping of features to documentation
- **[Version Changelog](docs/CHANGELOG.md)**: Detailed version history and feature updates
- **[Development Plan](docs/plan/PLAN.md)**: Project roadmap and implementation status

## Quick Start

### 1. Installation
```bash
# Clone or copy module to custom addons directory
cp -r sc_marketing_automation_tool /path/to/odoo/custom-addons/

# Install Python dependencies
pip install openai-agents>=0.2.9

# Install module in Odoo
./odoo-bin -d your_database -i sc_marketing_automation_tool
```

### 2. Configuration
1. Navigate to **Settings > General Settings > Marketing Automation Tool**
2. Enter your OpenAI API credentials
3. Configure AI agent instructions for your content strategy
4. Test the connection and start creating content

### 3. Content Workflow
1. **Research**: Create content research tasks to discover trending topics
2. **Review**: Approve discovered content ideas for generation  
3. **Generate**: Launch content generation for approved ideas
4. **Publish**: Review and publish generated blog posts

## Version Features Matrix

### ✅ Current Features (v18.0.1.0.1)

#### **Content Strategy**
- ✅ Content Research Agent with web search capabilities
- ✅ Content Generation Agent for blog post creation
- ✅ AI-powered image generation with gpt-image-1 model
- ✅ Multi-agent workflow from research to publication
- ✅ Content idea approval and review system

#### **Monitoring & Analytics**  
- ✅ Comprehensive OpenAI usage tracking
- ✅ Interactive usage dashboard with cost analytics
- ✅ Daily breakdown reporting and trend analysis
- ✅ Operation-specific monitoring (research/generation/images)

#### **Technical Architecture**
- ✅ OpenAI Agents SDK integration (v0.2.9+)
- ✅ Asynchronous background processing
- ✅ Centralized configuration management
- ✅ Enhanced security and error handling
- **gpt-image-1 Direct Images API**: Latest image generation model with advanced features
- **Static File Management**: Web-accessible image storage with proper URL generation
- **Structured AI Responses**: JSON-based content generation with defined schemas
- **Enhanced Usage Monitoring**: Persistent data storage with daily breakdown analysis
- **Placeholder Processing**: Dynamic content replacement ({today} support)
- **Enhanced Background Processing**: Separate cron jobs for research and generation agents
- **Improved Error Handling**: Agent-specific error patterns and recovery

#### **User Interface Enhancements**
- **Marketing Automation Menu**: Centralized navigation for all content features
- **Agent Configuration Wizards**: User-friendly interfaces with consistent agent selection patterns
- **Usage Monitoring Views**: Dashboard with graphs and historical data
- **Enhanced Task Management**: Color-coded status tracking with automatic page refresh
- **Improved Wizard Experience**: Truncated fields, Configure buttons, and better usability
- **Multiple Article Generation**: Generate multiple blog posts from single content ideas

#### **Latest UX Improvements (September 2025)**
- **Automatic Action Button Refresh**: Eliminated need for manual page refresh after task actions
- **Consistent Agent Selection**: Unified agent filtering patterns across all wizards (research/generation)
- **Enhanced Field Display**: Truncated agent model/instruction fields with ellipsis for better layout
- **Direct Configuration Access**: Quick "Configure" buttons next to agent selection for immediate settings access
- **Multiple Content Generation**: Reuse content ideas to create multiple articles with different approaches
- **Improved Error Handling**: Better error display with actionable suggestions and immediate feedback

### 🔧 Technical Architecture (v18.0.1.0.1)
- **Multi-Agent Architecture**: Specialized AI agents with dedicated configurations
- **Static Model Management**: Centralized model definitions with unified selection across all components
- **gpt-image-1 API Integration**: Native support with official OpenAI client initialization patterns
- **Comprehensive Usage Monitoring**: Complete tracking for text and image generation with operation-specific logging
- **Static File Management**: Module-based image storage with web accessibility
- **Enhanced Data Models**: New models for content ideas, generation tasks, image metadata, and usage tracking
- **Settings Migration**: Automatic migration from General Settings to Marketing Automation
- **Enhanced Security Model**: Agent-specific access controls and credential management

#### **Critical Fixes Applied (September 2025)**
- **OpenAI Client Initialization**: Fixed `property 'default_headers' of 'OpenAI' object has no setter` error
- **gpt-image-1 Model Validation**: Confirmed and documented proper usage of gpt-image-1 with all supported parameters
- **XML View Compliance**: Fixed all Odoo 18.0 XML validation errors (removed invalid attributes and OWL directives)
- **Field Assignment Corrections**: Fixed computed field assignment issues in content idea models
- **Action Method Returns**: Updated all task action methods to return proper reload actions instead of boolean values

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
- **sc.content.idea**: Manages content ideas generated by the research agent
- **sc.content.generation.task**: Tracks blog content generation tasks
- **sc.openai.request.log**: Comprehensive OpenAI API usage monitoring
- **sc.openai.model.statistics**: Aggregated usage statistics by model
- **sc.openai.models**: Centralized management of available OpenAI models
- **res.config.settings** (extended): Centralized Marketing Automation configuration management

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
   - Scroll to "Marketing Automation" section
   - Enter your OpenAI API Key and Organization ID
   - Configure AI agents for content research and generation

2. **Research Content Ideas**:
   - Navigate to Marketing Automation > Content Generation > Generate Ideas
   - Enter your search query and topic details
   - Let the AI research agent find relevant content sources
   - Review and approve generated ideas

3. **Generate Blog Content**:
   - Navigate to Marketing Automation > Content Generation > Generate Content
   - Select approved content ideas as sources
   - Configure generation parameters and instructions
   - Monitor content generation progress

4. **Monitor Operations**:
   - Access Marketing Automation > Analytics for usage dashboards
   - View detailed logs and statistics for all AI operations
   - Track costs and optimize AI model usage

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

This module is licensed under the Odoo Proprietary License v1.0 (OPL-1).  
See [LICENSE](LICENSE) for more details.

**Commercial Module**: This is a paid module available for $25 USD. Purchase includes:
- Lifetime license for your Odoo instance
- Full source code access
- Professional technical support
- Free updates and bug fixes
- Complete documentation package

## Version Information

- **Module Version**: 18.0.1.0.1
- **Odoo Version**: 18.0 Community
- **Last Updated**: September 2025

---

*This module follows Solutto Consulting's development standards and best practices for Odoo 18.0.*
