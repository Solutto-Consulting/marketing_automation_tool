# **Technical Specifications & Requirements**

## **Module: Content Management Tool for Odoo (sc\_marketing\_automation\_tool)**

**Author:** Gilson Rincón, CEO & Founder of Solutto Consulting LLC

**Support:** support@soluttoconsulting.com

Website: https://soluttoconsulting.com  
Odoo Version: 18.0 Community

### **1\. Overview**

The **Content Management Tool for Odoo** is an extension designed to enhance and automate marketing activities within the Odoo ecosystem. The initial version of this module will focus on leveraging Artificial Intelligence, specifically through OpenAI, to streamline the content translation process for blog articles (blog.post), providing a more efficient and scalable alternative to the standard Odoo translation workflow.

The primary goal is to enable administrators to select multiple blog posts, request translations into various languages via a simple wizard, and have the process executed asynchronously in the background, with clear status tracking and error management.

### **2\. Core Features**

* **OpenAI Integration:** Centralized configuration for OpenAI API credentials and model selection.  
* **Bulk Blog Post Translation:** A server action on the blog.post list view to initiate translation for multiple selected posts.  
* **User-Friendly Wizard:** A wizard to select the target language and provide optional "system instructions" to guide the AI's tone and style.  
* **Asynchronous Background Processing:** Translation tasks are managed by an Odoo automated action (cron job) to avoid UI blocking and handle long-running processes.  
* **Translation Task Logging:** A dedicated model and menu to track the status of each translation request (e.g., Pending, In Progress, Completed, Error).  
* **Status Management:** Ability to view task history and reset the status of a post in case of failure or if a re-translation is needed.

### **3\. Technical Requirements & Dependencies**

#### **3.1. Odoo Dependencies**

The module will depend on the following standard Odoo applications:

* base  
* website  
* website\_blog

#### **3.2. External Python Libraries**

* openai-agents: This SDK is **mandatory** for all interactions with the OpenAI API.  
  * **Installation:** pip install openai-agents  
  * This dependency must be added to the Odoo instance's requirements.txt file.

#### **3.3. OpenAI Agents SDK \- Usage and References**

It is crucial that the development team exclusively uses the openai-agents SDK for this integration.

* **Official GitHub Repository (Source & Docs):** [https://github.com/openai/openai-agents-python](https://github.com/openai/openai-agents-python)

**Key Concepts:**

* **Agent:** Represents the AI assistant. It is configured with instructions (which will be our system\_instructions), the model name, and other settings.  
* **Runner:** Executes the interaction with the agent, sending the user's prompt and returning the final result.

**Basic Example (hello\_world.py from SDK docs):**

import asyncio  
from agents import Agent, Runner

async def main():  
    agent \= Agent(  
        name="Assistant",  
        instructions="You only respond in haikus.",  
    )  
    result \= await Runner.run(agent, "Tell me about recursion in programming.")  
    print(result.final\_output)

if \_\_name\_\_ \== "\_\_main\_\_":  
    asyncio.run(main())

**Important Note:** The SDK is asynchronous. The implementation within the Odoo cron job must correctly manage an asyncio event loop to execute the API calls.

This is the URL of the repository in GitHub: https://github.com/openai/openai-agents-python/tree/main  
Here are more examples: https://github.com/openai/openai-agents-python/tree/main/examples/basic

### **4\. Configuration**

A new configuration section will be added to the Odoo general settings to manage AI provider credentials.

* **Location:** Settings \> General Settings \> AI Marketing Tools  
* **Model to Inherit:** res.config.settings  
* **Fields to Add:**  
  * sc\_openai\_api\_key (Char): The OpenAI API Key. The field must use the password=True attribute for security.  
  * sc\_openai\_organization\_id (Char): The OpenAI Organization ID. As per OpenAI documentation, this is optional but recommended.  
  * sc\_openai\_model (Selection): A selection field to choose the OpenAI model to be used for translations.  
    * **Dynamic Options:** The list of available models will be populated dynamically. This will be implemented using a function that calls the OpenAI v1/models API endpoint to retrieve an up-to-date list of models.  
    * **Implementation:** The Selection field's list will be provided by a method. This method will:  
      1. Attempt to retrieve the saved sc\_openai\_api\_key.  
      2. If an API key is present, make a request to the OpenAI API to list models.  
      3. Filter the results to include only relevant models (e.g., those starting with gpt-).  
      4. Return a list of tuples \[(model\_id, model\_id), ...\] for the selection field.  
      5. If the API key is not set or the call fails, a default list (e.g., \['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'\]) should be returned as a fallback.  
    * **Default:** gpt-4o

### **5\. Data Models (Database Schema)**

#### **5.1. New Model: sc.translation.task**

This model will store a record for each translation request.

* **Model Name:** sc.translation.task  
* **Description:** AI Translation Task  
* **Fields:**  
  * name (Char, required): A descriptive name for the task (e.g., "Translate 'My Blog Post' to Spanish").  
  * blog\_post\_id (Many2one, blog.post, required, ondelete='cascade'): The blog post to be translated.  
  * target\_lang\_id (Many2one, res.lang, required): The target language for the translation.  
  * system\_instructions (Text): Optional instructions provided by the user to guide the AI model.  
  * state (Selection, required, default='draft'): The status of the task.  
    * **Values:** draft, in\_progress, done, error.  
  * error\_message (Text): Stores any error details if the state is 'error'.

#### **5.2. Inherited Model: blog.post**

The blog.post model will be inherited to add fields for tracking the translation status.

* **Model to Inherit:** blog.post  
* **Fields to Add:**  
  * translation\_task\_ids (One2many, sc.translation.task): A link to all translation tasks associated with this blog post.  
  * translation\_in\_progress (Boolean, default=False): A flag to indicate that a translation for this post is currently queued or in progress.

### **6\. User Interface & Views (XML)**

#### **6.1. Server Action on blog.post**

An ir.actions.server record will be created to add a "Translate with AI" option to the "Action" menu in the blog.post tree view.

* **Name:** Translate with AI  
* **Model:** blog.post  
* **Action:** Launch the translation wizard sc.translate.blog.post.wizard.

#### **6.2. Translation Wizard**

A transient model (sc.translate.blog.post.wizard) will be used to gather user input.

* **Model:** sc.translate.blog.post.wizard (models.TransientModel)  
* **View:** A form view (ir.ui.view) presented as a modal dialog.  
  * **Fields:**  
    * target\_lang\_id (Many2one, res.lang, required): A field to select the target language. The domain should be limited to languages installed and active on the website (\[('website\_published', '=', True)\]).  
    * system\_instructions (Text): An optional text area for tone and style guidance.  
  * **Footer Buttons:**  
    * A "Translate" button that executes the wizard's action method.  
    * A "Cancel" button to close the wizard.

#### **6.3. sc.translation.task Views**

* **Menu Items:**  
  * A new top-level menu: Marketing Automation.  
  * A sub-menu: Content Translation \> Translation Tasks.  
* **Views:**  
  * A tree view for sc.translation.task showing: name, blog\_post\_id, target\_lang\_id, and state. The state field should use a widget="badge" for better visibility with colors (decoration-info for draft/in\_progress, decoration-success for done, decoration-danger for error).  
  * A form view for sc.translation.task to display all details, including error\_message (visible only when state is 'error'). The form should include a "Reset to Draft" button (visible only for tasks in 'error' state) that allows re-queuing the task.

#### **6.4. blog.post Form View**

* A new page titled "Translation History" will be added to the notebook (\<notebook\>) in the blog.post form view.  
* This page will contain the translation\_task\_ids field, rendered as a tree view, showing the history of translation attempts for that post.

### **7\. Business Logic & Workflow**

#### **7.1. Translation Initiation**

1. **User Action:** An administrator selects one or more records from the blog.post tree view and clicks "Action \> Translate with AI".  
2. **Wizard Display:** The sc.translate.blog.post.wizard is displayed in a modal window. The context will contain the active\_ids of the selected blog posts.  
3. **User Input:** The user selects a target language from the dropdown and optionally enters system instructions.  
4. **Wizard Confirmation:** Upon clicking the "Translate" button, the wizard's primary action method is executed.  
5. **Task Creation:** The method iterates through the active\_ids (the selected blog posts).  
   * For each blog.post that does **not** have translation\_in\_progress set to True:  
     * It sets blog\_post.translation\_in\_progress \= True.  
     * It creates a new sc.translation.task record with the details from the wizard (post ID, language, instructions) and sets its initial state to 'draft'.  
   * Posts that are already in progress (translation\_in\_progress \== True) are skipped to prevent duplicate requests. A notification can be shown to the user if some posts were skipped.

#### **7.2. Asynchronous Translation (Cron Job)**

1. **Job Trigger:** An ir.cron is configured to run periodically (e.g., every 5 minutes).  
2. **Task Fetching:** The cron method searches for sc.translation.task records with state \= 'draft', with a reasonable limit (e.g., 10 tasks per run) to avoid overloading the system.  
3. **Task Processing Loop:** For each task:  
   * **Update State:** Set task.state \= 'in\_progress'. Commit the transaction to lock the task.  
   * **Prepare Data:**  
     * Retrieve OpenAI config from res.config.settings.  
     * Get source blog post content for fields: name, subtitle, content, website\_meta\_title, website\_meta\_description, website\_meta\_keywords.  
     * Structure data into a JSON object.  
   * **Build Prompt:** Construct the prompt for the OpenAI Agent.  
     * **Example Prompt Structure:**  
       Translate the values in the following JSON object from {source\_language} to {target\_language}.  
       Respond ONLY with the translated JSON object, maintaining the exact same key structure.  
       JSON to translate:  
       { ... json data ... }

   * **Execute AI Call:**  
     * **This step MUST use the openai-agents SDK.** The logic should be encapsulated in an async function.  
     * **Implementation Guidance:**  
       import asyncio  
       from agents import Agent, Runner

       \# This function should be defined in a utility file and called from the cron method.  
       \# The OpenAI API key and Org ID should be set from Odoo config before calling.  
       \# For example, by setting environment variables for the current thread/process.  
       async def perform\_ai\_translation(model\_name, system\_instructions, prompt):  
           """  
           Performs translation using the OpenAI Agents SDK.  
           """  
           agent \= Agent(  
               name="Odoo Blog Translator",  
               instructions=system\_instructions, \# From task.system\_instructions  
               model=model\_name,             \# From Odoo settings  
           )

           result \= await Runner.run(agent, prompt)  
           return result.final\_output

       \# \--- Inside the Odoo cron method loop \---  
       \# try:  
       \#     \# ... get config and build prompt ...  
       \#     translated\_json\_str \= asyncio.run(perform\_ai\_translation(  
       \#         model, task.system\_instructions, prompt  
       \#     ))  
       \#     \# ... process translated\_json\_str ...  
       \# except Exception as e:  
       \#     \# ... handle errors ...

