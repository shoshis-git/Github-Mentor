import json
import os
import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from langchain.tools import tool
from urllib.parse import urlparse




@tool
def get_github_repo_pull_requests(owner: str, repo: str) -> dict:
    """Get the list of pull requests for a GitHub repository
    
    Args:
        owner: Owner of the repo
        repo: Name of the repo
    """
    owner = quote(owner.strip(), safe="")
    repo_name = quote(repo.strip(), safe="")
    url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls?state=open&per_page=10"

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-mentor",
        "X-GitHub-Api-Version": "2026-03-10",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, headers=headers)
    
    ssl_context = ssl._create_unverified_context()
    try:
        with urlopen(request, timeout=10,context= ssl_context) as response:
            raw_prs = json.loads(response.read().decode("utf-8"))
            simplified_prs = []
            for pr in raw_prs:
                simplified_prs.append({
                    "number": pr.get("number"),
                    "title": pr.get("title"),
                    "state": pr.get("state"),
                    "created_at": pr.get("created_at"),
                    "author": pr.get("user", {}).get("login")
                })
            return {"pull_requests": simplified_prs}
    except HTTPError as error:
        return {
            "error": error.reason,
            "status": error.code,
            "message": error.read().decode("utf-8", errors="replace"),
        }
    except URLError as error:
        return {"error": str(error.reason)}



@tool
def resolve_github_url(url: str) -> dict:
    """
    Takes a regular GitHub URL and extracts the repository owner and repository name.
    
    Args:
        url: The full GitHub URL (e.g., https://github.com/owner/repo)
    """
    try:
        # מפרק את הכתובת למרכיבים שלה
        parsed_url = urlparse(url)
        
        # לוקח רק את הנתיב (למשל: "/danny-avila/LibreChat") ומוריד לוכסנים מיותרים בקצוות
        path = parsed_url.path.strip("/")
        
        # מפצל את הנתיב לרשימה של מילים לפי הלוכסן
        parts = path.split("/")
        
        # אם יש לפחות שני איברים ברשימה, הראשון הוא הבעלים והשני הוא המאגר
        if len(parts) >= 2:
            owner = parts[0]
            repo = parts[1]
            print(owner,repo)
            return {"owner": owner, "repo": repo}
        else:
            return {"error": "Could not extract owner and repo from the provided URL. Please ensure it is a valid GitHub URL."}
            
    except Exception as e:
        return {"error": f"Failed to parse URL: {str(e)}"}




@tool
def list_prs(owner: str, repo: str) -> dict:
    """
    Search for merged pull requests in a GitHub repository that focus on refactoring.
    
    Args:
        owner: Owner of the repo
        repo: Name of the repo
    """
    owner = quote(owner.strip(), safe="")
    repo_name = quote(repo.strip(), safe="")
    
    # שימוש ב-Search API כדי לסנן PRs שמוזגו וכוללים את המילה Refactor
    query = f"repo:{owner}/{repo_name}+is:pr+is:merged+Refactor"
    url = f"https://api.github.com/search/issues?q={query}&per_page=10&sort=created&order=desc"

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-mentor",
        "X-GitHub-Api-Version": "2026-03-10", 
    }
    
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, headers=headers)
    ssl_context = ssl._create_unverified_context()

    try:
        with urlopen(request, timeout=10, context=ssl_context) as response:
            data = json.loads(response.read().decode("utf-8"))
            
            # ב-Search API, התוצאות יושבות בתוך מפתח שנקרא "items"
            raw_prs = data.get("items", [])
            
            # --- מיפוי הפלט ל-LLM לפי האפיון ---
            simplified_prs = []
            for pr in raw_prs:
                simplified_prs.append({
                    "number": pr.get("number"),
                    "title": pr.get("title"),
                    "state": "merged" # אנחנו יודעים בוודאות שזה מוזג בזכות הסיליון ב-API
                })
                print(simplified_prs)
            return {"pull_requests": simplified_prs}
            
    except HTTPError as error:
        return {
            "error": error.reason,
            "status": error.code,
            "message": error.read().decode("utf-8", errors="replace"),
        }
    except URLError as error:
        return {"error": str(error.reason)}

# @tool
# def get_pull_request(owner: str, repo: str)-> dict:
    


if __name__=="__main__":
    #resolve_github_url("https://github.com/shoshis-git/outlook")
    list_prs.invoke({"owner": "LibreChat-AI", "repo": "LibreChat"})
