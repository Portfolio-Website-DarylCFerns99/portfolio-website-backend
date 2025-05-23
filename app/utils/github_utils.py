import re
import httpx
from fastapi import HTTPException
import os
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

def is_absolute_url(url: str) -> bool:
    """Check if a URL is absolute (starts with http:// or https://)"""
    return url.startswith(('http://', 'https://'))

def is_relative_path(path: str) -> bool:
    """Check if a path is relative (not absolute URL, not starting with /, not email)"""
    if is_absolute_url(path):
        return False
    if path.startswith('/'):
        return False
    if '@' in path and not '/' in path:  # likely an email
        return False
    if path.startswith('#'):  # anchor link
        return False
    return True

def convert_relative_links(markdown_content: str, github_url: str, branch: str = 'main') -> str:
    """
    Convert relative links in markdown to absolute GitHub URLs
    
    Args:
        markdown_content (str): The markdown content to process
        github_url (str): The base GitHub repository URL (e.g., 'https://github.com/user/repo')
        branch (str): The branch name to use (default: 'main')
    
    Returns:
        str: Modified markdown content with absolute URLs
    """
    
    # Ensure github_url doesn't end with slash
    github_url = github_url.rstrip('/')
    
    # Pattern 1: Complex image links with clickable image [![alt](path)](path)
    def replace_complex_image_link(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        link_path = match.group(3)
        
        new_image_path = image_path
        new_link_path = link_path
        
        if is_relative_path(image_path):
            new_image_path = f"{github_url}/{image_path}"
        
        if is_relative_path(link_path):
            new_link_path = f"{github_url}/{link_path}"
        
        return f"[![{alt_text}]({new_image_path})]({new_link_path})"
    
    # Pattern 2: Simple image links ![alt](path)
    def replace_simple_image_link(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        
        if is_relative_path(image_path):
            new_path = f"{github_url}/{image_path}"
            return f"![{alt_text}]({new_path})"
        return match.group(0)
    
    # Pattern 3: Regular links [text](path)
    def replace_regular_link(match):
        link_text = match.group(1)
        link_path = match.group(2)
        
        if is_relative_path(link_path):
            new_path = f"{github_url}/{link_path}"
            return f"[{link_text}]({new_path})"
        return match.group(0)
    
    # Apply replacements in order (most specific first)
    
    # 1. Complex image links [![alt](path)](path)
    markdown_content = re.sub(
        r'\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)',
        replace_complex_image_link,
        markdown_content
    )
    
    # 2. Simple image links ![alt](path) (not already part of complex links)
    markdown_content = re.sub(
        r'(?<!\[)!\[([^\]]*)\]\(([^)]+)\)(?!\])',
        replace_simple_image_link,
        markdown_content
    )
    
    # 3. Regular links [text](path) (not image links)
    markdown_content = re.sub(
        r'(?<!!)(?<!\])\[([^\]]+)\]\(([^)]+)\)',
        replace_regular_link,
        markdown_content
    )
    
    return markdown_content

async def fetch_github_data(github_url: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Extracts username and repository name from a GitHub URL and fetches 
    repository data from the GitHub API.
    
    Args:
        github_url: The GitHub repository URL
        
    Returns:
        Tuple containing:
        - Dictionary with basic project data
        - Complete GitHub API response to store in additional_data
    """
    # Extract username and repo name from GitHub URL
    pattern = r"https?://github\.com/([^/]+)/([^/]+)(?:/.*)?$"
    match = re.match(pattern, github_url)
    
    if not match:
        raise HTTPException(
            status_code=400, 
            detail="Invalid GitHub URL format. Expected: https://github.com/{username}/{repo}"
        )
        
    username, repo_name = match.groups()
    
    # Construct GitHub API URL
    api_url = f"https://api.github.com/repos/{username}/{repo_name}"
    
    # GitHub token from environment variable (if available)
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
        headers["X-GitHub-Api-Version"] = "2022-11-28"
    
    logger.info(f"Fetching GitHub data for: {github_url}")
    
    # Make request to GitHub API
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"GitHub API error: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"GitHub API returned {response.status_code}: {response.text}"
            )
        
        # Complete GitHub API response
        github_data = response.json()
        
        # Fetch README.md file
        raw_github_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/main/"
        readme_url = f"{raw_github_url}/README.md"
        try:
            readme_response = await client.get(readme_url, follow_redirects=True)
            if readme_response.status_code == 200:
                github_data['readme_file'] = convert_relative_links(readme_response.text, raw_github_url)
            else:
                github_data['readme_file'] = None
                logger.info(f"README not found at main branch, status: {readme_response.status_code}")
        except Exception as e:
            github_data['readme_file'] = None
            logger.error(f"Error fetching README: {str(e)}")
        
        # Fetch languages data
        languages_url = github_data.get('languages_url')
        if languages_url:
            try:
                languages_response = await client.get(languages_url, headers=headers)
                if languages_response.status_code == 200:
                    github_data['languages'] = languages_response.json()
                else:
                    github_data['languages'] = {}
                    logger.info(f"Languages data not available, status: {languages_response.status_code}")
            except Exception as e:
                github_data['languages'] = {}
                logger.error(f"Error fetching languages data: {str(e)}")
        else:
            github_data['languages'] = {}
        
        # Extract relevant information for project fields
        basic_data = {
            "title": github_data.get("name", ""),
            "description": github_data.get("description", ""),
            "url": github_url,  # Use the original URL provided by the user
            # Other fields (type, image, tags) should be provided by the user
        }
        
        return basic_data, github_data
