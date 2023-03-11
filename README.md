# Customizable Kanban Board
In this repository, I create a Kanban board that allows users to create and manage tasks as well as collaborate with others in teams.

To run the code, from the same directory as the `app.py` file, run the following commands in the python shell. This will just initialize the database.

``` python
from board import app, db
from board.models import User, Task, Team
app.app_context().push()
db.create_all()
```


