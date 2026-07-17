from ddgs import DDGS



def web_search(query):

    try:

        results = []


        with DDGS() as ddgs:

            search_results = ddgs.text(

                query,

                max_results=5

            )


            for item in search_results:

                results.append(

                    {

                        "title":
                        item.get("title"),


                        "snippet":
                        item.get("body"),


                        "url":
                        item.get("href")

                    }

                )


        return results



    except Exception as e:

        print(
            "DuckDuckGo Error:",
            e
        )

        return []