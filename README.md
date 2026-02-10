# Monopoly

A browser-based 3D Monopoly demo built with Django, Django Channels and Three.js.

**This repository is a local/demo app. The previous public "Play Online" link has been removed from this README.**

## Prerequisites
- Python 3.6+ (recommended)
- Node.js/npm (optional, only required if you change front-end packages)

## Quick install (Windows)
1. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1   # PowerShell
```

2. Install Python dependencies:

```powershell
pip install -r requirement.txt
```

3. (Optional) Install front-end dependencies if you plan to modify the Three.js code:

```powershell
npm install
```

4. Apply database migrations and create a user:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

5. Run the development server:

```powershell
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser to view the app.

## Notes on Channels and deployment
- This project uses `channels` for WebSocket handling. For local development the default (in-memory) channel layer may work, but production deployments should configure a proper channel layer (for example Redis) and an ASGI server.
- Static assets are served by Django in development; for production run `python manage.py collectstatic` and serve static files with a proper web server.

## Gameplay / How to Play
- Create or join a game from the web UI. Use the on-screen controls to roll dice, move pieces, buy properties, and build houses/hotels.
- Game logic and player/model code lives under the `monopoly/core` and `monopoly/ws_handlers` packages.

## Development tips
- Front-end Three.js code is in `monopoly/static/3d_assets` and `monopoly/static/js`.
- Server code and routing is in the `monopoly` Django app and `webapps` project settings.

## Reference and assets
- See the `static` folder for included media and 3D asset files.

## Troubleshooting & Redis (optional)

- Quick checks:
	- Ensure dependencies are installed from `requirement.txt` and that migrations ran (`python manage.py migrate`).
	- If static files are missing, run `python manage.py collectstatic` (and configure `STATIC_ROOT` for production).
	- Check browser console/network for WebSocket errors when joining a game.

- Running Redis locally (Docker example):

```powershell
docker run -p 6379:6379 -d redis:6
```

- Example `CHANNEL_LAYERS` for `settings.py` (Channels 1.x):

```python
CHANNEL_LAYERS = {
		'default': {
				'BACKEND': 'asgi_redis.RedisChannelLayer',
				'CONFIG': {
						'hosts': [('127.0.0.1', 6379)],
				},
				# 'ROUTING': 'monopoly.routing.channel_routing',  # optional: point to your routing
		},
}
```

- Start sequence for a Redis-backed local dev server:

```powershell
# 1. Start Redis (see Docker command above)
# 2. Activate virtualenv and install requirements
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirement.txt
# 3. Run migrations and start server
python manage.py migrate
python manage.py runserver
```

- Notes:
	- For production consider running an ASGI server (for example `daphne` or `uvicorn`) and a persistent Redis instance.
	- If you see `ImportError` or channel-layer errors, confirm the `channels` and `asgi_redis` packages are installed and compatible with `Django==1.11` and `channels==1.1.8`.
