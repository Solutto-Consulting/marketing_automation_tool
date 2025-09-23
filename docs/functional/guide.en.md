# Functional User Guide: Content Management Tool for Odoo v18.0.1.0.1

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [AI Configuration](#ai-configuration)
4. [Content Research Agent](#content-research-agent)
5. [Content Generation Agent](#content-generation-agent)
6. [AI-Powered Blog Cover Images](#ai-powered-blog-cover-images)
7. [Usage Monitoring](#usage-monitoring)
8. [Task Management](#task-management)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)
11. [Version-Specific Features](#version-specific-features)

---

## Overview

The Content Management Tool for Odoo v18.0.1.0.1 is a comprehensive **AI-powered content automation platform** featuring specialized AI agents for content research and generation. This tool streamlines the entire content creation workflow from ideation to publication.

### Key Features in v18.0.1.0.1
- ✅ **Content Research Agent**: AI-powered topic discovery using web search
- ✅ **Content Generation Agent**: Automated blog post creation from research ideas
- ✅ **AI-Powered Image Generation**: Professional blog cover images using gpt-image-1
- ✅ **Comprehensive Usage Monitoring**: Complete tracking for text and image generation
- ✅ **Centralized Model Management**: Static model definitions with unified selection
- ✅ **Enhanced Settings**: Dedicated Marketing Automation configuration section
- ✅ **Multi-Agent Background Processing**: Separate cron jobs for each agent
- ✅ **Structured AI Responses**: JSON-based content generation with defined schemas

### Version Context
This documentation covers features available in **version 18.0.1.0.1** (September 2025). This represents the comprehensive content automation platform focused on AI-powered research and generation capabilities.

---

## Getting Started

### Prerequisites
- Odoo 18.0 Community or Enterprise
- Administrator access to configure OpenAI settings
- Valid OpenAI API account with organization access
- OpenAI Agents SDK dependency (>=0.2.9)
- Blog module installed and configured

### Initial Setup Checklist
1. ✅ Install the Content Management Tool module
2. ✅ Configure OpenAI API credentials in Marketing Automation settings
3. ✅ Set up Content Research Agent configuration
4. ✅ Configure Content Generation Agent settings
5. ✅ Configure Image Generation preferences (size, quality, format)
6. ✅ Verify OpenAI Usage monitoring is functional
6. ✅ Test complete content pipeline from research to publication

### New in v18.0.1.0.1: Agent-Based Architecture
This version introduces two specialized AI agents that work together to create a complete content strategy pipeline:

- **Content Research Agent**: Discovers trending topics and generates content ideas
- **Content Generation Agent**: Creates complete blog post drafts from research ideas

---

## AI Configuration

### Centralized Settings Location
All AI configuration has been moved from General Settings to a dedicated section:

**Navigation**: Settings → Marketing Automation

This new centralized approach provides better organization and dedicated configuration for each AI agent.

### Accessing Configuration Settings

**Navigation**: Settings → General Settings → AI Marketing Tools

**Note**: This section appears in the General Settings page after installing the module.

### Configuration Fields

#### 1. General OpenAI Configuration
- **OpenAI API Key** (Required): Authenticates all requests to OpenAI services
- **OpenAI Organization ID** (Optional): Links requests to your organization for usage tracking
- **OpenAI Model** (Required): Default model for content generation tasks (gpt-4o recommended)

#### 2. Content Research Agent Configuration
- **Research Agent Model**: Specific model for content research tasks
- **Research Agent Instructions**: System instructions that guide topic discovery behavior
- **Default Search Query**: Pre-filled search query template with placeholder support

#### 3. Content Generation Agent Configuration  
- **Generation Agent Model**: Specific model for blog post creation
- **Generation Agent Instructions**: System instructions for blog writing style and structure

### Static Model Management (v18.0.1.0.1)
The system uses a centralized, static model definition system that ensures consistency across all features without requiring API calls for model validation.

#### Available Text Models
- **GPT-5 Series**: GPT-5, GPT-5 Mini, GPT-5 Nano (Latest generation)
- **GPT-4.1 Series**: GPT-4.1, GPT-4.1 Mini, GPT-4.1 Nano
- **GPT-4o Series**: GPT-4o, GPT-4o Mini (Optimized for various tasks)

#### Available Image Models  
- **gpt-image-1**: Primary image generation model for blog cover images

#### Benefits of Static Model Management
- **Reliability**: No dependency on external API calls for model selection
- **Consistency**: Same model options across all configuration screens
- **Performance**: Faster loading times without API requests
- **Predictability**: Stable model selections independent of API changes

### Configuration Tips
- Use **gpt-4o** for highest quality research and generation
- Use **gpt-4o-mini** for faster, cost-effective operations
- Customize agent instructions to match your brand voice and content style

---

## Content Research Agent

The Content Research Agent uses web search capabilities to discover trending topics and generate relevant content ideas for your blog.

### Research Workflow

#### Step 1: Access Content Ideas
1. Navigate to **Marketing Automation → Content Ideas → All Ideas**
2. Click **Generate Content Ideas** button to open the wizard

#### Step 2: Configure Research Request
- **Search Query**: Enter or modify the search terms (supports {today} placeholder)
- **Number of Suggestions**: Specify how many ideas to generate (default: 5)
- **Example Query**: "Latest trends in digital marketing {today}"

#### Step 3: Background Processing
- The system creates a research task and processes it in the background
- Monitor progress in **Marketing Automation → Content Ideas → Generation Tasks**
- Tasks progress through: Draft → In Progress → Done/Error

#### Step 4: Review Generated Ideas
Each generated idea includes:
- **Title**: Headline from source article
- **URL**: Link to original source
- **Publication Date**: When the source was published
- **Summary**: AI-generated summary of key points

### Research Best Practices
- Use specific, targeted search queries for better results
- Include date placeholders like {today} for timely content
- Review source credibility before using ideas
- Customize research agent instructions for your industry focus

---

## Content Generation Agent

The Content Generation Agent takes research ideas and creates complete blog post drafts ready for review and publication.

### Generation Workflow

#### Step 1: Access Content Generation
1. Navigate to **Website → Blogs → Blog Posts**
2. Click **Generate Content** button in the header
3. This opens the content generation wizard

#### Step 2: Configure Generation Request
- **Content Idea**: Select from previously generated research ideas
- **User Prompt**: Add specific instructions or requirements
- **Target Blog**: Choose which blog to publish to
- **Author**: Select the post author
- **Language**: Set the content language

#### Step 3: Background Processing
- The system creates a generation task for background processing
- Monitor progress in **Marketing Automation → Content Generation → Generation Tasks**
- Tasks include full content creation pipeline

#### Step 4: Review Generated Content
Generated blog posts include:
- **Title**: Optimized headline based on research
- **Content**: Full HTML formatted blog post content
- **Meta Description**: SEO-optimized description
- **Keywords**: Relevant tags for discovery
- **Publication Status**: Initially saved as unpublished draft

### Generation Best Practices
- Provide clear, specific user prompts for better results
- Review and edit generated content before publishing
- Customize generation agent instructions for consistent brand voice
- Use generation tasks to track content creation pipeline

### Multiple Article Generation from Content Ideas (v18.0.1.0.1)

One of the key enhancements in v18.0.1.0.1 is the ability to generate multiple blog articles from a single content idea, maximizing the value of your research.

#### How It Works
- **Content Idea Reusability**: Each research idea can be used to generate multiple different blog posts
- **Usage Tracking**: The system tracks how many articles have been generated from each idea
- **Unique Content**: Each generation produces distinct content even from the same source idea
- **Status Monitoring**: View generation tasks and their relationship to source ideas

#### Content Idea Usage Statistics
When viewing content ideas, you'll see:
- **Generation Tasks Count**: Number of blog posts generated from this idea
- **Generated Blog Posts**: List of all articles created from this idea
- **Usage Status**: Visual indicators showing idea utilization

#### Workflow for Multiple Generations
1. **First Generation**: Use content idea wizard to create initial blog post
2. **Additional Generations**: Return to the same content idea and generate again
3. **Varied Approaches**: Use different user prompts to create diverse content angles
4. **Track Results**: Monitor all generated content in the content idea view

#### Benefits of Multiple Generation
- **Content Series**: Create related articles covering different aspects of a topic
- **Audience Targeting**: Generate versions for different reader personas
- **Content Depth**: Explore various angles of trending topics
- **ROI Maximization**: Get more value from quality research ideas

#### Example Use Case
From a single research idea about "AI in Healthcare":
- **Article 1**: "10 Ways AI is Transforming Healthcare in 2025" (user prompt: focus on current applications)
- **Article 2**: "The Future of AI in Medical Diagnosis" (user prompt: focus on future predictions)
- **Article 3**: "How Healthcare Providers Can Implement AI Solutions" (user prompt: focus on implementation guide)

---

## AI-Powered Blog Cover Images

The Content Management Tool includes advanced image generation capabilities using OpenAI's **gpt-image-1** model, the latest in AI image generation technology. This feature automatically creates professional blog cover images with extensive customization options including brand colors, visual styles, and personalized prompts.

### Enhanced Image Generation Features (Latest Update)

#### Brand Color Integration
- **Native Color Pickers**: Visual color selection tools for intuitive brand color management
- **Primary & Secondary Colors**: Define your brand palette with hex color validation
- **Automatic Color Integration**: Brand colors are intelligently incorporated into image prompts
- **Hex Format Validation**: System ensures proper color format with real-time validation

#### Advanced Style Selection
Choose from 8 professional image styles:
- **Realistic Photography**: Photographic quality images for professional content
- **Illustration**: Clean, vector-style illustrations perfect for tech and business topics
- **Minimalist Design**: Simple, elegant designs with focus on clarity
- **Abstract Art**: Creative, artistic interpretations for innovative content
- **Photographic Style**: High-quality photo-realistic renders
- **Artistic/Painterly**: Hand-painted aesthetic for creative industries
- **Modern/Contemporary**: Clean, current design trends
- **Vintage/Retro**: Classic styling for nostalgic or traditional content

#### Custom Prompt Templates
Create personalized image generation prompts with placeholder support:
- **Dynamic Placeholders**: Use `{article_title}`, `{article_content}`, `{brand_colors}`, `{image_style}`, and `{word_count}`
- **Template Library**: Save and reuse custom prompt templates across projects
- **Intelligent Processing**: System automatically replaces placeholders with actual content
- **Flexible Customization**: Override default prompts for specific content needs

### Image Generation Workflow

#### Step 1: Enable Image Generation
In the Content Generation wizard:
1. Check **"Generate Cover Image"** option
2. System automatically configures optimal settings

#### Step 2: Configure Brand Colors (Optional)
1. Enable **"Use Brand Colors"** toggle
2. Use **color picker widgets** to select:
   - **Primary Brand Color**: Main brand color (default: #3498DB)
   - **Secondary Brand Color**: Accent color (default: #E74C3C)
3. Colors are validated in real-time for proper hex format

#### Step 3: Select Image Style
Choose from the style dropdown:
- Consider your content type and target audience
- **Realistic** works well for business and professional content
- **Illustration** is perfect for technical tutorials and guides
- **Minimalist** suits modern, clean brand aesthetics

#### Step 4: Customize Image Prompt (Advanced)
1. Enable **"Use Custom Prompt"** for advanced control
2. Create custom prompt template with placeholders:
   ```
   Create a {image_style} cover image for '{article_title}'. 
   {brand_colors} The image should represent the article theme 
   without any text overlays.
   ```
3. Available placeholders automatically populate with:
   - `{article_title}`: Your blog post title
   - `{article_content}`: Summary of article content
   - `{brand_colors}`: Description of your selected brand colors
   - `{image_style}`: Chosen visual style
   - `{word_count}`: Target article length

#### Step 5: Configure Technical Settings
- **Size**: Choose from portrait, landscape, or square formats
- **Quality**: Standard or HD quality options
- **Format**: PNG, JPEG, or WebP output
- **Background**: Opaque or transparent options

#### Step 6: Generate and Review
1. Submit the generation task
2. Monitor progress in task management
3. Review generated image and regenerate if needed
4. Image automatically applies to your blog post

### Technical Specifications

#### Image Generation Models
- **Primary Model**: gpt-image-1 (OpenAI's latest image generation)
- **Output Formats**: PNG, JPEG, WebP
- **Supported Sizes**: 
  - 1024x1024 (Square)
  - 1024x1792 (Portrait)
  - 1792x1024 (Landscape)
  - 1536x1024 (Widescreen)
  - 1024x1536 (Tall)

#### Color Management
- **Format**: Hex color codes (#RRGGBB)
- **Validation**: Real-time format checking
- **Integration**: Colors are intelligently described and included in generation prompts
- **Consistency**: Same colors used across all generated images

### Best Practices for Enhanced Image Generation

#### Brand Consistency
- **Set Standard Colors**: Configure your brand colors once and reuse across all content
- **Consistent Style**: Choose a primary image style that matches your brand aesthetic
- **Template Reuse**: Create and save custom prompt templates for different content types

#### Content Optimization
- **Style Matching**: Match image style to content type (realistic for news, illustration for tutorials)
- **Color Psychology**: Use brand colors strategically to reinforce brand recognition
- **Prompt Clarity**: Write specific, descriptive custom prompts for better results

#### Performance Considerations
- **Quality vs Speed**: Use standard quality for faster generation, HD for premium content
- **Format Selection**: WebP for modern blogs, PNG for transparency needs, JPEG for compatibility
- **Style Impact**: Complex styles (artistic, abstract) may take longer to generate

### Troubleshooting Enhanced Features

#### Color Picker Issues
- **Invalid Colors**: System shows red validation for malformed hex codes
- **Color Not Applied**: Ensure brand colors are enabled and properly formatted
- **Inconsistent Results**: Check that color descriptions in prompts are accurate

#### Custom Prompt Problems
- **Placeholders Not Working**: Verify placeholder syntax with curly braces `{placeholder}`
- **Poor Results**: Try simpler, more descriptive language in custom prompts
- **Missing Content**: Ensure all required fields (title, content) are filled before generation

#### Style Selection
- **Unexpected Results**: Different styles can vary significantly; try alternative styles
- **Brand Mismatch**: Ensure selected style aligns with your brand and content type
- **Quality Issues**: Some styles work better with specific quality settings

#### Access Image Settings
1. Navigate to **Settings → General Settings**
2. Scroll to **Marketing Automation Tool** section
3. Locate **"Image Generation Settings"** subsection

#### Image Generation Options

**Enable Cover Image Generation**
- ✅ **Checked**: Automatically generates cover images for new blog posts
- ❌ **Unchecked**: Skips image generation (content-only mode)

**Image Size Selection**
- **1024x1024**: Square format, ideal for social media sharing
- **1536x1024**: Landscape format, perfect for blog headers
- **1024x1536**: Portrait format, suitable for mobile-first designs

**Quality Settings**
- **Auto**: Balanced quality and generation speed (recommended)
- **High**: Maximum visual quality, slower generation
- **Medium**: Good quality with faster generation
- **Low**: Basic quality, fastest generation time

**Output Format**
- **PNG**: Best for images with transparency, larger file sizes
- **JPEG**: Optimal for photographs, smaller file sizes
- **WebP**: Modern format with excellent compression and quality

**Background Options**
- **Auto**: AI decides the best background approach
- **Opaque**: Solid background, no transparency
- **Transparent**: Transparent background (PNG format recommended)

**Content Moderation**
- **Auto**: Standard content filtering (recommended)
- **Low**: Minimal filtering for artistic content

### Image Generation Workflow

#### Automatic Generation During Content Creation
1. **Content Generation**: When creating blog posts through the Content Generation Agent
2. **Image Prompt Creation**: System automatically generates a descriptive prompt based on blog content
3. **gpt-image-1 Processing**: OpenAI's advanced model creates the cover image
4. **Web Integration**: Image is saved to your Odoo instance and automatically set as blog cover
5. **Instant Preview**: Generated image appears immediately in the blog post

#### Manual Image Generation
You can also generate images independently:
1. Open any blog post in edit mode
2. Use the **"Generate Cover Image"** button
3. Review and approve the generated image
4. Image is automatically applied to your blog post

### Understanding Image Generation Results

#### Image Storage and URLs
- **Storage Location**: Images are saved in your module's static directory
- **Web Accessibility**: All generated images have proper web URLs for public viewing
- **File Naming**: Descriptive names based on blog title and generation timestamp
- **Format Consistency**: Generated images respect your configured format preferences

#### Quality and Performance Considerations

**High Quality Images**
- Best visual appeal for professional blogs
- Larger file sizes, slower page loading
- Recommended for marketing and promotional content

**Standard Quality Images**
- Balanced approach for most use cases
- Good visual quality with reasonable file sizes
- Ideal for regular blog content

**Performance-Optimized Images**
- Smaller file sizes for faster loading
- Suitable for high-traffic blogs
- WebP format recommended for best compression

### Image Generation Best Practices

#### Content Alignment
- **Descriptive Titles**: Clear blog titles produce better image prompts
- **Topic Focus**: Specific content themes generate more relevant images
- **Brand Consistency**: Use consistent style instructions across your blog

#### Technical Optimization
- **Format Selection**: Choose WebP for modern browsers, JPEG for compatibility
- **Size Planning**: Select image dimensions that match your blog theme
- **Quality Balance**: Use "Auto" quality for most cases, "High" for featured content

#### Creative Guidelines
- **Let AI Decide**: The gpt-image-1 model excels at creative interpretation
- **Trust the Process**: Generated images are optimized for your specific content
- **Review and Iterate**: You can regenerate images if the first result doesn't meet expectations

### Troubleshooting Image Generation

#### Common Issues and Solutions

**Image Generation Failed**
- **Check API Configuration**: Ensure OpenAI credentials are properly set
- **Verify Account Credits**: Confirm sufficient OpenAI account balance
- **Review Content**: Ensure blog content is appropriate for image generation

**Poor Image Quality**
- **Increase Quality Setting**: Switch from "Auto" to "High" quality
- **Try Different Formats**: PNG often provides better quality than JPEG
- **Regenerate**: AI image generation can vary; try generating again

**Slow Generation Times**
- **Lower Quality Setting**: Use "Medium" or "Low" for faster results
- **Optimize Format**: WebP offers good compression with reasonable quality
- **Check Network**: Ensure stable internet connection to OpenAI servers

#### Error Messages and Solutions

**"Image generation service unavailable"**
- **Solution**: OpenAI API may be temporarily down; retry in a few minutes

**"Invalid image configuration"**
- **Solution**: Review image generation settings in Marketing Automation configuration

**"Insufficient API credits"**
- **Solution**: Add credits to your OpenAI account or upgrade your plan

### Advanced Features

#### Custom Image Prompts
While the system automatically generates prompts from blog content, advanced users can:
- Review generated prompts before image creation
- Modify prompts for specific visual styles
- Save successful prompt patterns for reuse

#### Batch Image Generation
- Generate images for multiple blog posts simultaneously
- Consistent style across blog series
- Efficient processing for content campaigns

---

## Usage Monitoring

The Usage Monitoring feature provides comprehensive insights into OpenAI API consumption across all AI agents, including content research, content generation, and image generation. The enhanced dashboard offers persistent data storage and detailed daily breakdowns to help you track costs and optimize usage.

### Accessing Usage Dashboard

**Navigation**: Marketing Automation → OpenAI Usage

### Enhanced Dashboard Features

#### 1. Persistent Usage Statistics
- **Real-time Data**: Current usage statistics with automatic updates
- **Historical Persistence**: Data stored permanently in your Odoo database
- **30-Day Rolling View**: Comprehensive view of recent usage patterns
- **Daily Breakdown**: Detailed day-by-day usage analysis

#### 2. Comprehensive Usage Metrics
- **Total Token Consumption**: Combined view across all AI operations
- **Agent-Specific Breakdown**: Usage separated by:
  - Content Research Agent
  - Content Generation Agent  
  - Image Generation (gpt-image-1)
- **Cost Tracking**: Real-time cost calculations based on OpenAI pricing
- **Usage Trends**: Visual representation of consumption patterns

#### 3. Advanced Data Management
- **Manual Data Sync**: "Fetch Latest Data" button for immediate refresh
- **Automatic Sync**: Daily cron job ensures data stays current
- **Data Retention**: Up to 90 days of detailed historical data
- **Export Capabilities**: Download usage data for external analysis

#### 4. Interactive Dashboard Elements
- **Daily View Toggle**: Switch between summary and detailed daily views
- **Date Range Filters**: Focus on specific time periods
- **Usage Alerts**: Visual indicators for unusual consumption patterns
- **Performance Metrics**: Track AI operation success rates and response times

### Understanding Enhanced Usage Metrics

#### Token Categories
- **Prompt Tokens**: Input text sent to OpenAI APIs
  - Research queries and instructions
  - Content generation prompts

  - Content generation prompts
- **Completion Tokens**: AI-generated responses
  - Generated content and blog posts
  - AI research results
- **Total Tokens**: Combined prompt + completion tokens

#### Cost Analysis
- **GPT-4o**: Premium model pricing for highest quality content
- **GPT-4o Mini**: Optimized model for faster, cost-effective operations
- **Image Generation**: Fixed pricing per image (1024x1024, HD quality)

#### Performance Tracking
- **Success Rate**: Percentage of successful API calls
- **Average Response Time**: Time taken for content generation
- **Error Rate**: Failed requests and retry attempts

### Cost Optimization Strategies

#### 1. Model Selection
- Use **GPT-4o Mini** for research tasks and idea generation
- Reserve **GPT-4o** for final content generation and complex tasks
- Balance quality needs with cost considerations

#### 2. Prompt Optimization
- Create efficient prompts that minimize token usage
- Use structured output formats to reduce unnecessary text
- Cache successful prompt patterns for reuse

#### 3. Batch Processing
- Group related content requests together
- Process multiple tasks in single sessions
- Schedule operations during off-peak hours

---

## Task Management

### Accessing Content Tasks

**Navigation**: Marketing Automation → Content Management → Content Tasks

### Task List View

The task list displays all content-related tasks:
- **Task Name**: Descriptive name with content type and status
- **Content Type**: Research Ideas or Blog Generation tasks
- **Status**: Current task state with color coding
  - 🔵 Draft/In Progress (Blue)
  - 🟢 Done (Green)  
  - 🔴 Error (Red)
- Error messages (if applicable)
- Creation and completion timestamps
- Agent instructions used

### Task Actions

#### Reset to Draft
- **Available**: Only for tasks in "Error" status
- **Purpose**: Allows retrying failed content generation
- **Effect**: Changes status back to "Draft" for reprocessing

**Note**: Use this action when OpenAI API issues are resolved or configuration is corrected.

### Enhanced Task Action Experience (v18.0.1.0.1)

The latest version introduces significant improvements to task action buttons, eliminating the need for manual page refreshes and providing immediate feedback.

#### Automatic Page Refresh
All task action buttons now automatically refresh the page after completion, providing immediate visual feedback:

**Content Generation Tasks**:
- **Execute Immediately**: Starts task processing and auto-refreshes to show updated status
- **Retry**: Resets failed tasks and auto-refreshes to show draft status
- **View Blog Post**: Opens generated content without losing current context

**Content Idea Tasks**:
- **Reset to Draft**: Changes status and immediately shows the update
- **Mark Complete**: Updates status with instant visual feedback
- **Generate Content**: Opens generation wizard while maintaining task context

#### User Experience Benefits
- **No Manual Refresh Required**: Status changes are visible immediately after clicking action buttons
- **Improved Workflow**: Users can work continuously without interruption
- **Better Error Handling**: Error states are displayed immediately with actionable suggestions
- **Consistent Behavior**: Same auto-refresh pattern across all task types

#### Technical Implementation
The system now returns reload actions instead of simple boolean responses:
- Successful actions trigger automatic page reload
- Error conditions display notifications and refresh to show error state
- Status transitions are immediately visible to users

### Task History

From any blog post form:
1. Open the blog post record
2. Navigate to **"Content History"** tab
3. View all content generation attempts for that post
4. Track content creation status over time

---

## Usage Monitoring

The Usage Monitoring feature provides comprehensive insights into OpenAI API consumption across all AI agents, including content research, content generation, and image generation. The enhanced dashboard offers persistent data storage and detailed daily breakdowns to help you track costs and optimize usage.

### Accessing Usage Dashboard

**Navigation**: Marketing Automation → OpenAI Usage

### Enhanced Dashboard Features

#### 1. Persistent Usage Statistics
- **Real-time Data**: Current usage statistics with automatic updates
- **Historical Persistence**: Data stored permanently in your Odoo database
- **30-Day Rolling View**: Comprehensive view of recent usage patterns
- **Daily Breakdown**: Detailed day-by-day usage analysis

#### 2. Comprehensive Usage Metrics
- **Total Token Consumption**: Combined view across all AI operations
- **Agent-Specific Breakdown**: Usage separated by:
  - Content Research Agent
  - Content Generation Agent  
  - Image Generation (gpt-image-1)
- **Cost Tracking**: Real-time cost calculations based on OpenAI pricing
- **Usage Trends**: Visual representation of consumption patterns

#### 3. Advanced Data Management
- **Manual Data Sync**: "Fetch Latest Data" button for immediate refresh
- **Automatic Sync**: Daily cron job ensures data stays current
- **Data Retention**: Up to 90 days of detailed historical data
- **Export Capabilities**: Download usage data for external analysis

#### 4. Interactive Dashboard Elements
- **Daily View Toggle**: Switch between summary and detailed daily views
- **Date Range Filters**: Focus on specific time periods
- **Usage Alerts**: Visual indicators for unusual consumption patterns
- **Performance Metrics**: Track AI operation success rates and response times

### Understanding Enhanced Usage Metrics

#### Token Categories
- **Prompt Tokens**: Input text sent to OpenAI APIs
  - Research queries and instructions
  - Content generation prompts
  - Image generation descriptions
- **Completion Tokens**: AI-generated responses
  - Research summaries and ideas
  - Generated blog content
  - Image generation metadata
- **Total Tokens**: Combined prompt and completion tokens for accurate billing

#### Image Generation Costs
- **gpt-image-1 Usage**: Separate tracking for image generation API calls
- **Format Impact**: Cost variations between PNG, JPEG, and WebP formats
- **Quality Settings**: Cost differences between Auto, High, Medium, and Low quality
- **Size Considerations**: Pricing impact of different image dimensions

#### Image Generation Monitoring (Enhanced in v18.0.1.0.1)
The system now provides complete tracking for all image generation operations:
- **Full Request Logging**: Every gpt-image-1 API call is tracked with detailed metrics
- **Operation Type Tracking**: Dedicated 'image_generation' operation type in monitoring
- **Response Time Measurement**: Precise timing for image generation performance analysis
- **Token Usage Extraction**: Complete token usage data including input/output tokens
- **Error Tracking**: Comprehensive logging of failed image generation attempts
- **Blog Post Integration**: Image generation linked to specific blog posts for content attribution

#### Daily Breakdown Analysis
- **Peak Usage Times**: Identify when AI operations are most active
- **Agent Performance**: Compare efficiency across different AI agents
- **Cost Attribution**: Understand which features drive API costs
- **Usage Optimization**: Spot opportunities to reduce unnecessary consumption

### Cost Management and Optimization

#### Budget Planning
- **Daily Cost Tracking**: Monitor spending to stay within budget limits
- **Monthly Projections**: Estimate future costs based on usage trends
- **Agent Efficiency**: Compare cost-per-operation across different AI agents
- **Model Selection**: Make informed decisions about gpt-4 vs gpt-3.5-turbo usage

#### Performance Optimization
- **Prompt Engineering**: Optimize instructions to reduce token consumption
- **Batch Operations**: Group similar tasks for more efficient processing
- **Quality vs Cost**: Balance AI quality settings with budget constraints
- **Usage Patterns**: Identify and eliminate inefficient usage patterns

#### Image Generation Cost Control
- **Format Selection**: Choose optimal formats for your use case and budget
- **Quality Management**: Use appropriate quality settings for different content types
- **Size Optimization**: Select image dimensions that balance quality and cost
- **Generation Strategy**: Understand when to regenerate vs accept first results

### Dashboard Troubleshooting

#### Common Dashboard Issues

**Data Not Updating**
- **Check Cron Jobs**: Ensure automatic sync is running properly
- **Manual Refresh**: Use "Fetch Latest Data" button
- **API Connectivity**: Verify OpenAI API credentials are valid
- **Permissions**: Confirm user has access to usage monitoring features

**Missing Daily Breakdown**
- **Data Sync Status**: Check last successful sync timestamp
- **Historical Limits**: OpenAI provides limited historical data access
- **Database Health**: Verify usage data tables are functioning correctly

**Incorrect Cost Calculations**
- **Pricing Updates**: OpenAI pricing may change; verify current rates
- **Token Counting**: Ensure accurate token consumption reporting
- **Currency Settings**: Check if cost display matches your billing currency

### Usage Monitoring Best Practices

#### Regular Monitoring
- **Weekly Reviews**: Check dashboard weekly to track spending trends
- **Monthly Analysis**: Conduct detailed monthly usage and cost analysis
- **Alert Thresholds**: Set internal alerts based on daily consumption limits
- **Performance Tracking**: Monitor AI operation efficiency and success rates

#### Optimization Strategies
- **Agent Tuning**: Regularly review and optimize AI agent instructions
- **Model Selection**: Use appropriate models for different task complexity levels
- **Batch Processing**: Group similar operations for more efficient API usage
- **Feature Management**: Enable only necessary AI features to control costs

#### Reporting and Analysis
- **Export Data**: Regular export of usage data for external analysis
- **Trend Analysis**: Identify seasonal or cyclical usage patterns
- **ROI Assessment**: Measure AI feature value against operational costs
- **Budget Planning**: Use historical data for accurate budget forecasting

---

## Troubleshooting

### Common Issues

#### 1. Content Tasks Stuck in "Draft"
**Symptoms**: Tasks remain in draft status for extended periods

**Possible Causes**:
- OpenAI API credentials not configured
- API key invalid or expired
- Network connectivity issues
- Cron job not running

**Solutions**:
- Verify API configuration in Settings
- Check OpenAI account status and credits
- Restart Odoo server to reset cron jobs
- Check server logs for specific errors

#### 2. Content Generation Fails with API Errors
**Symptoms**: Tasks move to "Error" status with API-related messages

**Possible Causes**:
- API rate limits exceeded
- Insufficient OpenAI credits
- Invalid model selection
- Research prompts too large for processing

**Solutions**:
- Wait for rate limit reset (typically 1 minute)
- Add credits to OpenAI account
- Switch to available model (gpt-3.5-turbo)
- Refine research prompts to be more specific

#### 3. Poor Content Quality
**Symptoms**: Generated content is incorrect or inappropriate

**Possible Causes**:
- Suboptimal agent instructions
- Wrong model selection
- Unclear research context

**Solutions**:
- Refine agent instructions with specific guidance
- Upgrade to gpt-4o model for better quality
- Test with clearer research prompts first
- Provide more context-specific instructions

### Error Messages Reference

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| "API key not configured" | OpenAI credentials missing | Configure API key in Settings |
| "Model not available" | Selected model unavailable | Choose different model |
| "Rate limit exceeded" | Too many API requests | Wait and retry |
| "Content too long" | Research result exceeds API limits | Reduce prompt complexity |

---

## Best Practices

### Content Research Preparation
1. **Define Clear Objectives**: Set specific goals for content research and generation
2. **Optimize Search Queries**: Create targeted search terms for better research results
3. **Test Agent Instructions**: Validate agent configurations with sample requests
4. **Review Results**: Always review generated content before publication

### Content Generation Strategy
1. **Topic Planning**: Plan content themes and series for consistency
2. **Batch Processing**: Group related content requests for efficient processing
3. **Quality Review**: Always review AI-generated content before publishing
4. **SEO Optimization**: Ensure generated content includes relevant keywords and structure

### Agent Instructions Guidelines
1. **Be Specific**: Provide clear, detailed instructions for each agent
2. **Include Context**: Mention industry, audience, and content purpose
3. **Set Tone**: Specify formal, casual, technical, or conversational style
4. **Content Standards**: Request specific formatting and structural requirements

### Performance Optimization
1. **Schedule Operations**: Run content generation during off-peak hours for faster processing
2. **Monitor Resources**: Track API usage and costs through the usage dashboard
3. **Batch Wisely**: Process 5-10 content requests at a time for optimal performance
4. **Regular Maintenance**: Reset failed tasks and clean up completed ones

---

## Version-Specific Features

### New in v18.0.1.0.1 (September 2025)
- **Content Automation Platform**: Complete AI-powered content research and generation system
- **OpenAI Integration**: Advanced integration with openai-agents SDK v0.2.9+
- **Dual Agent Architecture**: Specialized research and generation agents working in harmony
- **Comprehensive Task Management**: Advanced status tracking and error handling for content operations
- **Enhanced Image Generation**: Professional blog cover images with gpt-image-1 integration
- **Advanced Usage Monitoring**: Persistent tracking with detailed analytics and cost management
- **Centralized Configuration**: Dedicated Marketing Automation settings section
- **Security Implementation**: Proper access controls and credential management
- **Bilingual Support**: English and Spanish interface support
- **Complete Documentation**: Comprehensive functional and technical guides

### Architecture Highlights
- **Odoo 18.0 Compliance**: Uses modern `<list>` views and proper conditionals
- **Mail Integration**: Chatter support for content tasks when applicable
- **Kanban Views**: Meaningful grouping by task status and content type
- **Stable Anchors**: Core settings inheritance from base_setup module
- **Static Model Management**: Centralized, consistent model definitions across all features

### Key Capabilities in v18.0.1.0.1
- **Content Research Agent**: Web-powered topic discovery with configurable search parameters
- **Content Generation Agent**: Complete blog post creation from research ideas
- **AI Image Generation**: Professional cover images with customizable prompts
- **Usage Analytics**: 90-day retention with detailed daily breakdowns
- **Cost Optimization**: Multiple model options balancing quality and efficiency

### Known Limitations in v18.0.1.0.1
- Content processing limited to configured batch sizes for optimal performance
- Manual task management required for complex error recovery scenarios
- Image generation limited to supported OpenAI formats (PNG, JPEG, WebP)
- Usage monitoring requires manual sync for immediate data updates

**Note**: This version represents a complete content automation platform focused on research and generation capabilities.

---

## External References

### Core Settings Implementation
- **Reference**: `/home/gilsonrincon/development/odoo18/odoo-src/addons/base_setup/views/res_config_settings_views.xml`
- **Anchor Used**: `//setting[@id='partner_autocomplete']` with `position="after"`
- **Pattern**: Stable xpath selectors following Odoo 18.0 standards

### Official Documentation
- **OpenAI Agents SDK**: https://github.com/openai/openai-agents-python
- **OpenAI API Documentation**: https://platform.openai.com/docs
- **Odoo 18.0 Development**: https://www.odoo.com/documentation/18.0/

---

*Documentation Version: 18.0.1.0.1 | Last Updated: September 2025*
