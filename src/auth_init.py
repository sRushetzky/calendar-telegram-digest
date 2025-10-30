
# ----------------------------------------------------------
# This script initializes Google Calendar authentication.
# It ensures that the OAuth flow works correctly by opening
# a browser window (if needed) for authorization, and then
# verifies access by listing the available calendars.
# ----------------------------------------------------------

from __future__ import annotations
from .google_client import get_service, list_calendars


def main():
    # Get the Google Calendar service object (runs OAuth flow if needed)
    svc = get_service()
    
    # Retrieve the list of calendars to confirm successful authentication
    cals = list_calendars()
    
    # Print confirmation message showing how many calendars were found
    print(f"Found {len(cals)} calendars. Auth OK ✅")


if __name__ == "__main__":
    # Entry point when this script is executed directly
    main()

