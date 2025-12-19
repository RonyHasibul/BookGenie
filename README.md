# 📖 Book Genie: Book Recommendation System

> **Book Genie** is a Machine Learning-powered web application that provides personalized book recommendations based on user preferences and collaborative filtering.

---

## 🚀 Features

* **Popular Books**: Displays top-rated books based on global user rankings.
* **Recommendation Engine**: Uses **Collaborative Filtering** to suggest books similar to a user's choice.
* **User Profiles**: Personalized greeting (*"Hi, Shuvro"*) and profile management.
* **Responsive Design**: A clean, horizontal navigation bar (Home, Recommend, Cart) optimized for all screen sizes.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Flask (Python) |
| **Database** | MySQL (via XAMPP) |
| **ML Libraries** | Scikit-learn, Pandas, NumPy |
| **Frontend** | HTML5, CSS3, Bootstrap |

---

## 📂 Project Structure

* `app.py`: Main application logic and routes.
* `Books Dataset/`: Contains the core `.csv` files for books, users, and ratings.
* `*.pkl`: Pre-trained ML models (`books.pkl`, `similarity_scores.pkl`, etc.) for fast recommendations.
* `Templates/`: HTML files for the UI layout.

---

## 🏃 How to Run

1. **Clone the repository:**
   ```bash
   𝙜𝙞𝙩 𝙘𝙡𝙤𝙣𝙚 𝙝𝙩𝙩𝙥𝙨://𝙜𝙞𝙩𝙝𝙪𝙗.𝙘𝙤𝙢/𝙍𝙤𝙣𝙮𝙃𝙖𝙨𝙞𝙗𝙪𝙡/𝘽𝙤𝙤𝙠𝙂𝙚𝙣𝙞𝙚.𝙜𝙞𝙩

2. **Install dependencies:**
   ```bash
   𝙥𝙞𝙥 𝙞𝙣𝙨𝙩𝙖𝙡𝙡 -𝙧 𝙧𝙚𝙦𝙪𝙞𝙧𝙚𝙢𝙚𝙣𝙩𝙨.𝙩𝙭𝙩

3. **Setup Database:**
    * Ensure your **XAMPP/MySQL** server is running.
    * Verify the database URI in `app.py` matches your local settings.

4. **Launch the app:**
   ```bash
   𝙥𝙮𝙩𝙝𝙤𝙣 𝙖𝙥𝙥.𝙥𝙮
