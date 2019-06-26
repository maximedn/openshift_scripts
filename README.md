# get_logs
Retrieves logs from pods

For now, to use the script, a constant has to be added to the get_logs.py script with PASSWORD as name.

## Execution
<code>python get_logs.py --env int --pod dbselect</code>

to retrieve the logs on the int for the pod with name dbselect.

<code>python get_logs.py --env ta</code>

to retrieve the logs on the ta, from all pods.

This also works with the "prod" environment.

