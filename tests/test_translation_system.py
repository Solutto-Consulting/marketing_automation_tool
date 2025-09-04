# -*- coding: utf-8 -*-
# Part of SC Marketing Automation Tool. See LICENSE file for full copyright and licensing details.

import json
from unittest.mock import patch, MagicMock

from odoo.tests import tagged, TransactionCase
from odoo.exceptions import UserError, ValidationError


@tagged('post_install', '-at_install')
class TestScTranslationTask(TransactionCase):
    """Test translation task functionality"""
    
    def setUp(self):
        super().setUp()
        
        # Create test blog and blog post
        self.test_blog = self.env['blog.blog'].create({
            'name': 'Test Blog',
        })
        
        self.test_post = self.env['blog.post'].create({
            'blog_id': self.test_blog.id,
            'name': 'Test Blog Post',
            'content': '<p>This is a test blog post content for translation.</p>',
            'subtitle': 'Test subtitle',
            'website_published': True,
            'website_meta_title': 'Test Meta Title',
            'website_meta_description': 'Test meta description for SEO',
        })
        
        # Create test language
        self.test_lang = self.env['res.lang'].search([('code', '=', 'es_ES')], limit=1)
        if not self.test_lang:
            self.test_lang = self.env['res.lang'].create({
                'name': 'Spanish (Spain)',
                'code': 'es_ES',
                'iso_code': 'es',
                'website_published': True,
            })
        
        # Configure OpenAI settings for tests
        self.env['ir.config_parameter'].sudo().set_param(
            'sc_marketing_automation.openai_api_key', 'test-api-key-123'
        )
        self.env['ir.config_parameter'].sudo().set_param(
            'sc_marketing_automation.openai_model', 'gpt-4o'
        )
    
    def test_translation_task_creation(self):
        """Test creating a translation task"""
        task = self.env['sc.translation.task'].create({
            'blog_post_id': self.test_post.id,
            'target_lang_id': self.test_lang.id,
            'system_instructions': 'Translate with formal tone',
        })
        
        self.assertTrue(task.name)
        self.assertEqual(task.state, 'draft')
        self.assertEqual(task.blog_post_id, self.test_post)
        self.assertEqual(task.target_lang_id, self.test_lang)
        self.assertIn('es_ES', task.name)
    
    def test_blog_post_content_required(self):
        """Test that blog post content is required"""
        empty_post = self.env['blog.post'].create({
            'blog_id': self.test_blog.id,
            'name': 'Empty Post',
            'content': '',
            'website_published': True,
        })
        
        with self.assertRaises(ValidationError):
            self.env['sc.translation.task'].create({
                'blog_post_id': empty_post.id,
                'target_lang_id': self.test_lang.id,
            })
    
    def test_same_language_validation(self):
        """Test that translation to same language is prevented"""
        # Set post language to Spanish
        self.test_post.write({'website_lang_id': self.test_lang.id})
        
        with self.assertRaises(ValidationError):
            self.env['sc.translation.task'].create({
                'blog_post_id': self.test_post.id,
                'target_lang_id': self.test_lang.id,
            })
    
    def test_state_transitions(self):
        """Test translation task state transitions"""
        task = self.env['sc.translation.task'].create({
            'blog_post_id': self.test_post.id,
            'target_lang_id': self.test_lang.id,
        })
        
        # Test draft to in_progress
        task.action_start_processing()
        self.assertEqual(task.state, 'in_progress')
        
        # Test in_progress to done
        translated_content = {
            'content': '<p>Este es un contenido de prueba traducido.</p>',
            'subtitle': 'Subtítulo de prueba',
            'meta_title': 'Título Meta de Prueba',
            'meta_description': 'Descripción meta de prueba para SEO',
        }
        task.action_mark_done(translated_content, processing_duration=5.0)
        self.assertEqual(task.state, 'done')
        self.assertIn('traducido', task.translated_content)
        self.assertEqual(task.processing_duration, 5.0)
        
        # Test reset to draft
        task.action_reset_to_draft()
        self.assertEqual(task.state, 'draft')
        self.assertFalse(task.translated_content)
    
    def test_error_handling(self):
        """Test error state handling"""
        task = self.env['sc.translation.task'].create({
            'blog_post_id': self.test_post.id,
            'target_lang_id': self.test_lang.id,
        })
        
        error_message = "Test error message"
        task.action_mark_error(error_message)
        
        self.assertEqual(task.state, 'error')
        self.assertEqual(task.error_message, error_message)
        self.assertTrue(task.processed_date)


@tagged('post_install', '-at_install')
class TestBlogPostTranslation(TransactionCase):
    """Test blog post translation extension"""
    
    def setUp(self):
        super().setUp()
        
        self.test_blog = self.env['blog.blog'].create({
            'name': 'Test Blog',
        })
        
        self.test_post = self.env['blog.post'].create({
            'blog_id': self.test_blog.id,
            'name': 'Test Blog Post',
            'content': '<p>Test content</p>',
            'website_published': True,
        })
        
        self.test_lang = self.env['res.lang'].search([('code', '=', 'es_ES')], limit=1)
        if not self.test_lang:
            self.test_lang = self.env['res.lang'].create({
                'name': 'Spanish (Spain)',
                'code': 'es_ES',
                'iso_code': 'es',
                'website_published': True,
            })
    
    def test_translation_computed_fields(self):
        """Test computed fields for translation status"""
        # Initially no translations
        self.assertEqual(self.test_post.translation_task_count, 0)
        self.assertFalse(self.test_post.translation_in_progress)
        self.assertEqual(self.test_post.completed_translation_count, 0)
        
        # Create translation task
        task = self.env['sc.translation.task'].create({
            'blog_post_id': self.test_post.id,
            'target_lang_id': self.test_lang.id,
        })
        
        self.test_post._compute_translation_status()
        self.assertEqual(self.test_post.translation_task_count, 1)
        
        # Start processing
        task.action_start_processing()
        self.test_post._compute_translation_status()
        self.assertTrue(self.test_post.translation_in_progress)
        
        # Complete translation
        task.action_mark_done({'content': 'Translated content'})
        self.test_post._compute_translation_status()
        self.assertFalse(self.test_post.translation_in_progress)
        self.assertEqual(self.test_post.completed_translation_count, 1)
    
    def test_action_view_translation_tasks(self):
        """Test viewing translation tasks from blog post"""
        # Create tasks
        task1 = self.env['sc.translation.task'].create({
            'blog_post_id': self.test_post.id,
            'target_lang_id': self.test_lang.id,
        })
        
        action = self.test_post.action_view_translation_tasks()
        
        self.assertEqual(action['res_model'], 'sc.translation.task')
        self.assertIn(task1.id, action['domain'][0][2])
    
    def test_action_open_translation_wizard(self):
        """Test opening translation wizard from blog post"""
        action = self.test_post.action_open_translation_wizard()
        
        self.assertEqual(action['res_model'], 'sc.translate.blog.post.wizard')
        self.assertEqual(action['target'], 'new')
        self.assertEqual(action['context']['default_blog_post_ids'], [self.test_post.id])


@tagged('post_install', '-at_install')
class TestTranslationWizard(TransactionCase):
    """Test translation wizard functionality"""
    
    def setUp(self):
        super().setUp()
        
        self.test_blog = self.env['blog.blog'].create({
            'name': 'Test Blog',
        })
        
        self.test_post = self.env['blog.post'].create({
            'blog_id': self.test_blog.id,
            'name': 'Test Blog Post',
            'content': '<p>Test content for translation</p>',
            'website_published': True,
        })
        
        self.test_lang = self.env['res.lang'].search([('code', '=', 'es_ES')], limit=1)
        if not self.test_lang:
            self.test_lang = self.env['res.lang'].create({
                'name': 'Spanish (Spain)',
                'code': 'es_ES',
                'iso_code': 'es',
                'website_published': True,
            })
    
    def test_wizard_creation(self):
        """Test wizard creation and computed fields"""
        wizard = self.env['sc.translate.blog.post.wizard'].create({
            'blog_post_ids': [(6, 0, [self.test_post.id])],
            'target_lang_id': self.test_lang.id,
        })
        
        self.assertEqual(wizard.blog_post_count, 1)
        self.assertIn('Test Blog Post', wizard.estimated_cost)
    
    def test_wizard_validation(self):
        """Test wizard validation"""
        wizard = self.env['sc.translate.blog.post.wizard'].create({
            'target_lang_id': self.test_lang.id,
        })
        
        # Should fail without blog posts
        with self.assertRaises(UserError):
            wizard.action_translate()
    
    def test_translation_task_creation_from_wizard(self):
        """Test creating translation tasks from wizard"""
        wizard = self.env['sc.translate.blog.post.wizard'].create({
            'blog_post_ids': [(6, 0, [self.test_post.id])],
            'target_lang_id': self.test_lang.id,
            'system_instructions': 'Test instructions',
        })
        
        result = wizard.action_translate()
        
        # Should create a translation task
        task = self.env['sc.translation.task'].search([
            ('blog_post_id', '=', self.test_post.id),
            ('target_lang_id', '=', self.test_lang.id),
        ])
        
        self.assertTrue(task)
        self.assertEqual(task.system_instructions, 'Test instructions')
        
        # Should return action to view tasks
        self.assertEqual(result['res_model'], 'sc.translation.task')


@tagged('post_install', '-at_install')
class TestResConfigSettings(TransactionCase):
    """Test OpenAI configuration settings"""
    
    def test_openai_config_retrieval(self):
        """Test getting OpenAI configuration"""
        # Set test parameters
        self.env['ir.config_parameter'].sudo().set_param(
            'sc_marketing_automation.openai_api_key', 'test-key'
        )
        self.env['ir.config_parameter'].sudo().set_param(
            'sc_marketing_automation.openai_org_id', 'test-org'
        )
        self.env['ir.config_parameter'].sudo().set_param(
            'sc_marketing_automation.openai_model', 'gpt-4o'
        )
        
        config = self.env['res.config.settings'].get_openai_config()
        
        self.assertEqual(config['api_key'], 'test-key')
        self.assertEqual(config['organization_id'], 'test-org')
        self.assertEqual(config['model'], 'gpt-4o')
    
    @patch('requests.get')
    def test_openai_connection_test_success(self, mock_get):
        """Test successful OpenAI connection test"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        settings = self.env['res.config.settings'].create({
            'sc_openai_api_key': 'test-key',
        })
        
        result = settings.action_test_openai_connection()
        
        self.assertEqual(result['params']['type'], 'success')
        self.assertIn('successful', result['params']['message'])
    
    @patch('requests.get')
    def test_openai_connection_test_failure(self, mock_get):
        """Test failed OpenAI connection test"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        settings = self.env['res.config.settings'].create({
            'sc_openai_api_key': 'invalid-key',
        })
        
        with self.assertRaises(UserError) as cm:
            settings.action_test_openai_connection()
        
        self.assertIn('Invalid API key', str(cm.exception))


@tagged('post_install', '-at_install')
class TestCronJobs(TransactionCase):
    """Test cron job functionality"""
    
    def setUp(self):
        super().setUp()
        
        self.test_blog = self.env['blog.blog'].create({
            'name': 'Test Blog',
        })
        
        self.test_post = self.env['blog.post'].create({
            'blog_id': self.test_blog.id,
            'name': 'Test Blog Post',
            'content': '<p>Test content</p>',
            'website_published': True,
        })
        
        self.test_lang = self.env['res.lang'].search([('code', '=', 'es_ES')], limit=1)
        if not self.test_lang:
            self.test_lang = self.env['res.lang'].create({
                'name': 'Spanish (Spain)',
                'code': 'es_ES',
                'iso_code': 'es',
                'website_published': True,
            })
    
    def test_process_pending_translations(self):
        """Test processing pending translations cron"""
        # Create draft task
        task = self.env['sc.translation.task'].create({
            'blog_post_id': self.test_post.id,
            'target_lang_id': self.test_lang.id,
        })
        
        # Mock the processing to avoid actual API calls
        with patch.object(task, 'action_start_processing') as mock_process:
            self.env['sc.translation.task'].process_pending_translations()
            mock_process.assert_called_once()
    
    def test_cleanup_old_tasks(self):
        """Test cleanup of old tasks cron"""
        # Create old completed task (mock old date)
        task = self.env['sc.translation.task'].create({
            'blog_post_id': self.test_post.id,
            'target_lang_id': self.test_lang.id,
            'state': 'done',
        })
        
        # Update create_date to simulate old task
        self.env.cr.execute(
            "UPDATE sc_translation_task SET create_date = %s WHERE id = %s",
            ('2023-01-01 00:00:00', task.id)
        )
        
        # Run cleanup
        self.env['sc.translation.task'].cleanup_old_tasks()
        
        # Task should be deleted
        self.assertFalse(task.exists())
    
    def test_monitor_translation_health(self):
        """Test translation health monitoring cron"""
        # Create stuck task (in_progress for too long)
        task = self.env['sc.translation.task'].create({
            'blog_post_id': self.test_post.id,
            'target_lang_id': self.test_lang.id,
            'state': 'in_progress',
        })
        
        # Update write_date to simulate stuck task
        self.env.cr.execute(
            "UPDATE sc_translation_task SET write_date = %s WHERE id = %s",
            ('2023-01-01 00:00:00', task.id)
        )
        
        # Run health monitoring
        self.env['sc.translation.task'].monitor_translation_health()
        
        # Task should be marked as error
        task.refresh()
        self.assertEqual(task.state, 'error')
        self.assertIn('timeout', task.error_message.lower())


@tagged('post_install', '-at_install')
class TestMultiCompany(TransactionCase):
    """Test multi-company functionality"""
    
    def setUp(self):
        super().setUp()
        
        # Create test companies
        self.company_1 = self.env['res.company'].create({
            'name': 'Test Company 1',
            'currency_id': self.env.ref('base.USD').id,
        })
        self.company_2 = self.env['res.company'].create({
            'name': 'Test Company 2',
            'currency_id': self.env.ref('base.EUR').id,
        })
        
        # Create test data
        self.test_blog = self.env['blog.blog'].create({
            'name': 'Test Blog',
        })
        
        self.test_post = self.env['blog.post'].create({
            'blog_id': self.test_blog.id,
            'name': 'Test Blog Post',
            'content': '<p>Test content</p>',
            'website_published': True,
        })
        
        self.test_lang = self.env['res.lang'].search([('code', '=', 'es_ES')], limit=1)
        if not self.test_lang:
            self.test_lang = self.env['res.lang'].create({
                'name': 'Spanish (Spain)',
                'code': 'es_ES',
                'iso_code': 'es',
                'website_published': True,
            })
    
    def test_company_isolation(self):
        """Test that translation tasks are isolated by company"""
        # Create task in company 1
        task_company_1 = self.env['sc.translation.task'].with_company(self.company_1).create({
            'blog_post_id': self.test_post.id,
            'target_lang_id': self.test_lang.id,
            'company_id': self.company_1.id,
        })
        
        # Create task in company 2
        task_company_2 = self.env['sc.translation.task'].with_company(self.company_2).create({
            'blog_post_id': self.test_post.id,
            'target_lang_id': self.test_lang.id,
            'company_id': self.company_2.id,
        })
        
        # Search from company 1 perspective should only see company 1 task
        company_1_tasks = self.env['sc.translation.task'].with_company(self.company_1).search([])
        self.assertIn(task_company_1, company_1_tasks)
        self.assertNotIn(task_company_2, company_1_tasks)
        
        # Search from company 2 perspective should only see company 2 task
        company_2_tasks = self.env['sc.translation.task'].with_company(self.company_2).search([])
        self.assertIn(task_company_2, company_2_tasks)
        self.assertNotIn(task_company_1, company_2_tasks)
