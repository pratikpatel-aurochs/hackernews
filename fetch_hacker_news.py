import requests
import os

# Function to get top story IDs
def get_top_story_ids():
    top_stories_url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
    response = requests.get(top_stories_url)
    return response.json()

# Function to get story details by ID
def get_story_by_id(story_id):
    story_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
    response = requests.get(story_url)
    return response.json()

# Function to filter stories based on keywords
def is_coding_related(story, keywords):
    title = story.get('title', '').lower()
    return any(keyword in title for keyword in keywords)

# Function to construct Google Chat card message
def create_google_chat_card(stories):
    sections = []
    for story in stories:
        sections.append({
            "widgets": [
                {
                    "keyValue": {
                        "topLabel": "Title",
                        "content": story['title'],
                        "contentMultiline": "true"
                    }
                },
                {
                    "keyValue": {
                        "topLabel": "URL",
                        "content": f"<a href='{story['url']}'>{story['url']}</a>",
                        "contentMultiline": "true"
                    }
                }
            ]
        })
    
    card_message = {
        "cards": [
            {
                "header": {
                    "title": "Coding-related Hacker News Stories",
                    "subtitle": "Curated stories related to coding and development",
                    "imageUrl": "https://news.ycombinator.com/favicon.ico",
                    "imageStyle": "IMAGE"
                },
                "sections": sections
            }
        ]
    }
    return card_message

# Function to send a message to Google Chat
def send_to_google_chat(card_message, webhook_url):
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    response = requests.post(webhook_url, json=card_message, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to send message to Google Chat: {response.content}")

# Main script
if __name__ == "__main__":
    # Fetch top stories
    top_story_ids = get_top_story_ids()

    # Define how many stories per page and which page you want
    stories_per_page = 30
    page_number = 2

    # Calculate offset
    start_index = (page_number - 1) * stories_per_page
    end_index = start_index + stories_per_page

    # Define coding-related keywords
    coding_keywords = ['code', 'programming', 'software', 'developer', 'coding', 'python', 'javascript', 'java', 'ruby', 'c#', 'c++', 'algorithm', 'data structures', 'web development', 'backend', 'frontend']

    # Fetch and filter stories for the specified page
    filtered_stories = []
    for story_id in top_story_ids[start_index:end_index]:
        story = get_story_by_id(story_id)
        if story and 'title' in story and 'url' in story and is_coding_related(story, coding_keywords):
            filtered_stories.append(story)

    # Prepare the card message to send to Google Chat
    if filtered_stories:
        card_message = create_google_chat_card(filtered_stories)
        webhook_url = os.environ.get('GOOGLE_CHAT_WEBHOOK')
        if webhook_url:
            send_to_google_chat(card_message, webhook_url)
        else:
            raise Exception("Google Chat webhook URL not found.")
    else:
        print("No coding-related stories found for the specified page.")
