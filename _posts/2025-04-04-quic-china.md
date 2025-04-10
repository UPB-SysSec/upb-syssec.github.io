---
layout: distill
title: "China Extended its SNI Censorship to QUIC"
date: 2025-04-04
description: "The GFW enforces QUIC-specific censorship"
citation: true

authors:
  - name: Nico Heitmann
    affiliations:
      name: Paderborn University
    bibtex: Heitmann, Nico
  - name: Anonymous
    affiliations:
      name: Paderborn University
    bibtex: Anonymous
  - name: Felix Lange
    affiliations:
      name: Paderborn University
    bibtex: Lange, Felix
  - name: Niklas Niere
    affiliations:
      name: Paderborn University
    url: https://twitter.com/JonSnowWhite2
    bibtex: Niere, Niklas

bibliography: quic-china.bib

toc:
  - name: Introduction and Background
    subsections:
      - name: QUIC
      - name: Prior QUIC Censorship
      - name: Residual Censorship
  - name: Evaluation and Results
    subsections:
      - name: Censorship
      - name: Does This Affect Real QUIC Connections?
      - name: Why Does China Use Residual-Only Censorship?
  - name: Conclusion
---

QUIC, the successor to TLS over TCP, has become popular in recent years.
Despite its increase in popularity, QUIC has remained largely uncensored:
Only Russian TSPU devices analyzed QUIC connections and could extract the server's hostname from the SNI extension.
Other censors---such as China's GFW---have not been found capable of sophisticated QUIC analysis;
in January 2025, we noticed sophisticated QUIC censorship in China.

Similar to Russian TSPU devices, the GFW now extracts the SNI extension from QUIC connections and blocks unwanted connections.
As of now, the GFW's QUIC censorship operates on a limited list of hostnames, is _residual-only_, and triggers inconsistently.
Based on these characteristics, we suspect that the deployment of QUIC censorship in the GFW is an ongoing process:
This process might culminate in broad QUIC censorship by the GFW.
This blog post details our findings.

## Introduction and Background

This section introduces the QUIC protocol and its relevance for Internet censorship.

### QUIC

QUIC was standardized as a successor to TLS in 2021&nbsp;<d-cite key="rfc9000"/>.
While regular TLS uses TCP as a transport layer protocol, QUIC uses UDP.
Since its standardization, QUIC has gained popularity and is supported by an increasing amount of websites&nbsp;<d-cite key="internetarchive_HTTPArchiveState_2025"/>.
Naturally, this makes QUIC a target for censors.

![Left: Protocol stack of HTTP/2 over TLS: IP, TCP, TLS, HTTP/2. Right: Protocol stack of HTTP/3 over QUIC: IP, UDP, QUIC (containing TLS 1.3), HTTP/2.](/assets/img/2025/quic-china/quic-layers.svg){:width="80%" .only-light style="margin: 0 auto;"}
![Left: Protocol stack of HTTP/2 over TLS: IP, TCP, TLS, HTTP/2. Right: Protocol stack of HTTP/3 over QUIC: IP, UDP, QUIC (containing TLS 1.3), HTTP/2.](/assets/img/2025/quic-china/quic-layers-dark.svg){:width="80%" .only-dark style="margin: 0 auto;"}

<div class="caption">
Left: Protocol stack of HTTP/2 over TLS.
Right: Protocol stack of HTTP/3 over QUIC. TLS&nbsp;1.3 is contained in QUIC.
</div>

Under the hood, QUIC uses TLS&nbsp;1.3 for its cryptographic handshake.
Therefore, it also inherits the Server Name Indication (SNI) field of TLS, which censors commonly use to detect whether a connection should be censored&nbsp;<d-cite key="hall_SurveyWorldwideCensorship_2023"/>.
Censors target this field instead of IP addresses, as servers may host multiple websites that should not all be blocked.
In QUIC, the client's first packet contains the SNI.
The packet is encrypted, but the key is derived from its header.
Therefore, this encryption does not protect confidentiality; still, censors need to implement additional logic to extract the SNI value.

QUIC's choice of UDP over TCP also affects how censors deal with QUIC.
For TCP-based protocols, censors can inject TCP Reset packets to the peers to tear down connections.
In UDP, there is no generic connection close mechanism.
Instead, it has been suggested that censors may need to drop packets to stop or tear down active QUIC connections&nbsp;<d-cite key="rfc9000,elmenhorst_QuickLookQUIC_2022"/>.

QUIC can be used as a transport for different protocols, most notably HTTP/3.
Before attempting to connect via HTTP/3 over QUIC, browsers determine whether the destination supports QUIC.
A server can indicate support using response headers in a previous HTTP over TLS connection, or by adding DNS `HTTPS` entries that indicate support for QUIC.
Because of this, TLS and DNS censorship can interfere with QUIC detection.

### Prior QUIC Censorship

In 2021 and 2022, Elmenhorst et al.&nbsp;<d-cite key="elmenhorst_WebCensorshipMeasurements_2021,elmenhorst_QuickLookQUIC_2022"/> identified QUIC censorship in several countries.
Notably, in Russia, they already identified specialized QUIC blocking.
Russia detected the version field in the QUIC handshake and dropped all international QUIC traffic.
For domestic traffic, the censor analyzed the SNI and dropped packets if the SNI was not `vk.com`.
In China, they did not identify QUIC-specific censorship.
However, IP-blocking still interfered with QUIC connections.
In particular, the IP ranges of Google---an early adopter of QUIC---were blocked in China.

In mid-2023, a user in the net4people BBS reported intermittent QUIC censorship in China&nbsp;<d-cite key="ujuiujumandan_NewQUICBlock_2023"/>.
They observed that, when censorship triggers, many Cloudflare IPs were blackholed in addition to the original IP.
At the time, a QUIC-based tunneling protocol called TUIC was also affected in the Xray community&nbsp;<d-cite key="ujuiujumandan_NewQUICBlock_2023"/>.
The scope and triggers for this blocking remained unclear.

### Residual Censorship

Besides directly blocking connection attempts, censors also employ so-called _residual censorship_&nbsp;<d-cite key="wang_YourStateNot_2017,bock_YourCensorMy_2021"/>.
When a user makes a censored request, such censors not only directly block the original request, but also block future requests---regardless of whether they contain a censored keyword or SNI.
Residual censorship usually applies for a few minutes, and is limited to a specific destination.

When a censor residually censors all packets from a client IP and port to a specific destination (IP and port), it applies 4-tuple residual censorship.
When the censor ignores the port on the client side, it applies 3-tuple residual censorship.
When only the IP addresses need to match, the scope is called 2-tuple.

<div class="l-screen">
<table style="margin: 0 auto; text-align: center;">
<thead>
<tr class="header">
<th style="text-align: left; border-bottom: none;"><span>Type</span></th>
<th style="text-align: right; border-bottom: none;" colspan="2"><span>Source Address</span></th>
<th style="text-align: right; border-bottom: none;" colspan="2"><span>Destination Address</span></th>
</tr>
<tr class="header">
<th><span></span></th>
<th style="text-align: right;"><span>IP</span></th>
<th style="text-align: right;"><span>Port</span></th>
<th style="text-align: right;"><span>IP</span></th>
<th style="text-align: right;"><span>Port</span></th>
</tr>
</thead>
<tbody>
<tr>
<td><span>2-tuple</span></td>
<td style="text-align: right;"><span>X</span></td>
<td style="text-align: right;"><span></span></td>
<td style="text-align: right;"><span>X</span></td>
<td style="text-align: right;"><span></span></td>
</tr>
<tr>
<td><span>3-tuple</span></td>
<td style="text-align: right;"><span>X</span></td>
<td style="text-align: right;"><span></span></td>
<td style="text-align: right;"><span>X</span></td>
<td style="text-align: right;"><span>X</span></td>
</tr>
<tr>
<td><span>4-tuple</span></td>
<td style="text-align: right;"><span>X</span></td>
<td style="text-align: right;"><span>X</span></td>
<td style="text-align: right;"><span>X</span></td>
<td style="text-align: right;"><span>X</span></td>
</tr>
</tbody>
</table>
</div>
<div class="caption">
Basic types of residual censorship&nbsp;<d-cite key="bock_YourCensorMy_2021"/>.
Packets where all highlighted protocol fields match a censored request are censored, even when they would not be censored by themselves.
</div>

Implementations of residual censorship differ widely between censors and even between protocols in specific censors.
For a given censor, the timing may vary between different protocols.
In some cases, sending a censored packet during residual censorship restarts the timer, while in others it does not.

The connections or packets that trigger residual censorship are usually censored themselves.
But this is not always true:
In 2021, Bock et al.&nbsp;<d-cite key="bock_YourCensorMy_2021"/> found that China's ESNI censorship did not directly react to the original packet.
Only after less than one second, the GFW started dropping packets on the 3-tuple and 4-tuple, with different durations.

## Evaluation and Results

While investigating other censorship, we encountered unexpected behavior in China.
We observed failing QUIC connections and decided to investigate further.
In the following, we show that---despite not being directly censored---QUIC is residually censored in China.

For our scans, we rented a server in China and a server in Germany.
From China, we attempted to open QUIC connections to our server in Germany.
The QUIC packets were restricted to a single QUIC Initial Packet from China to Germany, which was followed up with different 10-byte UDP packets in both directions.

We used different values on the SNI field of the QUIC connections.
As an uncensored domain, we used `example.com`; as a censored domain, we used `en.m.wikipedia.org`.
We performed the scans in March and April&nbsp;2025.

### Censorship

In our tests, we found China has started censoring QUIC, based on the SNI value in the ClientHello.
For the uncensored SNI, we found no indication of interference.
In contrast, when the QUIC Initial Packet included a forbidden domain, further packets on the same 4-tuple were likely to be dropped:

![Two plots of packet loss over time. One of them, labeled "after allowed SNI", is consistently near zero. The other, labeled "after forbidden SNI", is near 90% for the first three minutes and then returns to zero.](/assets/img/2025/quic-china/packet-loss-time.svg){:width="80%" .only-light style="margin: 0 auto;"}
![Two plots of packet loss over time. One of them, labeled "after allowed SNI", is consistently near zero. The other, labeled "after forbidden SNI", is near 90% for the first three minutes and then returns to zero.](/assets/img/2025/quic-china/packet-loss-time-dark.svg){:width="80%" .only-dark style="margin: 0 auto;"}

<div class="caption">
Average packet loss after censored and uncensored QUIC requests over one day (4-tuple). For the first 3 minutes after censored requests, the packet loss is significantly larger than in control measurements.
</div>

Interestingly, the average packet loss seen in this plot does not match the packet loss of individual connection attempts.
For many connections, we observed that no packets arrived in Germany during the residual censorship window, while at other times, all packets arrived after sending an identical censored packet.

To illustrate these cases, we categorized each connection attempt by the effectiveness of residual censorship that followed.
In addition to packets on the 4-tuple, we also sent packets that only match the 3-tuple, using a new client port in China:

![Four histograms that classify connection attempts by packet loss. Two of them, labeled "after allowed SNI" show connections having less than 5% packet loss. The two others, labeled "after fobidden SNI" show most connections near 100% packet loss, with the rest of them near 0% packet loss.](/assets/img/2025/quic-china/packet-loss-histogram.svg){:width="80%" .only-light style="margin: 0 auto;"}
![Four histograms that classify connection attempts by packet loss. Two of them, labeled "after allowed SNI" show connections having less than 5% packet loss. The two others, labeled "after fobidden SNI" show most connections near 100% packet loss, with the rest of them near 0% packet loss.](/assets/img/2025/quic-china/packet-loss-histogram-dark.svg){:width="80%" .only-dark style="margin: 0 auto;"}

<div class="caption">
Histogram of packet loss rates in the residual censorship windows.
Of the requests containing a forbidden domain, almost all trigger 4-tuple residual censorship.
For most, but not all, of the requests, residual censorship also extends to the 3-tuple.
The control scans with uncensored domains show no residual censorship.
</div>

We conclude that there are three possible censor reactions to a QUIC packet with a forbidden SNI: either all following packets on the 3-tuple are dropped, only the packets on the 4-tuple are dropped, or no censorship occurs at all.
This may be because the current infrastructure in the GFW is unreliable, but may also be a deliberate choice to obfuscate or experiment with different censorship.

During the residual censorship windows, we also sent packets from Germany to the server in China.
These reverse packets were not affected by the residual censorship, even when they are a response on the original packet's 4-tuple.
This matches prior findings of residual censorship being unidirectional in China&nbsp;<d-cite key="bock_YourCensorMy_2021"/>.

We also found that not all domains censored over TLS are affected by QUIC censorship.
For example, the SNI `freetibet.org` did not trigger QUIC censorship in our experiments.
Connections without an SNI did not trigger QUIC censorship either.

#### 3-Tuple Residual Censorship

In 58% of connection attempts, we found residual censorship that drops all follow-up packets on the 3-tuple.
This residual censorship lasts 3 minutes, with no packets being dropped afterwards.
Packets following the censored packet do not get dropped immediately:
It takes a moment for residual censorship to start---usually less than 500ms.

#### 4-Tuple Residual Censorship with Additional Ports

In 37% of connection attempts, follow-up packets were dropped on the 4-tuple of the trigger packet, but not on the complete 3-tuple.
In this case, the time frame is also 3 minutes. After the time frame, packet loss returns to normal.

Besides 4-tuple residual censorship, we observed unusual behavior in this case:
While most client ports were unaffected by residual censorship, some unrelated client ports were residually censored.<d-footnote>The histograms above use only one new client port. This skews the histogram when the new port is residually censored this way. We controlled for this in the percentages in the text (3-tuple and 4-tuple) using additional port scans.</d-footnote>
This seems to affect approximately one fifth of client ports.
This could be a deliberate choice by the censor, or it could be an unreliable implementation that is intended to censor the 3-tuple.

#### No Censorship Triggered

In the remaining 5% of connection attempts, we did not observe the trigger packets leading to any residual censorship.
We assume that these packets were not seen by the censorship system, possibly due to high overall load.

#### Comparison to Prior Observations

Censored QUIC connections recorded in 2023&nbsp;<d-cite key="ujuiujumandan_NewQUICBlock_2023"/> showed timeouts after communication was initially successful.
This indicates similar residual-only censorship, but the details are not clear from the captured packets.
For ESNI, residual-only censorship has also been observed&nbsp;<d-cite key="bock_YourCensorMy_2021"/>.
In this case, residual censorship started “less than 1 second” after the censored packet reached the GFW.

For QUIC, we also found the residual censorship to take less than one second to start.
At 3&nbsp;minutes, the time of residual censorship is also similar to the ESNI censorship that was observed in 2021.
In contrast to the ESNI censorship from 2021, we did not see staggered 3-tuple and 4-tuple censorship.
Instead, both types had the same duration for our QUIC scans.

### Does This Affect Real QUIC Connections?

The QUIC packet that triggers censorship still reaches the server, and the following residual censorship does not start immediately; there is a short delay of up to 500ms before the censor starts dropping packets.
This leaves potential for connections to succeed despite censorship triggering.
While long-lived QUIC connections cannot proceed on the 4-tuple when censorship triggers, short-lived connections may be able to complete within the uncensored window.
However, as international traffic from China is fairly slow, it remains unlikely that forbidden QUIC connections can pass the GFW.

### Why Does China Use Residual-Only Censorship?

The GFW often prefers injection attacks over null routing packets.
For TCP connections, it injects TCP Reset packets, and for DNS, it injects additional responses without stopping the censored request or response directly.
As a result of IP blocking, the GFW does drop packets.
However, IP blocking is mostly static.

China's prior ESNI censorship&nbsp;<d-cite key="bock_YourCensorMy_2021"/> and new QUIC censorship are both residual-only.
The fact that the original packets are not dropped indicates that packets are still analyzed off-path.
We assume that, once a censored packet is detected, the GFW reconfigures routers or other specialized network devices to drop packets that match the 3-tuple.
If this process is unreliable, this may explain the 4-tuple censorship we observed, where unrelated ports are also affected.

Another reason the GFW might use such a split approach is that it could simplify censorship for new protocols.
In this split approach, protocol-specific infrastructure would remain off-path, while a shared in-path system only implements generic residual censorship.

## Conclusion

In summary, we observed that China extended its SNI censorship to QUIC.
We did not identify direct QUIC censorship---instead, QUIC censorship in China is _residual-only_.
However, the QUIC censorship of the GFW still proves effective at disrupting QUIC, especially for long-lived connections, such as VPN tunnels.

With residual-only censorship already seen in the past for ESNI in China&nbsp;<d-cite key="bock_YourCensorMy_2021"/>, residual-only censorship may continue to be implemented for other protocols.
This method may allow the GFW to limit in-path infrastructure and to still flexibly block new protocols.
As a mix of off-path and in-path methods, residual-only censorship blurs the line between these classes of censorship.
Circumvention tools that rely on QUIC should anticipate further efforts by the GFW to block QUIC and increased residual censorship against new protocols.
