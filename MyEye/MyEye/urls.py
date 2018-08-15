"""MyEye URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from django.conf.urls import url
from audit import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^login.html',views.login),
    url(r'^index.html', views.index),
    url(r'^multi_cmd.html', views.multi_cmd),
    url(r'^celery_test.html', views.celery_test),
    url(r'^multi_task_result.html', views.multi_task_result),
    url(r'^multi_task_cancel.html', views.multi_task_cancel),
    url(r'^multi_file.html', views.multi_file),
    url(r'^bootstrap.html', views.bootstrap),
    url(r'^rule$', views.rule_page),
    url(r'^rule/ID$', views.rule_operation),
    url(r'^rule/del/ID$', views.rule_del),
]
