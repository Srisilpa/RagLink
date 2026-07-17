from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import json

from .services import ChatService

chat_service = ChatService()


@login_required
def chatbot_page(request):
    return render(request, "chatbot/chat.html")


@csrf_exempt
def chat(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required"},
            status=405
        )

    try:
        data = json.loads(request.body)

        question = data.get("message", "")

        result = chat_service.ask(question)

        print("\n========== RESULT ==========")
        print(result)
        print("============================\n")

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )