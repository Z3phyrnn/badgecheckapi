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
