from django.test import TestCase
from user.models import User
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken , AccessToken

# write a test case for User model & UserRegistrationView view

class BaseTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.create_user()
        self.login_user()
        self.post_user_profile()

    def create_user(self):
        """Set up a user for register tests."""
        url = reverse("register_user")
        
        # Register the user
        self.user_data = {
            "user_name": "test_user",
            "email": "test_user@gmail.com",
            "password": "Prem@@1234567890",
            "confirm_password": "Prem@@1234567890",
        }
        response = self.client.post(url, self.user_data, format="json")
        user = User.objects.get(user_name="test_user")
        user.is_registered_with_email = True
        user.is_active = True
        user.is_registered = True
        user.is_email_verified = True
        user.is_confirm_tnc = True
        user.mfa_enabled = True
        user.save()

        self.user = user
        self.refresh_token = (RefreshToken.for_user(user))
        self.access_token = self.refresh_token.access_token
        self.assertEqual(response.status_code, 201)

    def login_user(self):
        """Set up a user for login tests."""    
        url = reverse("login")
        data = {"email": self.user.email,"password": self.user_data['password']}
        response = self.client.post(url, data)
        print('*****test-login*******')
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.auth_token = response.data.get('data').get('auth_token')

    def post_user_profile(self):
        """Set up a userprofile tests."""    
        url = reverse("profile_create_update_get")
        data = {
            "auth_token":self.auth_token,
            "first_name":"test",
            "middle_name":"test",
            "last_name":"test",
            "address":"test",
            "dob":"2002-07-02",
            "race":"White",
            "sex":"M",
            "what3words":"test.t.t",
            "national_id":"CM0BCDEFGHIJKL",
            "tribe":"test",
            "zipcode":5556546
        }

        get_response = self.client.post(url,data=data)
        print('*****test-user_profle*******')
        self.assertEqual(get_response.status_code, 201)
    
class UserTestCase(BaseTestCase):
       
    def test_01_user_profle(self):
        print(str(self.access_token))
        headers = {'AUTHORIZATION': 'Bearer ' + str(self.access_token)}
        url = reverse("profile_create_update_get")
        response = self.client.get(url,headers=headers)
        print(response.data)
        self.assertEqual(response.status_code, 200)
























# --------------------------------------------------------------------------------------------------------------------------------
# import pytest
# from django.urls import reverse
# from rest_framework.test import APIClient
# from rest_framework_simplejwt.tokens import RefreshToken
# from user.models import User
# @pytest.mark.django_db
# def test_post_list_view():
#     # Arrange: Create a test user
#     user = User.objects.create_user(user_name="testuser",email="testuser@gmail.com", password="testpassword")
    
#     # Generate a valid refresh token for the user
#     refresh = RefreshToken.for_user(user)

#     # Create a test client
#     client = APIClient()

#     # Act: Make a POST request to the refresh token endpoint
#     url = reverse('refresh_token')  # Replace with your actual view name
#     data = {"refresh": str(refresh)}
#     response = client.post(url, data, format="json")

#     # Assert: Verify the response
#     assert response.status_code == 200