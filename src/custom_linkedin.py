from linkedin_api.linkedin import Linkedin
from typing import Optional, List, Dict, Union
from urllib.parse import urlencode

class CustomLinkedin(Linkedin):
    def search_jobs(self, keywords: Optional[str] = None, listed_at=24 * 60 * 60, limit=-1, offset=0, **kwargs) -> List[Dict]:
        """Perform a LinkedIn search for jobs with custom parameters.

        :param keywords: Search keywords (str)
        :type keywords: str, optional
        :param listed_at: maximum number of seconds passed since job posting. Default is 24 hours.
        :type listed_at: int/str, optional
        :param limit: maximum number of results obtained from API queries. Default is -1 (no limit).
        :type limit: int, optional
        :param offset: indicates how many search results shall be skipped
        :type offset: int, optional
        :return: List of jobs
        :rtype: list
        """
        count = self._MAX_SEARCH_COUNT
        if limit is None:
            limit = -1

        query: Dict[str, Union[str, Dict[str, str]]] = {
            "origin": "JOB_SEARCH_PAGE_QUERY_EXPANSION"
        }
        if keywords:
            query["keywords"] = "KEYWORD_PLACEHOLDER"

        query["selectedFilters"] = {}
        query["selectedFilters"]["timePostedRange"] = f"List(r{listed_at})"
        query["spellCorrectionEnabled"] = "true"

        query_string = (
            str(query)
            .replace(" ", "")
            .replace("'", "")
            .replace("KEYWORD_PLACEHOLDER", keywords or "")
            .replace("{", "(")
            .replace("}", ")")
        )
        results = []
        while True:
            if limit > -1 and limit - len(results) < count:
                count = limit - len(results)
            default_params = {
                "decorationId": "com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-174",
                "count": count,
                "q": "jobSearch",
                "query": query_string,
                "start": len(results) + offset,
            }

            print(f"/voyagerJobsDashJobCards?{urlencode(default_params, safe='(),:')}")

            res = self._fetch(
                f"/voyagerJobsDashJobCards?{urlencode(default_params, safe='(),:')}",
                headers={"accept": "application/vnd.linkedin.normalized+json+2.1"},
            )
            data = res.json()

            elements = data.get("included", [])
            new_data = [
                i
                for i in elements
                if i["$type"] == "com.linkedin.voyager.dash.jobs.JobPosting"
            ]
            if not new_data:
                break
            results.extend(new_data)

            print("Results amount: ", len(results))
            print("Total amount: ", data.get("data", {}).get("paging", {}).get("total", 0))

            if (
                (-1 < limit <= len(results))
                or len(results) / count >= self._MAX_REPEATED_REQUESTS
            ) or len(elements) == 0:
                break

        return results