---
name: Platform Support Request
about: Want UMD to support a new website/platform?
title: '[PLATFORM] '
labels: platform-request, enhancement
assignees: ''
---

## Platform Support Request

### What Platform?

<!--
What website/service do you want UMD to support?
Please provide the main URL.
-->

**Platform Name:** 
**Website URL:** 

### What Content?

<!--
What type of content do you want to download from this platform?
Check all that apply:
-->

- [ ] Videos
- [ ] Audio/Music
- [ ] Playlists/Albums
- [ ] Live Streams
- [ ] Stories/Shorts
- [ ] Other: 

### Example URLs

<!--
Provide some example URLs of content you'd like to download.
(Public content only, please!)
-->

```
Example URL 1
Example URL 2
Example URL 3
```

---

## Platform Details

<!-- Fill out what you know -->

| Question | Answer |
|----------|--------|
| **Requires Login?** | <!-- Yes/No/Sometimes --> |
| **Has API?** | <!-- Yes/No/Unknown --> |
| **Age Restricted?** | <!-- Yes/No/Sometimes --> |
| **Region Locked?** | <!-- Yes/No/Sometimes --> |

### Is This Already Supported?

<!--
Have you tried downloading from this platform already?
Sometimes yt-dlp (which UMD uses) already supports it!

Try: umd "URL" --verbose
-->

- [ ] Yes, I tried and it didn't work
- [ ] Yes, I tried and it partially works (explain below)
- [ ] No, I haven't tried yet

**What happened when you tried?**
```
Paste any error messages here
```

---

## Additional Info

<!--
Anything else we should know?
- Is this platform popular?
- Are there similar platforms already supported?
- Any technical details you know about the site?
-->



---

## Important Notes

<!--
Before submitting, please consider:
-->

- [ ] This platform allows downloading content (check their ToS)
- [ ] This is a legitimate platform (not a piracy site)
- [ ] I understand this might take time to implement

---

**Note:** We prioritize platforms based on:
1. User demand (reactions on this issue)
2. Technical feasibility
3. Legal considerations
4. Maintainer availability

If yt-dlp already supports the platform, it might already work with UMD! Try it first with `--verbose` flag.
