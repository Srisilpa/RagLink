import re


def classify_query(question: str) -> str:
    """
    Classifies user query into:

    calculator
    date
    time
    web
    rag
    chat

    """

    q = question.lower().strip()


    # =========================================================
    # EMPTY QUERY
    # =========================================================

    if not q:
        return "rag"



    # =========================================================
    # SIMPLE CHAT
    # =========================================================

    chat_keywords = [

        "hi",
        "hello",
        "hey",
        "thanks",
        "thank you",
        "good morning",
        "good evening",

    ]


    if q in chat_keywords:

        return "chat"



    # =========================================================
    # CALCULATOR
    #
    # Examples:
    # 44/4
    # 10 + 20
    # (5*4)/2
    #
    # Avoid:
    # 2026
    # employee123
    # project 101
    #
    # =========================================================

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



    # =========================================================
    # DATE
    #
    # Only real calendar date questions.
    #
    # Avoid:
    # joining date
    # project date
    # release date
    #
    # =========================================================

    date_keywords = [

        "today's date",

        "todays date",

        "today date",

        "current date",

        "what is today's date",

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



    # =========================================================
    # TIME
    #
    # Avoid broad "time"
    #
    # Because:
    #
    # "salary discrepancy resolution time"
    #
    # should go to RAG.
    #
    # =========================================================

    time_keywords = [

        "current time",

        "what time is it",

        "what is the time",

        "what's the time",

        "time now",

        "current time now",

    ]


    if any(

        phrase in q

        for phrase in time_keywords

    ):

        return "time"



    # =========================================================
    # WEB SEARCH
    #
    # External/current information.
    #
    # =========================================================

    web_keywords = [

        "latest",

        "latest news",

        "recent news",

        "news about",

        "current news",

        "today's news",

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



    # =========================================================
    # DEFAULT
    #
    # Company documents:
    # - HR policies
    # - projects
    # - technical docs
    # - infrastructure
    #
    # =========================================================

    return "rag"