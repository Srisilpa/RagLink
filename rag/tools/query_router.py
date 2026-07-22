import re


def classify_query(question: str) -> str:

    q = question.lower().strip()

    # =========================================================
    # EMPTY QUERY
    # =========================================================

    if not q:
        return "rag"


    # =========================================================
    # CALCULATOR
    # Examples:
    # 44/4
    # 10 + 20
    # (5 * 4) / 2
    # =========================================================

    if re.fullmatch(
        r"[0-9+\-*/().\s]+",
        q
    ):
        return "calculator"


    # =========================================================
    # DATE
    # =========================================================

    date_keywords = [

        "date",

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
    # =========================================================

    time_keywords = [
    "time",
    "current time",
    "what time is it",
    "what is the time",
    "what's the time",
    "time now",
    "current time now",
    "what time",
]

    if any(
        phrase in q
        for phrase in time_keywords
    ):
        return "time"


    # =========================================================
    # WEB SEARCH
    #
    # These are questions that require external/current
    # information.
    #
    # IMPORTANT:
    # Do NOT use broad keywords like:
    # "where is"
    # "who is"
    #
    # because company questions such as:
    # "Where is Series Tech headquartered?"
    # should go to RAG.
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
    # Company policies, HR, projects and technical questions
    # go to the internal RAG knowledge base.
    # =========================================================

    return "rag"