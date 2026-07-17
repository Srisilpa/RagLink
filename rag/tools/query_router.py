import re



def classify_query(question):

    q = question.lower().strip()



    # Calculator

    if re.match(
        r"^[0-9+\-*/().\s]+$",
        q
    ):

        return "calculator"



    # Date

    date_keywords = [

        "date",
        "current date",
        "what day",
        "what is the date"

    ]


    if any(
        word in q
        for word in date_keywords
    ):

        return "date"



    # Time

    time_keywords = [

        "time",
        "current time",
        "what time"

    ]


    if any(
        word in q
        for word in time_keywords
    ):

        return "time"



    # Web Search

    web_keywords = [

        "latest",
        "news",
        "who is",
        "ceo of",
        "founder of",
        "headquarters of",
        "where is",
        "website of",
        "stock price",
        "share price",
        "market value",
        "revenue of",
        "profit of",
        "acquisition",
        "merger",
        "launch",
        "announcement",
        "recent update"

    ]


    if any(
        word in q
        for word in web_keywords
    ):

        return "web"



    # Default

    return "rag"