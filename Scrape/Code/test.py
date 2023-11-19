import sys
import os
import csv
import requests
from bs4 import BeautifulSoup

# Check if there are enough command-line arguments
if len(sys.argv) < 3:
    print("Please provide the URL of the website and the path to save the CSV files.")
    sys.exit(1)

# Get the URL from the command-line argument
url = str(sys.argv[1])
redirect_url = f"{url}/questions"
save_path = sys.argv[2].strip('"')  # Loại bỏ dấu ngoặc kép từ đầu và cuối đường dẫn

def get_question_details(post_url):
    question_response = requests.get(post_url)

    if question_response.status_code == 200:
        answers_soup = BeautifulSoup(question_response.content, "html.parser")

        # Find all containers for answers
        answers_containers = answers_soup.find_all("div", class_="answercell post-layout--right")

        if answers_containers:
            # Create a list to store the answer texts
            answer_texts = []

            # Iterate over each answers_container
            for answers_container in answers_containers:
                # Find the individual answer within the container
                answer = answers_container.find("div", class_="s-prose js-post-body")

                # Get the text of the answer
                answer_text = answer.text if answer else "No answer text available"

                # Append the answer text to the list
                answer_texts.append(answer_text)

            return answer_texts
        else:
            return ["No answer text available"]
    else:
        return ["Cannot access the question"]


# Send a GET request to the website
response = requests.get(redirect_url)

# Check if the request was successful
if response.status_code == 200:
    # Use BeautifulSoup to parse the HTML of the website
    soup = BeautifulSoup(response.content, "html.parser")

    # Get the total number of pages
    total_pages = soup.find("div", class_="s-pagination site642 themed pager float-left").find_all("a", class_="")
    if len(total_pages) >= 2:
        last_page = int(total_pages[-2].text)
    else:
        last_page = 1

    # Open the CSV files
    questions_file_path = os.path.join(save_path, "questions.csv")
    answers_file_path = os.path.join(save_path, "answers.csv")

    with open(questions_file_path, "w", newline='', encoding="utf-8") as questions_csv_file, open(answers_file_path, "w", newline='', encoding="utf-8") as answers_csv_file:
        questions_writer = csv.writer(questions_csv_file)
        answers_writer = csv.writer(answers_csv_file)

        questions_writer.writerow(["Question_Title", "Link", "Tags"])
        answers_writer.writerow(["Question_Title", "Answer"])

        # Iterate over each page
        for page in range(1, last_page + 1):  # Sửa ở đây để bao gồm cả trang cuối cùng
            page_url = f"{redirect_url}?tab=newest&page={page}"

            # Send a GET request to the page
            page_response = requests.get(page_url)

            if page_response.status_code == 200:
                page_soup = BeautifulSoup(page_response.content, "html.parser")

                # Create a list of posts
                posts = page_soup.find_all("div", class_="s-post-summary")

                # Iterate over each post on the page
                for post in posts:
                    question_title = post.find("h3", class_="s-post-summary--content-title").text
                    link = url + post.find("a", class_="s-link")['href']
                    tags = post.find_all("li", class_="d-inline mr4 js-post-tag-list-item")
                    tag_list = [tag.text for tag in tags]
                    questions_writer.writerow([question_title, link, ", ".join(tag_list)])

                    # Get the answers for the question
                    answer_list = get_question_details(link)
                    
                    # Check if the answer list is not ["Cannot access the question"] and not ["No answer text available"]
                    if answer_list != ["Cannot access the question"] and answer_list != ["No answer text available"]:
                        answers_writer.writerow([question_title, "\n".join(answer_list)])

    print(f"Data has been saved to {questions_file_path} and {answers_file_path}")
else:
    print("Request was unsuccessful")
