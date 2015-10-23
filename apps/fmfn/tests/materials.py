# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from apps.fmfn.models import (
    ActionLog,
    Material,
    Role,
    Campus,
    Language,
    SchoolGrade
)
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

__all__ = [
    'MaterialTest'
]
User = get_user_model()

class MaterialTest(TestCase):
    """ Material CRUD tests:
        - test_material_created: basic material creation flow
        - test_material_edited: basic material edition flow
        - test_material_deleted: basic material deletion flow
        - test_too_much_content: alternative flow where the user inputs both a link and a file
        - test_not_enough_content: alternative flow where the user doesn't input a file nor a link
        - test_material_detail: basic material display flow
        - test_file_uploaded: checks that a file is correctly uploaded to the destination path
    """
    fixtures = [ 'roles', 'grades', 'campus']

    def setUp(self):

        self.client = Client(enforce_csrf_checks = False)
        self.user = User.objects.create_user(
            email_address = 'test1@example.com',
            password = 'asdfgh',
            role = Role.objects.get(id = 4),
            campus = Campus.objects.get(id = 1)
        )

    """ After executing content/create function, verifies that:
        - the http responses are successful
        - the ActionLog contains the latest operation registry
        - the latest entry in the log contains a 200 response code
        - the materials count increased by one
    """
    def test_material_created(self):

        material_count = len(Material.objects.active())
        log_count = len(ActionLog.objects.active())

        # Test case: a valid submission arrives
        self.client.login(email_address = 'test1@example.com', password = 'asdfgh')

        response = self.client.post(reverse_lazy('content:create'), data = {
            'title': 'A material test',
            'description': 'This material works best for testing purposes',
            'link':'http://www.google.com'
        }, follow = True)

        # Check the response status sequence
        self.assertEqual(response.status_code, 200)
        url, status = response.redirect_chain[-1]
        self.assertEqual(status, 302)

        # Check the materials count increased by one
        self.assertEqual(len(Material.objects.active()), (material_count + 1))

        # Check the action log
        self.assertTrue(bool(ActionLog.objects.active()))
        self.assertEqual(len(ActionLog.objects.active()), (log_count + 2))
        self.assertEqual(ActionLog.objects.latest('action_date').category, 2)

        self.assertEqual(ActionLog.objects.latest('action_date').status, 200)

    """ After executing edit function, verifies that:
        - the http responses are successful
        - the ActionLog contains the latest operation registry
        - the latest entry in the log contains a 200 response code
        -the fields edited did change in the database
    """
    def test_material_edited(self):
        self.client.login(email_address = 'test1@example.com', password = 'asdfgh')
        log_count = len(ActionLog.objects.active())

        test_material = Material.objects.create(
                                title = 'Material a editar',
                                description = 'Descripcion de prueba',
                                link = 'http://blah.com'
        )
        test_data = {
            'title': 'Material editado',
            'description': 'Descripción editada',
            'link': 'http://www.hola.com'
        }
        response = self.client.post(reverse_lazy('content:edit', kwargs= {'content_id':test_material.id}), data=test_data, follow=True)
        test_material = Material.objects.active().get(title = 'Material editado')
        # Check the response status sequence
        self.assertEqual(response.status_code, 200)
        url, status = response.redirect_chain[-1]
        self.assertEqual(status, 302)
        # Check the action log
        self.assertTrue(bool(ActionLog.objects.active()))
        self.assertEqual(len(ActionLog.objects.active()), (log_count + 2))
        self.assertEqual(ActionLog.objects.latest('action_date').category, 2)
        self.assertEqual(ActionLog.objects.latest('action_date').status, 200 )
        self.assertEqual(test_data['description'],test_material.description)
        self.assertEqual(test_data['link'],test_material.link)

    """ After executing delete function, verifies that:
        - the http responses are successful
        - the ActionLog contains the latest operation registry
        - the latest entry in the log contains a 200 response code
        - the active materials count decreased by one
        - the document schema reflects the last operation
    """
    def test_material_deleted(self):

        material = Material.objects.create(
            title = 'Test material',
            description = 'A material destined to test deletion',
            link = 'http://127.0.0.1:8000/',
            user = self.user
        )
        material_count = len(Material.objects.active())
        material_id = material.id

        # Test case: a valid submission arrives
        self.client.login(email_address = 'test1@example.com', password = 'asdfgh')
        response = self.client.delete(reverse_lazy('content:edit', kwargs = { 'content_id': material_id }), follow = True)

        # Check the response status sequence
        self.assertEqual(response.status_code, 200)

        # Test the document schema
        self.assertJSONEqual(str(response.content), {
            'version': '1.0.0',
            'status': 200,
            'material': { 'id': material_id, 'status': 'delete' }
        })

        # Check the materials count increased by one
        self.assertEqual(len(Material.objects.active()), (material_count - 1))

        # Check the action log
        self.assertTrue(bool(ActionLog.objects.active()))
        self.assertEqual(len(ActionLog.objects.active()), 1)
        self.assertEqual(ActionLog.objects.latest('action_date').category, 2)
        self.assertEqual(ActionLog.objects.latest('action_date').status, 200)

    """ After executing the create function with an invalid set of data (both a file and a link are sent to the function) , verifies that:
        - the http responses are unsuccessful
        - the ActionLog contains the latest operation registry
        - the latest entry in the log contains a 401 response code
        - the object wasn't modified
    """
    def test_too_much_content(self):
        self.client.login(email_address = 'test1@example.com', password = 'asdfgh')

        with open('test_data/oli.txt','r') as file :
            test_data = {
                'title': 'Material editado',
                'description': 'Descripción editada',
                'link': 'http://www.hola.com',
                'content': file
            }
            response = self.client.post(reverse_lazy('content:create'),data=test_data)
        # Check the response status sequence
        self.assertEqual(response.status_code, 401)
        # Check the action log
        self.assertTrue(bool(ActionLog.objects.active()))
        self.assertEqual(len(ActionLog.objects.active()), 1)
        self.assertEqual(ActionLog.objects.latest('action_date').category, 2)
        self.assertEqual(ActionLog.objects.latest('action_date').status, 401)
        self.assertFalse(bool(Material.objects.get(title='Material editado')))

    """ After executing the create function with an invalid set of data (neither a file nor a link are sent to the function) , verifies that:
        - the http responses are unsuccessful
        - the ActionLog contains the latest operation registry
        - the latest entry in the log contains a 401 response code
        - the object wasn't modified
    """
    def test_not_enough_content(self):
        self.client.login(email_address = 'test1@example.com', password = 'asdfgh')


        response = self.client.post(reverse_lazy('content:create'), data = {
            'title': 'A material test',
            'description': 'This material works best for testing purposes',
        })
        # Check the response status
        self.assertEqual(response.status_code, 401)

        # Check the action log
        self.assertTrue(bool(ActionLog.objects.active()))
        self.assertEqual(len(ActionLog.objects.active()), 1)
        self.assertEqual(ActionLog.objects.latest('action_date').category, 2)
        self.assertEqual(ActionLog.objects.latest('action_date').status, 401 )

    """ After executing the view material function, verifies that:
        - the http responses are successful
        - the ActionLog contains the latest operation registry
        - the latest entry in the log contains a 200 response code
    """
    def test_material_detail(self):
        self.client.login(email_address = 'test1@example.com', password = 'asdfgh')

        test_material = Material.objects.create(
                                title = 'Material a editar',
                                description = 'Descripcion de prueba',
                                link = 'http://blah.com'
        )
        response = self.client.get(reverse_lazy('content:view',kwargs={'content_id':test_material.id}))
        self.assertEqual(response.status_code,200)
        # Check the action log
        self.assertTrue(bool(ActionLog.objects.active()))
        self.assertEqual(len(ActionLog.objects.active()), 1)
        self.assertEqual(ActionLog.objects.latest('action_date').category, 2)
        self.assertEqual(ActionLog.objects.latest('action_date').status, 200 )

    """ After executing the create function, having selected a content file, verifies that:
        - the http responses are successful
        - the ActionLog contains the latest operation registry
        - the latest entry in the log contains a 200 response code
        - the file stored equals the file sent in the form
    """
    def test_file_uploaded(self):
        self.client.login(email_address = 'test1@example.com', password = 'asdfgh')
        with open('oli.txt', 'w') as file:
            response = self.client.post(reverse_lazy('content:create'), data = {
                'title': 'file test',
                'description': 'This material works best for testing purposes',
                'content':file
            }, follow = True)
        #check that the file exists in destination path
        saved_file = list(Material.objects.active())[-1].content
        self.assertEqual(response.status_code,200)
        self.assertTrue(cmp(saved_file,file))


