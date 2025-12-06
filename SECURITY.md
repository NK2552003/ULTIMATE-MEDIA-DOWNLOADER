# Security Policy

## Hey, Thanks for Helping Keep UMD Secure!

Finding security issues is important work, and I appreciate you taking the time to report vulnerabilities responsibly. This document explains how to report security issues and what to expect.

---

## Supported Versions

I actively maintain and provide security updates for the following versions:

| Version | Supported | Notes |
|---------|-----------|-------|
| 2.x.x   | Yes    | Current major version - full support |
| 1.x.x   | Limited | Critical security fixes only |
| < 1.0   | No     | Please upgrade to a supported version |

**Pro tip:** Always use the latest version! Run `umd --version` to check yours.

---

## Reporting a Vulnerability

### Found a Bug? Here's What to Do:

**IMPORTANT: Please DO NOT open a public GitHub issue for security vulnerabilities!**

Instead, follow these steps:

### Step 1: Gather Information

Before reporting, collect as much info as you can:

- What version of UMD are you using? (`umd --version`)
- What operating system are you on?
- What's the vulnerability? (Be specific)
- How can someone reproduce it?
- What's the potential impact?

### Step 2: Report Privately

**Option A: GitHub Security Advisories (Preferred)**
1. Go to the [Security tab](https://github.com/NK2552003/ULTIMATE-MEDIA-DOWNLOADER/security)
2. Click "Report a vulnerability"
3. Fill out the form with all the details

**Option B: Direct Contact**
- Create a private security report via GitHub
- Or reach out to [@NK2552003](https://github.com/NK2552003) directly

### Step 3: Wait for Response

I'll acknowledge your report within **48-72 hours** (usually faster). Please be patient—I'm a student/developer with other commitments too!

---

## What to Expect

Here's the typical timeline:

| Stage | Timeframe | What Happens |
|-------|-----------|--------------|
| **Acknowledgment** | 48-72 hours | I confirm I received your report |
| **Initial Assessment** | 1 week | I evaluate the severity and validity |
| **Fix Development** | 1-4 weeks | I work on a patch (depends on complexity) |
| **Release** | ASAP after fix | Security update is published |
| **Public Disclosure** | After fix | I credit you (if you want) in the changelog |

---

## What Counts as a Security Issue?

### Yes, Report These:

- **Remote Code Execution (RCE)** - If someone can run arbitrary code
- **Path Traversal** - Accessing files outside intended directories
- **Credential Exposure** - Leaking API keys, passwords, tokens
- **Injection Vulnerabilities** - Command injection, etc.
- **Privilege Escalation** - Gaining unauthorized access
- **Dependency Vulnerabilities** - Issues in libraries I use
- **Data Exposure** - Unintended data leaks

### Not Security Issues (Open Regular Issues Instead):

- Bugs that don't have security implications
- Feature requests
- Performance issues
- UI/UX problems
- Documentation errors
- Platform-specific quirks

---

## Security Best Practices for Users

While using UMD, keep yourself safe:

### Do's

- **Keep UMD updated** - I patch vulnerabilities in new releases
- **Download from official sources** - Only use the official GitHub repo
- **Use secure networks** - Avoid downloading on public WiFi without VPN
- **Verify checksums** - If I provide them for releases
- **Review batch files** - Before running batch downloads from unknown sources

### Don'ts

- **Don't run as root/admin** - Unless absolutely necessary
- **Don't use unofficial forks** - They might contain malicious code
- **Don't share your config** - It might contain sensitive paths or preferences
- **Don't ignore update warnings** - They might be security-related

---

## Recognition

We believe in giving credit where it's due!

If you report a valid security vulnerability, I'll:

- Thank you publicly (with your permission)
- Credit you in the release notes/changelog
- Add you to the contributors list

I don't have a formal bug bounty program (this is an open-source project, not a corporation), but I genuinely appreciate your help keeping UMD safe for everyone.

---

## My Security Commitments

I promise to:

1. **Respond promptly** to security reports
2. **Keep you informed** about the status of your report
3. **Fix valid issues** as quickly as possible
4. **Credit reporters** who want to be acknowledged
5. **Not take legal action** against good-faith security researchers
6. **Be transparent** about security issues (after they're fixed)

---

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Common security risks
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Python Security](https://python-security.readthedocs.io/)

---

## Questions?

Not sure if something is a security issue? Err on the side of caution and report it privately anyway. I'd rather have false alarms than missed vulnerabilities!

Thanks for helping keep Ultimate Media Downloader safe!

---

*Last updated: December 2024*
