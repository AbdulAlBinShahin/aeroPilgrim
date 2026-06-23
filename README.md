# aeroPilgrim (UmrahFly)

AI-powered Umrah flight search and trip-planning assistant built with Django. Search calendar fares from Bangladesh to Saudi Arabia, compare dates, and get personalized help on each trip — including an n8n-powered chat assistant on the flight details page.

**Live demo:** [aeropilgrim-production.up.railway.app](https://aeropilgrim-production.up.railway.app/)

## Features

- **Flight price calendar** — Search routes between Dhaka, Chattogram, Sylhet, Jeddah, and Medina via the [Sky Scrapper](https://rapidapi.com/apiheya/api/sky-scrapper) API (RapidAPI).
- **User accounts** — Register, log in, and save searches (results require login).
- **Smart caching** — Reuses saved `Search` records from the database so repeat lookups avoid extra API calls.
- **Rate limiting** — One new external flight API call per IP per week; cached routes remain available.
- **Trip details page** — View a selected departure date, price category, stay length, and return date.
- **AI travel actions** — One-click prompts for booking plans, hotels, itineraries, and budget breakdowns (OpenAI or built-in fallbacks).
- **n8n trip assistant** — Custom glass-style chat on the flight details page only, proxied through Django to your n8n workflow with full trip context from the database. Responses are English-only.
- **Bot APIs for n8n** — HTTP endpoints so workflows can query flight data and trip context using a shared secret key.

## Project structure

```
Umrah/
├── manage.py
├── requirements.txt
├── Dockerfile
├── start.sh                    # Docker / Railway entrypoint
├── .env.example
├── core/                       # Main Django app
│   ├── models.py               # Search, SearchRateLimit
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── context_processors.py
│   ├── admin.py
│   └── services/
│       ├── flight_api.py       # Sky Scrapper API + airport lookup
│       ├── rate_limit.py       # IP cooldown + cache helpers
│       ├── ai_service.py       # OpenAI action buttons
│       ├── chat_service.py     # Trip context builder (DB)
│       └── n8n_chat_service.py # n8n webhook proxy
├── templates/
│   ├── base.html
│   └── core/
│       ├── home.html
│       ├── search_results.html
│       ├── flight_detail.html  # Trip page + n8n chat UI
│       ├── login.html
│       └── register.html
├── static/                     # CSS, JS, fonts, video
└── search/                     # Django project settings
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

## Local development

1. Create and activate a virtual environment:

```bash
python -m venv env
source env/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create your environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys (see table below).

4. Run migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | Yes | `True` locally, `False` on Railway |
| `FLIGHT_API_KEY` | Yes | RapidAPI key for Sky Scrapper |
| `FLIGHT_API_HOST` | Yes | `sky-scrapper.p.rapidapi.com` |
| `N8N_CHAT_WEBHOOK_URL` | For chat | n8n chat webhook URL (flight details assistant) |
| `BOT_API_KEY` | For n8n bots | Shared secret for `/api/bot-*` endpoints |
| `OPENAI_API_KEY` | Optional | Powers AI action buttons on trip details |
| `AI_MODEL` | Optional | Defaults to `gpt-4o-mini` |
| `DATABASE_URL` | Optional | Neon Postgres URL; omit to use local SQLite |
| `CONN_MAX_AGE` | Optional | DB connection pool age in seconds (default `30`) |
| `ALLOWED_HOSTS` | Production | Comma-separated hosts |
| `CSRF_TRUSTED_ORIGINS` | Production | Full origin URLs with `https://` |

## Main routes

| Path | Description |
|------|-------------|
| `/` | Home — flight search form |
| `/search/` | Search results (login required) |
| `/search/flight/<id>/<date>/` | Trip details + n8n chat assistant |
| `/search/flight/<id>/<date>/ai/` | AI action button endpoint (POST) |
| `/search/flight/<id>/<date>/chat/` | n8n chat proxy (POST, login required) |
| `/api/bot-search/` | Flight search JSON for n8n workflows (GET) |
| `/api/bot-trip-context/` | Full trip record from DB for n8n (GET) |

### n8n bot API usage

Both bot endpoints require the header:

```
X-Bot-Api-Key: <your BOT_API_KEY>
```

**Search flights**

```
GET /api/bot-search/?from_city=DAC&to_city=MED&stay_days=7&timespan_to_search=30
```

**Get trip context from database**

```
GET /api/bot-trip-context/?search_id=3&flight_date=2026-06-29
```

Returns route, selected price, cheaper alternative dates, calendar size, stay length, and more.

The flight-details chat sends the same trip fields to your n8n webhook on each message, with an English-only instruction, so your workflow can call these APIs when it needs live data.

## Docker

Build and run locally:

```bash
docker build -t aeropilgrim .
docker run -p 8000:8000 --env-file .env aeropilgrim
```

The container runs `start.sh`, which:

1. Applies migrations
2. Collects static files
3. Starts Gunicorn on port `8000` (or Railway's `$PORT`)

## Deploy on Railway

1. Push this repo to GitHub.
2. Create a new Railway project from the GitHub repo.
3. Railway detects the `Dockerfile` and builds automatically.
4. Add these variables in Railway **Variables** (do not commit `.env`):

```
SECRET_KEY=your-strong-secret
DEBUG=False
ALLOWED_HOSTS=your-app.up.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app.up.railway.app
FLIGHT_API_KEY=your-key
FLIGHT_API_HOST=sky-scrapper.p.rapidapi.com
N8N_CHAT_WEBHOOK_URL=https://your-n8n-instance/webhook/.../chat
BOT_API_KEY=your-bot-secret
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
CONN_MAX_AGE=30
```

5. Deploy. Railway sets `PORT` automatically — Gunicorn binds to it via `start.sh`.

## Common commands

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
python manage.py test
```

## Contributors

- [Muhammad Sharf Uddin](https://github.com/developersharf)
- [Ayon914](https://github.com/Ayon914)
- [AbdulAlBinShahin](https://github.com/AbdulAlBinShahin)

## License

MIT — see [LICENSE](LICENSE).
