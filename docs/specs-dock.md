# **Documento de Requerimientos: Content Management Tool for Odoo**

Versión: 1.0  
Fecha: 30 de agosto de 2025  
Módulo Técnico: marketing\_automation\_tool

### **1\. Visión General y Alcance**

#### **1.1. Introducción**

El presente documento define los requerimientos para la creación de un nuevo módulo en Odoo 18.0 Community Edition, denominado "Content Management Tool for Odoo". El objetivo principal de este módulo es centralizar y simplificar tareas de marketing y gestión de contenido, aprovechando herramientas externas de automatización como n8n.

#### **1.2. Objetivo del Módulo**

Desarrollar una solución integrada en Odoo que permita a los administradores de contenido realizar operaciones complejas de marketing de manera eficiente. La primera funcionalidad a implementar será un flujo de trabajo semi-automatizado para la traducción de artículos de blog (blog.post).

#### **1.3. Alcance de la Versión 1.0**

La versión inicial del módulo se centrará exclusivamente en las siguientes funcionalidades:

* **Configuración General:** Un panel para configurar las credenciales y el endpoint de la API del servicio de automatización (n8n).  
* **Traducción de Artículos de Blog:** Un flujo de trabajo completo que incluye el envío de artículos para traducir, la gestión de estados y la recepción de contenido traducido desde el servicio externo.

### **2\. Requerimientos Funcionales**

#### **2.1. Configuración del Módulo**

* **RF-001:** Se debe crear una nueva sección de configuración dentro de los "Ajustes Generales" de Odoo.  
* **RF-002:** En esta sección, el administrador debe poder configurar los siguientes campos:  
  * **URL del Hub de Automatización (n8n):** Un campo de tipo Char para almacenar la URL base del endpoint de n8n.  
  * **Token de Autenticación:** Un campo de tipo Char (preferiblemente con password=True) para almacenar el token de seguridad que se usará para autenticar las peticiones.  
* **RF-003:** Estos valores deben ser almacenados y accesibles globalmente para ser utilizados por otras funcionalidades del módulo.

#### **2.2. Flujo de Traducción de Artículos (Envío)**

* **RF-004:** En la vista de lista (árbol) del modelo blog.post, se debe añadir un nuevo botón en el menú "Acción" llamado **"Enviar a Traducir"**.  
* **RF-005:** Este botón solo debe estar visible para usuarios con permisos de administrador del sitio web (website.group\_website\_designer o superior).  
* **RF-006:** El usuario podrá seleccionar uno o varios artículos de la lista. Al hacer clic en el botón "Enviar a Traducir", se abrirá un asistente (wizard).  
* **RF-007:** El asistente deberá contener un único campo:  
  * **Idioma de Destino:** Un campo de selección (Many2one) que muestre la lista de idiomas activos en la configuración del sitio web. No debe permitir seleccionar el idioma original del artículo.  
* **RF-008:** Al confirmar la acción en el asistente, el sistema realizará las siguientes acciones por cada artículo seleccionado:  
  * **Validación:** Comprobar que el artículo no se encuentre ya en proceso de traducción (ver RF-014). Si es así, omitirlo y notificar al usuario.  
  * **Actualización de Estado:** Cambiar el estado del artículo a "Enviado para traducción".  
  * **Petición a n8n:** Enviar una petición POST a la URL configurada (RF-002). El cuerpo de la petición deberá ser un JSON con la siguiente estructura:  
    {  
      "post\_id": 123, // ID del blog.post en Odoo  
      "source\_lang": "es\_ES", // Código del idioma origen  
      "target\_lang": "en\_US", // Código del idioma destino seleccionado  
      "callback\_url": "https://\<odoo\_base\_url\>/marketing\_tool/translation\_callback", // URL del controlador de Odoo  
      "content\_to\_translate": {  
        "name": "Título del Artículo",  
        "subtitle": "Subtítulo del Artículo",  
        "content": "\<h1\>Contenido HTML del artículo...\</h1\>",  
        "website\_meta\_title": "Meta Título para SEO",  
        "website\_meta\_description": "Meta Descripción para SEO",  
        "website\_meta\_keywords": "palabra1, palabra2, palabra3"  
      }  
    }

  * **Autenticación:** La petición debe incluir el token (RF-002) en las cabeceras (Authorization: Bearer \<token\>).

#### **2.3. Controlador para Recepción de Traducciones**

* **RF-009:** Se debe crear un controlador (endpoint) en Odoo para recibir los datos traducidos desde n8n.  
* **RF-010:** La ruta del controlador será /marketing\_tool/translation\_callback y deberá aceptar peticiones de tipo POST.  
* **RF-011:** El controlador debe ser de tipo http y con auth="public", pero debe validar el token de autenticación recibido en las cabeceras para garantizar que la petición proviene de un servicio autorizado.  
* **RF-012:** El controlador esperará un cuerpo JSON con la siguiente estructura:  
  {  
    "post\_id": 123,  
    "source\_lang": "es\_ES",  
    "target\_lang": "en\_US",  
    "translated\_content": {  
      "name": "Translated Article Title",  
      "subtitle": "Translated Article Subtitle",  
      "content": "\<h1\>Translated HTML content...\</h1\>",  
      "website\_meta\_title": "Translated Meta Title for SEO",  
      "website\_meta\_description": "Translated Meta Description for SEO",  
      "website\_meta\_keywords": "keyword1, keyword2, keyword3"  
    }  
  }

* **RF-013:** Al recibir los datos, el controlador deberá:  
  1. Buscar el blog.post correspondiente usando el post\_id.  
  2. Utilizar el mecanismo de traducción de Odoo (ir.translation) para almacenar cada campo traducido (name, content, etc.) para el idioma de destino (target\_lang). No se debe sobreescribir el contenido del idioma original.  
  3. Actualizar el estado de traducción del artículo a "Traducido".  
  4. Devolver una respuesta HTTP 200 OK si el proceso fue exitoso o un HTTP 400/500 con un mensaje de error en caso de fallo.

#### **2.4. Modelo de Datos y Vistas**

* **RF-014:** Se debe extender el modelo blog.post para añadir un nuevo campo:  
  * translation\_status: Un campo Selection con los siguientes estados:  
    * not\_translated (No traducido) \- Estado por defecto.  
    * in\_progress (Enviado para traducción).  
    * completed (Traducido).  
    * failed (Error de traducción).  
* **RF-015:** Modificar la vista de lista (árbol) de blog.post para:  
  * Añadir una columna que muestre el campo translation\_status, preferiblemente usando un widget de "badge" para una mejor visualización.  
  * El botón "Enviar a Traducir" debe ser condicional. No se debe poder ejecutar la acción sobre artículos cuyo estado sea in\_progress.

### **3\. Requerimientos No Funcionales**

* **RNF-001 (Seguridad):** La comunicación entre Odoo y n8n debe estar asegurada mediante el uso de un token de autenticación. El endpoint de Odoo no debe procesar ninguna petición que no contenga un token válido.  
* **RNF-002 (Usabilidad):** El flujo de trabajo debe ser intuitivo para un administrador de Odoo. El estado de la traducción debe ser visible y claro en todo momento.  
* **RNF-003 (Rendimiento):** Las peticiones salientes a n8n deben gestionarse de forma que no bloqueen la interfaz de usuario por un tiempo prolongado, especialmente al enviar múltiples artículos. Se podría considerar el uso de trabajos encolados (queued jobs) en una futura versión.  
* **RNF-004 (Compatibilidad):** El módulo debe ser compatible exclusivamente con Odoo 18.0 Community Edition.

### **4\. Consideraciones Técnicas**

* **Modelos a Investigar:**  
  * blog.post (addon website\_blog): Para entender su estructura y los campos a traducir.  
  * ir.translation: Es crucial comprender cómo Odoo gestiona el almacenamiento de traducciones a nivel de modelo y campo para implementar correctamente el RF-013.  
* **Librerías/Herramientas de Odoo:**  
  * **Controladores HTTP:** Para crear el endpoint de recepción.  
  * **Modelos Transitorios (TransientModel):** Para la implementación del asistente (wizard).  
  * **res.config.settings:** Para crear la pantalla de configuración.  
* **Archivos del Módulo (Estructura Sugerida):**  
  * \_\_manifest\_\_.py  
  * models/  
    * res\_config\_settings.py  
    * blog\_post.py (para heredar y añadir el campo de estado)  
  * wizards/  
    * blog\_post\_translation\_wizard.py  
    * blog\_post\_translation\_wizard\_view.xml  
  * controllers/  
    * main.py (para el callback)  
  * views/  
    * res\_config\_settings\_view.xml  
    * blog\_post\_view.xml (para añadir el botón y la columna de estado)  
* **Manejo de Errores:** Se debe implementar un manejo de errores robusto. Por ejemplo, si la API de n8n no está disponible o devuelve un error, el estado del artículo debería cambiar a failed y registrar el error en el log de Odoo.