from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import json
import traceback

from .services import ChatService

# Lazy initialization
chat_service = None


@login_required
def chatbot_page(request):
    return render(
        request,
        "chatbot/chat.html"
    )


@csrf_exempt
def chat(request):

    global chat_service

    if chat_service is None:
        print("Initializing ChatService...")
        chat_service = ChatService()

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required"},
            status=405
        )

    try:

        data = json.loads(request.body)

        question = data.get("message", "")

        result = chat_service.ask(question)

        return JsonResponse(result)

    except Exception as e:

        traceback.print_exc()

        return JsonResponse(
            {
                "error": str(e)
            },
            status=500
        )