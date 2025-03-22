import requests
import random
from protego import Protego
import logging

class WebUtils:
    """
    A utility class providing static methods for web-related operations.
    
    This class includes functionality for checking robots.txt rules and retrieving file sizes
    from URLs. It implements proper web crawling etiquette by respecting robots.txt directives
    and implementing appropriate delays between requests.
    """
    @staticmethod
    def check_robots_txt(base_url, target_url, user_agent):
        """
        Checks robots.txt for crawl permissions and delay.

        Args:
            base_url: The base URL of the website.
            target_url: The URL to check against robots.txt.
            user_agent: The user agent string.

        Returns:
            A tuple (can_fetch, request_delay).
            can_fetch: True if allowed to crawl, False otherwise.
            request_delay: Delay in seconds, or -1 on error.
        """
        try:
            rb_txt = requests.get(f"{base_url}/robots.txt")
            if rb_txt.status_code == 404: #robots.txt not found.
                return True, 0 #allow crawling, no delay.
            rb_txt.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx) other than 404

            rp = Protego.parse(rb_txt.text)
            can_fetch = rp.can_fetch(target_url, user_agent)
            crawl_delay = rp.crawl_delay(user_agent) or 0
            request_delay = random.uniform(crawl_delay, crawl_delay + 3)

            return can_fetch, request_delay

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching robots.txt: {e}")
            return True, 0 #allow crawling, no delay.
        except Exception as e:
            logging.error(f"Error processing robots.txt: {e}")
            return False, -1


    @staticmethod
    def get_file_size(url: str) -> int:
        """
        Retrieve the size of a file at the specified URL using a HEAD request.

        Args:
            url (str): The URL of the file to check

        Returns:
            int: The size of the file in bytes, or -1 if the size cannot be determined
                 or an error occurs

        Raises:
            Exception: Logs any errors that occur during the size check and returns -1

        Note:
            This method uses HEAD requests to minimize bandwidth usage when checking file sizes.
            The size is logged in megabytes for convenience but returned in bytes.
        """

        try:
            response = requests.head(url, allow_redirects=True)
            size = int(response.headers.get('Content-Length', -1))
            logging.info(f"File size: {size / (1024 * 1024):.2f} MB")
            return size
        except Exception as e:
            logging.error(f"Error getting file size: {e}")
            return -1
