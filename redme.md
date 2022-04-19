1. How to run it

- Go to the project root directory
- `sudo docker-compose build web`
- `sudo docker-compose up`
---
2. Testing

`python3 manage.py test tests/ --pattern="*_tests.py"`

---
3. Assumptions

- SWAPI data can be modified between requests, so I can't cache home world name 

---
4. What should be done, but was not due to the lack of time

- Error handling on accessing SWAPI endpoints, and error handling in general
- The fetching view should be asynchronous so user is not blocked, while waiting
for the response
- Move it to ASGI
- Maybe 'load more' should be taking only new rows, old could be stored in the
session, browser, or cache system
- Store csv data folder name in config file
- Better to use key-value database instead of relational db,
especially because the reports are immutable
- Split unit tests and integration

---
5. Implementation details

- I didn't want to store cached response between sessions, so implemented
map_homeworld_to_name_with_cache which stores cache only within current reqeust
closure