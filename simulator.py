import heapq
import random
import numpy as np
from collections import deque

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
        self.completed = False


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
        self.thread_queue = deque()
        self.core_queue = deque()
        self.max_threads = max_threads
        self.active_threads = 0

    def idle_server(self):
        for s in self.servers:
            if not s.busy:
                return s
        return None

    # def enqueue(self, r):
    #     self.queue.append(r)

    # def dequeue(self):
    #     if self.queue:
    #         return self.queue.pop(0)
    #     return None

    def enqueue_thread(self, r):
        self.thread_queue.append(r)

    def dequeue_thread(self):
        if self.thread_queue:
            return self.thread_queue.popleft()
        return None

    def enqueue_core(self, r):
        self.core_queue.append(r)

    def dequeue_core(self):
        if self.core_queue:
            return self.core_queue.popleft()
        return None

class Simulator:

    def __init__(self,
                 users=50,
                 cores=4,
                 max_threads=50,
                 service_dist="exp",
                #  service_params=(0.02,),
                 quantum=2,
                 context=0,
                 sim_time=2000,
                 warmup=200):

        self.users = users
        self.cores = cores
        self.trace = False

        self.service_dist = service_dist
        # self.service_params =service_params

        self.quantum = quantum
        self.context = context
        self.sim_time = sim_time
        self.warmup = warmup

        self.system = QueueSystem(cores, max_threads)

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
        return random.normalvariate(2,1)+.5

    def schedule(self, ev):
        heapq.heappush(self.event_list, ev)
        print(f"[{self.time:.4f}] schedule event={ev.etype} req={getattr(ev.request,'uid',None)} at {ev.time:.4f}")

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

        self.area_q += len(self.system.thread_queue) * dt

        busy = sum([1 for s in self.system.servers if s.busy])

        if self.last_event >= self.warmup:
            self.area_busy += busy * dt

    def think_done(self, ev):
        if self.trace:
            print(f"[{self.time:.4f}] THINK_DONE user={ev.request.uid}")

        uid = ev.request.uid

        service = self.service()

        timeout = self.timeout()

        r = Request(uid, self.time, service, timeout)

        print(f"[{self.time:.4f}] create request uid={uid} service={service:.4f} timeout={timeout:.4f}")

        self.schedule(Event(self.time, ARRIVAL, r))

        self.schedule(Event(self.time + timeout, TIMEOUT, r))

    def arrival(self, ev):
        
        r = ev.request
        if self.trace:
            print(f"[{self.time:.4f}] ARRIVAL req={r.uid}")


        if self.system.active_threads < self.system.max_threads:
            self.system.active_threads += 1


            s = self.system.idle_server()

            if s:

                self.start_service(s, r)

            else:

                self.system.enqueue_core(r)


        else:

            self.system.enqueue_thread(r)
            if self.trace:
                print(f"[{self.time:.4f}] THREAD_WAIT req={r.uid}")


    def start_service(self, s, r):

        s.busy = True
        s.req = r
        r.server = s
        s.last_start = self.time

        run = min(self.quantum, r.remaining)

        r.remaining -= run

        if r.remaining >0:
            delay=run+self.context
        else:
            delay=run

        if self.trace:
            print(f"[{self.time:.4f}] START core={s.sid} req={r.uid} remaining={r.remaining:.4f}")

        self.schedule(Event(self.time + delay, DEPARTURE, r))

    def departure(self, ev):

        r = ev.request
        s = r.server

        if r.remaining > 0:

            self.system.enqueue_core(r)

            next_r = self.system.dequeue_core()

            if next_r:

                self.start_service(s, next_r)
            else:
                s.busy = False

            if self.trace:
                print(f"[{self.time:.4f}] PREEMPT core={s.sid} req={r.uid} remaining={r.remaining:.4f}")

        else:

            s.busy = False

            r.completed = True

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

            next_r = self.system.dequeue_thread()

            if next_r:

                self.system.active_threads += 1
                idle = self.system.idle_server()
                if idle:
                    self.start_service(idle, next_r)
                else:
                    self.system.enqueue_core(next_r)

            next_core_req=self.system.dequeue_core()

            if next_core_req:
                self.start_service(s,next_core_req)

        if self.trace:
            print(f"[{self.time:.4f}] COMPLETE req={r.uid} RT={self.time - r.arrival:.4f} timeout={r.timed_out}")

    def timeout_event(self, ev):

        r = ev.request

        if r.completed:
            return

        if not r.timed_out:

            r.timed_out = True

            if self.time > self.warmup:
                self.metrics["timeouts"] += 1

        if self.trace:
            print(f"[{self.time:.4f}] TIMEOUT req={r.uid}")

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

        dur = self.time-self.warmup
        util = self.area_busy / (self.cores * dur)

        return {
            "response_time": rt,
            "throughput": throughput,
            "goodput": goodput,
            "badput": badput,
            "drop_rate": drop,
            "utilization": util
        }