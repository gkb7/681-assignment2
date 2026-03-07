import heapq
import random
import numpy as np

ARRIVAL = 1
DEPARTURE = 2
THINK_DONE = 3
TIMEOUT = 4

class Event:
    def __init__(self, time, etype, request=None):
        self.time = time
        self.etype = etype
        self.request = request

    def __lt__(self, other):
        return self.time < other.time


class Request:
    def __init__(self, uid, arrival, service, timeout):
        self.uid = uid
        self.arrival = arrival
        self.service = service
        self.remaining = service
        self.timeout = timeout
        self.server = None
        self.timed_out = False


class Server:
    def __init__(self, sid):
        self.sid = sid
        self.busy = False
        self.req = None
        self.last_start = 0
        self.busy_time = 0


class QueueSystem:
    def __init__(self, cores, max_threads):

        self.servers = [Server(i) for i in range(cores)]
        self.queue = []
        self.max_threads = max_threads
        self.active_threads = 0

    def idle_server(self):
        for s in self.servers:
            if not s.busy:
                return s
        return None

    def enqueue(self, r):
        self.queue.append(r)

    def dequeue(self):
        if self.queue:
            return self.queue.pop(0)
        return None


class Simulator:

    def __init__(self,
                 users=50,
                 cores=4,
                #  max_threads=20,
                 service_dist="exp",
                #  service_params=(0.02,),
                 quantum=0.01,
                 context=0.001,
                 sim_time=2000,
                 warmup=200):

        self.users = users
        self.cores = cores

        self.service_dist = service_dist
        # self.service_params =service_params

        self.quantum = quantum
        self.context = context
        self.sim_time = sim_time
        self.warmup = warmup

        self.system = QueueSystem(cores, cores)

        self.time = 0
        self.event_list = []

        self.metrics = {
            "resp": [],
            "good": 0,
            "bad": 0,
            "timeouts": 0,
            "completed": 0
        }

        self.last_event = 0
        self.area_q = 0
        self.area_busy = 0

    def expon(self, mean):
        return -mean * np.log(random.random())

    def think(self):
        return max(0,random.normalvariate(6,3))

    # def service(self):
    #     return np.random.exponential(0.02)

    def service(self):

        if self.service_dist == "exp":

            # mean = self.service_params[0]

            return np.random.exponential(0.045)+0.045

        elif self.service_dist == "const":

            # value = self.service_params[0]

            return 0.045

        elif self.service_dist == "uniform":

            # low = self.service_params[0]
            # high = self.service_params[1]

            return random.uniform(.03, .06)

        else:
            raise ValueError("Unknown service distribution")

    def timeout(self):
        return random.uniform(0.05, 0.2)

    def schedule(self, ev):
        heapq.heappush(self.event_list, ev)

    def initialize(self):

        for u in range(self.users):

            t = self.think()

            r = Request(u, 0, 0, 0)

            self.schedule(Event(t, THINK_DONE, r))

    def timing(self):

        ev = heapq.heappop(self.event_list)

        self.time = ev.time

        return ev

    def update_stats(self):

        dt = self.time - self.last_event

        self.last_event = self.time

        self.area_q += len(self.system.queue) * dt

        busy = sum([1 for s in self.system.servers if s.busy])

        self.area_busy += busy * dt

    def think_done(self, ev):

        uid = ev.request.uid

        service = self.service()

        timeout = self.timeout()

        r = Request(uid, self.time, service, timeout)

        self.schedule(Event(self.time, ARRIVAL, r))

        self.schedule(Event(self.time + timeout, TIMEOUT, r))

    def arrival(self, ev):

        r = ev.request

        if self.system.active_threads < self.system.max_threads:

            s = self.system.idle_server()

            if s:

                self.start_service(s, r)

            else:

                self.system.enqueue(r)

            self.system.active_threads += 1

        else:

            self.system.enqueue(r)

    def start_service(self, s, r):

        s.busy = True
        s.req = r
        r.server = s
        s.last_start = self.time

        run = min(self.quantum, r.remaining)

        r.remaining -= run

        self.schedule(Event(self.time + run + self.context,
                            DEPARTURE, r))

    def departure(self, ev):

        r = ev.request
        s = r.server

        if r.remaining > 0:

            self.system.enqueue(r)

            next_r = self.system.dequeue()

            if next_r:

                self.start_service(s, next_r)

        else:

            s.busy = False

            s.busy_time += self.time - s.last_start

            self.system.active_threads -= 1

            if self.time > self.warmup:

                rt = self.time - r.arrival

                self.metrics["resp"].append(rt)

                self.metrics["completed"] += 1

                if r.timed_out:
                    self.metrics["bad"] += 1
                else:
                    self.metrics["good"] += 1

            think = self.think()

            self.schedule(Event(self.time + think,
                                THINK_DONE, r))

            next_r = self.system.dequeue()

            if next_r:

                self.system.active_threads += 1

                self.start_service(s, next_r)

    def timeout_event(self, ev):

        r = ev.request

        if not r.timed_out:

            r.timed_out = True

            if self.time > self.warmup:
                self.metrics["timeouts"] += 1

    def run(self):

        self.initialize()

        while self.event_list and self.time < self.sim_time:

            ev = self.timing()

            self.update_stats()

            if ev.etype == THINK_DONE:
                self.think_done(ev)

            elif ev.etype == ARRIVAL:
                self.arrival(ev)

            elif ev.etype == DEPARTURE:
                self.departure(ev)

            elif ev.etype == TIMEOUT:
                self.timeout_event(ev)

        return self.report()

    def report(self):

        if not self.metrics["resp"]:
            return None

        rt = np.mean(self.metrics["resp"])

        dur = self.sim_time - self.warmup

        throughput = self.metrics["completed"] / dur
        goodput = self.metrics["good"] / dur
        badput = self.metrics["bad"] / dur
        drop = self.metrics["timeouts"] / (self.metrics["completed"] + self.metrics["timeouts"] + 1e-9)

        util = self.area_busy / (self.cores * self.sim_time)

        return {
            "response_time": rt,
            "throughput": throughput,
            "goodput": goodput,
            "badput": badput,
            "drop_rate": drop,
            "utilization": util
        }