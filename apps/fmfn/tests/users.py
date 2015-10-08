from django.test import TestCase, Client
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth import get_user_model
from apps.fmfn.models import (
	SchoolGrade,
	Campus,
	Role,
	ActionLog
)

User = get_user_model()

__all__ = [
	'UsersTest'
]

class UsersTest(TestCase):

	# Admin User Data
	first_name_admin = 'Erick'
	last_name_father_admin = 'Garcia'
	last_name_mother_admin = 'Garcia'
	email_admin = 'test_admin@gmail.com'
	password_admin = 'test_9s92hs'

	# Self Professor User Data
	first_name = 'Daniel'
	last_name_father = 'Blanco'
	last_name_mother = 'Castillo'
	email = 'daniel.blanco.castillo@gmail.com'
	password = 'test_jk1ls'

	# Other Professor User Data
	first_name_other = 'Pepe'
	last_name_father_other = 'Troll'
	last_name_mother_other = 'Del Campo'
	email_other = 'ptdco@gmail.com'
	password_other = 'test_kswmc'

	fixtures = [
		'grades',
		'campus',
		'roles'
	]

	def setUp(self):
		"""Tests associated with the "Edit User" view. Both the normal flow and all alternative flows are tested, regarding the
		following scenarios:

			Edit:
				* The admin posts user data changes
				* The professor posts data changes to its own account
				* Other professor posts data changes to other account
			Delete:
				* The admin deletes a user
				* The professor tries to delete its own account
				* Other professor tries to delete other account
		"""
		# TODO: Enforce once tests pass without it and retry
		# Configure the test client
		self.client = Client(enforce_csrf_checks = False)

		# Create the users required for the tests

		self.user = User.objects.create_user(
		 	email_address = self.email,
		 	password = self.password,
		 	first_name = self.first_name,
		 	father_family_name = self.last_name_father,
			mother_family_name = self.last_name_mother,
			role = Role.objects.get(id = 1),
			campus = Campus.objects.active().filter(id = 1).get()
		 )

		self.assertEqual(self.user.email_address, self.email)

		self.user_admin = User.objects.create_user(
		 	email_address = self.email_admin,
		 	password = self.password_admin,
		 	first_name = self.first_name_admin,
		 	father_family_name = self.last_name_father_admin,
			mother_family_name = self.last_name_mother_admin,
			role = Role.objects.get(id = 4),
			campus = Campus.objects.active().filter(id = 1).get()
		 )

		self.assertEqual(self.user_admin.email_address, self.email_admin)

		self.user_other = User.objects.create_user(
		 	email_address = self.email_other,
		 	password = self.password_other,
		 	first_name = self.first_name_other,
		 	father_family_name = self.last_name_father_other,
			mother_family_name = self.last_name_mother_other,
			role = Role.objects.get(id = 1),
			campus = Campus.objects.active().filter(id = 1).get()
		 )

		self.assertEqual(self.user_other.email_address, self.email_other)


# Edit:

	def test_profiles_are_correctly_edited_admin(self):
		""" User profiles are modified correctly on demand if role is account manager or above"""

		self.assertEqual(self.client.login(
            email_address = self.email_admin,
			password = self.password_admin
        ), True)

		#Submit changes using post:
		new_first_name = 'John'
		new_last_name_father = 'Albert'
		new_last_name_mother = 'Einstein'
		new_email = 'jalb@mail.com'

		response = self.client.post(reverse_lazy('users:edit', kwargs = { 'user_id': self.user.id }), data = {
			'first_name' : new_first_name,
			'father_family_name' : new_last_name_father,
			'mother_family_name' : self.user.mother_family_name,
			'email_address' : new_email,
			'photo' : None,
			'grades' : self.user.grades,
			'campus' : self.user.campus,
			'role' : self.user.role
        })

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.redirect_chain[-1], 302)

		self.user.refresh_from_db()

		#Check whether user has been correctly modified

		self.assertEqual(self.user.first_name, new_first_name)
		self.assertEqual(self.user.lastname, new_last_name_father)
		self.assertEqual(self.user.email_address, new_email)

		# The action should have been logged - check the action category (account control) and status code (200)

		self.assertEqual(ActionLog.objects.latest('action_date').category, 1)
		self.assertEqual(ActionLog.objects.latest('action_date').status, 200)

		self.client.logout()

	def test_self_profile_is_modified_correctly_if_self_edited(self):
		""" Self profile is modified correctly on demand if the user modified its own profile respecting the limitations on the fields"""

		self.assertEqual(self.client.login(
            email_address = self.user.email_address,
			password = self.user.password
        ), True)

		#Submit changes using post:
		new_password = 'test_saldkjsal'

		response = self.client.post(reverse_lazy('users:edit', kwargs = { 'user_id': self.user.id }), data = {
			'password' : new_password
        })

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.redirect_chain[-1], 302)

		self.user.refresh_from_db()

		#Check whether user has been correctly modified

		self.assertEqual(self.user.check_password(new_password), True)

		# The action should have been logged - check the action category (account control) and status code (200)

		self.assertEqual(ActionLog.objects.latest('action_date').category, 1)
		self.assertEqual(ActionLog.objects.latest('action_date').status, 200)

		self.client.logout()

	def test_profiles_are_rejected_if_other_edited(self):
		""" User profiles are rejected from edition if other role is not account manager or above"""

		self.assertEqual(self.client.login(
            email_address = self.user_other.email_address,
			password = self.user_other.password
        ), True)

		#Submit changes using post:
		new_first_name = 'John'
		new_last_name = 'Albert'
		new_email = 'jalb@mail.com'

		response = self.client.post(reverse_lazy('users:edit', kwargs = { 'user_id': self.user.id }), data = {
			'first_name' : new_first_name,
			'last_name' : new_last_name,
			'email' : new_email,
			'campus': self.user.campus,
			'role': self.user.role
        })

		self.assertEqual(response.status_code, 401)
		self.assertEqual(response.redirect_chain[-1], 302)

		self.user.refresh_from_db()

		#Check whether user has not been modified

		self.assertEqual(self.user.first_name, self.first_name)
		self.assertEqual(self.user.mother_family_name, self.last_name_mother_admin)
		self.assertEqual(self.user.email_address, self.email)

		# The action should have been logged - check the action category (account control) and status code (401)

		self.assertEqual(ActionLog.objects.latest('action_date').category, 1)
		self.assertEqual(ActionLog.objects.latest('action_date').status, 401)

		self.client.logout()

# Delete:

	def test_profiles_are_correctly_deleted_admin(self):
		""" User profiles are deleted correctly on demand if role is account manager or above"""

		self.assertEqual(self.client.login(
            email_address = self.email_admin,
			password = self.password_admin
        ), True)

		response = self.client.delete(reverse_lazy('users:edit', kwargs = { 'user_id': self.user.id }), follow = True)

		self.assertEqual(response.status_code, 200)
		url, status = response.redirect_chain[-1]
		self.assertEqual(status, 301)

		#Check whether user has been correctly modified
		self.assertEqual(len(User.objects.active()), 2)

		# The action should have been logged - check the action category (account control) and status code (200)

		self.assertEqual(ActionLog.objects.latest('action_date').category, 1)
		self.assertEqual(ActionLog.objects.latest('action_date').status, 200)

		self.client.logout()

	def test_self_profile_deletion_is_rejected_if_self_deleted(self):
		""" Self profile is rejected from deletion if the user requested its own profile deleted and does not have the minimum required role"""

		self.assertEqual(self.client.login(
            email_address = self.user.email_address,
			password = self.user.password
        ), True)

		response = self.client.delete(reverse_lazy('users:edit', kwargs = { 'user_id': self.user.id }), follow = True)
		self.assertEqual(response.status_code, 403)

		#Check whether user has been correctly rejected from deletion:
		self.assertEqual(len(User.objects.active()), 3)

		# The action should have been logged - check the action category (account control) and status code (401)

		self.assertEqual(ActionLog.objects.latest('action_date').category, 1)
		self.assertEqual(ActionLog.objects.latest('action_date').status, 401)

		self.client.logout()

	def test_self_profile_deletion_rejected_if_other_deleted(self):
		""" User profiles are rejected from deletion if other tried to delete it without required base role or above"""

		self.assertEqual(self.client.login(
            email_address = self.user_other.email_address,
			password = self.user_other.password
        ), True)

		response = self.client.delete(reverse_lazy('users:edit', kwargs = { 'user_id': self.user.id }), follow = True)

		self.assertEqual(response.status_code, 403)

		#Check whether user has been correctly rejected from deletion:
		self.assertEqual(len(User.objects.active()), 3)

		# The action should have been logged - check the action category (account control) and status code (401)

		self.assertEqual(ActionLog.objects.latest('action_date').category, 1)
		self.assertEqual(ActionLog.objects.latest('action_date').status, 401)

		self.client.logout()
