"""
EEE5138Z Lab 1 — Custom Mininet topology
Three switches in a line; two hosts per switch.

Usage:
  sudo mn --custom topology_custom.py --topo lab1topo \
          --mac --switch ovs --controller default
"""

from mininet.topo import Topo
from mininet.link import TCLink

LINK_BW   = 10    # Mbps
LINK_DELAY = '5ms'


class Lab1Topo(Topo):
    """
    h1 ─┐              ┌─ h5
        s1 ─── s2 ─── s3
    h2 ─┘  h3─┘ └─h4  └─ h6
    """

    def build(self):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')
        h4 = self.addHost('h4', ip='10.0.0.4/24')
        h5 = self.addHost('h5', ip='10.0.0.5/24')
        h6 = self.addHost('h6', ip='10.0.0.6/24')

        lo = dict(bw=LINK_BW, delay=LINK_DELAY)

        self.addLink(h1, s1, **lo)
        self.addLink(h2, s1, **lo)
        self.addLink(h3, s2, **lo)
        self.addLink(h4, s2, **lo)
        self.addLink(h5, s3, **lo)
        self.addLink(h6, s3, **lo)

        self.addLink(s1, s2, **lo)
        self.addLink(s2, s3, **lo)


topos = {'lab1topo': Lab1Topo}
