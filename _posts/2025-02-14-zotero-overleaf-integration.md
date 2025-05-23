---
layout: distill
title: Automated Bibliography Management in Overleaf with Zotero and a Custom Proxy
description: how to integrate Zotero with Overleaf for efficient reference management
date: 2025-02-14
citation: false

authors:
  - name: Jost Rossel
    affiliations:
      name: Paderborn University
    bibtex: Rossel, Jost

toc:
  - name: Parts of the Puzzle
  - name: Using The Zotero API Directly
  - name: Utilizing Our Custom Proxy
---

<!-- CSS snippet to make svg images with transparent background dark mode friendly.
     Add class="wkd-dark-invert" to invert the color iff dark-theme active -->
<style>
    html[data-theme="dark"] img.wkd-dark-invert {
        filter: invert(1);
    }
</style>

If you have ever worked with LaTeX you know the struggles of manual reference management.
To ease their struggles, many people automate reference management with a reference manager tool.
In many cases---especially when working offline on a single-author document---a simple export to Bib(La)TeX from the reference manager of you choice is sufficient.
But when working on the same document as a group, manual exporting references gets more cumbersome even more so when the export also has to be uploaded to a website such as Overleaf.
Both problems---automatically syncing references with Overleaf and managing references as a group---can be solved in a myriad of ways.
In this post, I present a few solutions that fully or partially address them.
Our own solution is a Zotero group with a small proxy that allows us to access the references in Overleaf; **the proxy is available on [GitHub](https://github.com/UPB-SysSec/Zotero-Overleaf-BibTeX-Proxy)**.

The solutions presented in this blog post is tailored towards the Zotero reference manager.
For the rest of this blog post, I assume that the reader is familiar with the basics of LaTeX, Overleaf, and Zotero as a reference manager.

## Parts of the Puzzle

![Three puzzle pieces in a row. Reading from left to right: “Manage References”, “Export BibTeX”, and “Import to Overleaf”.](/assets/img/2025/zotero-proxy/puzzle.svg){:width="70%" .wkd-dark-invert style="display: block; margin: 0 auto;"}

The problem of managing references in a group and syncing them with Overleaf can be broken down into three parts: managing references, exporting them to BibTeX, and importing them into Overleaf.
There are multiple facets of this that can be addressed separately and all have their upsides and downsides, so you might chose one over the other based on your specific needs.

### Managing References in a Group

The only solution we identified is by using a Zotero [group library](https://www.zotero.org/groups).
Of course that implies that you collaborators are willing to use this, otherwise you are back to square one.
When you get most people in a project to use Zotero, you can manually import the references from the remaining people into the library; this works especially well if the main authors use Zotero.
The duplicate detection from Zotero works quite well in our experience, so you can easily merge any duplicates from the import.

### Exporting BibTeX from Zotero

There are two ways (that I know of) to export references for LaTeX from Zotero:

1. the built-in export function, and
2. the [Better BibTeX for Zotero](https://retorque.re/zotero-better-bibtex/installation/index.html) plugin.

The built-in export function has allows BibTeX and BibLaTeX, but as no real configuration options.
The main downside I personally see is that the Bib-keys are generated by Zotero: you, thus, have no control over them and they are not visible in the Zotero interface.
The Better BibTeX plugin allows you to configure many aspects of the export and to automatically update the `.bib` file upon change.
In my opinion, the Better BibTeX plugin is the better choice for offline use.
The main downside is that there is no online support via the Zotero API---but more on that later.

### Importing `.bib` Files into Overleaf

The most straightforward way to import a `.bib` file into Overleaf is to upload it.
We want to avoid this, its manual work after all, and automation is always worth it. [Right?](https://xkcd.com/1205/) [Right??](https://xkcd.com/1319/)<d-footnote>One could argue that with our proxy the main effort of the automation is already done.</d-footnote>

<!-- alternatives to what? I assume alternatives to a manual import? -->

Alternatives to a manual import, anytime the references change, are

- using the Overleaf Zotero integration,
- using the Overleaf Git integration, or
- exposing the `.bib` file via a public URL and including it as a file in Overleaf.<d-footnote>When adding files in Overleaf you can also add them from external URLs. If you want to update the content, Overleaf provides you with a “Refresh” button.</d-footnote>

The Overleaf Zotero and Git integrations are only available for premium users, so it is not an option for everyone.
Additionally, with the Zotero integration only the premium user can refresh the collection, and you cannot select specific sub-collections of your Zotero library.
The Git integration is a good option if you are already using Git for your project, but it is not a solution for everyone.
You need to

- automatically update the `.bib` file in the repository, or
- (if you work in the web interface) manually push the changes or have a script running that pushes the changes.

So we decided to go with the third option: using the file inclusion method in Overleaf.
This, again, can be achieved multiple ways.
One option is to let Better BibTeX automatically update the `.bib` file into a folder that is synced to a cloud and have a direct download link for the cloud-file included in Overleaf.
The other option is to use the Zotero API to get the references and import them into Overleaf.

## Using The Zotero API Directly

If you sync your references to the Zotero server (default behavior) they can be accessed via the [Zotero API](https://www.zotero.org/support/dev/web_api/v3/start).
This API allows you to access your references in various formats, such as BibTeX.<d-footnote>This uses the default BibTeX format, not the one from the Better BibTeX plugin.</d-footnote>
In this section, we are assuming that you want to access the references from a group library, but the same principles apply to a personal library (but the URLs are different).

To use the API you need to create a [Zotero API key](https://www.zotero.org/settings/keys/new) and use it in the requests.
The key should be as limited as possible, so only give it the permissions it needs (e.g., only read access on one group).
Once you have a key you can use it to generate a BibTeX file of your references.

```
https://api.zotero.org/groups/GGGGGG/items/top?format=bibtex&key=KKKKKK&limit=100
```

This will give you the first 100 references in the group with the ID `GGGGGG` using the key `KKKKKK`.<d-footnote>100 being the maximum allowed number.</d-footnote>
If your library has more than 100 references you can use the `start` parameter to get the next 100 references.

```
https://api.zotero.org/groups/GGGGGG/items/top?format=bibtex&key=KKKKKK&limit=100&start=100
```

Similarly, you can get the references of a specific collection with the ID `CCCCCC`:

```
https://api.zotero.org/groups/GGGGGG/collections/CCCCCC/items/top?format=bibtex&key=KKKKKK&limit=100
```

You can find the required IDs by navigating to the group or collection in the Zotero _web_ library and looking at the URL.
We have not found a way to get the IDs in the Zotero desktop app.

### Advantages and Limitations of the Zotero API Approach

✅ No additional tools are required.  
✅ Direct integration with Overleaf.  
❌ API responses are restricted to **100 entries per request**, so managing extensive bibliographies necessitates multiple “external files” on Overleaf.  
❌ Requires manual retrieval and inclusion of sub-collection IDs.

## Utilizing Our Custom Proxy

To overcome the limitations of the Zotero API, we have developed a **Zotero-Overleaf BibTeX Proxy**.
The proxy needs to be hosted on a publicly accessible server and can be used to retrieve references from Zotero in a more user-friendly manner.

Assuming the proxy is hosted at `https://example.com` and the key and group ID are configured, the following URLs can be used to retrieve references:

```
example.com/collection/a
```

to access a collection `collection` with sub-collection `a`.

```
example.com
```

will return the full library.

Further details and usage instructions are available in the **[GitHub repository](https://github.com/UPB-SysSec/Zotero-Overleaf-BibTeX-Proxy)**.

### Advantages and Limitations of the Custom Proxy Approach

✅ No API-imposed entry limits (all references in a single file).  
✅ You can chose which sub-collection to include.  
✅ Simplified user-friendly URLs.  
✅ Eliminates the need for manual sub-collection ID identification.  
❌ You need to set up a server to host the proxy.

Both solutions using the Zotero API are limited in the configuration of the BibTeX output.
If you need more control over the output, the methods using the Better BibTeX plugin seem to be the only choice.

## Conclusion

Automating bibliography management in Overleaf with Zotero simplifies collaboration and reduces manual effort.
While the Zotero API provides direct access to references, it has limitations such as entry limits and manual sub-collection selection.
Our custom Zotero-Overleaf BibTeX Proxy overcomes these issues, offering a more flexible solution.

For teams seeking an efficient, automated workflow, our proxy provides seamless integration with Overleaf.
To get started, visit our **[GitHub repository](https://github.com/UPB-SysSec/Zotero-Overleaf-BibTeX-Proxy)**.
