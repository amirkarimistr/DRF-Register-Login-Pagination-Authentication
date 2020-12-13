from django.shortcuts import render
from rest_framework.authtoken.views import ObtainAuthToken
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from .models import *
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.generics import ListAPIView
from .serializers import UserRegisterSerializer


class IndexPage(TemplateView):
    def get(self, request, **kwargs):
        all_articles = Article.objects.all().order_by('-created_at')
        promote_articles = Article.objects.filter(promote=True)

        context = {
            'article_data': all_articles,
            'promote_articles': promote_articles
        }

        return render(request, 'blog/index.html', context=context)


class ContactPage(TemplateView):
    template_name = 'blog/page-contact.html'


class PromoteArticleApiView(APIView):
    def get(self, request, format=None):
        try:
            promote_articles = Article.objects.filter(promote=True)
            data = []
            for article in promote_articles:
                data.append({
                    'title': article.title,
                    'category': article.category.title,
                    'cover': article.cover.url,
                    'avatar': article.author.avatar.url,
                    'author': article.author.user.username,
                    'created_at': article.created_at,
                    'promote': article.promote

                })

            return Response(data, status=status.HTTP_200_OK)

        except:
            return Response({'status': 'Bade request'}, status=status.HTTP_400_BAD_REQUEST)


class AllArticleApiView(APIView):
    def get(self, request, format=None):

        try:
            all_article = Article.objects.all().order_by('-created_at')[:10]
            data = []
            for article in all_article:
                data.append({
                    'title': article.title,
                    'cover': article.cover.url if article.cover.url else None,
                    'content': article.content,
                    'created_at': article.created_at,
                    'category': article.category.title,
                    'author': article.author.user.first_name + ' ' + article.author.user.last_name,
                    'promote': article.promote
                })

            return Response(data, status=status.HTTP_200_OK)
        except:
            return Response({'status': 'Bade request'}, status=status.HTTP_400_BAD_REQUEST)


class SingleArticleApiView(APIView):
    def get(self, request, format=None):
        try:
            article_title = request.GET['article_title']
            articles = Article.objects.filter(title__contains=article_title)
            serializer = SingleArticleSerializer(articles, many=True)
            data = serializer.data

            return Response({'data': data}, status=status.HTTP_200_OK)
        except:
            return Response({'status': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)


class SearchArticleApiView(APIView):
    def get(self, request, format=None):
        try:
            from django.db.models import Q

            query = request.GET['query']
            articles = Article.objects.filter(Q(content__icontains=query))

            data = []

            for article in articles:
                data.append({
                    'title': article.title,
                    'cover': article.cover.url if article.cover else None,
                    'content': article.content,
                    'created_at': article.created_at,
                    'category': article.category.title,
                    'author': article.author.user.first_name + ' ' + article.author.user.last_name,
                    'promote': article.promote
                })

                return Response({'data': data}, status=status.HTTP_200_OK)

        except:
            return Response({'status': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)


class SubmitArticleApiView(APIView):
    def post(self, request, format=None):
        try:
            serializer = SubmitArticleSerializer(data=request.data)

            if serializer.is_valid():
                title = serializer.data.get('title')
                cover = request.FILES['cover']
                content = serializer.data.get('content')
                category_id = serializer.data.get('category_id')
                author_id = serializer.data.get('author_id')
                promote = serializer.data.get('promote')
            else:
                return Response({'status': serializer.error_messages}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.get(id=author_id)
            author = UserProfile.objects.get(user=user)
            category = Category.objects.get(id=category_id)

            article = Article()
            article.title = title
            article.cover = cover
            article.content = content
            article.category = category
            article.author = author
            article.promote = promote

            article.save()
            return Response({'status': 'Ok'}, status=status.HTTP_200_OK)

        except:
            return Response({'status': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)


class UpdateArticleApiView(APIView):
    def post(self, request, format=None):
        try:

            serializer = UpdateArticleCoverSerializer(data=request.data)
            if serializer.is_valid():
                article_id = serializer.data.get('article_id')
                cover = request.FILES['cover']
            else:
                return Response({'status': 'Bad Request'}, status=status.HTTP_200_OK)

            Article.objects.filter(id=article_id).update(cover=cover)

            return Response({'status': 'ok'}, status=status.HTTP_200_OK)
        except:
            return Response({'status': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)


class DeleteArticleApiView(APIView):

    def post(self, request, format=None):
        try:
            serializer = DeleteArticleSerializer(data=request.data)
            if serializer.is_valid():
                article_id = serializer.data.get('article_id')
            else:
                return Response({'status': 'Bad Request'}, status=status.HTTP_200_OK)

            Article.objects.filter(id=article_id).delete()
            return Response({'status': 'Ok'}, status=status.HTTP_200_OK)


        except:
            return Response({'status': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    template_name = 'blog/create_article.html'
    fields = ['title', 'cover', 'content', 'category', 'promote']

    def form_valid(self, form):
        form.instance.author = self.request.user.userprofile
        return super().form_valid(form)


class SubmitUser(APIView):
    def post(self, request, format=None):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.data.get('username')
            email = serializer.data.get('email')
            password = serializer.data.get('password')
        else:
            return Response({'status': serializer.error_messages}, status=status.HTTP_400_BAD_REQUEST)

        User.objects.create_user(username=username, password=password, email=email).save()
        user = User.objects.filter(username=username).first()
        token = Token.objects.get(user=user).key
        user_id = user.pk
        return Response({'status': 'ok', 'token':token, 'user_id':user_id}, status=status.HTTP_200_OK)


class ApiArticleListView(ListAPIView):
    queryset = Article.objects.all()
    serializer_class = SingleArticleSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

