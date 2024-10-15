from django.test import TestCase, SimpleTestCase
from django.contrib.auth.models import User
from .models import Donation, Crowdfunding
from decimal import Decimal
from django.urls import reverse, resolve
from .forms import FundraiserForm
from .models import Crowdfunding
from django.core.files.uploadedfile import SimpleUploadedFile
from .views import dashboard_view
from PIL import Image
import io

class DonationModelTest(TestCase):
    def setUp(self):
        # Set up user and crowdfunding objects for use in tests
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.crowdfunding = Crowdfunding.objects.create(
            title="Test Campaign", 
            amountNeeded=5000
        )

    def test_donation_creation(self):
        """Test that a Donation object can be created and its fields saved correctly."""
        donation = Donation.objects.create(user=self.user, amount=Decimal('100.50'), crowdfunding=self.crowdfunding)
        
        # Check that the donation was created
        self.assertEqual(Donation.objects.count(), 1)
        
        # Check the values of the donation fields
        self.assertEqual(donation.user, self.user)
        self.assertEqual(donation.amount, Decimal('100.50'))
        self.assertEqual(donation.crowdfunding, self.crowdfunding)

    def test_donation_without_user(self):
        """Test that a Donation can be created without a user (i.e., user is null)."""
        donation = Donation.objects.create(amount=Decimal('50.00'), crowdfunding=self.crowdfunding)
        
        # Check that the donation was created and user is null
        self.assertEqual(donation.user, None)
        self.assertEqual(donation.amount, Decimal('50.00'))

    def test_donation_relationship(self):
        """Test that the Donation model is related to the User and Crowdfunding models correctly."""
        donation = Donation.objects.create(user=self.user, amount=Decimal('25.75'), crowdfunding=self.crowdfunding)
        
        # Check if donation is correctly linked to user and crowdfunding
        self.assertEqual(donation.user.username, 'testuser')
        self.assertEqual(donation.crowdfunding.title, 'Test Campaign')
        
class ViewTests(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/campaign-list/') # Direct URL path
        self.assertEqual(response.status_code, 200)

    def test_view_accessible_by_name(self):
        response = self.client.get(reverse('campaign-list'))  # URL name from urls.py
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('campaign-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/campaign-list.html')
        
class URLTests(SimpleTestCase):
    def test_my_view_url_is_resolved(self):
        url = reverse('dashboard')  # URL name from urls.py
        self.assertEqual(resolve(url).func, dashboard_view)  # Ensures URL resolves to the correct view function/class

# class FundraiserFormTest(TestCase):
#     def test_fundraiser_form_valid(self):
#         image = io.BytesIO()
#         img = Image.new('RGB', (100, 100), color='red')
#         img.save(image, format='JPEG')
#         image.seek(0)  # Go back to the beginning of the BytesIO object

#         # Create a SimpleUploadedFile instance with the valid image
#         image_file = SimpleUploadedFile("test_image.jpg", image.read(), content_type="image/jpeg")
#         print(f"{image_file}, image file")
#         # Create valid form data
#         form_data = {
#             'title': 'Test Campaign',
#             'description': 'This is a test description',
#             'address': '123 Test St',
#             'state': 'Test State',
#             'lga': 'Test LGA',
#             'firstName': 'John',
#             'lastName': 'Doe',
#             'amountNeeded': 5000,
#             'image': image_file  # Include image directly in form data
#         }

#         # Create the form with valid data and files
#         form = FundraiserForm(data=form_data)

#         # Combine form data with the image
#         # form_data_with_file = {**form_data, 'image': image_file}

#         # Create the form with valid data
#         # form = FundraiserForm(data=form_data, files={'image': image})

#         # Check if the form is valid
#         if not form.is_valid():
#             print(form.errors)  # Debug output to see form errors
#         self.assertTrue(form.is_valid())

#         # Save the form and verify it saves correctly
#         crowdfunding = form.save()
#         self.assertEqual(crowdfunding.title, form_data['title'])
#         self.assertEqual(crowdfunding.state, form_data['state'])
        
#Testing fundraiser form with invalid data.
class FundraiserFormInvalidTest(TestCase):
    def test_fundraiser_form_invalid(self):
        # Test form data with missing required fields (e.g., missing 'title')
        form_data = {
            'description': 'This is a test description',
            'address': '123 Test St',
            'state': 'Test State',
            'lga': 'Test LGA',
            'firstName': 'John',
            'lastName': 'Doe',
            'amountNeeded': 5000
        }

        form = FundraiserForm(data=form_data)
        
        # Check if the form is invalid
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        
#testing custom labels
class FundraiserFormLabelTest(TestCase):
    def test_fundraiser_form_labels(self):
        form = FundraiserForm()

        # Check custom labels
        self.assertEqual(form.fields['image'].label, 'Profile Picture')
        self.assertEqual(form.fields['amountNeeded'].label, 'Amount Needed')


