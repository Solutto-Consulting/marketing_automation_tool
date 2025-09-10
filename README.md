# Content Management Tool for Odoo (sc_marketing_automation_tool)

[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-blue.svg)](https://odoo.com)
[![License](https://img.shields.io/badge/License-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

## Overview

The **Content Management Tool for Odoo** enhances and automates marketing activities within the Odoo ecosystem by integrating Artificial Intelligence for content translation processes. This module provides administrators with powerful tools to streamline blog post translation workflows using OpenAI's advanced language models.

## Key Features

- **OpenAI Integration**: Centralized configuration for OpenAI API credentials and model selection
- **Bulk Blog Translation**: Server action on blog posts for simultaneous translation of multiple articles
- **AI-Powered Translation**: Leverages OpenAI's language models for high-quality content translation
- **User-Friendly Wizard**: Intuitive interface for selecting target languages and providing AI instructions
- **Asynchronous Processing**: Background translation processing to avoid UI blocking
- **Task Management**: Comprehensive tracking and status management for translation requests
- **Error Handling**: Robust error management with task reset capabilities
- **Multi-Language Support**: Built-in internationalization with Spanish translation support

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

### Detailed Guides
- **Functional Documentation**: [docs/functional/](docs/functional/)
- **Technical Documentation**: [docs/technical/](docs/technical/)
- **Implementation Plan**: [docs/plan/PLAN.md](docs/plan/PLAN.md)

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
