# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from apps.fmfn.models import (
    ActionLog,
    Material,
    Comment,
    Rating
)
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

__all__ = [
    'RatingsTest'
]
User = get_user_model()
fixtures = [ 'roles', 'grades', 'campus','materials']

class RatingsTest(TestCase):
    """
    Tests for the Comment/Rate Material use cases.
    """
    def setup(self):
        self.client = Client(enforce_csrf_checks = False)
        self.material = Material.objects.create(title = "Material 1", description = "test description", link = "http://www.google.com")

    """
    When a comment and a rating is added to a material, this test verifies:
     - the response status code is 200 (OK)
     - the comment count increased by one
     - the comment is registered correctly in the database
     - a rating is assigned along with the comment
     - the comment's length is not greater than 500
     - the comment is not empty
     - the user who published the comment appears as the comment's author
     - the ActionLog contains the latest operation registry
     - the latest entry in the log contains a 200 response code
    """
    def test_comment_material(self):
        self.client.login(email_address = 'test1@example.com', password = 'asdfgh')
        comment_count = len(Comment.objects.active())
        log_count = len(ActionLog.objects.active())
        self.client.post(reverse_lazy('ratings:create'),kwargs={'content_id':1},data = {'rating_value':4,'user':self.user})
        response = self.client.post(reverse_lazy('comments:create'), kwargs = { 'content_id': 1 }, data = {'user':self.user, 'content':'Test comment' })
        comment = Comment.objects.get(id=1)
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(Comment.objects.active()), comment_count + 1)
        self.assertEqual(comment.content,'Test comment')
        self.assertEqual(comment.user,self.user)
        self.assertTrue(bool(Rating.objects.get(material=1)))
        self.assertLessEqual(len(comment.content),500)
        self.assertTrue(bool(comment.content))
        self.assertTrue(bool(ActionLog.objects.active()))
        self.assertEqual(len(ActionLog.objects.active()), (log_count + 2))
        self.assertEqual(ActionLog.objects.latest('action_date').category, 2)
        self.assertEqual(ActionLog.objects.latest('action_date').status, 200)

    """
    When a comment and a rating is added to a material and a rating hasn't been , this test verifies:
     - the response status code is 400 (Bad Request)
     - the comment count did not increase
     - the ActionLog contains the latest operation registry
     - the latest entry in the log contains a 400 response code
    """
    def test_comment_no_rating(self):
        self.client.login(email_address = 'test1@example.com', password = 'asdfgh')
        comment_count = len(Comment.objects.active())
        log_count = len(ActionLog.objects.active())
        response = self.client.post(reverse_lazy('comments:create'), kwargs = { 'content_id': 1 }, data = {'user':self.user, 'content':'Test comment' })
        self.assertEqual(response.status_code,400)
        self.assertEqual(comment_count,0)
        self.assertTrue(bool(ActionLog.objects.active()))
        self.assertEqual(len(ActionLog.objects.active()), (log_count))
        self.assertEqual(ActionLog.objects.latest('action_date').category, 2)
        self.assertEqual(ActionLog.objects.latest('action_date').status, 200)


