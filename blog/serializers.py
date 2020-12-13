from rest_framework import serializers
from django.contrib.auth import get_user_model


UserModel = get_user_model()


class SingleArticleSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=128, required=True, allow_null=False, allow_blank=False)
    cover = serializers.ImageField(required=True,use_url=True)
    content = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=2048)
    created_at = serializers.DateTimeField(required=True, allow_null=False, format='%d-%m-%Y')


class SubmitArticleSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=128)
    cover = serializers.FileField(required=True, allow_empty_file=False)
    content = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=2048)
    category_id = serializers.IntegerField(required=True, allow_null=False)
    author_id = serializers.IntegerField(required=True, allow_null=False)
    promote = serializers.BooleanField(required=True, allow_null=False)


class UpdateArticleCoverSerializer(serializers.Serializer):
    article_id = serializers.IntegerField(required=True, allow_null=False)
    cover = serializers.FileField(required=True, allow_null=False, allow_empty_file=False)


class DeleteArticleSerializer(serializers.Serializer):
    article_id = serializers.IntegerField(required=True, allow_null=False)


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128, allow_null=False)
    email = serializers.CharField(max_length=128, allow_null=False)
    password = serializers.CharField(max_length=128, allow_null=False)
