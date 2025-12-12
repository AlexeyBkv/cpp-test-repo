import argparse
import subprocess
import time
import random
import shlex
import os
import pwd

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

double_pipe =  f'perf script -i perf.data | ./FlameGraph/stackcollapse-perf.pl | ./FlameGraph/flamegraph.pl > graph.svg'
p1 = subprocess.Popen(shlex.split(f'perf script -i perf.data'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
p2 = subprocess.Popen(shlex.split(f'FlameGraph/stackcollapse-perf.pl'), stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
p1.stdout.close()
p3 = subprocess.Popen(shlex.split(f'FlameGraph/flamegraph.pl > graph.svg'), stdin=p2.stdout, shell=True)
p2.stdout.close()
p3.wait()

"double_pipe_process = run(double_pipe);"
"stop(double_pipe_process)"

stop(server)
time.sleep(1)
print('Job done')
