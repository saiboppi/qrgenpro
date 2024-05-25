from django.urls import path, include
from . import views as v

urlpatterns = [
    # path('/capimg'), v.members
    path('', v.members, name='members'),
    path('capimg/', v.capture_image, name='capimg'),
    path('imshow/', v.imshow, name='imshow'),


]