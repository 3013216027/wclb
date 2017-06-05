.PID=wclb.pid

.default: run

run:
	@rm -vf nohup.out
	@make daemon
	@sleep 3
	@make login

daemon: main.py stop
	@nohup python -u main.py &

stop:
	@cat ${.PID} 2> /dev/null | xargs kill 2> /dev/null || true && rm -f ${.PID}

login:
	@cat nohup.out

