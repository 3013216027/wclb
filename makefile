.PID=wclb.pid

.default: run

run:
	@make daemon
	@sleep 2
	@make login

daemon: main.py stop
	@echo "====================" >> access.log
	@nohup python -u main.py >> access.log 2>&1 &

stop:
	@cat ${.PID} 2> /dev/null | xargs kill 2> /dev/null || true && rm -f ${.PID}

login:
	@tac access.log | sed -n -e '1,/====================/p' | tac

