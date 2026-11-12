import datetime


mock_projects = [
    {
        "id": 1,
        "name": "Project 1",
        "description": "Description for project 1",
        "timestamp": datetime.datetime.now() - datetime.timedelta(days=1),
        "status": 1,
    },
    {
        "id": 2,
        "name": "Project 2",
        "description": "Description for project 2",
        "timestamp": datetime.datetime.now() - datetime.timedelta(days=2),
        "status": 2,
    },
    {
        "id": 3,
        "name": "Project 3",
        "description": "Description for project 3",
        "timestamp": datetime.datetime.now() - datetime.timedelta(days=3),
        "status": 3,
    },
]
