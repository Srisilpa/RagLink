def calculate(expression):

    try:

        result = eval(expression)


        # remove .0 from integer answers
        if isinstance(result, float) and result.is_integer():

            result = int(result)


        return f"{expression} = {result}"


    except ZeroDivisionError:

        return "Cannot divide by zero"


    except Exception:

        return "Invalid calculation"