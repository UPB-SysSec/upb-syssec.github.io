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

# toc:
#   - name: How We Collected the Data
#   - name: Overview of the Data
#   - name: Trend of Usage over Time
#   - name: How to Get the Data
---

If you have ever worked with Overleaf in larger groups you might know how annoying reference management can be.
A lot of people already use their own reference manager, such as Zotero, and import their references manually into Overleaf.
This can lead to duplicates in the references and is annoying manual work.

While Overleaf offers a built-in Zotero integration, it

1. is limited to premium users,
2. only the premium user can refresh the collection, and
3. you cannot select specific sub-collections.

There two ways one can work around these issues:

1. Directly using the Zotero API to get the references and import them into Overleaf.
2. Using the proxy we have implemented that simplifies the process.

## The Zotero API and how to use it with Overleaf

Zotero is a free, open-source reference management software that helps you collect, organize, cite, and share your research materials.
While you can use it on your own, it also offers [group libraries](https://www.zotero.org/groups) that can be shared with others.
If you sync your references to the Zotero server they can be accessed via the [Zotero API](https://www.zotero.org/support/dev/web_api/v3/start).
This API allows you to access your references in various formats, such as BibTeX.

To use the API you need to create a [Zotero API key](https://www.zotero.org/settings/keys/new) and use it in the requests.
The key should be as limited as possible, so only give it the permissions it needs (e.g., only read access on one group).
Once you have a key you can use it to generate a BibTeX file of your references.

```
https://api.zotero.org/groups/GGGGGG/items/top?format=bibtex&key=KKKKKK&limit=100
```

This will give you the first 100 references in the group with the ID `GGGGGG` using the key `KKKKKK`.
Similarly, you can get the references of a specific collection with the ID `CCCCCC`:

```
https://api.zotero.org/groups/GGGGGG/collections/CCCCCC/items/top?format=bibtex&key=KKKKKK&limit=100
```

You can find the required IDs by navigating to the group or collection in the Zotero *web* library and looking at the URL.
We have not found a way to get the IDs in the Zotero desktop app.

### Integration with Overleaf

When adding files in Overleaf you can also add them from external URLs.
If you want to refresh the content, Overleaf provides you with a “Refresh” button.

You can directly use the URLs from above to import your references into Overleaf.

### Zotero Configuration

When importing references from the API we recommend using external tools to manage the BibTeX keys.
By default Zotero generates the keys in the backend and you have to search in the generated file to find them.

You can avoid this by using the [Better BibTeX for Zotero](https://retorque.re/zotero-better-bibtex/installation/index.html) plugin.

1. Open Zotero and navigate to **Edit** -> **Preferences** -> **Better BibTeX** -> **Citation keys**.
2. Define the **Citation key formula** (if you want to).
3. Ensure that citation keys are automatically pinned by configuring **“Automatically pin citation key after”** to a value greater than zero.
4. If citation key inconsistencies arise, manually refresh them by selecting all items, right-clicking, and selecting **Better BibTeX** -> **Refresh BibTeX Key**.

Now the keys can be viewed and managed in via the Zotero interface.

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
