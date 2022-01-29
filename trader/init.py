import time, os, time

from services.stocks.example import Example

os.environ["TZ"] = "Asia/Kolkata"
time.tzset()

# import the object with aliase name Process
from threading import (
    Thread as Process,
)

# {'name': 'example_strategy', 'script': ExampleStrategy(name='example').start, 'args': []}
services = [{"name": "example", "script": Example(name="example").start, "args": []}]

processes = {}

# start each process from init.d as children
for service in services:
    processes[service["name"]] = Process(target=service["script"], args=service["args"])

print("starting services ...")

# start all processes
for process in processes:
    print(f"starting {process}")
    processes[process].start()
    time.sleep(1)


# wait for all process to complete
for process in processes:
    processes[process].join()
