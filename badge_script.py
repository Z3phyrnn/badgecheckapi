import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from time import sleep

# Will print current amount of badges tracked if True
PRINT_PROGRESS = True
BATCH_PER_PRINT = 3000

def get_user_id_from_username(username: str) -> str:
    url = f"https://users.roblox.com/v1/usernames/users"
    params = {"usernames": [username]}
    response = requests.post(url, json=params)
    data = response.json()
    if response.status_code == 200 and data["data"]:
        return data["data"][0]["id"]
    raise Exception(f"Could not find the user ID for username {username}")

def check_can_view_inventory(user_id: str) -> bool:
    url = f"https://inventory.roproxy.com/v1/users/{user_id}/can-view-inventory"
    response = requests.get(url)
    retry_after = 5
    while response.status_code == 429:
        print(f"Rate limited. Retrying after {retry_after} seconds.")
        sleep(retry_after)
        response = requests.get(url)
        retry_after += 5
    response.raise_for_status()
    return response.json()["canView"]

def fetch_badges(user_id: str) -> list[dict]:
    url = f"https://badges.roproxy.com/v1/users/{user_id}/badges?limit=100&sortOrder=Desc"
    badges = []
    cursor = None
    while True:
        params = {}
        if cursor:
            params['cursor'] = cursor
        response = requests.get(url, params=params)
        data = response.json()
        for badge in data['data']:
            badges.append(badge)
            if PRINT_PROGRESS and len(badges) % BATCH_PER_PRINT == 0:
                print(f"{len(badges)} badges for {user_id} requested.")
        if data['nextPageCursor']:
            cursor = data['nextPageCursor']
        else:
            break
    return badges

def convertDateToDatetime(date: str) -> datetime:
    milliseconds_length = len(date.split('.')[-1])
    if '.' in date:
        if milliseconds_length > 4:
            dotInd = date.find('.')
            date = date[:dotInd + 4] + date[-1]
        elif milliseconds_length < 4:
            date = date[:-1] + '0' * (4 - milliseconds_length) + date[-1]
    else:
        date = date[:-1] + ".000" + date[-1]
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")

def fetch_award_dates(user_id: str, badges: list[dict]) -> list[str]:
    dates = []
    badge_ids = [badge["id"] for badge in badges]
    url = f"https://badges.roproxy.com/v1/users/{user_id}/badges/awarded-dates"
    STEP = 100
    for i in range(0, len(badge_ids), STEP):
        try:
            params = {"badgeIds": badge_ids[i:i + STEP]}
            response = requests.get(url, params=params)
            retry_after = 5
            while response.status_code == 429:
                print(f"Rate limited. Retrying after {retry_after} seconds.")
                sleep(retry_after)
                response = requests.get(url, params=params)
                retry_after += 5
            response.raise_for_status()
            for badge in response.json()["data"]:
                dates.append(badge["awardedDate"])
                if PRINT_PROGRESS and len(dates) % BATCH_PER_PRINT == 0:
                    print(f"{len(dates)} awarded dates for {user_id} requested.")
        except Exception as e:
            print(f"Error fetching data: {e}")
    return dates

def generate_badge_graph(username: str) -> str:
    user_id = get_user_id_from_username(username)
    can_view_inventory = check_can_view_inventory(user_id)

    if not can_view_inventory:
        raise Exception(f"Inventory for user {username} is not public.")

    badges = fetch_badges(user_id)
    if not badges:
        raise Exception(f"No badges found for user {username}.")

    dates = fetch_award_dates(user_id, badges)
    if not dates:
        raise Exception(f"No awarded dates found for badges for user {username}.")

    # Plot and save the image
    y_values = [convertDateToDatetime(date) for date in dates]
    y_values.sort()
    curr_count = 0
    cumulative_counts = []
    for date in y_values:
        curr_count += 1
        cumulative_counts.append(curr_count)

    plt.style.use('dark_background')
    plt.xlabel('Badge Earned Date')
    plt.ylabel('Badge Count')
    plt.title(f'{username} Badge History ({user_id})')
    plt.scatter(y_values, cumulative_counts, color='white', marker='o', alpha=0.1)

    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_facecolor('none')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.3, color='white')
    plt.figtext(0.05, 0.95, f"Badge Count: {len(y_values)}", ha="left", va="top", color="white", transform=ax.transAxes)
    
    output_path = f"BadgeCount-{username}-{user_id}.png"
    plt.savefig(output_path, bbox_inches="tight", transparent=True)
    plt.close()  # Free up memory
    return output_path
