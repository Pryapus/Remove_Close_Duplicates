from closeio_api import Client
import os
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

api = Client(os.getenv('CLOSE_API_KEY'))

# Function to get all leads
def get_all_leads():
    has_more = True
    offset = 0
    leads = []
    while has_more:
        resp = api.get('lead', params={'_skip': offset, '_limit': 100})
        leads.extend(resp['data'])
        has_more = resp['has_more']
        offset += len(resp['data'])
    return leads

# Function to find exact duplicates by name
def find_duplicates(leads):
    duplicates = defaultdict(list)
    for lead in leads:
        duplicates[lead['name']].append(lead)
    return {k: v for k, v in duplicates.items() if len(v) > 1}

# Function to merge leads
def merge_leads(source_id, destination_id):
    data = {
        "source": source_id,
        "destination": destination_id
    }
    return api.post('lead/merge', data=data)

# Main execution
if __name__ == "__main__":
    error_list = []
    # Get all leads
    print("Fetching all leads...")
    all_leads = get_all_leads()
    print(f"Found {len(all_leads)} leads.")

    # Find duplicates
    print("Checking for duplicates...")
    duplicate_groups = find_duplicates(all_leads)
    print(f"Found {len(duplicate_groups)} groups of duplicates.")

    # Merge duplicates
    for name, dupes in duplicate_groups.items():
        print(f"\nMerging duplicates for '{name}':")
        destination = dupes[0]  # Use the first lead as the destination
        for source in dupes[1:]:
            print(f"Merging {source['id']} into {destination['id']}...")
            try:
                result = merge_leads(source['id'], destination['id'])
                print("Merge successful.")
            except Exception as e:
                error_list.append((source['id'], destination['id'], str(e)))
                print(f"Error merging leads: {str(e)}")

    print("\nDuplicate merging process completed.")