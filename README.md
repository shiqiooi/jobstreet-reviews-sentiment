# jobstreet-reviews-sentiment
Web scraping &amp; sentiment analysis of JobStreet employee reviews (Top Glove case study) using Python, Selenium, NLTK, and Matplotlib.

# JobStreet Reviews Sentiment Analysis

This project was developed for **SWA2124: Social and Web Analytics** (April 2024, Sunway University).  
It scrapes employee reviews of **Top Glove** from JobStreet and analyzes sentiments to provide insights into employee satisfaction.

---

## 📄 Contents
- `src/mainfile.py` → Python script for scraping & analysis
- `data/Top_Glove_Reviews.csv` → cleaned dataset (200 reviews)  
- `docs/SWA_Assignment.pdf` → full report & analysis 

---

## ⚙️ Tools & Libraries
- **Web Scraping**: Selenium WebDriver  
- **Text Processing**: NLTK (tokenization, stopwords, sentiment)  
- **Data Handling**: pandas, numpy  
- **Visualization**: matplotlib, seaborn  

---

## 🚀 How to Run
```bash
# Clone repo
git clone https://github.com/<your-username>/jobstreet-reviews-sentiment.git
cd jobstreet-reviews-sentiment

# Install dependencies
pip install -r requirements.txt

# Run scraper & analysis
python src/mainfile.py
