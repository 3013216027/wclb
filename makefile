.PID=wclb.pid
.default: test

test: main.py
	@python -u main.py

daemon: main.py stop
	@echo "====================" >> access.log
	@nohup python -u main.py >> access.log 2>&1 &
	@sleep 5 && tail -n45 access.log

stop:
	@cat ${.PID} 2> /dev/null | xargs kill || true && rm -f ${.PID}

