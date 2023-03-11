# Customizable Kanban Board
In this repository, I create a Kanban board that allows users to create and manage tasks as well as collaborate with others in teams.

To run the code, from the same directory as the `app.py` file, run the following commands in a python shell. This will initialize the database.

``` python
from board import app, db
from board.models import User, Task, Team
app.app_context().push()
db.create_all()
```

The demonstration for the application can be found [here](https://www.loom.com/share/bd32354138f844bdbb07046a0903675c).

Note: In the recording, the dropdown for task status doesn't show for some reason. The same goes for selecting due dates. I just wanted to mention it so there is no confusion. Everything should work fine when the app is run, though.
