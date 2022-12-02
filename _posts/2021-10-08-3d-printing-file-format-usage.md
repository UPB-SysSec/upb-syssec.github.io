---
layout: distill
title: Usage Statistics of 3D Printing File Formats
description: an overview of the usage of different file formats used for 3D printing
date: 2021-10-08

authors:
  - name: Jost Rossel
    affiliations:
      name: Paderborn University

bibliography: 2021-10-08-3d-printing-file-format-usage.bib

toc:
  - name: How We Collected the Data
  - name: Overview of the Data
  - name: Trend of Usage over Time
  - name: How to Get the Data

---

During our current research on the security of 3D printers and the surrounding ecosystem, we asked ourselves how well different file formats are used.
As there seems to be no clear data, just anecdotal evidence, we decided to check for ourselves.

We analyze which are the most used file formats on two popular 3D model online-marketplaces, namely [Thingiverse](https://www.thingiverse.com/) and [MyMiniFactory](https://www.myminifactory.com/).
The data presented here is based on the publicly available files uploaded to both platforms.
The data does not contain any information about the usage of different file formats outside this specific use case of private users sharing their 3D printing model with others; especially not regarding an industrial context.
No other data is freely available.
The [How to Get the Data](#how-to-get-the-data) section below provides download links and how-tos for our dataset.

## How We Collected the Data

Both *Thingiverse* and *MyMiniFactory* provide application programming interfaces (APIs) that allow access to their data sets, specifically JSON-based HTTP REST APIs <d-cite key="rfc8259,rfc2616,fielding2000architectural,MyMiniFactoryAPIDocumentation,thingiverse.comRESTAPIReference"/>.
In both cases, there is no API endpoint to list existing objects, but both websites use incrementing numbers to identify the objects.
Thus, gathering a complete data set is a matter of incrementally trying every number until no more objects are found.
This can be done for both marketplaces.
For both marketplaces, we incremented the object IDs and attempted to download the JSON metadata for the ID.

The data set for *Thingiverse* contains more than two million entries, where the set for *MyMiniFactory* amounts to roughly 130,000 entries.
For each object the downloaded metadata includes the file names of all files uploaded to that object.
To ease the analysis, we stored the uploaded file names and their upload timestamp for each object.
Then, we reduced the file name to their suffix(es) (i.e. their file extension) and unified the them to a lower case version.
This means our analysis is limited to the knowledge derived from the file suffixes the uploader used.
It might be the case that the uploaded file does not match the actual content.
Additionally, we do not analyze the content of uploaded `.zip` (or similar) files.

## Overview of the Data

[Table 1](#tab:file-format-occurrences) lists the file formats that occur the most often in our data sets.<d-footnote>All file formats that occur more than 10,000 times. The remaining files account for 8% of all files.</d-footnote>
*Total Occurrences* shows the sum of all files uploaded for every object.
Multiple files of the same format can be uploaded for the same object.
That explains why the number of STL files can exceed that of the total number of objects in the data sets by about a factor of four.
There are more than five times as many STL files uploaded than all other file uploads combined.<d-footnote>There are 4,592,742 STL files and 787,577 other files in total.</d-footnote>
The *Repetition Factor* indicates how many files of the same format are uploaded for the same object on average.
For each format, we only counted objects where the given file format was present at least once.
Hence, the minimal value of the repetition factor is one.
Most repetition values are higher than 1.5 which shows that most file formats are rarely uploaded on their own.
That can be attributed to different variants of the same model being uploaded, for example, different scalings or colors.
The difference in the repetition factor between formats might be caused by limitations of the format itself or by common practices.

<div class="l-body-outset"><hr></div>

<style>
.footnote-ref sup{color: var(--global-theme-color);}
.distill-fn-style li{color: var(--global-distill-app-color) !important; font-size: 0.8em; line-height: 1.7em;}
.distill-fn-style a{color: var(--global-distill-app-color) !important;}
</style>

<span id='tab:file-format-occurrences'>**Table 1**</span>
Total number of occurrences/uploads of all file formats that occur more than 10,000 times.
The suffixes where unified to their lower-case version an the following suffixes were omitted: `.pdf`, `.zip`, `.0`, `.1`, `.svg`. AMF is included as it is mentioned by various rankings <d-cite key="3DPrinterFile2021,Common3DPrinting2019,WhatFileFormats2021"/>.
The repetition factor indicates how many files of this type were uploaded to a single object on average.

| Suffix             | File Format Description                                                                                                                               |  Total Occurrences |  Repetition Factor |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- | -----------------: | -----------------: |
| `.stl`             | STereoLithography <a href="#fn1" class="footnote-ref" id="fnref1" role="doc-noteref"><sup>a</sup></a>                                                 |          4,592,742 |               2.13 |
| `.scad`            | [OpenSCAD](http://openscad.org/) project file                                                                                                         |             77,585 |               1.42 |
| `.obj`             | Wavefront Object <a href="#fn2" class="footnote-ref" id="fnref2" role="doc-noteref"><sup>b</sup></a>                                                  |             65,556 |               1.86 |
| `.step`            | <span>*STandard for the Exchange of Product model data* <a href="#fn3" class="footnote-ref" id="fnref3" role="doc-noteref"><sup>c</sup></a>           |             44,920 |               1.72 |
| `.sldprt`          | [SolidWorks](https://www.solidworks.com/) Part file                                                                                                   |             43,599 |               2.00 |
| `.skp`             | [SketchUp](https://www.sketchup.com/) project file                                                                                                    |             32,522 |               1.48 |
| `.f3d`             | [Fusion 360](https://www.autodesk.com/products/fusion-360) project file                                                                               |             32,275 |               1.30 |
| `.fcstd`           | [FreeCAD](https://www.freecadweb.org/) project file                                                                                                   |             21,436 |               1.52 |
| `.dxf`             | *Drawing Interchange File* for *AutoCAD* <a href="#fn4" class="footnote-ref" id="fnref4" role="doc-noteref"><sup>d</sup></a>                          |             20,566 |               1.94 |
| `.gcode`           | Toolpath instruction for manufacturing devices <a href="#fn5" class="footnote-ref" id="fnref5" role="doc-noteref"><sup>e</sup></a>                    |             16,713 |               1.52 |
| `.ipt`             | [Inventor](https://www.autodesk.com/products/inventor) project file                                                                                   |             14,905 |               1.96 |
| `.3mf`             | 3D Manufacturing Format <a href="#fn6" class="footnote-ref" id="fnref6" role="doc-noteref"><sup>f</sup></a>                                           |             14,823 |               1.63 |
| `.blend`           | [Blender](https://www.blender.org/) project file                                                                                                      |             13,720 |               1.61 |
| `.123dx`           | [123D](https://www.autodesk.com/solutions/123d-apps) project file <a href="#fn7" class="footnote-ref" id="fnref7" role="doc-noteref"><sup>g</sup></a> |             12,146 |               1.55 |
| $\quad\vdots\quad$ | $\quad\vdots\quad$                                                                                                                                    | $\quad\vdots\quad$ | $\quad\vdots\quad$ |
| `.amf`             | Additive Manufacturing Format <a href="#fn8" class="footnote-ref" id="fnref8" role="doc-noteref"><sup>h</sup></a>                                     |              2,451 |               1.54 |

<ol class="distill-fn-style" type="a">
<li id="fn1">Defined by <i>3D Systems</i> in 1988 <d-cite key="STLSTereoLithographyFile2019"/>. The original specification is not available, but various resources describe the format based on the original specification<d-cite key="STL,STLAFilesASCII,StLFormatFabbers"/>.<a href="#fnref1" class="footnote-backlink" role="doc-backlink">[↩︎]</a></li>
<li id="fn2">First specified by <i>Wavefront Technologies</i> for their <i>Advanced Visualizer</i> software in the 1990s <d-cite key="wavefronttechnologiesAdvancedVisualizerAppendixearly1990s"/>. “[From] a legal standpoint, the specification is probably proprietary to Autodesk” <d-cite key="WavefrontOBJFile2020"/> as Wavefront Technologies was eventually indirectly acquired by Autodesk <d-cite key="WavefrontOBJFile2020"/>.<a href="#fnref2" class="footnote-backlink" role="doc-backlink">[↩︎]</a></li>
<li id="fn3">Designed as an exchange format between CAD applications. Standardized through the ISO 10303 family <d-cite key="iso10303-1"/>, part 21 <d-cite key="iso10303-21"/> defines the file format. Alternatively, uses the suffix <code>.stp</code>.<a href="#fnref3" class="footnote-backlink" role="doc-backlink">[↩︎]</a></li>
<li id="fn4">Designed as an exchange format between CAD applications. Standardized by Autodesk for their AutoCAD software <d-cite key="dxf"/>.<a href="#fnref4" class="footnote-backlink" role="doc-backlink">[↩︎]</a></li>
<li id="fn5">There are multiple standards defining G-codes (e.g. <d-cite key="din66025-1,iso6983-1"/>) but most applications and/or firmwares define their own extensions and variations.<a href="#fnref5" class="footnote-backlink" role="doc-backlink">[↩︎]</a></li>
<li id="fn6">The specification <d-cite key="3MF-core"/> is created by the 3MF Consortium. The first version of the specification was published in 2015. The specification is open-source and managed in a Git repository. The specification was not uploaded to GitHub until 2018 (Version 1.2) <d-cite key="3MF-core"/>. <a href="http://web.archive.org/web/20160320020131/https://3mf.io/wp-content/uploads/2015/04/3MFcoreSpec_1.0.1.pdf">Version 1.0 was initially uploaded to the 3MF Consortium’s website</a> but has since been removed.<a href="#fnref6" class="footnote-backlink" role="doc-backlink">[↩︎]</a></li>
<li id="fn7">Discontinued by AutoDesk in 2016. <a href="http://web.archive.org/web/20150430070500/http://www.123dapp.com/">Original Webpage</a>.<a href="#fnref7" class="footnote-backlink" role="doc-backlink">[↩︎]</a></li>
<li id="fn8">Initially proposed as “STL 2.0” by Hiller et.al. <d-cite key="hillerSTLProposalUniversal2009"/>. Since the initial proposal, it has been jointly specified by ISO &amp; ASTM <d-cite key="iso52915"/>.<a href="#fnref8" class="footnote-backlink" role="doc-backlink">[↩︎]</a></li>
</ol>



<div class="l-body-outset"><hr></div>

Overall, only 3% of objects do not have an associated STL file.<d-footnote>In total about 56,000 objects.</d-footnote>
The top three file formats of objects where no STL is uploaded are `.obj`, `.scad`, and `.dxf`.
Further, nine of the fifteen listed files are project files for specific programs.
Together these facts suggest that the most common use case is for a user to upload an STL file and their project file of the software they created the STL with.
Alternatively, the model is uploaded as an OBJ file, or in popular exchange file formats for Computer Aided Design (CAD) software (i.e. `.scad` and `.dxf`).


## Trend of Usage over Time

To get an overview of the change in usage we ploted the uploads per month of each file format.

As some file formats support multiple models in one file and others do not, we ignore duplicate suffixes on files for the same object that were uploaded on the same day.
This sanitization is required, as otherwise there might be biases towards the formats that do not support multiple models in one file, as a user would have to upload multiple files for a complex model with separated parts.
This reduces the variance in the repetition factor from [Table 1](#tab:file-format-occurrences).

As you can see in the graph below, `.obj`, `.step`, and `.f3d` all follow a near identical curve that shows rapid increases in usage.
`.3mf` shows fewer usage overall, but a rapid increase since its inital release.
`.sldprt`, `.fcstd`, `.dxf`, `.gcode`, and `.blend` show a more steady growth.
`.ipt` and `.amf` both fluctuate more than others and seem more or less stagnant.
`.skp`, `.123dx` are declining in usage.
In the case of `.123dx` this is expected, since AutoDesk discontinued the 123D program suite in 2016.

<div class="l-page">
  <canvas id="usageOverTime"></canvas>
</div>

<style>
.btn{border:none;display:inline-block;border:none;padding:3px 16px;vertical-align:middle;background-color:var(--global-code-bg-color);text-align:center;cursor:pointer;white-space:nowrap}
.btn:hover{box-shadow:0 4px 8px 0 rgba(0,0,0,0.2),0 6px 20px 0 rgba(0,0,0,0.19)}
</style>

<button type="button" id="yAxisButton" class="btn" style="width: calc(100% - 10em); margin-left: 5em; margin-top: 1em;">make X axis linear</button>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.0.1/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/moment@2.29.4/moment.min.js"></script>

<script>
  var chart;

  // Event Listener
  var button = document.querySelector('#yAxisButton');
  var buttonClick = button && button.addEventListener('click', function(event) {
    if (chart) {
      if (chart.options.scales.yAxes[0].type == 'logarithmic') {
        button.textContent="make X axis logarithmic"
        chart.options.scales.yAxes[0].type = 'linear'
      } else {
        button.textContent="make X axis linear"
        chart.options.scales.yAxes[0].type = 'logarithmic'
      }
      chart.update()
    }
  });

  fetch("/assets/data/2021-10-08-3d-printing-file-format-usage/parsed_data/format_uploads_per_month_per_object.json")
    .then((response) => response.json())
    .then(function(data) {
      const ctx = document.getElementById('usageOverTime');

      function map(name) {
        return Array.from(data.months, (entry, index) => {return {x:entry, y:data["data"][name][index]}})
      }

      color_map = [ "#1ba3c6", "#2cb5c0", "#30bcad", "#21B087", "#33a65c", "#57a337", "#a2b627", "#d5bb21", "#f8b620", "#f89217", "#f06719", "#e03426", "#f64971", "#fc719e", "#eb73b3", "#ce69be", "#a26dc2", "#7873c0", "#4f7cba" ]

      chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.months,
          datasets: [
            { label: ".stl", data: map(".stl"), borderColor: color_map[0]},
            { label: ".scad", data: map(".scad"), hidden: true, borderColor: color_map[1]},
            { label: ".obj", data: map(".obj"), borderColor: color_map[2]},
            { label: ".step/.stp", data: Array.from(data.months, (entry, index) => {return {x:entry, y:data["data"]['.step'][index] + data["data"]['.stp'][index]}}), hidden: true, borderColor: color_map[3]},
            { label: ".sldprt", data: map(".sldprt"), hidden: true, borderColor: color_map[4]},
            { label: ".skp", data: map(".skp"), hidden: true, borderColor: color_map[5]},
            { label: ".f3d", data: map(".f3d"), hidden: true, borderColor: color_map[6]},
            { label: ".fcstd", data: map(".fcstd"), hidden: true, borderColor: color_map[7]},
            { label: ".dxf", data: map(".dxf"), hidden: true, borderColor: color_map[8]},
            { label: ".gcode", data: map(".gcode"), hidden: true, borderColor: color_map[9]},
            { label: ".ipt", data: map(".ipt"), hidden: true, borderColor: color_map[10]},
            { label: ".3mf", data: map(".3mf"), borderColor: color_map[11]},
            { label: ".blend", data: map(".blend"), hidden: true, borderColor: color_map[12]},
            { label: ".123dx", data: map(".123dx"), hidden: true, borderColor: color_map[13]},
            { label: ".amf", data: map(".amf"), borderColor: color_map[14]},
          ]
        },
        options: {
          scales: {
            yAxes: [{
              scaleLabel: {
                display: true,
                labelString: 'Number of Uploads per File Format per Month',
              },
              type: 'logarithmic',
              position: 'left',
            }],
            xAxes: [{
              scaleLabel: {
                display: true,
                labelString: 'Time',
              },
              type: 'time',
            }]
          },
          elements: {
            point: {
              radius: 0,
            },
            line: {
              borderWidth: 2,
              fill: false,
              tension: 0,
            }
          },
        },
      });
    })
</script>


## How to Get the Data

### Option 1

Download the data we used (collected in June 2021):

- `/raw_data`
  - [`thingiverse.zip`](/assets/data/2021-10-08-3d-printing-file-format-usage/raw_data/thingiverse.zip) (5.8 GB)
  - [`myminifactory.zip`](/assets/data/2021-10-08-3d-printing-file-format-usage/raw_data/myminifactory.zip) (296 KB)

- `/parsed_data`
  - <a href="/assets/data/2021-10-08-3d-printing-file-format-usage/parsed_data/extracted_data.json" download><code>extracted_data.json</code></a> (228 MB)  
    The raw file information from both datasets.
    This is an array where each entry matches a single object in the database of either webpages.
    The entries are an array again that lists all file names uploaded for that entry.
    The single files are tuples of the file name and the upload time in UNIX format.
    `failed_opens` states how many source files failed to open (corrupted file).
    `nr_thingiverse_files` and `nr_myminifactory_files` state how many files where added from the respective database.
  - <a href="/assets/data/2021-10-08-3d-printing-file-format-usage/parsed_data/file_analysis_raw.json" download><code>file_analysis_raw.json</code></a> (6.7 MB)  
    - `suffix_raw` all suffixes counted.
    - `suffixes_unified` all suffixes converted to lower case and counted.
    - `combinations_of_filetypes` all suffixes that contain one of the types listed in [Table 1](#tab:file-format-occurrences) counted.
    - `object_w_type_file` number of objects that have an associated file with a suffix from [Table 1](#tab:file-format-occurrences).
  - <a href="/assets/data/2021-10-08-3d-printing-file-format-usage/parsed_data/file_analysis.json" download><code>file_analysis.json</code></a> (9.4 KB)  
    Statistics about the file types in [Table 1](#tab:file-format-occurrences).
  - <a href="/assets/data/2021-10-08-3d-printing-file-format-usage/parsed_data/format_uploads_per_day.json" download><code>format_uploads_per_day.json</code></a> (1.6 MB)  
    Maps the upload day of an object and counts them.
  - <a href="/assets/data/2021-10-08-3d-printing-file-format-usage/parsed_data/format_uploads_per_day_per_object.json" download><code>format_uploads_per_day_per_object.json</code></a> (1.5 MB)  
    Same as `format_uploads_per_day` but uploads of the same type are ignored on the same day and object.
  - <a href="/assets/data/2021-10-08-3d-printing-file-format-usage/parsed_data/format_uploads_per_month_per_object.json" download><code>format_uploads_per_month_per_object.json</code></a> (12 KB)  
    Data from `format_uploads_per_day_per_object` but ordered so it can be used in the webpage for the graph.
    Data is grouped by month and their type.
  - <a href="/assets/data/2021-10-08-3d-printing-file-format-usage/parsed_data/number_of_files_per_object.json" download><code>number_of_files_per_object.json</code></a> (2.8 KB)  
    Multiple statistics about the file types from [Table 1](#tab:file-format-occurrences).

- `/scripts`
  - [`analyze_data.py`](/assets/data/2021-10-08-3d-printing-file-format-usage/scripts/analyze_data.py) (11 KB)
  - [`extract_data.py`](/assets/data/2021-10-08-3d-printing-file-format-usage/scripts/extract_data.py) (2.3 KB)
  - [`get_data.py`](/assets/data/2021-10-08-3d-printing-file-format-usage/scripts/get_data.py) (2.6 KB)
  - [`plot_data.py`](/assets/data/2021-10-08-3d-printing-file-format-usage/scripts/plot_data.py) (1.5 KB)

### Option 2

Download the data yourself.

As of June 2021 this will produce roughly 40 GB of JSON data and make about 10 million requests.
The script creates a file for each available entry containing the JSON metadata.
This means there will be millions of files in a single folder.
I did it this way because it was the simplest, reasonably fast, method that works well with threading.
This will obviously be terribly slow with a slow disk.
I used an NVME SSD and had a total execution time of about 12 hours.

If you want to do something less stupid, go ahead and change the script ;)
For downloading the data once this was fine.

1. Get access tokens for `thingiverse.com` and `myminifactory.com`'s APIs.
   - `thingiverse.com`
     - [register an app](https://www.thingiverse.com/apps/create) here: `https://www.thingiverse.com/apps/create`
     - after the creation you get an token for the whole app
   - `myminifactory.com`
     - [register an app](https://www.myminifactory.com/settings/developer) here: `https://www.myminifactory.com/settings/developer`
     - the token shown after creation has not the required access right, you need a user-based token
     - go to: `https://auth.myminifactory.com/web/authorize?client_id=XXX&redirect_uri=YYY&response_type=token&state=RANDOM_STRING`
       where `client_id` should be the name of you app and `redirect_uri` the same redirect URI that was given for the registration.
       I used `ngrok` for the callback URI, but I'm not sure you'd actually need that.
     - You will be forwarded to an URL like: `YYY#access_token=TTT&expires_in=604800&state=RANDOM_STRING&token_type=Bearer`
     - The token `TTT` is the one we need.
2. Run the `get_data.py` script with these parameters:
   - The first value is the website you want to get the data from.
   - The second the access token.
   - The third and fourth are the minimal and maximal ID, both sites use IDs for their objects, the API script simply tries all ID between the given values.
     Typically between `1` and the highest value you can find under "newest" on the respective site.
3. We also recommend to ZIP the data after their processing so your computer is not slowed down by the number of files.
   (Also the extraction script uses the ZIP files.)
