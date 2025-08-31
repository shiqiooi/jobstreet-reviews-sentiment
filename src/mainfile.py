from csv import QUOTE_ALL, QUOTE_NONNUMERIC
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import os
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk import pos_tag
from collections import Counter
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style

def get_ratings(
    driver: webdriver.Chrome | webdriver.Firefox | webdriver.Safari | webdriver.Edge,
    url: str,
):
    driver.get(url)

    css_selector = "div[id^='review-card-'] > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) :nth-child(2) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1)"
    page = 0
    ratings: list[float] = []
    while page < 2:
        page += 1
        elems = driver.find_elements(By.CSS_SELECTOR, css_selector)
        ratings_in_page = [float(e.text) for e in elems]
        print(page, ratings_in_page)
        if ratings_in_page:
            ratings.extend(ratings_in_page)
        try:
            next_button = driver.find_element(
                By.CSS_SELECTOR, "a[title='Next'][aria-hidden='false']"
            )
            if next_button:
                next_button.click()
        except NoSuchElementException:
            break
    return ratings

def get_reviews(
    driver: webdriver.Chrome | webdriver.Firefox | webdriver.Safari | webdriver.Edge,
    url: str,
):
    limit = 200
    driver.get(url)
    company_name_selector = "div#app > div > div > div > :nth-child(1) > :nth-child(2) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(2) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(3) > :nth-child(1) > div > :nth-child(1) > :nth-child(1) > :nth-child(1) > h4"
    position_selector = ":nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(1) > :nth-child(2) > :nth-child(1) > span"
    summary_selector = "h4"
    rating_selector = "div > div > div > div > div > div > div > div:nth-child(1) > div > div:nth-child(1) > div > div > div > div:nth-child(2) > div > div > div:nth-child(1) > span"
    good_selector = "div > div > div > div > div:nth-child(2)> div > div > div:nth-child(2) > div > div:nth-child(2) > span"
    challenges_selector = "div > div > div > div > div:nth-child(2) > div > div > div:nth-child(3) > div > div:nth-child(2) > span"
    reviews = []
    page = 0
    chains = ActionChains(driver)

    company_name = driver.find_element(
        By.CSS_SELECTOR, company_name_selector).text
    print(company_name)

    while len(reviews) < 200:
        page += 1

        review_cards = driver.find_elements(
            By.CSS_SELECTOR, "div[id^='review-card-']")
        for card in review_cards:
            rating = card.find_element(By.CSS_SELECTOR, rating_selector)
            position = card.find_element(By.CSS_SELECTOR, position_selector)
            summary = card.find_element(By.CSS_SELECTOR, summary_selector)
            good = card.find_element(By.CSS_SELECTOR, good_selector)
            challenges = card.find_element(
                By.CSS_SELECTOR, challenges_selector)
            reviews.append(
                {
                    "rating": float(rating.text),
                    "position": position.text,
                    "summary": summary.text,
                    "good": good.text,
                    "challenges": challenges.text
                }
            )
            if limit > 0 and len(reviews) == limit:
                break
        print(f"Page {page:3d} ✅")

        if limit > 0 and len(reviews) == limit:
            break

        try:
            next_button = driver.find_element(
                By.CSS_SELECTOR, "a[title='Next'][aria-hidden='false']"
            )
            if next_button:
                chains.scroll_to_element(next_button)
                next_button.click()
                sleep(.5)
        except NoSuchElementException:
            break
    return reviews

def analyze_reviews(df: pd.DataFrame):

    reviews = df['good'].tolist() + df['challenges'].tolist()

    # Tokenize and preprocess the reviews
    stop_words = set(stopwords.words('english'))
    all_words = []
    for review in reviews:
        words = word_tokenize(review)
        words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]
        all_words.extend(words)

    # Calculate word frequencies
    freq_dist = FreqDist(all_words)

    # Use SentimentIntensityAnalyzer to determine sentiment
    sia = SentimentIntensityAnalyzer()
    positive_words = []
    negative_words = []
    for word, frequency in freq_dist.items():
        sentiment_score = sia.polarity_scores(word)['compound']
        if sentiment_score >= 0.5:
            positive_words.append((word, frequency))
        elif sentiment_score <= -0.5:
            negative_words.append((word, frequency))

    # Sort words by frequency and print top 5
    positive_words.sort(key=lambda x: x[1], reverse=True)
    negative_words.sort(key=lambda x: x[1], reverse=True)

    print("Top 5 positive keywords:")
    for word, frequency in positive_words[:5]:
        print(f"{word}: {frequency}")

    print("\nTop 5 negative keywords:")
    for word, frequency in negative_words[:5]:
        print(f"{word}: {frequency}")
        
def filtering(words):
  words = [word.lower() for word in words] 
  tagged_words = pos_tag(words)
  filter_tags = {
      'CC', 'DT', 'EX', 'IN','LS',
      'MD','NNP','NNPS','PRP$','SYM',
      'TO','UH','WDT','WP','WP$','WRB'
  }
  filtered_words = [word for word, pos in tagged_words if pos not in filter_tags and word != 'i']  # Added explicit check for 'i'
  return filtered_words

def count_repetitives(df: pd.DataFrame):
  column_name = "summary"
  words = df['summary'].str.lower().str.split()
  all_words = [word for sublist in words for word in sublist]
  all_words = filtering(all_words)
  word_counts = Counter(all_words)
  top_5_words = word_counts.most_common(5)

  print("The top 5 most repetitive words are:")
  for word, count in top_5_words:
      print(word, ":", count)
      


def main():
    url = "https://www.jobstreet.com.my/companies/top-glove-168556710434867/reviews"

    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)

    options = webdriver.ChromeOptions()
    binary_location = os.path.join(os.getcwd(), "chrome-linux64/chrome")
    options.binary_location = binary_location
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        result = get_reviews(driver, url)

        df = pd.DataFrame(result)
        df.to_csv("Top_Glove_Reviews.csv", quoting=QUOTE_NONNUMERIC)

        analyze_reviews(df)
        count_repetitives(df)
    except Exception as e:
        print(e)
    finally:
        driver.close()

os.chdir(r'/Users/chloe/swaassignment')
def reviews_barchart():
    top_glove_r = pd.read_csv("Top_Glove_Reviews.csv") # Read the CSV file into a DataFrame
    top_glove_r.head() # Check the first few rows of the DataFrame
    
    ratings = [1.0, 2.0, 3.0, 4.0, 5.0] 
    ratings_count = top_glove_r['rating'].value_counts().reindex(ratings, fill_value=0)
    plt.bar(ratings_count.index, ratings_count.values, tick_label=ratings_count.index)
    plt.xlabel('Rating Stars')
    plt.ylabel('Number of Ratings', fontsize=14)
    plt.title('Distribution of Ratings')
    
    plt.show()

# Plot bar chart for challenges column
def challenges_bar_chart(negative_words):
    negative_w = [x[0] for x in negative_words][:5]
    frequency = [x[1] for x in negative_words][:5]
    

plt.figure(figsize=(10,5))
plt.bar(negative_w, frequency, color ='blue')
plt.xlabel('Top 5 Negative Keywords')
plt.ylabel('Frequency')
plt.title('Frequency of Top 5 Negative Keywords in Reviews for Top Glove Graph')

plt.show()


if __name__ == "__main__":
    main()
    reviews_barchart()
