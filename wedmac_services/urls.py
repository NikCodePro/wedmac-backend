"""
URL configuration for wedmac_services project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/artists/', include('artists.urls')), 
    path('api/leads/', include('leads.urls')),  # Include leads app
    path('api/documents/', include('documents.urls')),  # Include documents app
    path('api/admin/', include('adminpanel.urls')),  # Include notifications app
    path('api/payment/', include('paymentgateway.urls')),
    path('api/masterdata/', include('masterdata.urls')),
    path('api/public/', include('public.urls')),  # Include public app
    path('api/blogs/', include('blogs.urls')),
    path('api/superadmin/', include('superadmin_auth.urls')),
    path('api/credits/', include('credit_history.urls')),
    path('api/support/', include('support_help.urls')),
    path('api/artist-services/', include('artist_services.urls')),
    path('api/reviews/', include('content_management.urls')),
    path('api/artist-comments/', include('artist_comments.urls')),
]
