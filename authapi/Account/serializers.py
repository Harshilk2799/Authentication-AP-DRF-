from rest_framework import serializers
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .models import CustomUser
from .utils import Util

class UserRegistrationSerializer(serializers.ModelSerializer):
    # We are writing this because we need password2 field in our Registration Request
    password2 = serializers.CharField(style={"input_type":"password"}, write_only=True)
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "password", "password2"]
        extra_kwargs = {"password": {"write_only":True}}
        
    # Validating password and confirm password while registration
    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")

        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password doesn't Match!")
        return attrs
    
    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)
    
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=255)
    class Meta:
        model = CustomUser
        fields = ["email", "password"]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "first_name", "last_name"]


class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255,style={"input_type":"password"}, write_only=True)
    password2 = serializers.CharField(max_length=255,style={"input_type":"password"}, write_only=True)
    class Meta:
        fields = ["password", "password2"]

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        user = self.context.get("user")
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password doesn't Match!")
        user.set_password(password)
        user.save()
        return attrs
    

class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email")
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            print("ID: ", user.id, "Byte: ", force_bytes(user.id))
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print("UID: ", uid) 
            token = PasswordResetTokenGenerator().make_token(user)
            print("Token: ", token)
            link = f"http://localhost:3000/api/user/reset/{uid}/{token}/"
            print("Link: ", link)
            
            # Send Email
            body = f"Click Following link to reset password {link}"
            data = {
                "subject":"Rest your password",
                "body":body,
                "to_email":user.email
            }
            Util.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError("You are not a Registered User...")
        

class UserPasswordRestSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255,style={"input_type":"password"}, write_only=True)
    password2 = serializers.CharField(max_length=255,style={"input_type":"password"}, write_only=True)
    class Meta:
        fields = ["password", "password"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            password2 = attrs.get("password2")
            uid = self.context.get("uid")
            token = self.context.get("token")
            
            if password != password2:
                raise serializers.ValidationError("Password and Confirm Password doesn't Match!")
            id = urlsafe_base64_decode(smart_str(uid))
            user = CustomUser.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Token is not Valid or Expired!")
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError("Token is not Valid or Expired!")