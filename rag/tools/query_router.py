import re


def classify_query(question: str) -> str:

    q = question.lower().strip()

    # Normalize punctuation
    q = re.sub(
        r"[^\w\s?]",
        "",
        q
    )

    # =====================================================
    # EMPTY
    # =====================================================

    if not q:
        return "rag"

    # =====================================================
    # CHAT
    # =====================================================

    chat_keywords = [
        "hi",
        "hii",
        "hiii",
        "hello",
        "hey",
        "thanks",
        "thank you",
        "good morning",
        "good afternoon",
        "good evening",
        "good night",
    ]

    if q in chat_keywords:
        return "chat"

    chat_patterns = [
        "can you help me",
        "could you help me",
        "how can you help me",
        "what can you do",
        "who are you",
        "how are you",
        "what are you",
    ]

    if any(
        phrase in q
        for phrase in chat_patterns
    ):
        return "chat"

    # =====================================================
    # CALCULATOR
    # =====================================================

    if (
        re.fullmatch(
            r"[0-9+\-*/().\s]+",
            q
        )
        and any(
            c.isdigit()
            for c in q
        )
        and any(
            op in q
            for op in "+-*/"
        )
    ):
        return "calculator"

    # =====================================================
    # DATE
    # =====================================================

    date_keywords = [
        "todays date",
        "today date",
        "current date",
        "what is todays date",
        "what is the current date",
        "what day is today",
        "what day is it today",
    ]

    if any(
        phrase in q
        for phrase in date_keywords
    ):
        return "date"

    # =====================================================
    # TIME
    # =====================================================

    time_keywords = [
        "current time",
        "what time is it",
        "what is the time",
        "whats the time",
        "time now",
        "current time now",
    ]

    if any(
        phrase in q
        for phrase in time_keywords
    ):
        return "time"

    # =====================================================
    # WEB
    # =====================================================

    web_keywords = [
        "latest",
        "latest news",
        "recent news",
        "news about",
        "current news",
        "todays news",
        "who is the ceo of",
        "who is ceo of",
        "ceo of",
        "chief executive officer of",
        "founder of",
        "website of",
        "stock price",
        "share price",
        "market value",
        "revenue of",
        "profit of",
        "acquisition",
        "merger",
        "recent update",
        "latest update",
        "current update",
        "recent announcement",
        "latest announcement",
        "current announcement",
    ]

    if any(
        phrase in q
        for phrase in web_keywords
    ):
        return "web"

    # =====================================================
    # DEFAULT → COMPANY KNOWLEDGE BASE
    # =====================================================

    return "rag"