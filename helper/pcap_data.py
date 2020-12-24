class PcapData:
    def __init__(self, rtt, inflight, throughput, fairness, avg_rtt, sending_rate, bbr_values,
                 bbr_total_values, cwnd_values, retransmissions, retransmissions_interval, buffer_backlog, goodput,
                 data_info=None):
        self.rtt = rtt
        self.inflight = inflight
        self.throughput = throughput
        self.fairness = fairness
        self.avg_rtt = avg_rtt
        self.sending_rate = sending_rate
        self.bbr_values = bbr_values
        self.bbr_total_values = bbr_total_values
        self.cwnd_values = cwnd_values
        self.retransmissions = retransmissions
        self.retransmissions_interval = retransmissions_interval
        self.buffer_backlog = buffer_backlog
        self.goodput = goodput
        self.data_info = data_info

    def values_as_dict(self):
        return {
            'rtt': self.rtt,
            'inflight': self.inflight,
            'throughput': self.throughput,
            'fairness': self.fairness,
            'avg_rtt': self.avg_rtt,
            'sending_rate': self.sending_rate,
            'bbr_values': self.bbr_values,
            'bbr_total_values': self.bbr_total_values,
            'cwnd_values': self.cwnd_values,
            'retransmissions': self.retransmissions,
            'retransmissions_interval': self.retransmissions_interval,
            'buffer_backlog': self.buffer_backlog,
            'goodput': self.goodput
        }

    @staticmethod
    def from_dict(pcap_dict):
        return PcapData(
            rtt=pcap_dict['rtt'],
            inflight=pcap_dict['inflight'],
            throughput=pcap_dict['throughput'],
            fairness=pcap_dict['fairness'],
            avg_rtt=pcap_dict['avg_rtt'],
            sending_rate=pcap_dict['sending_rate'],
            bbr_values=pcap_dict['bbr_values'],
            bbr_total_values=pcap_dict['bbr_total_values'],
            cwnd_values=pcap_dict['cwnd_values'],
            retransmissions=pcap_dict['retransmissions'],
            retransmissions_interval=pcap_dict['retransmissions_interval'],
            buffer_backlog=pcap_dict['buffer_backlog'],
            goodput=pcap_dict['goodput']
        )


class DataInfo:

    def __init__(self, sync_duration, sync_phases):
        self.sync_duration = sync_duration
        self.sync_phases = sync_phases
