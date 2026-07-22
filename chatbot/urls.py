from django.urls import path
from .views import chatbot_page, chat


urlpatterns = [

    path(
        "",
        chatbot_page,
        name="chatbot"
    ),

    path(
        "chat/",
        chat,
        name="chat_api"
    ),

]