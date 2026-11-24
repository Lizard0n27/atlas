# atlas
Atlas is a personal fitness review tool. It helps people make better fitness decisions from the data they already collect.
Its goal is not to replace existing tracking apps. Instead, it helps users interpret fitness data and make better decisions through trend analysis and simple rule-based recommendations.

## purpose
Atlas is designed to reduce noise, not increase tracking.
If focuses on a small number of useful inputs and helps users make better decisions based on trends instead of day-to-day fluctuations.

# Atlas - Personal Fitness Review Tool

#### Video Demo: https://youtu.be/rZVlPdeOU6s?is=mndB37M2JwzgI6hm

#### Description:

Atlas 0.1 is a command-line fitness tracking and review tool designed to help users make evidence-based decisions about their fitness progress with minimal daily tracking effort. Unlike traditional fitness apps that encourage obsessive tracking of every meal and workout, Atlas focuses on the most impactful metrics—weight, calories, and training frequency—and provides weekly trend analysis with actionable recommendations.

**The Problem:** Most fitness apps overwhelm users with excessive tracking requirements, leading to burnout and abandonment. Users don't want more tools; they want to get the job done efficiently. Atlas addresses this by requiring only essential daily inputs and providing clear, data-driven guidance.

**How It Works:** Users start by setting up a profile with their age, height, fitness goal (lose, gain, or maintain weight), and estimated maintenance calories. Each day, they log their weight, calorie intake, and whether they trained. After collecting at least seven entries, Atlas generates a progress review showing average weight, average calories, training frequency, and weight change over the past week. Based on these trends and the user's goal, Atlas provides up to two personalized recommendations, such as "Your weight is trending down. Stay consistent" or "Your weight is not trending down. Reduce calories slightly."

**Technical Implementation:** Atlas is built entirely in Python using the standard library's `sqlite3` module for data persistence. The database consists of two tables: `users` (storing profile information with a UNIQUE constraint on username) and `entries` (storing daily logs with a composite UNIQUE constraint on user_id and entry_date to prevent duplicate entries per day). Foreign key constraints ensure referential integrity between entries and users.

## planned features
see roadmap.md

## version
Current version: 0.1
