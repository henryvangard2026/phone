import subprocess
import sys
import time

# 1. Start RabbitMQ (if not already running)
subprocess.Popen(["docker", "start", "rabbitmq"])
time.sleep(3)  # give RabbitMQ a moment to start

# 2. Start the consumer in a separate process
subprocess.Popen([sys.executable, "phoneconsumer.py"])
time.sleep(1)

# 3. Start the GUI (blocks until GUI closes)
subprocess.call([sys.executable, "gui2/gui2.py"])