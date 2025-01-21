# simple-etl

## Project Structure
```plaintext
simple_etl/
│
├── config/
│   ├── config.py
│   └── logging.conf
│
├── data/
│   ├── database/
│   │   └── shop.db
│   └── files/
│       └── users.csv
│
├── docs/
│   ├── flowchart.drawio
│   └── flowchart.jpg
│
├── src/
│   ├── __init__.py
│   ├── extract.py
│   ├── load.py
│   └── transform.py
│
├── tests/                        
│   └── __init__.py
│
├── logs/
│   └── app.log
│
├── main.py
├── pyproject.toml
├── README.md
└── requirements.txt
