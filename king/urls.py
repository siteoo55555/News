from django.urls import path,include
from .views import *   
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('register/', register, name='user'),
    path('confirm/', Confirm.as_view(), name='confirm'),
    path('name/', Create_Group.as_view(), name='name'),
    path('add/<int:id>/', Add_Members.as_view(),name='add'),
    path('help/', help, name='help'),
    path('channel/', Create_Channel.as_view(), name='channel'),
    path('login/', Login, name='login'),
    path('change/', Change_Password.as_view(), name='change_password'),
    path('user_edit/', User_Edit.as_view(), name='user_edit'),
    path('profile/', Create_Profile.as_view(), name='create_profile'),
    path('create_friend_chat/', Create_Friend_Chat.as_view(), name='create_friend_chat'),
    path('community/', about, name='about'),
    path('logout/', Logout, name='logout'),
    path('edit/<int:sen>',edit_function,name='edit'),
    path('delete/<int:me>',delete,name='delete'),
    path('remove/<int:id>/', Remove_Members.as_view(),name='remove'),
    path('delete_sms/<int:sms_id>/', delete_sms, name='delete_sms'),
    path('calculator/', calculator, name='calculator'),
    path('snake/', snake, name='snake'),
    path('flappy_bird/', flappy_bird, name='flappy_bird'),
    path('quiz/', quiz, name='quiz'),
    path('memory_game/', memory, name='memory_game'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)