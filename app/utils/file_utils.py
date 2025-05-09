import os
import base64
import uuid
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

async def process_social_links(social_links: List[Dict[str, Any]], files: Dict = None) -> List[Dict[str, Any]]:
    """
    Process social links data, handling both URL-based links and file uploads.
    
    Args:
        social_links (List[Dict]): List of social link objects that may contain file data
        files (Dict): Dictionary of uploaded files from the request
        
    Returns:
        List[Dict]: Processed social links with file data converted to appropriate format
    """
    if not social_links:
        return []
    
    processed_links = []
    
    for link in social_links:
        processed_link = {
            "platform": link.get("platform"),
            "tooltip": link.get("tooltip")
        }
        
        # If icon is provided, add it
        if "icon" in link and link["icon"]:
            processed_link["icon"] = link["icon"]
            
        # If this is a document/file type social link
        if link.get("platform") == "document" and "fileName" in link:
            processed_link["fileName"] = link.get("fileName")
            
            # Check if this is a file placeholder and we have the corresponding file
            url = link.get("url", "")
            if isinstance(url, str) and url.startswith("__FILE_PLACEHOLDER_") and files:
                # Extract the file index from the placeholder
                file_index = url.replace("__FILE_PLACEHOLDER_", "").replace("__", "")
                file_key = f"file_{file_index}"
                
                if file_key in files:
                    # Get the uploaded file
                    file = files[file_key]
                    
                    # Read the file content and encode it as base64
                    content = await file.read()
                    encoded_content = base64.b64encode(content).decode("utf-8")
                    
                    # Store the encoded content
                    processed_link["url"] = encoded_content
                else:
                    # File not found, use a placeholder
                    processed_link["url"] = "file_not_found"
                    logger.warning(f"File {file_key} not found in request files")
            else:
                # Use the provided URL (might be a base64 string already)
                processed_link["url"] = url
        else:
            # For regular links, just copy the URL
            processed_link["url"] = link.get("url")
                
        processed_links.append(processed_link)
    
    return processed_links

def extract_file_data_from_social_links(social_links: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract file data from social links for display in API responses.
    This function prepares social links for frontend consumption.
    
    Args:
        social_links (List[Dict]): Social links stored in the database
        
    Returns:
        List[Dict]: Social links with file data properly formatted for the frontend
    """
    if not social_links:
        return []
    
    formatted_links = []
    
    for link in social_links:
        formatted_link = {
            "platform": link.get("platform"),
            "tooltip": link.get("tooltip")
        }
        
        # Include icon if available
        if "icon" in link and link["icon"]:
            formatted_link["icon"] = link["icon"]
            
        # Handle document type links specially
        if link.get("platform") == "document" and "fileName" in link:
            formatted_link["fileName"] = link.get("fileName")
            formatted_link["url"] = link.get("url")  # Already contains the file data
        else:
            # For regular links, just copy the URL
            formatted_link["url"] = link.get("url")
            
        formatted_links.append(formatted_link)
    
    return formatted_links
