# Blog RestAPI

## API for creating and managing a blog.

### Description:

- PostgreSQL database.
- Backend on Django and Rest Framework.
- Automatic Spectacular frontend.
- Filtering posts by author, category, tags, any search word.
- Dockerized app.
- Unit tests.

Command to run the app:

```commandline
    docker compose up
```

Command to run tests:

```commandline
    docker compose run --rm app sh -c "python manage.py test"
```