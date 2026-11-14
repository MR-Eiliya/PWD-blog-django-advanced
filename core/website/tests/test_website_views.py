from django.test import TestCase
from django.urls import reverse
from website.models import Contact


class ContactViewTests(TestCase):

    # Test contact page response and form rendering
    def test_contact_page_get(self):
        response = self.client.get(reverse("website:contact"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "website/contact.html")
        self.assertIn("form", response.context)


    # Test valid contact form submission
    def test_contact_form_valid_submission(self):
        data = {
            "first_name": "Ilya",
            "last_name": "Sharifi",
            "email": "ilya@example.com",
            "message": "I need a website.",
        }

        response = self.client.post(reverse("website:contact"), data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("website:contact"))
        self.assertEqual(Contact.objects.count(), 1)


    # Test invalid contact form submission
    def test_contact_form_invalid_submission(self):
        data = {
            "first_name": "Ilya",
            "last_name": "Sharifi",
            "email": "invalid-email",
            "message": "I need a website.",
        }

        response = self.client.post(reverse("website:contact"), data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(Contact.objects.count(), 0)