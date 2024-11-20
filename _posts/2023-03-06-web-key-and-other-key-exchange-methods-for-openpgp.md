---
layout: distill
title: "Bachelor's Thesis: Web Key Directory and Other Key Exchange Methods for OpenPGP"
date: 2023-03-06
description: a security analysis on the OpenPGP key exchange method Web Key Directory
citation: true

authors:
  - name: Philipp Michael Breuch
    affiliations:
      name: Paderborn University
    bibtex: Breuch, Philipp Michael

bibliography: web-key-and-other-key-exchange-methods-for-openpgp.bib

toc:
  - name: "In a Nutshell: Web Key Directory"
    subsections:
      - name: Key Discovery Protocol
      - name: Update Protocol
  - name: Security Analysis
    subsections:
      - name: Update Protocol Main Assumption
      - name: Implementation Errors and Faults
      - name: Attack on the Update Protocol Implementation
  - name: Conclusion
---

<!-- CSS snippet to make svg images with transparent background dark mode friendly.
     Add class="wkd-dark-invert" to invert the color iff dark-theme active -->
<style>
    html[data-theme="dark"] img.wkd-dark-invert {
        filter: invert(1);
    }
</style>

Philipp Breuch completed his Bachelor's degree at Paderborn University in August, 2022.
He wrote his Bachelor's Thesis "Web Key Directory and Other Key Exchange Methods for OpenPGP" <d-cite key="Breuch:22:BA-WKD"/> at the System Security Research Group supervised by Prof. Dr.-Ing. Juraj Somorovsky and Dipl.-Math. Marcus Brinkmann.

---

OpenPGP is used in various different application areas like securing mails, encrypting files, and validating the integrity and authenticity of exchanged files.
A core design principle of OpenPGP is decentralization.
In contrast to cryptographic protocols utilizing the public key infrastructure (e.g., S/MIME in the context of securing mails, or HTTPS for web), OpenPGP has no centralized trust anchors.

As direct key distribution and key validation do not scale, the OpenPGP ecosystem evolved two indirect concepts:

- **key servers** for key distribution
- the **Web of Trust** as a decentralized trust model for validating the authenticity of keys

It turned out that both concepts have fundamental problems:

- Key servers do not verify uploaded keys.
  Everyone can upload keys for any e-mail address, which leads to different attack vectors.
  For example, the "evil32" attack <d-cite key="evil32"/> showed that it is very efficient to generate and upload keys with the same short fingerprint (the last 4 bytes of the full fingerprint).
  Users who check only the short fingerprint can not distinguish between the legitimate and the counterfeit key.
- To make the "web of trust" possible, users can sign a specific public key to express its validity.
  However, this process can also be exploited by an attacker; if they massively sign and upload a victim’s key to a key server, the key size will grow steadily.
  As a result, a key with too many signatures (the specific amount depends on the used software) can not be processed anymore.
  Synchronizing key servers are practically only appending key material, which complicates mitigation of such attacks.
- Not only manipulated keys, but also public keys where users no longer possess the corresponding private key, remain in the system.
- It turned out that only a fraction of the users of the "web of trust" can significantly profit from it <d-cite key="Ulrich:11:IWoT"/>.
  This is contrasted by the disclosure of personal data and the social graphs of the users, which can be derived from the key signatures.
- The SKS key server network, which was used as the default key server in GnuPG, is no longer maintained and has been shutdown on 2021-06-21 due to privacy problems and legal problems resulting from the European General Data Protection Regulation.

An approach to improve this situation is Web Key Directory.
It provides a method to associate OpenPGP keys to a well-known URI and distribute them over HTTPS.
Web Key Directory incorporates security properties of the TLS ecosystem by the use of HTTPS for key exchange.
Trusting exchanged keys over this method, therefore, implies trusting in TLS and the (web)server responsible for the publication.

## In a Nutshell: Web Key Directory

Web Key Directory (WKD) <d-cite key="koch-openpgp-webkey-service-14"/> is an IETF Internet Draft which consists of two protocols, which will be briefly described here before presenting the results of the security analysis:

1. The Key Discovery Protocol can be used to discover and receive OpenPGP keys published via the Web Key Directory.
2. The Directory Update Protocol can be used to submit keys in an automated, e-mail driven way to the Web Key Directory.

### Key Discovery Protocol

Web Key Directory associates keys with their e-mail addresses.
These keys are provided by a webserver on the domain of the e-mail address.
To locate and request a key, the client sends a GET request over an HTTPS secured connection to this webserver.
There are two variants of URIs, the _advanced_ and the _direct_ variant.

In the following, we look briefly at the URI constructed for the e-mail address *Alice.Wonderland@example.org* in the advanced variant:

![An annotated example of a WKD URL. The domain is the 'openpgpkey' subdomain of the e-mail address domain. The last part of the path is the Z-Base-32 encoded SHA-1 hash of the lower-case local-part of the e-mail address. The GET parameter 'l' has the local-part of the e-mail address with URI percentage encoding as needed. The complete example URI is: https://openpgpkey.example.org/.well-known/openpgpkey/example.org/hu/5gt5gnaq1zccz7f19kq9whu4ezf1uofq?l=Alice.Wonderland](/assets/img/web-key-and-other-key-exchange-methods-for-openpgp_-_wkd-uri-advanced.svg){:width="100%" .wkd-dark-invert}

We see that most of the URI construction is pretty straight-forward.
The second variant, the direct URI, is only used if the _openpgp_ subdomain does not exist and is simply the advanced URI omitting the subdomain and the repetition of the e-mail address domain in the path.
The response to this HTTPS GET request is the OpenPGP key for the given e-mail address, regardless of URI variant.

Some attention should be lent to the last part of the path, which is the local-part of the e-mail address, mapped to lower-case, hashed, and encoded in alpha-numerical characters (e.g., a hash of "alice.wonderland").
This is done in part to ease the implementation of WKD servers by ensuring this path element is always a valid file name without special characters that might be rejected, for example, by the webserver's operating system.
However, it is not strictly compliant to the e-mail specification to treat the local-part always case-insensitive; but it reflects the typical real-world usage of e-mail addresses.

Therefore, if a Web Key Directory should be provided for an e-mail server that distinguishes e-mail addresses by case, the WKD server has to make sure to check the verbatim local-part in the `l` parameter.
Otherwise e-mail addresses which only differ in case would be mapped to the same key.
This could make it possible to publish an OpenPGP key for all of those e-mail addresses by only possessing one.

### Update Protocol

The purpose of the e-mail driven update protocol is to automate and ease the publication process of OpenPGP keys to the Web Key Directory.
It is based primarily on OpenPGP secured e-mail exchange between the user and their Web Key Directory provider.

For the submission process, we need to know the submission e-mail address to which we submit our key and the OpenPGP key for that submission address.
The submission address is defined in a file which is served by the Web Key Directory webserver.
The corresponding key is treated like every other published key and can therefore be requested via the key discovery protocol.

To ensure that only the legitimate key owner can publish their keys, the update protocol uses a challenge-response mechanism.

![Exchanged e-mails in the WKD Update Protocol between user Alice and her WKD provider in a Message Sequence Graph. First, Alice sends a submission mail to her WKD provider. This submission mail is encrypted to the WKD provider and contains the key with one User-ID (e-mail address). Second, the WKD provider sends a confirmation request to the e-mail address of the submitted key (i.e. Alice). This confirmation request mail is encrypted to the submitted key and signed by the WKD provider. It contains the e-mail address, the fingerprint of the submitted key, and the nonce as a secret. Third, Alice sends a confirmation response back to the WKD provider. This confirmation response is encrypted to the WKD provider and signed by Alice. It contains the e-mail address and the nonce. Fourth, the WKD provider publishes the submitted key to the Web Key Directory and notifies Alice via an optional success mail.](/assets/img/web-key-and-other-key-exchange-methods-for-openpgp_-_wkd-update-protocol.svg){:width="100%" .wkd-dark-invert}

This mechanism is implemented via the confirmation request and confirmation response mails.
The confirmation request is sent to the e-mail address of the submitted key and is encrypted with the submitted key and signed by the WKD provider.
The critical contents are the randomly chosen nonce as the secret, the e-mail address and fingerprint of the submitted key.
E-mail address and fingerprint can be used by the user to verify that the correct key should be published for the correct e-mail address.

The nonce is only accessible by the key owner because they should be the only person in possession of the corresponding private key and thus able to decrypt the nonce.
If the nonce is sent back correctly, the server can assume that the key owner wants to publish the submitted key and makes the key available via the Web Key Directory.
The server can send an optional success message to the user.

The challenge-response mechanism has to be done with the person for which the key should be published for.
But how do we know that the key supposedly for *alice@example.org* is indeed from Alice and not from an attacker like Mallory?
The update protocol is based on the assumption that the WKD provider can securely deliver mail to the owner of the mail address without third-parties able to read its contents.
We will address this assumption below in the security analysis.

## Security Analysis

During the analysis, it became apparent that we had to distinguish between the Web Key Directory specification and the reference implementation ([GnuPG 2.2.35 (LTS)/ 2.3.6](https://git.gnupg.org/cgi-bin/gitweb.cgi?p=gnupg.git;a=tags)) in regard to the security implications.
Regarding the WKD specification we found one major concern in the lax and vague main assumption for the update protocol.
The _GnuPG_ implementation of WKD is the only implementation we know about which tries to implement both the discovery and update protocol.
We found several implementation errors and faults in this implementation, which were not always security relevant.
However, a combination of two errors made it possible to find an attack which allowed us to completely compromise a Web Key Directory installation.

### Update Protocol Main Assumption

The main assumption regarding the security of the WKD Update Protocol reads as follows:

> The protocol defined here is entirely based on mail and the assumption that a mail provider can securely deliver mail to the INBOX of a user (e.g., an IMAP folder).

This assumption is vague and unclear.
It is neither clear which security properties are requested nor from whom.
E-mail infrastructure can be very complex.
An e-mail from a Web Key Directory provider to their user might take several hops before reaching its destination.

We created three scenarios how the e-mail infrastructure topology could look like and considered several interpretations of the main assumption.
We examined these interpretations with the topology scenarios and discussed their impact on the security of WKD.

Only in one interpretation we could find no attack points in any scenario.
This interpretation, however, was the most unrealistic: the assumption, that a mail provider can "securely" (i.e. at least confidentially) deliver e-mails to the inbox of the recipient user's mail client, even for recipients on other servers.

The security of the update protocol should not be based on such a vague assumption.
Our discussion showed potential attack points which might also exist in real-world setups.
For details see Thesis Section 6.3.

### Implementation Errors and Faults

We found out that the reference implementation is not completely specification-compliant.
This is due to not implementing requirements of the specification correctly or at all.
In addition there are two MIME headers (`Wks-Phase`, `Wks-Draft-Version`) in each message of the reference implementation which are not specified.
These headers are not secured (e.g., integrity-protected) in any way.
Problematic is the use of the `Wks-Draft-Version` header because it makes the reference implementation mostly incompatible to specification-compliant implementations.
The reference implementation decides which WKD specification version is used for the processed mail based on this header.
However, this header could easily be changed which could open potential possibilities for downgrade attacks on future protocol changes.

In addition, we found further conceptual and implementation errors like missing and incorrect signature generation and verification in the reference implementation.
The confirmation response may be sent unencrypted and attacker controlled data like `nonce` and `address` fields in the mails are not checked properly.
See section 6.4 in the thesis for more information.

### Attack on the Update Protocol Implementation

Two of the above implementation errors led to a vulnerability, which allowed an attacker to publish OpenPGP keys for **any** e-mail address for **any** domain managed by a Web Key Directory provider.
Assume an attacker Mallory wants to publish a self generated key impersonating Alice to their WKD provider.
This attack has almost no assumptions:

1.  Victim Alice has an e-mail address like <alice@example.net>
2.  Attacker Mallory has an e-mail address like <mallory@example.org>
3.  The Web Key Directory provider uses
    - the GnuPG implementation of WKD
    - provides the WKD for both domains example.net and example.org
    - provides the WKD Update Protocol

The attack also works with Alice and Mallory using e-mail addresses with the same domain.

The attack is demonstrated in the below picture of the update protocol run:

![Attack on the Update Protocol shown as a Message Sequence Graph. It is similar to the Message Sequence Graph for the WKD Update Protocol (from above) but users are Alice, Mallory, and the WKD Provider. Mallory submits a key and then participates in the challenge-response mails with the server. Alice receives only an encrypted confirmation request and the optional success message after successful publication of the submitted key. Parts in the graph which are changed by Mallory in comparison to the regular WKD Update Protocol run are highlighted. These are the submitted key which contains both a User-ID for Alice and for Mallory, as well as the changed address and nonce fields in the confirmation response.](/assets/img/web-key-and-other-key-exchange-methods-for-openpgp_-_wkd-update-protocol-attack.svg){:width="100%" .wkd-dark-invert}

Mallory submits a key to the WKD provider with two User-IDs (i.e. names/addresses assigned to the key): one User-ID for alice@example.net and one for mallory@example.org.
It turned out that the GnuPG implementation sends a confirmation request to each of these e-mail addresses.
Each of these contain the distinct e-mail address in the `address` field, a distinct `nonce`, and the same `fingerprint` (key is the same for both).
Mallory is in possession of the private key and can decrypt the confirmation request to send a confirmation response back to the server.
Mallory must achieve two goals to succeed:

1. The server has to believe the confirmation response is for a confirmation request for Alice
2. The server has to see the nonce in the confirmation response as valid for a confirmation request for Alice.

The first goal is quite simple. The `address` field is not protected or validated and Mallory changes it simply in her confirmation response from mallory@example.org to alice@example.net.
The second goal is not that simple because Mallory does not know the nonce sent to Alice.
By digging into the source code we found that the nonce in the `nonce` field is not checked directly:
The nonce sent in the confirmation response is _not_ compared with the nonce in the confirmation request.
Instead the existence of a file path created with the nonce is checked.
The path consists of the following: '**domain / "pending" / nonce**'.
The domain is taken from the `address` field, "pending" is a fixed string, and the nonce is the value of the `nonce` field.
Both fields are not sanitized.

So, great! We can bend the path to every location in the file system via a simple path traversal on the `nonce` field.

To understand how our path traversal has to look like, we will have to look at how the implementation handles submitted keys internally:

![A directory tree containing paths like example.net/pending/o3euik... and example.org/pending/7mpzp4..., with example.net being the domain used by Alice and example.org the domain used by Mallory.](/assets/img/web-key-and-other-key-exchange-methods-for-openpgp_-_wkd-directory.svg){:width="100%" .wkd-dark-invert}

The implementation can handle a Web Key Directory for multiple e-mail address domains.
Each domain has its own directory.
In this directory there is, for example, the `hu` directory which contains all published keys.
Submitted but not yet verified keys are stored in the `pending` directory and named after the nonce used in the confirmation request.

Mallory submitted a key with two User-IDs (one for Alice and one for her).
The complete key is stored twice:
once in the pending directory for example.net named after the nonce only send to Alice _(o3euik3tr3d6rjwr...)_;
once in the pending directory for example.org named after the nonce only send to Mallory _(7mpzp4cgkr5uy3bz...)_.

Based on the path creation and the file structure we can see that a path traversal string '**../../example.org/pending/**' has to be prepended to the nonce in the confirmation response.
The resulting path '**example.net/pending/../../example.org/pending/7mpzp4cgkr5uy3bz...**' exists and contains the full submitted key.
The implementation will then publish the key (with only the User-ID of Alice) as the key for *alice@example.net*.

Thus we have an attack to publish a key for _any_ e-mail address of _any_ domain on a Web Key Directory.
The path traversal indeed is only necessary if the domain used by Alice and Mallory differs. Otherwise the changed address field would be sufficient to accomplish the attack.
This issue has been fixed in GnuPG version 2.2.37.

## Conclusion

In this blog post we have seen a brief overview of the two Web Key Directory Protocols.
We presented an attack based on improper checking of the nonce and missing input sanitization which allows publishing of illicit public keys for all e-mail addresses for all domains a Web Key Directory manages.
While this has been fixed, other issues like the update protocol main assumption might not be as easy to fix.
The GnuPG authors don't seem to consider issues like signature verification as important to fix, either.
