def calculator(expression):

    try:
        return str(eval(expression))

    except Exception:
        return "Invalid calculation"