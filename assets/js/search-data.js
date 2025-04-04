// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "about",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-blog",
          title: "blog",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/blog/";
          },
        },{id: "post-china-extended-its-sni-censorship-to-quic",
      
        title: "China Extended its SNI Censorship to QUIC",
      
      description: "The GFW enforces QUIC-specific censorship",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/quic-china/";
        
      },
    },{id: "post-automated-bibliography-management-in-overleaf-with-zotero-and-a-custom-proxy",
      
        title: "Automated Bibliography Management in Overleaf with Zotero and a Custom Proxy",
      
      description: "how to integrate Zotero with Overleaf for efficient reference management",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2025/zotero-overleaf-integration/";
        
      },
    },{id: "post-censors-ignore-unencrypted-http-2-traffic",
      
        title: "Censors Ignore Unencrypted HTTP/2 Traffic",
      
      description: "Using Unencrypted HTTP/2 to Circumvent Censorship",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2024/http2/";
        
      },
    },{id: "post-circumventing-the-gfw-with-tls-record-fragmentation",
      
        title: "Circumventing the GFW with TLS Record Fragmentation",
      
      description: "How Fragmentation Can Be Extended to the TLS Layer",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2023/record-fragmentation/";
        
      },
    },{id: "post-we-really-need-to-talk-about-session-tickets",
      
        title: "We Really Need to Talk About Session Tickets",
      
      description: "A Large-Scale Analysis of Cryptographic Dangers with TLS Session Tickets",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2023/session-tickets/";
        
      },
    },{id: "post-bachelor-39-s-thesis-web-key-directory-and-other-key-exchange-methods-for-openpgp",
      
        title: "Bachelor&#39;s Thesis: Web Key Directory and Other Key Exchange Methods for OpenPGP",
      
      description: "a security analysis on the OpenPGP key exchange method Web Key Directory",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2023/web-key-and-other-key-exchange-methods-for-openpgp/";
        
      },
    },{id: "post-usage-statistics-of-3d-printing-file-formats",
      
        title: "Usage Statistics of 3D Printing File Formats",
      
      description: "an overview of the usage of different file formats used for 3D printing",
      section: "Posts",
      handler: () => {
        
          window.location.href = "/blog/2022/3d-printing-file-format-usage/";
        
      },
    },{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
