# Trainer Bot
A personal Telegram bot for fitness tracking with AI-powered analysis by Claude.
The bot tracks daily meals and macros (calories, protein, fats, carbs), logs workouts, 
and generates weekly reports using an LLM.

# Screenshots
<img width="737" height="215" alt="product_search" src="https://github.com/user-attachments/assets/442fc60a-2c1c-43bc-bee0-a94910c9192f" />
<img width="549" height="338" alt="body_log" src="https://github.com/user-attachments/assets/851a0e46-e087-4582-b0a0-9d32dd17137e" />
<img width="543" height="176" alt="new_log" src="https://github.com/user-attachments/assets/0e55b4f0-9fb9-48a4-ad9c-c6f2473d0768" />

## Stack
**Backend:** Python, Django ORM
**Bot:** Python, aiogram, FSM states
**AI:** Claude Sonnet (Anthropic)
**Infrastructure:** Docker, Docker Compose
**Tests:** pytest

## Project Structure
```
trainer_bot/
├── config/                 # Django settings and urls        
├── core/
│   ├── management/         # Commands for uploading Products and Exercises
│   ├── meal_nutrition.py   # Functions for meals macros
|   ├── llm_report.py       # Config and functions for LLM      
│   ├── tests.py            # Testing functions of macros calculation
│   ├── admin.py
|   ├── views.py
│   └── apps.py
├── bot/
│   ├── handlers.py          # File with handlers  and keyboards
│   ├── states.py            # States for FSM
│   └──  main.py             # Main file for bot starting and polling
├── docker-compose.yml
├── Dockerfile
├── .dockerignore
├── .gitignore
├── pytest.ini
├── requirements.txt
├── manage.py
└── .env.example
```

## Environment Variables
Create `.env` file based on `.env.example` and fill in all variables

## Installation and Running

### Prerequisites
- Docker and Docker Compose installed on your server
- Git installed

### Steps
1. Clone the repository
```bash
git clone https://github.com/ladron711/trainer_bot.git
cd trainer_bot
```
2. Create `.env` file based on `.env.example` and fill in all variables
| `BOT_TOKEN` | Telegram bot token from @BotFather |
| `SECRET_KEY` | Django secret key |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | PostgreSQL host (use `db` for Docker) |
| `DB_PORT` | PostgreSQL port (default: 5432) |
| `ANTHROPIC_API_KEY` | API key from console.anthropic.com |

3. Build and start containers
```bash
docker compose up --build -d
```
4. Apply database migrations and fill DB with Products and Exercises 
```bash
docker compose exec bot python manage.py migrate
docker compose exec bot python manage.py load_products
docker compose exec bot python manage.py load_workout_types
```
5. The bot is now running and ready to use

## Tests
```bash
pytest
```
Tests cover macros calculation logic (BMR/TDEE formulas, goal-based adjustments).

## How It Works

### User Registration
- User starts the bot with `/start`
- To create user press **New User** button
- Fill fields: gender, date of birth, weight, height, activity and goal (weight loss, muscle gain, physical health)

### Using bot
- There are categories for entries:
  1. **Body Measurement** — log body measurement
  2. **Workout** — choosing type of exercises with entries of sets-reps-weights
  3. **Meal** — choosing eating products with entries of products quantities (gram)
The bot shows how many daily macros was eaten and how many left.

### AI Analysis
All analysis is done by **Claude Sonnet** and works with typing '/report':
- LLM takes 7 days for analyze and shows problems in nutrition and activity

### Macros Calculation
Daily targets are calculated using the Mifflin-St Jeor equation:
BMR is adjusted by activity level (1.375–1.725) and goal (0.85 for weight loss,
1.1 for muscle gain). Protein and fats are set per kg of body weight,
carbs fill the remaining calories.
