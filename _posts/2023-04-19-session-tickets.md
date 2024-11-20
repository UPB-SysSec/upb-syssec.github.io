---
layout: distill
title: "We Really Need to Talk About Session Tickets"
date: 2023-04-19
description: "A Large-Scale Analysis of Cryptographic Dangers with TLS Session Tickets"
citation: true

authors:
  - name: Sven Hebrok
    affiliations:
      name: Paderborn University
    url: https://twitter.com/xoimex
    bibtex: Hebrok, Sven
#   - name: Simon Nachtigall
#     affiliations:
#         name: Paderborn University and achelos GmbH
#     url: https://twitter.com/snachti
#     bibtex: Nachtigall, Simon
#   - name: Marcel Maehren
#     affiliations:
#         name: Ruhr University Bochum
#     url: https://twitter.com/marcelmaehren
#     bibtex: Maehren, Marcel
#   - name: Nurullah Erinola
#     affiliations:
#         name: Ruhr University Bochum
#     url: https://twitter.com/nerinola1
#     bibtex: Erinola, Nurullah
#   - name:  Robert Merget
#     affiliations:
#         name: Technology Innovation Institute and Ruhr University Bochum
#     url: https://twitter.com/ic0nz1
#     bibtex: Merget, Robert
#   - name: Juraj Somorovsky
#     affiliations:
#         name: Paderborn University
#     url: https://twitter.com/jurajsomorovsky
#     bibtex: Somorovsky, Juraj
#   - name: Jörg Schwenk
#     affiliations:
#         name: Ruhr University Bochum
#     url: https://twitter.com/JoergSchwenk
#     bibtex: Schwenk, Jörg

bibliography: 2023/04/session-tickets.bib

toc:
  - name: What are Session Tickets?
    subsections:
      - name: Issues with Session Tickets
  - name: Scanning the Web
    subsections:
      - name: First Findings
        subsections:
          - name: AWS
          - name: Stackpath
      - name: Further Weak STEKs
  - name: Impact
  - name: Takeaways
    subsections:
      - name: Further Results
---

<!-- Add possibility to only display some elements in light or dark mode. Using invert does not play nicely with colors in an svg -->
<style>
    /* hide light only when in dark mode, hide dark in any other mode (on initial page view, the attribute might not be set to light properly...) */
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
</style>

We recently published the paper "[We Really Need to Talk About Session Tickets: A Large-Scale Analysis of Cryptographic Dangers with TLS Session Tickets][paper]"&nbsp;<d-cite key="sessiontickets2023"/>.
In this paper, we analyze the security of TLS session ticket implementations and deployed servers.
Many servers used guessable keys to encrypt session tickets, allowing attackers to decrypt TLS traffic or to impersonate the server.
We'll present this in person at [RuhrSec in May](https://www.ruhrsec.de/2023/) and at [USENIX in August](https://www.usenix.org/conference/usenixsecurity23).
In this post, we give a brief overview of the paper and our results.

---

## What are Session Tickets?

![Absract representation of a TLS 1.2 handshake and session resumption.](/assets/img/2023/04/session-tickets/handshake.drawio.svg){:width="100%" .light-only}
![(Dark mode image - for description see light mode image)](/assets/img/2023/04/session-tickets/handshake.dark.svg){:width="100%" .dark-only}

<div class="caption">
(Left) A TLS 1.2<d-footnote>TLS 1.0 and TLS 1.1 behave the same way. For simplicity, we write TLS 1.2.</d-footnote> handshake with a DH key exchange. Here the server issues a ticket containing key material for the second handshake.

(Right) A TLS 1.2 handshake using a ticket to resume the session.
It does not perform another key exchange or authentication.

<details class="legend">
<summary>
Explanation of icons
</summary>
<table>
<tr>
<th>Icon</th>
<th>Description</th>
</tr>
<tr>
<td><img alt="user (Tessa) using behind a laptop" src="/assets/img/2023/04/session-tickets/ke-assets/tessa.png"></td>
<td>User who is connecting to the server</td>
</tr>
<tr>
<td><img alt="server rack" src="/assets/img/2023/04/session-tickets/ke-assets/server.svg"></td>
<td>Server the user is connecting to</td>
</tr>
<tr>
<td><img alt="speech bubble containing CH" src="/assets/img/2023/04/session-tickets/ke-assets/ch.drawio.svg"></td>
<td>Client Hello. A message containing a list of supported parameters.</td>
</tr>
<tr>
<td><img alt="speech bubble containing SH" src="/assets/img/2023/04/session-tickets/ke-assets/sh.drawio.svg"></td>
<td>Server Hello. A message containing the chosen parameters.</td>
</tr>
<tr>
<td><img alt="document with a wax seal" src="/assets/img/2023/04/session-tickets/ke-assets/certificate.svg"></td>
<td> Certificate sent by the server. The client has to verify it (including contained signatures).</td>
</tr>
<tr>
<td><img alt="left half of a key" src="/assets/img/2023/04/session-tickets/ke-assets/ke-1.svg"></td>
<td> Key Exchange sent by the server. This is signed and has to be verified by the client.</td>
</tr>
<tr>
<td><img alt="right half of a key" src="/assets/img/2023/04/session-tickets/ke-assets/ke-2.svg"></td>
<td> Key Exchange sent by the client.</td>
</tr>
<tr>
<td><img alt="complete key" src="/assets/img/2023/04/session-tickets/ke-assets/key.svg"></td>
<td> The symmetric key derived from the key exchange.</td>
</tr>
<tr>
<td><img alt="database" src="/assets/img/2023/04/session-tickets/ke-assets/db.svg"></td>
<td> Local storage of the client.</td>
</tr>
<tr>
<td><img alt="blue key" src="/assets/img/2023/04/session-tickets/ke-assets/stek.drawio.svg"></td>
<td> Session Ticket Encryption Key (STEK). Used to encrypt the ticket. This should only be known to the server.</td>
</tr>
<tr>
<td><img alt="entrance ticket" src="/assets/img/2023/04/session-tickets/ke-assets/ticket.svg"></td>
<td> The ticket containing key material for resumption.</td>
</tr>
</table>
</details>
</div>

Session tickets (RFC&nbsp;5077&nbsp;<d-cite key="rfc5077"/>) improve the performance of the TLS protocol.
In a normal TLS handshake, the client and server have to agree on a shared secret key.<d-footnote>Depicted in the figure above as <img alt="left half of a key" src="/assets/img/2023/04/session-tickets/ke-assets/ke-1.svg"> and <img alt="right half of a key" src="/assets/img/2023/04/session-tickets/ke-assets/ke-2.svg">.</d-footnote>
Further, the server has to authenticate itself to the client using a certificate.
The certificate contains a signature the client has to verify.<d-footnote>
<img alt="A document with a wax-seal on it" src="/assets/img/2023/04/session-tickets/ke-assets/certificate.svg"> Actually, the server sends a chain of certificates. Each certificate contains a signature of the parent certificate. Each signature has to be checked.<br/> The server also includes a signature over its key exchange <img alt="Right part of a key" src="/assets/img/2023/04/session-tickets/ke-assets/ke-1.svg"> which the server has to compute, and the client has to verify.
</d-footnote>
Both of these are computationally expensive.
To skip these steps in future connections, the server can send a ticket to the client.
The ticket contains the established secret<d-footnote>The actual key material is not directly included. The master secret (1.2) or resumption secret/PSK (1.3). Additionally, some information about the connection parameters is included.</d-footnote> which is used in the next handshake.
This allows the key exchange and certificate to be skipped.
The client stores the ticket and established secret for the next handshake.

Upon resumption, the client sends the ticket to the server, which can retrieve the secret from the ticket and resume the connection.
As the client sends the ticket in plain upon resumption, the secret is encrypted with a key only known to the server.
This key is called a Session Ticket Encryption Key (STEK).
This way only the server is able to read the secret from the ticket.

### Issues with Session Tickets

While TLS session tickets bring significant performance improvements for TLS connections&nbsp;<d-cite key="BlogCloudflareSessionResumption"/>, they have become a major target of criticism raised by security experts&nbsp;<d-cite key="ValsordaBlogPost, TlsShortCuts, sy2018tracking"/>; if an attacker can extract the state from a ticket, they can impersonate the server or decrypt recorded TLS connections.<d-footnote>This holds for all versions of TLS. TLS 1.3 improved this by allowing to perform an additional key exchange. This prevents the passive decryption of data transmitted after the key exchange. It is still possible to decrypt the 0RTT data (sent before key exchange) or impersonate the server.</d-footnote>

Such dangers are not only theoretical; in 2020, Fiona Klute discovered a vulnerability affecting the security of the session resumption mechanism in GnuTLS&nbsp;<d-cite key="GnuTLSBugBlog,GnuTLSBug"/>.
The server used an all-zero STEK in the initial key rotation interval, allowing an attacker to decrypt the session tickets and learn the included secret TLS state.

Even if a client does not resume the ticket, their initial connection is still endangered by the ticket issuance.
In TLS 1.2 a resumed session uses the same key material as the initial connection.<d-footnote>The actual cryptographic keys differ, however they are derived from the same master secret and other publicly observable fields.</d-footnote>
This means, that an attacker able to extract the state from the ticket can also decrypt the initial connection.
As the ticket is issued in plain, it is observable by an attacker.

## Scanning the Web

We analyzed 12 open-source implementations to see how session tickets are usually formatted and which cryptographic algorithms are used to protect them.
Using this knowledge, we implemented tests for five implementation pitfalls and vulnerabilities with TLS-Scanner<d-footnote><a href="https://github.com/tls-attacker/TLS-Scanner">TLS-Scanner (on GitHub)</a> is an open-source tool to evaluate TLS implementations.</d-footnote>.
In this post, we focus on the tests of weak STEKs and reused keystreams.
We scanned hosts from the Tranco List&nbsp;<d-cite key="LePochat2019"/> as well as randomly chosen IPv4 hosts with port 443 open.
We performed three sets of scans:

1. **pre&#8209;T1M** and **T1M**:
   Our first scan of the Tranco top 1M was performed in May 2021 during the master thesis of Simon Nachtigall<d-cite key="nachtigallEvaluationTLSSession2021"/>.
   We only scanned for keys consisting exclusively of zero bytes in TLS 1.2 and 1.3.
   <br/>
   Before performing the final T1M scan, we performed several test scans, summarized as the **pre&#8209;T1M** scan.

1. **T100k** and **IP100k**
   We performed two smaller but more detailed scans of 100k hosts each in April 2022.
   These were chosen as the top 100k from the Tranco list and 100k random IPv4 hosts that responded on port 443.
   For these, we also performed further tests not covered in this post.

1. **IPF**
   Last, we scanned the entire IPv4 address range in August 2022.
   To this end, we only collected session tickets and performed the tests afterward without having to contact the servers again.
   We performed three TLS connections per host using ZGrab2, each time attempting to obtain a session ticket.
   We chose this number as it reduces the number of connections while hopefully still managing to connect to different servers if there is a load balancer.

### First Findings

<table>
<thead>
<tr class="header">
<th style="text-align: left;"></th>
<th style="text-align: right;"></th>
<th style="text-align: center;"></th>
<th colspan="2"
style="text-align: center;"><strong>Encryption</strong></th>
<th style="text-align: center;"></th>
<th colspan="2"
style="text-align: center;"><strong>Authentication</strong></th>
<th style="text-align: center;"></th>
<th style="text-align: center;"></th>
</tr>
</thead>
<tbody>
<tr>
<th style="text-align: left;"><span>Scan</span></th>
<th style="text-align: right;">Servers<br>Found</th>
<th style="text-align: center;"></th>
<th style="text-align: right;">Algorithm</th>
<th style="text-align: center;">Key</th>
<th style="text-align: center;"></th>
<th style="text-align: center;">Algorithm</th>
<th style="text-align: center;">Key</th>
<th style="text-align: center;"></th>
<th style="text-align: center;"></th>
</tr>
<tr>
<td rowspan="2" style="text-align: left;">pre-T1M</td>
<td style="text-align: right;">1903</td>
<td style="text-align: center;"></td>
<td style="text-align: right;">AES-256-CBC</td>
<td style="text-align: left;"><code>00 00 ... 00 00</code></td>
<td style="text-align: center;"></td>
<td colspan="2" style="text-align: center;">&ndash;</td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
</tr>
<tr>
<td style="text-align: right;">20</td>
<td style="text-align: center;"></td>
<td style="text-align: right;">AES-128-CBC</td>
<td style="text-align: left;"><code>00 00 ... 00 00</code></td>
<td style="text-align: center;"></td>
<td style="text-align: center;">HMAC-SHA256</td>
<td style="text-align: left;"><code>00 00 ... 00 00</code></td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
</tr>
</tbody>
</table>

Unexpectedly, the pre-T1M scan directly uncovered many servers using an all-zero STEK.
In the pre-T1M scan, we scanned the Tranco top 100k hosts multiple times.
Summed up over all scans, we found 1923 (**1.9%**) distinct servers using an all-zero STEK.
These belonged to AWS and Stackpath.

#### AWS

1,903 of the servers using an all-zero STEK were identified as belonging to AWS.
These used AES-256-CBC to encrypt the tickets.
We did not find the HMAC key and assume it was set correctly.
Due to the high impact, we decided to report our finding before continuing with the full scan.
The issue was promptly resolved<d-cite key="amazon_aws_issue"/>.

We could see that the hosts were not vulnerable at all times but only in some time intervals.
This suggested an error in the key rotation, which was later confirmed to us by AWS developers.

#### Stackpath

We also found 20 hosts belonging to Stackpath that used an all-zero STEK and HMAC key.
These tickets were encrypted using AES-128-CBC and authenticated using HMAC-SHA256.
Again, we immediately reported the issue.

The affected servers behaved differently from the AWS servers.
When connecting to the server multiple times, only some tickets were encrypted using a weak STEK.
This was not limited to a specific timeframe as in the case of AWS.
Interestingly, we found all servers were hosted on the same IP address.
Using an online reverse DNS lookup tool, we found a total of 171 domains on the same IP.<d-footnote>We used <a href="https://www.yougetsignal.com/tools/web-sites-on-web-server/">https://www.yougetsignal.com/tools/web-sites-on-web-server/</a>.</d-footnote>
By scanning these, and collecting 1,000 tickets per hostname, we found a total of 90 hostnames for which we could observe vulnerable tickets.
We identified that on vulnerable hosts, on average 1.4% of the issued tickets per host were affected.
Stackpath did not give us any insight into how this came to be but resolved the issue.

### Further Weak STEKs

<style>
.footnote-ref {color: var(--global-theme-color) !important; border-bottom: none; text-decoration: none;}
.distill-fn-style li{color: var(--global-distill-app-color) !important; font-size: 0.8em; line-height: 1.7em;}
.distill-fn-style a{color: var(--global-distill-app-color) !important; border-bottom: none; text-decoration: none;}
.distill-fn-style a:hover{color: var(--global-hover-color) !important; border-bottom: none; text-decoration: none;}
</style>

<div class="threeparttable l-page" style="margin: auto">
<table>
<thead>
<tr class="header">
<th style="text-align: left;"></th>
<th style="text-align: right;"></th>
<th style="text-align: center;"></th>
<th colspan="2"
style="text-align: center;"><strong>Encryption</strong></th>
<th style="text-align: center;"></th>
<th colspan="2"
style="text-align: center;"><strong>Authentication</strong></th>
<th style="text-align: center;"></th>
<th style="text-align: center;"></th>
</tr>
</thead>
<tbody>
<tr>
<th style="text-align: left;"><span>Scan</span></th>
<th style="text-align: right;">Servers<br>Found</th>
<th style="text-align: center;"></th>
<th style="text-align: right;">Algorithm</th>
<th style="text-align: center;">Key</th>
<th style="text-align: center;"></th>
<th style="text-align: center;">Algorithm</th>
<th style="text-align: center;">Key</th>
<th style="text-align: center;"></th>
<th style="text-align: center;"></th>
</tr>
<tr>
<td style="text-align: left;">T1M</td>
<td style="text-align: right;">3</td>
<td style="text-align: center;"></td>
<td style="text-align: right;">AES-128-CBC</td>
<td style="text-align: left;"><code>00 00 ... 00 00</code></td>
<td style="text-align: center;"></td>
<td style="text-align: center;">HMAC-SHA256</td>
<td style="text-align: left;"><code>00 00 ... 00 00</code></td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
</tr>
<tr>
<td style="text-align: left;">IP100k</td>
<td style="text-align: right;">0</td>
<td style="text-align: center;"></td>
<td colspan="2" style="text-align: center;">&ndash;</td>
<td style="text-align: center;"></td>
<td colspan="2" style="text-align: center;">&ndash;</td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
</tr>
<tr>
<td style="text-align: left;">T100k</td>
<td style="text-align: right;">1</td>
<td style="text-align: center;"></td>
<td style="text-align: right;">AES-128-CBC</td>
<td style="text-align: left;"><code>00 00 ... 00 00</code></td>
<td style="text-align: center;"></td>
<td style="text-align: center;">HMAC-SHA256</td>
<td style="text-align: left;"><code>00 00 ... 00 00</code></td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
</tr>
<tr>
<td rowspan="5" style="text-align: left;">IPF</td>
<td style="text-align: right;">5</td>
<td style="text-align: center;"></td>
<td style="text-align: right;">AES-256-CBC</td>
<td style="text-align: left;"><code>00 00 ... 00 00</code></td>
<td style="text-align: center;"></td>
<td colspan="2" style="text-align: center;">&ndash;</td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
</tr>
<tr>
<td style="text-align: right;">94</td>
<td style="text-align: center;"></td>
<td style="text-align: right;">AES-128-CBC</td>
<td style="text-align: left;"><code>00 00 ... 00 00</code></td>
<td style="text-align: center;"></td>
<td style="text-align: center;">HMAC-SHA256</td>
<td style="text-align: left;"><code>00 00 ... 00 00</code></td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
</tr>
<tr>
<td style="text-align: right;">12</td>
<td style="text-align: center;"></td>
<td style="text-align: right;">AES-256-CBC</td>
<td style="text-align: left;"><code>00 00 ... 00 00</code></td>
<td style="text-align: center;"></td>
<td style="text-align: center;">HMAC-SHA384</td>
<td style="text-align: left;"><code>00 00 ... 00 00</code></td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
</tr>
<tr>
<td style="text-align: right;">3</td>
<td style="text-align: center;"></td>
<td style="text-align: right;">AES-128-CBC</td>
<td style="text-align: left;"><code>10 11 ... 1e 1f</code></td>
<td style="text-align: center;"></td>
<td style="text-align: center;">HMAC-SHA256</td>
<td style="text-align: left;"><code>20...2f 00...00</code><sup><a href="#fn1" class="footnote-ref" id="fnref1" role="doc-noteref">a</a></sup></td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
</tr>
<tr>
<td style="text-align: right;">75</td>
<td style="text-align: center;"></td>
<td style="text-align: right;">AES-256-CBC</td>
<td style="text-align: left;"><code>31...31 00...00</code><sup><a href="#fn2" class="footnote-ref" id="fnref2" role="doc-noteref">b</a></sup></td>
<td style="text-align: center;"></td>
<td style="text-align: center;">HMAC-SHA256</td>
<td style="text-align: left;"><code>31...31 00...00</code><sup><a href="#fn2" class="footnote-ref" id="fnref2" role="doc-noteref">b</a></sup></td>
<td style="text-align: center;"></td>
<td style="text-align: center;"></td>
</tr>
</tbody>
</table>

<ol class="distill-fn-style" type="a">
<li id="fn1">This key consists of 16 consecutively increasing bytes followed by 16 <code>0x00</code> bytes. <a href="#fnref1" class="footnote-backlink" role="doc-backlink">[↩︎]</a></li>
<li id="fn2">This key consists of 16 <code>0x31</code> bytes followed by 16 <code>0x00</code> bytes. <a href="#fnref2" class="footnote-backlink" role="doc-backlink">[↩︎]</a></li>
</ol>
</div>

During the T1M scan, after AWS and Stackpath have resolved the issue, we found three further hosts using an all-zero key for both encryption and HMAC.
These hosts used AES-128-CBC with HMAC-SHA256 and supported TLS 1.2.
One of these hosts also supported TLS 1.3, also using zero-keys for session tickets.

As can be seen in the table, with our subsequent IPF scan we could detect more interesting keys.
We found 189 servers using a weak key.
Out of these, 111 servers were using an all-zero key.
For 5 hosts we did not detect a weak key for the HMAC algorithm.
12 hosts used SHA384, which no analyzed open-source library uses.
This implies, they use a different implementation or reconfigured the used library.
The remaining 78 servers did not use keys that solely consisted of zero bytes.
We explore the detected keys in our paper.

## Impact

The presented issues allowed to decrypt TLS session tickets.
This allows a passive adversary to decrypt all resumed sessions.
In TLS 1.2 this even allows decrypting the session where the ticket was issued, even if it was never resumed.
TLS 1.3 mitigates parts of this issue by deriving the keys for the new session using a one-way function instead of plainly reusing them.
This means, even if the ticket is decrypted, the attacker cannot decrypt the resumed session.
Further, TLS 1.3 allows performing another key exchange when resuming a session.
After this key exchange, the encrypted data is secure against a passive adversary again.
This still leaves the 0-RTT data vulnerable to decryption.

All versions are vulnerable to active impersonation.
An attacker able to decrypt the session ticket can impersonate the server as the authentication solely relies on the ticket.
The server does not send a certificate or signature, hence the client cannot verify the identity of the server.
This undermines the security guarantees of TLS.

As of now, we have not released a version of TLS-Scanner that can test whether you are affected by this issue.
We plan on releasing it in time for the artifact evaluation for Usenix (June-August).

## Takeaways

We showed that improper usage of session tickets can have devastating consequences for TLS connections and break forward secrecy guarantees delivered by TLS.
The concrete issues discovered seem unlikely, but are an important reminder that looking for seemingly trivial or contrived issues can be worthwhile for auditors.

At its core, we attribute the observed issues to the unauditability of session tickets.
Since the STEK and the layout are unknown and never revealed to the client, clients cannot simply validate the strength of the key, the presence of a MAC, or even the algorithms used.
This lack of transparency creates a space for bad implementations, silently failing crypto, and hidden backdoors.

While key generation always seems to have this potential, it is especially severe for one-sided symmetric keys, as with asymmetric keys, at least the public key can be audited externally&nbsp;<d-cite key="USS:180213, USENIX:SNSKFKM16"/>.
Having hard-to-analyze keys in a protocol at a place where a weak or leaked key causes the protocol to fail catastrophically is a huge risk that requires careful consideration.
Since these keys cannot be audited externally, we argue that libraries should start auditing them themselves before they use them.

In public key cryptosystems, it is already common practice to ensure that the generated key material is of a specific form, for example, to ensure that the key material will result in a strong key or as a safety net for failing random number generators. Adding additional checks to randomly drawn symmetric keys could, at least to some extent, ensure that accidentally weak key material does not break the protocol.

### Further Results

In our paper, we have seen a single case of a reused nonce.
As we did not perform a long time study, we cannot say whether this is a one-time issue or a more general problem.
We argue that libraries should use nonce reuse-resistant algorithms to avoid this issue.
In general misuse-resistant APIs should be developed and enforced.

We cover further attacks that can be applicable to session tickets in our paper.
We also present the analysis of open-source implementations and their usage of session tickets.
See our preprint for more details:

{::options parse_block_html="true" /}

<div style="text-align: center;">
[**We Really Need to Talk About Session Tickets:<br/>A Large-Scale Analysis of Cryptographic Dangers with TLS Session Tickets**][paper]
<br/>
[Sven Hebrok](https://twitter.com/xoimex),
[Simon Nachtigall](https://twitter.com/snachti),
[Marcel Maehren](https://twitter.com/marcelmaehren),
[Nurullah Erinola](https://twitter.com/nerinola1),
<br/>
[Robert Merget](https://twitter.com/ic0nz1),
[Juraj Somorovsky](https://twitter.com/jurajsomorovsky),
[Jörg Schwenk](https://twitter.com/JoergSchwenk)
</div>

[paper]: https://www.usenix.org/conference/usenixsecurity23/presentation/hebrok
