.PID=wclb.pid

.default: daemon

test: main.py
	@python -u main.py

daemon: main.py stop
	@echo "====================" >> access.log
	@nohup python -u main.py >> access.log 2>&1 &

stop:
	@cat ${.PID} 2> /dev/null | xargs kill 2> /dev/null || true && rm -f ${.PID}

login:
	@tac access.log | sed -n -e '1,/====================/p' | tac

