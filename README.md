## On the Server

```
ps aux | grep flask
kill 27423 or whatever it is
source env/bin/activate
nohup flask run -p 8501 &
./start_dashboard.sh
python press_tab.py
```

.env file is in 1pass