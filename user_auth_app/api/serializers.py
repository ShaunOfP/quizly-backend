from rest_framework import serializers

from django.contrib.auth.models import User

class RegistrationSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {
                'required': True
            }
        }

    def save(self):
        """Checks if passwords match and if email is already in use. Sets the account details and saves afterwards."""
        password = self.validated_data['password']
        confirmed_password = self.validated_data['confirmed_password']

        if password != confirmed_password:
            raise serializers.ValidationError({'error': 'Passwords do not match'})

        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({'error': 'Email already exists'})

        user = User(
            email=self.validated_data['email'],
            username=self.validated_data['username']
        )
        user.set_password(password)
        user.save()
        return user