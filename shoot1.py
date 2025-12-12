import argparse
import subprocess
import time
import random
import shlex
import os
import pwd
import sys

RANDOM_LIMIT = 1000
SEED = 123456789
random.seed(SEED)

AMMUNITION = [
    'localhost:8080/api/v1/maps/map1',
    'localhost:8080/api/v1/maps'
]

SHOOT_COUNT = 100
COOLDOWN = 0.1


def start_server():
    parser = argparse.ArgumentParser()
    parser.add_argument('server', type=str)
    return parser.parse_args().server


def run(command, output=None):
    process = subprocess.Popen(shlex.split(command), stdout=output, stderr=subprocess.DEVNULL)
    return process


def stop(process, wait=False):
    if process.poll() is None and wait:
        process.wait()
    process.terminate()


def shoot(ammo):
    hit = run('curl ' + ammo, output=subprocess.DEVNULL)
    time.sleep(COOLDOWN)
    stop(hit, wait=True)


def make_shots():
    for _ in range(SHOOT_COUNT):
        ammo_number = random.randrange(RANDOM_LIMIT) % len(AMMUNITION)
        shoot(AMMUNITION[ammo_number])
    print('Shooting complete')


server = run(start_server())
perf_command = f'perf record -p {server.pid} -g -o perf.data'
process_perf = run(perf_command)
make_shots()
stop(process_perf)

command = "perf script -i perf.data | ./FlameGraph/stackcollapse-perf.pl | ./FlameGraph/flamegraph.pl > graph.svg"
time.sleep(1)
try:
    subprocess.run(command, shell=True, check=True, stderr=subprocess.STDOUT)
    print("Success. Plot save in graph.svg")
except subprocess.CalledProcessError as e:
    print(f"Error1: {e.returncode}")
except Exception as e:
    print(f"Error2: {e}")

stop(server)
time.sleep(1)
print('Job done')
