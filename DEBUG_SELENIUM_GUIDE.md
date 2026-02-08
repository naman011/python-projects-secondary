# Debug Selenium Issues - Guide

## Problem
Selenium can't find form fields (`#phone`, `[name="phone"]`) on job pages, resulting in "No form fields found" errors.

## Quick Debug Command

```bash
# Debug a specific job URL (browser will open so you can see)
python3 debug_selenium.py "https://in.indeed.com/viewjob?jk=3e09234960611d78"

# Or run headless
python3 debug_selenium.py "https://in.indeed.com/viewjob?jk=3e09234960611d78" headless
```

## What the Script Does

1. **Loads the page** and shows current URL
2. **Checks for login requirements** (sign in, log in, etc.)
3. **Detects redirects** (if page redirected to external site)
4. **Finds all form elements** and lists their fields
5. **Finds all input elements** (even outside forms)
6. **Checks for iframes** (forms might be inside iframes)
7. **Takes a screenshot** for visual inspection
8. **Analyzes page content** for application keywords

## Common Issues Found

### Issue 1: Login Required
**Symptom**: Script finds "sign in" or "log in" keywords
**Solution**: Indeed requires login before showing application forms

### Issue 2: External Redirect
**Symptom**: Current URL differs from job URL
**Solution**: Job redirects to company's own application system (Greenhouse, Lever, etc.)

### Issue 3: Dynamic Loading
**Symptom**: No forms found initially
**Solution**: Forms load via JavaScript - need longer wait times or wait for specific elements

### Issue 4: Iframe Forms
**Symptom**: Forms found but inputs not accessible
**Solution**: Form is in an iframe - need to switch to iframe context

### Issue 5: No Forms at All
**Symptom**: No `<form>` tags, no inputs
**Solution**: Page might be a job listing page, not an application page. Need to click "Apply" button first.

## Next Steps After Debugging

1. **If login required**: Add login functionality or mark as "Needs Manual Check"
2. **If external redirect**: Detect redirect and mark as "Needs Manual Check" or handle specific ATS systems
3. **If dynamic loading**: Increase wait times or use explicit waits for form elements
4. **If iframe**: Switch to iframe context before finding fields
5. **If no forms**: Check if "Apply" button needs to be clicked first

## Example Output

The script will show:
- How many forms are found
- What fields are in each form
- Whether login is required
- If page redirected
- Screenshot location

Use this information to fix the Selenium selectors or add proper handling for each case.
