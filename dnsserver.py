#!/usr/bin/env python
from dnslib.server import BaseResolver, DNSLogger, DNSRecord, DNSServer
from dnslib import RCODE, RR, A
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", default=40002)
parser.add_argument("-n", default="cs5700cdnorigin.ccs.neu.edu")
args = parser.parse_args()
port = int(args.p)
name = args.n

resolver = BaseResolver()
logger = DNSLogger(prefix=False)
server = DNSServer(resolver,port=port,address="localhost",logger=logger)

class DNSResolver(BaseResolver):

    def __init__(self):
        self.addresses = open("http-repls.txt").readlines()
        self.curr_address = 0

    def resolve(self,request,handler):
        reply = request.reply()
        a = RR(name, rdata=A(self.addresses[self.curr_address]), ttl=0)
        reply.add_answer(a)
        if self.curr_address == len(self.addresses)-1:
            self.curr_address = 0
        else:
            self.curr_address += 1
        return reply

if __name__ == "__main__":
        resolver = DNSResolver()
        logger = DNSLogger(prefix=False)
        server = DNSServer(resolver,port=port,address="localhost",logger=logger)
        server.start_thread()
        q = DNSRecord.question("cs5700cdnorigin.ccs.neu.edu")
        a = q.send("localhost",port)
        print(DNSRecord.parse(a))
        server.stop()
