"""Search trustworthy public web sources when course RAG has no evidence."""

from dataclasses import dataclass

import httpx

from backend.app.core.config import Settings


@dataclass(slots=True)
class WebSearchHit:
    title: str
    url: str
    snippet: str


@dataclass(slots=True)
class WebSearchResult:
    hits: list[WebSearchHit]
    available: bool
    message: str | None = None


@dataclass(slots=True)
class SearchWebTool:
    """A Tavily-backed tool; it is only called after local RAG has no results."""

    settings: Settings

    async def search(self, query: str) -> WebSearchResult:
        clean_query = query.strip()
        if not clean_query:
            return WebSearchResult(hits=[], available=False, message="Không có từ khóa để tìm web.")
        if self.settings.web_search_provider.casefold() != "tavily":
            return WebSearchResult(
                hits=[],
                available=False,
                message="Nhà cung cấp web search hiện chưa được hỗ trợ.",
            )
        if not self.settings.web_search_api_key:
            return WebSearchResult(
                hits=[],
                available=False,
                message="Web search chưa được cấu hình API key.",
            )

        payload = {
            "api_key": self.settings.web_search_api_key,
            "query": clean_query,
            "search_depth": "basic",
            "max_results": self.settings.web_search_max_results,
            "include_answer": False,
            "include_raw_content": False,
        }
        try:
            async with httpx.AsyncClient(timeout=self.settings.web_search_timeout_seconds) as client:
                response = await client.post("https://api.tavily.com/search", json=payload)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError:
            return WebSearchResult(
                hits=[],
                available=True,
                message="Không thể kết nối web search ở thời điểm này.",
            )

        hits: list[WebSearchHit] = []
        seen_urls: set[str] = set()
        for item in body.get("results", []):
            url = str(item.get("url", "")).strip()
            title = str(item.get("title", "")).strip()
            snippet = str(item.get("content", "")).strip()
            if not url or not title or url in seen_urls:
                continue
            seen_urls.add(url)
            hits.append(WebSearchHit(title=title, url=url, snippet=snippet))
        return WebSearchResult(hits=hits, available=True)
