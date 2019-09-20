#!/usr/bin/python2
import sys
import dns.resolver

sblList = ['zen.spamhaus.org',
           'sbl.spamhaus.org',
           'dnsbl.sorbs.net',
           'block.dnsbl.sorbs.net',
           'spam.dnsbl.sorbs.net',
           'bl.spamcop.net']


class sbl(object):

    def __init__(self, ips):
        self.ips = ips.split(",")
        self.result = {}

    @staticmethod
    def dnsLookup(name):
        resolver = dns.resolver.Resolver(configure=True)
        try:
            resolver.query(name, 'A')
            return resolver.query(name, 'TXT')[0].to_text()
        except dns.resolver.NoAnswer:
            return False
        except dns.resolver.NXDOMAIN:
            return False

    def Check(self):
        for ip in self.ips:
            for sbl in sblList:
                name = '.'.join(reversed(ip.split('.')))
                txt = self.dnsLookup("{}.{}".format(name,sbl))
                if txt:
                    if not ip in self.result:
                        self.result[ip] = [ "{} - {}".format(sbl,txt) ]
                    else:
                        self.result[ip].append("{} - {}".format(sbl,txt))


def main():
    a = sbl(sys.argv[1])
    a.Check()
    if len(a.result) > 0:
        print(a.result)
        sys.exit(1)
    else:
        print("OK")
        sys.exit(0)


if __name__ == '__main__':
    main()

