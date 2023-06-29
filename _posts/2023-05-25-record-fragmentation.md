---
layout: distill
title: "Circumventing the GFW with TLS Record Fragmentation"
date: 2023-06-27
description: "How Fragmentation Can Be Extended to the TLS Layer"

authors:
  - name: Niklas Niere
    affiliations:
        name: Paderborn University
    url: https://twitter.com/JonSnowWhite2
    bibtex: Niere, Niklas

bibliography: record_frag.bib

toc:
    - name: Introduction
      subsections: 
        - name: TLS (Censorship)
        - name: TCP Fragmentation
        - name: TLS Record Fragmentation
    - name: Contributions
      subsections:
      - name: Proof of Concept
      - name: TLS Server Support
    - name: Discussion
      subsections:
        # - name: How Can You Manipulate the TLS Handshake with a Proxy?
        # - name: How Long Will This Work...
        # - name: Can’t the GFW Block TLS Record Fragmentation Completely?
        # - name: I Want To Add TLS Record Fragmentation to my DPI Circumvention Tool. What Do I Have to Consider?
    - name: Conclusion

---

<!-- Add possibility to only display some elements in light or dark mode. Using invert does not play nicely with colors in an svg -->
<style>
    .light-only {
        display: block;
    }
    .dark-only {
        display: block;
    }
    html[data-theme="dark"] .light-only,
    html:not([data-theme="dark"]) .dark-only{
        display: none;
    }
    d-footnote-list img {
        height: 1.5em;
    }
    d-footnote img {
        height: 2em;
    }

    details.legend img {
        height: 2em;
    }
    details.legend {
        text-align: left;
    }
    .l-screen img{
        max-width: 100%;
        margin-left: auto;
        margin-right: auto;
    }
</style>

TCP fragmentation has long been known as a viable deep packet inspection (DPI) circumvention technique.
However, censors are increasingly aware of this technique.
We propose TLS record fragmentation as a new censorship circumvention technique on the TLS layer that functions analogously to TCP fragmentation.
Using TLS record fragmentation, we successfully circumvented the DPI of the Great Firewall of China (GFW).
We also found that over 90% of TLS servers support this new circumvention technique.
To contextualize TLS record fragmentation for future work, we discuss its possibilities and limitations.

> ```
> 0x1703030005436972637517030300056d76656e74170303
>   0005696e67207417030300056865204746170303000157
> ```


---

## Introduction

In this section, we provide background information on TLS censorship and fragmentation before showing the viability of TLS record fragmentation in later sections.

### TLS (Censorship)

The TLS protocol provides confidentiality, authenticity, and integrity to internet traffic in a client&#8209;server setting&nbsp;<d-cite key="tls12,tls13"/>.
While TLS can encrypt arbitrary application data, it is prominently used to encrypt HTTP connections.
Google Chrome reports that Chrome serves around 93% of its connections over HTTPS (HTTP+TLS)&nbsp;<d-cite key="chrome_https"/>.
The encryption of HTTP makes HTTPS connections resilient to censors' analyses of fields such as the HTTP Host header.
However, before TLS can transmit encrypted application data it performs a so-called handshake.
This unencrypted handshake contains the Server Name Indication (SNI), which mirrors the content of the HTTP Host header.
The handshake is depicted below.

![A TLS 1.2 handshake with an HTTP GET request.](/assets/img/2023/06/record-frag/handshake-light.svg){: width="70%" style="margin: 0 auto" .light-only}
![(Dark mode image - for description see light mode image)](/assets/img/2023/06/record-frag/handshake-dark.svg){: width="70%" style="margin: 0 auto" .dark-only}
<div class="caption">
A TLS 1.2 handshake. Unencrypted messages are marked in blue while encrypted messages are marked in yellow.
The SNI extension is visible in the unencrypted ClientHello message while the Host header of the HTTP GET request is encrypted.
</div>

Censors around the globe utilize the SNI extension to facilitate the censorship of HTTPS connections&nbsp;<d-cite key="russia_sni_throttling,sni_china,sni_india,sni_south_korea"/>. 
As a countermeasure, the IETF has proposed ESNI and ECH&nbsp;<d-cite key="ietf-tls-esni-16"/>.
Both encrypt the SNI extension in the ClientHello message.
Unfortunately, the standard is still in the drafting phase, and its adoption is far from widespread&nbsp;<d-cite key="sni_china"/>.
The only website for which we could find a valid [ECH configuration](https://dns.google/query?name=crypto.cloudflare.com&rr_type=HTTPS&ecs=) is Cloudflare's designated testing server.
The slow adoption of ECH necessitates intermediate solutions for SNI censorship circumvention.
One such solution is the fragmentation of TLS messages across multiple TCP fragments, known as TCP fragmentation.


### TCP Fragmentation

TCP is a stream-based protocol over which users and applications can send data using abstract data streams.
These data streams are translated by TCP into actual network packets called TCP segments.
Each TCP segment can contain either complete application messages or only parts of it.
The latter is called TCP fragmentation and is depicted below with an HTTP GET message.

![TCP fragmented HTTP GET request.](/assets/img/2023/06/record-frag/tcp_frag-light.svg){: width="80%" style="margin: 0 auto" .light-only}
![(Dark mode image - for description see light mode image)](/assets/img/2023/06/record-frag/tcp_frag-dark.svg){: width="80%" style="margin: 0 auto" .dark-only}
<div class="caption">
The left side contains an unfragmented HTTP GET request.
The same request is depicted in two TCP segments on the right side.
Censors that want to extract the hostname of the website from the fragmented HTTP GET request have to concatenate both fragments.
</div>


Interestingly, TCP fragmentation can be used in censorship circumvention as it aggravates the complexity of traffic analysis.
In the above example, a censor has to concatenate both TCP fragments to correctly identify the destination of the GET request.
This effectively forces the censor to maintain a state and allocate costly memory for every connection it analyzes.
The costs of analyzing TCP fragmentation caused many censors to ignore it in the past&nbsp;<d-cite key="geneva,liberate,throttling_twitter,india_sni"/>.
As it proved successful, TCP fragmentation was implemented in various censorship circumvention tools&nbsp;<d-cite key="goodbyedpi,zapret,powertunnel,greentunnel"/>.
Recently, though, China's censor has become more sophisticated and begun handling TCP fragmentation&nbsp;<d-cite key="geneva"/>.

### TLS Record Fragmentation

While TLS messages can be fragmented over multiple TCP segments, they can also be fragmented on the TLS layer alone.
This is possible because the TLS layer consists of two different layers: the TLS message layer and the TLS record layer.
On the TLS record layer, every TLS message is wrapped in a TLS record structure.
Most importantly, a single TLS message can be split across multiple TLS records, resulting in TLS record fragmentation.
This is depicted in the figure below.

![TLS Record fragmented ClientHello message.](/assets/img/2023/06/record-frag/record_frag-light.svg){: width="80%" style="margin: 0 auto" .light-only}
![TLS Record fragmented ClientHello message.](/assets/img/2023/06/record-frag/record_frag-dark.svg){: width="80%" style="margin: 0 auto" .dark-only}
<div class="caption">
The left side depicts a TLS ClientHello message in a complete TLS record and TCP segment.
A TLS record fragmented ClientHello message is depicted on the right. Both TLS records are contained in the same TCP segment.
A censor that wants to analyze the SNI extension of the fragmented TLS message has to concatenate both TLS records.
</div>

In this example, the SNI extension is split across different TLS records.
Similar to TCP fragmentation, this forces the censor to maintain a state and allocate memory for potential reassembly.
To the best of our knowledge, TLS record fragmentation has been proposed for censorship circumvention only by [Thomas Pornin since 2014](https://security.stackexchange.com/questions/56338/identifying-ssl-traffic).
We are not aware of any analyses or implementations of TLS record fragmentation as a censorship circumvention technique.
In this blog post, we bridge this gulf and effectively rediscover TLS record fragmentation as a viable censorship circumvention technique.

## Contributions

Our primary contribution is circumventing China's censor&#8212;The Great Firewall of China (GFW)&#8212;with TLS record fragmentation.
To infer the feasibility of TLS record fragmentation on the internet, we also measured its support by TLS servers.

### Proof Of Concept

As mentioned, we circumvented the GFW with TLS record fragmentation.
To this end, we implemented a [DPYProxy](https://github.com/UPB-SysSec/DPYProxy): a simple Python proxy that applies TLS record fragmentation to all handshake messages passing through it.
Next to TLS record fragmentation, DPYProxy supports TCP fragmentation both standalone and in combination with TLS record fragmentation.
The proxy runs locally and can be set as an HTTP(S) proxy in browsers like Firefox or Chrome.
Any previous HTTP(S) proxy&#8212;needed for IP censorship circumvention&#8212;can be provided to DPYProxy, which routes traffic through it as well.
The figure below visualizes both our setup and the behavior of the GFW.

<div class="l-screen">
  <img src="/assets/img/2023/06/record-frag/setup-light.svg" class="light-only" alt="Setup and censor handling of two test vectors.">
  <img src="/assets/img/2023/06/record-frag/setup-dark.svg" class="dark-only" alt="Setup and censor handling of two test vectors.">
</div>
<div class="caption">
This figure depicts the setup of our scans for two test vectors.
We can see that the GFW intercepts unfragmented TLS ClientHello messages.
It ignores TLS record fragmented TLS ClientHello messages.
We omitted HTTP CONNECT messages sent to DPYProxy and the HTTP Proxy for improved readability.
</div>

We set up DPYProxy on a vantage point in China (AS4837) and let it connect to an HTTP proxy in the [DFN](https://www.dfn.de/en/).
From there, we queried [https://wikipedia.org/wiki/turtle](https://wikipedia.org/wiki/turtle) using curl<d-footnote><code>curl -Ls --proxy 127.0.0.1:4433 https://wikipedia.org/wiki/turtle</code></d-footnote> with different settings of our DPYProxy.
Specifically, we ran DPYProxy with any combination of TCP and TLS record fragmentation enabled.
When combining TCP and TLS record fragmentation, we fit one TLS record into exactly one TCP segment.
In all tests, we fragmented the ClientHello message before and after the SNI extension.
We refer to this as "Early Split" and "Late Split" in the table of results below.

<table width="50%" style="margin: 0 auto; text-align:center">
<thead>
<tr class="header">
<th style="text-align: left;"><span>Fragmentation</span></th>
<th style="text-align: center;"><span>Split</span></th>
<th style="text-align: right;"><span>Circumvents Censor</span></th>
</tr>
</thead>
<tbody>
<tr>
<th style="text-align: left;"><span>None</span></th>
<th style="text-align: left;"><span>-</span></th>
<th style="text-align: right;"><span>-</span></th>
</tr>
<tr>
<td rowspan="2" style="text-align: left;">TCP</td>
<th style="text-align: left;"><span>Early</span></th>
<th style="text-align: right;"><span>Yes</span></th>
</tr>
<tr>
<th style="text-align: left;"><span>Late</span></th>
<th style="text-align: right;"><span>-</span></th>
</tr>
<tr>
<td rowspan="2" style="text-align: left;">TLS</td>
<th style="text-align: left;"><span>Early</span></th>
<th style="text-align: right;"><span>Yes</span></th>
</tr>
<tr>
<th style="text-align: left;"><span>Late</span></th>
<th style="text-align: right;"><span>Yes</span></th>
</tr>
<tr>
<td rowspan="2" style="text-align: left;">TLS+TCP</td>
<th style="text-align: left;"><span>Early</span></th>
<th style="text-align: right;"><span>Yes</span></th>
</tr>
<tr>
<th style="text-align: left;"><span>Late</span></th>
<th style="text-align: right;"><span>Yes</span></th>
</tr>
</tbody>
</table><br>

Our results lead to a few interesting conclusions.
First, we could verify that TCP fragmentation can still circumvent the GFW.
Specifically, the GFW only censored our connection attempts when the SNI extension was present in the first TCP segment.
Here, we encountered both the primary and secondary censors of the GFW detected by Bock et al.&nbsp;<d-cite key="censor_backup"/>.
Both censors are circumventable reliably with TLS record fragmentation;
it suffices to place any byte of the ClientHello message into a different TLS record.
For that, multiple TLS records can be either contained in a single TCP segment or split across multiple TCP segments.
Overall, we detect that the GFW handles TCP fragmentation partially but is overchallenged with any kind of TLS record fragmentation.

### TLS Server Support

To assess the usability of TLS record fragmentation, we also measured TLS servers' support for it.
To this end, we analyzed the domains of the [Tranco Top 1M list](https://tranco-list.eu/) and all `https://` domains from the [global list of censored domains by the CitizenLab](https://github.com/citizenlab/test-lists/blob/master/lists/global.csv).
We provide the per-server results of our analysis on [GitHub](https://github.com/UPB-SysSec/TlsRecordFragmentationResults).
Below, we summarize our results.

<style>
.footnote-ref {color: var(--global-theme-color) !important; border-bottom: none; text-decoration: none;}
.distill-fn-style li{color: var(--global-distill-app-color) !important; font-size: 0.8em; line-height: 1.7em;}
.distill-fn-style a{color: var(--global-distill-app-color) !important; border-bottom: none; text-decoration: none;}
.distill-fn-style a:hover{color: var(--global-hover-color) !important; border-bottom: none; text-decoration: none;}
</style>

<table width="70%" style="margin: 0 auto; text-align:center">
<thead>
<tr class="header">
<th style="text-align: left;"><span>List</span></th>
<th style="text-align: right;"><span>Scanned<br>Domains</span><sup><a href="#fn1" class="footnote-ref" id="fnref1" role="doc-noteref">a</a></sup></th>
<th style="text-align: right;"><span>Support TLS<br>record fragmentation</span></th>
</tr>
</thead>
<tbody>
<tr>
<th style="text-align: left;"><span>CitizenLab</span></th>
<th style="text-align: right;"><span>1 135  </span></th>
<th style="text-align: right;"><span>1 092 (96.21%)</span></th>
</tr>
<tr>
<th style="text-align: left;"><span>Tranco Top 1M</span></th>
<th style="text-align: right;"><span>830 357</span></th>
<th style="text-align: right;"><span>766 909 (92.36%)</span></th>
</tr>
</tbody>
</table><br>

<ol class="distill-fn-style" type="a">
<li id="fn1">We excluded domains that are not resolvable, do not handshake TLS, or requested exclusion from our scans in a previous scan.<a href="#fnref1" class="footnote-backlink" role="doc-backlink">[↩︎]</a></li>
</ol>


We found that slightly over 96% of domains from the CitizenLab list support TLS record fragmentation.
In comparison, the domains from the Tranco Top 1M list support TLS record fragmentation with a slightly smaller share of over 92%.
Interestingly, TLS record fragmentation enjoys widespread support across all ranks of the Tranco Top 1M list as can be seen below.

![TLS server support for TLS record fragmentation by Tranco rank.](/assets/img/2023/06/record-frag/record_frag_by_tranco_rank.svg){:width="70%" style="display: block; margin: 0 auto"}


Overall, we determined that TLS record fragmentation is largely supported by TLS servers as of today.
This holds for the top TLS servers on the internet as well as censored domains.

## Discussion

The GFW is the most sophisticated censor in the world and often also the first censor to implement new protocol analyses.
As even the GFW does not analyze TLS messages that are fragmented over multiple TLS records, we believe that TLS record fragmentation circumvents other censors as well.
To ascertain the viability of TLS record fragmentation around the world, we endorse an analysis in other countries.

### How Can You Manipulate the TLS Handshake with a Proxy?

One might think that it's impossible to manipulate TLS traffic as a MitM/proxy server.
Fundamentally, that is correct.
The TLS protocol authenticates TLS handshake messages with the Finished message.
However, TLS does not authenticate the encompassing TLS record headers.
These are only authenticated for encrypted handshake messages and application data.
As we only manipulated the TLS record headers of unencrypted handshake messages we did not break the TLS handshake in our analyses.
Any manipulation of other parts of the handshake such as the SNI extension would indeed break authentication.

As another nitty-gritty detail: 
The addition of implicit sequence numbers with the addition of additional records does not break the following authentication of data. Sequence numbers are reset before encryption starts.


### How Long Will TLS Record Fragmentation Stay Viable?
Currently, we are not sure why TLS record fragmentation works so well on the GFW.
We suggest that the GFW is currently only able to hold state on the TCP layer but not in its DPI of the TLS layer.
If that is the case, we conjecture the GFW and other censors to require some time until they can reassemble TLS records as well.
We are even more positive about the viability of circumvention techniques that combine alterations on the TLS and TCP layer.
For instance, one could fragment a TLS handshake message on the TLS and TCP layer, send these segments out-of-order, and inject TLS or TCP packets with a low TTL in between.
In the end, we cannot definitely answer how long TLS record fragmentation will work on the GFW.
We still conjecture it to be viable for a non-negligible amount of time, especially as a building block for more sophisticated circumvention techniques.

### Can't the GFW Block TLS Record Fragmentation Completely?
Yes, and no.
The GFW could completely block all fragmented TLS messages.
Doing so risks blocking all connections that exhibit naturally occurring TLS record fragmentation.
TLS record fragmentation can occur naturally when the size of a TLS message (2^24 bytes max) exceeds the maximum size of a TLS record (2^16 bytes).
Additionally, the maximum size of TLS records can be lowered with TLS extensions&nbsp;<d-cite key="rfc6066,rfc8449"/>.
To minimize the viability of a complete block of TLS record fragmentation, we encourage browser vendors and other TLS clients to incorporate fragmented TLS records in their connection attempts.
This might also convince the remaining server owners to start supporting TLS record fragmentation, improving the interoperability of the TLS landscape as a whole.

### I Want to Add TLS Record Fragmentation to my DPI Circumvention Tool. What Do I Have to Consider?

As an application layer protocol, the TLS layer can be manipulated without root privileges on the operating system.
This makes it possible for TLS clients such as custom browsers to enforce TLS fragmentation from user space.
As TLS record headers can be manipulated as a MitM, it is also possible to implement TLS record fragmentation into DPI-circumventing proxies.
DPYProxy does exactly that.
Limitations exist for tools such as [GoodByeDpi](https://github.com/ValdikSS/GoodbyeDPI) that manipulate TCP packets.
For each newly added record, five bytes are inserted into the TCP stream.
This leads to a mismatch in TCP sequence numbers between the client and server application.
While the TCP sequence numbers can be changed accordingly this has to be done for all subsequent messages in the handshake.
Ironically, this forces the circumvention tool to maintain a TCP connection state.

# Conclusion

In this blog post, we extended fragmentation-based censorship circumvention to the TLS layer.
We hope to aid both researchers and people affected by censorship with an additional tool in the ongoing struggle against internet censorship.
The code of our TLS record fragmentation proxy is accessible on [GitHub](https://github.com/UPB-SysSec/DPYProxy).
Feel free to get in touch for discussions and follow-up work at <a href="mailto:niklas.niere@upb.de">niklas.niere@upb.de</a>.