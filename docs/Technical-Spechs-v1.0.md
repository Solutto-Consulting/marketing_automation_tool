# **Technical Specifications and Requirements**

## **Module: Content Management Tool for Odoo (sc\_marketing\_automation\_tool)**

* **Odoo Version:** 18.0 (Community Edition)
* **Module Version:** 1.0  
* **Developing Company:** Solutto Consulting LLC  
* **Author:** Gilson Rincón, CEO & Founder  
* **Support:** support@soluttoconsulting.com  
* **Website:** https://soluttoconsulting.com

### **1\. Module Summary and Objective**

The **Content Management Tool for Odoo** module aims to enhance Odoo's marketing capabilities by integrating Generative Artificial Intelligence providers. The goal is to automate and simplify content management tasks, starting with the advanced translation of blog posts.

This module will allow content managers to use state-of-the-art AI models (Google Gemini, OpenAI, Claude) to generate high-quality translations, respecting the brand's tone and style, and managing the entire process asynchronously and traceably within Odoo.

### **2\. Main Features**

1. **Centralized Configuration of AI Providers:** A single panel in the general settings to manage AI provider credentials and preferences.  
2. **Dynamic Model Selection:** The system will query available AI models in real-time based on the selected provider, ensuring the most suitable versions are always used.  
3. **Batch Translation of Blog Posts:** Functionality to select multiple blog posts and send them for translation into a specific language through an intuitive wizard.  
4. **Asynchronous Processing (Background Jobs):** Translations will be processed in the background to avoid blocking the user interface, allowing for efficient management of large volumes of work.  
5. **Style Guide (System Instructions):** An option to provide instructions to the AI model on the tone, style, and terminology to be used in the translations.  
6. **Tracking and Traceability:** A new model to record and monitor the status of each translation task, with the ability to view details, errors, and reset failed tasks.  
7. **Native Integration with Odoo:** The module will use Odoo's translation system (ir.translation) to store translated content, ensuring full compatibility with the platform's multi-language functionality.

### **3\. Detailed Technical Specifications**

#### **3.1. Module Configuration (res.config.settings)**

The **General Settings** view must be extended to include a new "Marketing AI Tools" section.

* **Model to extend:** res.config.settings  
* **View to extend:** res\_config\_settings\_view\_form

**Fields to add:**

1. sc\_ai\_provider (Selection): Field to select the AI provider.  
   * **Options:** \[('gemini', 'Google Gemini'), ('openai', 'OpenAI'), ('claude', 'Claude')\]  
   * This field will control the visibility of the credential and model fields.  
2. sc\_gemini\_api\_key (Char): API Key for Google Gemini. (Visible if sc\_ai\_provider \== 'gemini').  
3. sc\_openai\_api\_key (Char): API Key for OpenAI. (Visible if sc\_ai\_provider \== 'openai').  
4. sc\_claude\_api\_key (Char): API Key for Claude. (Visible if sc\_ai\_provider \== 'claude').  
5. sc\_ai\_model (Selection): Dropdown to select the AI model to use.  
   * **Logic:** This field will be populated dynamically. When sc\_ai\_provider changes, an API call must be made to the corresponding provider to get the list of available models. The result will be stored for selection. It is crucial to handle exceptions (e.g., invalid API Key).

**Implementation Logic:**

* Use a method \_get\_available\_ai\_models that, based on the provider and the entered API key, performs the external query.  
* API keys must be stored securely, preferably using system parameters (ir.config\_parameter), and the field should be of type password.

#### **3.2. Blog Post Model Extension (blog.post)**

Fields need to be added to manage the translation status.

* **Model to extend:** blog.post  
* **File:** models/blog\_post.py

**Fields to add:**

1. sc\_translation\_status (Selection): Field to indicate the article's translation status.  
   * **Options:** \[('not\_translated', 'Not Translated'), ('in\_progress', 'In Progress'), ('translated', 'Translated'), ('error', 'Error')\]  
   * **Default value:** 'not\_translated'  
   * This field must be visible in the list (list) and form views of blog.post.  
2. sc\_translation\_task\_ids (One2many): Relation to the new translation task model.  
   * **Comodel:** sc.translation.task  
   * **Inverse Name:** blog\_post\_id

#### **3.3. Translation Task Model (sc.translation.task)**

A new model will be created to log each translation request.

* **Model Name:** sc.translation.task  
* **File:** models/sc\_translation\_task.py  
* **Security:** Define access rules in ir.model.access.csv.

**Model Fields:**

* name (Char): Task description (e.g., "Translate Article 'X' to Spanish").  
* blog\_post\_id (Many2one): Blog post to translate. Relation to blog.post. (Required)  
* target\_lang\_id (Many2one): Target language. Relation to res.lang. (Required)  
* status (Selection): Task status.  
  * **Options:** \[('pending', 'Pending'), ('in\_progress', 'In Progress'), ('done', 'Done'), ('error', 'Error')\]  
  * **Default value:** 'pending'  
* system\_instructions (Text): System instructions provided in the wizard.  
* error\_message (Text): Field to store error messages from the API or the process.  
* provider\_used (Char): AI provider used for this task.  
* model\_used (Char): Specific AI model used.

**Actions and Methods:**

* action\_reset\_task(): A button in the form view that allows changing the task status to 'pending' and the associated blog.post status to 'error' or 'not\_translated', allowing it to be processed again.

#### **3.4. Translation Wizard**

A TransientModel will be created for the user to select the language and instructions.

* **Model Name:** sc.blog.translation.wizard  
* **File:** wizards/sc\_blog\_translation\_wizard.py

**Wizard Fields:**

* lang\_id (Many2one): Field to select the target language. Relation with res.lang.  
  * **Domain:** Show only active languages in the website configuration.  
* system\_instructions (Text): Optional field for 'system instructions'.

**Wizard Logic:**

1. The wizard is invoked from a server action (ir.actions.server) on the blog.post model.  
2. The action's context will pass the selected articles' IDs.  
3. When clicking the "Translate" button, the wizard's main method (action\_start\_translation) will do the following for each selected article:  
   a. Validate that the sc\_translation\_status is not 'in\_progress'.  
   b. Create a new record in sc.translation.task with the 'pending' status, blog\_post\_id, lang\_id, and system\_instructions.  
   c. Change the blog.post's sc\_translation\_status to 'in\_progress'.  
   d. Schedule the task for background execution.

#### **3.5. Background Processing Logic (Queue Job)**

The queue\_job module (dependency to add) will be used to process tasks asynchronously.

* **Dependency:** queue\_job  
* **Logic:**  
  1. A method will be defined in the sc.translation.task model, for example \_process\_translation(), decorated with @job.  
  2. The wizard (sc.blog.translation.wizard) will enqueue the call to this method.  
  3. The \_process\_translation() method will execute the following steps:  
     a. Change the task status to 'in\_progress'.  
     b. Get the AI provider configuration from res.config.settings.  
     c. Collect the fields to be translated from the blog.post: name, subtitle, content, website\_meta\_title, website\_meta\_description, website\_meta\_keywords.  
     d. Build the prompt for the AI API, including the content to translate and the system\_instructions.  
     e. Make the API call to the selected provider.  
     f. Handle the response:  
     \- Success: Parse the response and get the translated text for each field. Use the odoo.tools.translate functions to create or update the records in ir.translation for each field, the target language, and the corresponding blog\_post.  
     \- Update the blog.post's sc\_translation\_status to 'translated'.  
     \- Update the sc.translation.task's status to 'done'.  
     \- Error: Catch the exception. Update the blog.post's sc\_translation\_status to 'error'. Update the sc.translation.task's status to 'error' and save the message in error\_message.

#### **3.6. Views and Menus (UI)**

* **Main Menu:** "Marketing AI" or similar in Odoo's main menu.  
  * **Submenu:** "Translation Tasks", which will open the list view of the sc.translation.task model.  
* **List View (sc.translation.task):** Show key fields like name, blog\_post\_id, target\_lang\_id, status, and create\_date. Use colors on rows according to the status (decoration-success for 'done', decoration-danger for 'error', etc.).  
* **Form View (sc.translation.task):** Show all model fields, including the error\_message. Add the "Reset Task" button.  
* **View Extension (blog.post):**  
  * Add the sc\_translation\_status field to the list view.  
  * Add a "Translate" action button in the list view ("Action" header) that invokes the wizard.  
  * In the form view, add a "Translations" tab that shows the sc\_translation\_task\_ids records.

### **4\. Development Plan (Tasks)**

1. **Task 1: Module Structure and Manifest**  
   * Create the module's directory structure for sc\_marketing\_automation\_tool.  
   * Define the \_\_manifest\_\_.py file with general information and dependencies (website\_blog, queue\_job).  
2. **Task 2: General Configuration (res.config.settings)**  
   * Extend the res.config.settings model with the provider and API key fields.  
   * Create the XML view to display these fields in the General Settings.  
   * Implement the logic for dynamic loading of AI models (requires research of each provider's APIs).  
3. **Task 3: Main Models**  
   * Extend the blog.post model with the status and relation fields.  
   * Create the new sc.translation.task model with all its fields.  
   * Define the access rules (ir.model.access.csv).  
4. **Task 4: Translation Wizard**  
   * Create the TransientModel sc.blog.translation.wizard.  
   * Design the wizard's XML view.  
   * Implement the action\_start\_translation logic to create tasks and update statuses.  
5. **Task 5: Integration with AI APIs and Job Logic**  
   * Create a library or service class (services/ai\_connector.py) that abstracts communication with the different APIs (Gemini, OpenAI, Claude).  
   * Implement the \_process\_translation method in sc.translation.task with the @job decorator.  
   * Integrate the API call logic and response handling to create/update records in ir.translation.  
6. **Task 6: User Interface (Views and Menus)**  
   * Create the access menus.  
   * Develop the list and form views for sc.translation.task.  
   * Add the action button and fields to the blog.post views.  
7. **Task 7: Testing and Refinement**  
   * Perform functional tests of the complete flow: selection, wizard, task creation, job execution, and translation verification.  
   * Test error handling (e.g., incorrect API Key, API failure).  
   * Adjust views and usability based on the results.

### **5\. \_\_manifest\_\_.py**

{  
    'name': 'Content Management Tool for Odoo',  
    'version': '18.0.1.0.0',  
    'category': 'Marketing/Content',  
    'summary': 'Enhances Odoo content management with Generative AI integrations for tasks like translation and content generation.',  
    'author': 'Solutto Consulting LLC',  
    'website': '\[https://soluttoconsulting.com\](https://soluttoconsulting.com)',  
    'support': 'support@soluttoconsulting.com',  
    'license': 'OPL-1',  
    'depends': \[  
        'base',  
        'website\_blog',  
        'queue\_job',  
    \],  
    'data': \[  
        'security/ir.model.access.csv',  
        'views/res\_config\_settings\_views.xml',  
        'views/blog\_post\_views.xml',  
        'views/sc\_translation\_task\_views.xml',  
        'wizards/sc\_blog\_translation\_wizard\_views.xml',  
        'views/sc\_menus.xml',  
    \],  
    'installable': True,  
    'application': True,  
    'auto\_install': False,  
}  
