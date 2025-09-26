from django.test import TestCase
from artists.serializers.serializers import ArtistProfileSerializer
from artists.models.models import ArtistProfile
from users.models import User


class ArtistProfileSerializerTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testartist',
            email='test@example.com',
            password='testpass123'
        )

        # Create a test artist profile
        self.artist_profile = ArtistProfile.objects.create(
            user=self.user,
            first_name='Test',
            last_name='Artist',
            phone='1234567890',
            email='test@example.com',
            gender='female',
            date_of_birth='1990-01-01'  # This should not appear in serializer output
        )

    def test_date_of_birth_not_in_serializer_fields(self):
        """Test that date_of_birth is not included in the serializer fields"""
        serializer = ArtistProfileSerializer(self.artist_profile)
        data = serializer.data

        # Assert that date_of_birth is not in the serialized data
        self.assertNotIn('date_of_birth', data)

        # Assert that other expected fields are present
        expected_fields = [
            'id', 'first_name', 'last_name', 'phone', 'email', 'gender',
            'referel_code', 'offer_chosen', 'bio'
        ]

        for field in expected_fields:
            self.assertIn(field, data)

    def test_serializer_fields_list(self):
        """Test that date_of_birth is not in the Meta.fields"""
        meta_fields = ArtistProfileSerializer.Meta.fields

        # Assert that date_of_birth is not in the fields list
        self.assertNotIn('date_of_birth', meta_fields)

        # Assert that other fields are present
        self.assertIn('first_name', meta_fields)
        self.assertIn('last_name', meta_fields)
        self.assertIn('phone', meta_fields)
        self.assertIn('email', meta_fields)
        self.assertIn('gender', meta_fields)
