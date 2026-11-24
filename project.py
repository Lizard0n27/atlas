import sqlite3
import sys
from datetime import date

DB_NAME = "atlas.db"


def main():
    """Main entry point: display menu and handle user choices."""
    init_db()

    while True:
        print("\nAtlas\n1: Setup user\n2: Add entry\n3: Review progress\n4: Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            new_user()
        elif choice == "2":
            new_entry()
        elif choice == "3":
            review_progress()
        elif choice == "4":
            sys.exit("See you soon!")
        else:
            print("Invalid option.")

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """create tables if they dont exist"""
    with connect_db() as conn:
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        age INTEGER NOT NULL,
        height REAL NOT NULL,
        goal TEXT NOT NULL CHECK(goal IN ('lose', 'gain', 'maintain')),
        maintenance_cal INTEGER NOT NULL
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        weight REAL NOT NULL,
        calories INTEGER NOT NULL,
        trained INTEGER NOT NULL CHECK(trained IN (0, 1)),
        entry_date TEXT NOT NULL,
        UNIQUE(user_id, entry_date)
        )""")
        #no explicit conn.commit() needed: 'with' block commits automatically

def new_user():
    """Add a new user to the database"""
    while True:
        try:
            username = input("username: ").strip()
            age = int(input("age: ").strip())
            height = float(input("height in cm: ").strip())
            goal = check_goal(input("goal (lose/gain/maintain): ").strip())
            maintenance_cal = int(input("maintenance calories: ").strip())
            #checks on negative integers
            if age > 0 and height > 0 and maintenance_cal > 0 and goal :
                break
            else:
                print("Values cannot be negative. Please try again \n")
        #catches errors
        except ValueError as e:
            print(f"Invalid input: {e}. Please try again.\n")
    try:
        #inserts information into db
        with connect_db() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO users (username, age, height, goal, maintenance_cal)
                VALUES (?, ?, ?, ?, ?)
            """, (username, age, height, goal, maintenance_cal))
        print(f"New user '{username}' saved.")

    except sqlite3.IntegrityError:
        print(f"Username '{username}' already exists. Please choose a different one.")


def get_user(username):
    """Fetch user by username. Returns None if not found."""
    with connect_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id, username, age, height, goal, maintenance_cal FROM users WHERE username = ?", (username,))
        return c.fetchone()

def check_goal(goal):
    """Validate the user's fitness goal."""
    goal = goal.lower()
    if goal in ["lose", "gain", "maintain"]:
        return goal
    raise ValueError("Goal must be 'lose', 'gain' or 'maintain'")

def new_entry():
    """Add a new fitness entry for a user."""
    user = get_user(input("Username?: ").strip())
    if not user:
        print("Please set up a user first.")
        return
    while True:
        try:
            user_id = user[0]
            weight = float(input("Todays weight in kg: ").strip())
            calories = int(input("Calories: ").strip())
            trained = 1 if input("Training today? (y/n)").strip().lower() == "y" else 0
            entry_date = date.today().isoformat()  # Explicit date
            break
        except ValueError as e:
            print(f"Invalid Input: {e}. Please try again.\n")
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT OR REPLACE INTO entries (user_id, weight, calories, trained, entry_date)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, weight, calories, trained, entry_date))
        print("Entry saved.")
    except sqlite3.IntegrityError as e:
        print(f"Database error: {e}")

def count_entries(username):
    """Count total entries for a user."""
    user = get_user(username)
    if not user:
        return 0

    with connect_db() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM entries WHERE user_id = ?", (user[0],))
        return c.fetchone()[0]


def get_last_entries(uid, limit=7):
    """Fetch the last N entries for a user, ordered by date descending."""
    with connect_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT entry_date, weight, calories, trained, id FROM entries WHERE user_id = ?
            ORDER BY entry_date DESC
            LIMIT ?
        """, (uid, limit))
        row = c.fetchall()
        return row

def compute_trends(entries):
    """Calculate average calories, training days, and weight change from entries."""
    if not entries:
        raise ValueError("No entries available")

    weights = [row[1] for row in entries]
    calories = [row[2] for row in entries]
    days_trained = sum(row[3] for row in entries)

    avg_calories = sum(calories) / len(calories)
    avg_weight = sum(weights) / len(weights)

    #simple weight change: newest - oldest in fetched window
    weight_change = weights[0] - weights[-1]


    return {
        "avg_weight": avg_weight,
        "avg_calories": avg_calories,
        "days_trained": days_trained,
        "weight_change": weight_change,
    }


def generate_recommendation(goal, avg_calories, days_trained, weight_change, maintenance_cal):
    """Generate up to 2 fitness recommendations based on trends."""
    recommendations = []

    if goal == "lose":
        if weight_change < 0:
            recommendations.append("Your weight is trending down. Stay consistent.")
        else:
            recommendations.append("Your weight is not trending down. Reduce calories slightly.")
    elif goal == "gain":
        if weight_change > 0:
            recommendations.append("Your weight is trending up. Stay consistent.")
        else:
            recommendations.append("Your weight is not trending up. Increase calories slightly.")
    elif goal == "maintain":
        if abs(weight_change) <= 0.3:
            recommendations.append("Your weight is stable. Stay consistent.")
        else:
            recommendations.append("Your weight is fluctuating too much. Adjust calories slightly toward maintenance.")

    if avg_calories < maintenance_cal and goal == "gain":
        recommendations.append("Average calories might be too low for gaining.")
    elif avg_calories > maintenance_cal and goal == "lose":
        recommendations.append("Average calories might be too high for losing.")

    if days_trained < 3:
        recommendations.append("Try to improve training consistency.")
    #return of max 2 recommendations
    return recommendations[:2]

def review_progress():
    """Show progress review and recommendations for a user."""
    username = input("Username?: ").strip()
    user = get_user(username)
    if not user:
        print("Please set up a user first.")
        return

    # Check if user has at least 7 entries
    entry_count = count_entries(username)
    if entry_count < 7:
        print(f"You need at least 7 entries to review progress. You currently have {entry_count}.")
        return

    entries = get_last_entries(user[0])
    if not entries:
        print("No entries found.")
        return

    goal = user[4]
    maintenance_cal = user[5]

    try:
        trends = compute_trends(entries)
    except ValueError as e:
        print(f"Error computing trends: {e}")
        return

    recommendations = generate_recommendation(
        goal=goal,
        avg_calories=trends["avg_calories"],
        days_trained=trends["days_trained"],
        weight_change=trends["weight_change"],
        maintenance_cal=maintenance_cal,
    )

    print(f"""
\nReview
Average weight: {trends['avg_weight']:.2f} kg
Average calories: {trends['avg_calories']:.0f} kcal
Gym days: {trends['days_trained']}
Weight change: {trends['weight_change']:.2f} kg""")

    print("\nRecommendations:")
    for rec in recommendations:
        print(f"- {rec}")


if __name__ == "__main__":
    main()

