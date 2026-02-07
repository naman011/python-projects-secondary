# URL Test Results Summary

## Overall Statistics

- **Total Companies**: 195
- **Working URLs**: 159 (81.5%)
- **Broken URLs**: 36 (18.5%)

## Broken URLs by Category

### 1. 404 Not Found (Need URL Updates)

These companies' career pages don't exist at the current URLs:

- **Cred**: `https://cred.club/careers` → Needs update
- **Quikr**: `https://www.quikr.com/careers` → Needs update
- **Rapido**: `https://www.rapido.bike/careers` → Needs update
- **Urban Company**: `https://www.urbancompany.com/careers` → Needs update
- **InfoEdge**: `https://www.infoedge.in/careers` → Needs update
- **Tech Mahindra**: `https://www.techmahindra.com/en-in/careers/` → Needs update
- **CRED_Club**: `https://cred.club/careers` → Duplicate of Cred, needs update
- **MPL**: `https://mpl.live/careers` → Needs update
- **Udaan_Lever**: `https://jobs.lever.co/udaan` → Needs update
- **Tata_1mg**: `https://www.1mg.com/careers` → Needs update
- **WebEngage**: `https://webengage.com/jobs/` → Needs update
- **Constructor**: `https://constructor.io/careers/` → Needs update
- **Arkency**: `https://arkency.com/careers` → Needs update
- **Deltek**: `https://www.deltek.com/en-us/about-us/careers` → Needs update
- **Affordmate**: `https://www.affordmate.com/careers` → Needs update
- **Funded.club**: `https://funded.club/careers` → Needs update
- **Goinstacare**: `https://goinstacare.com/careers` → Needs update

### 2. 403 Forbidden (Bot Protection - May Still Work with Browser)

These may work with browser fallback:

- **Meesho**: `https://careers.meesho.com/` → 403 (bot protection)
- **Infosys**: `https://www.infosys.com/careers.html` → 403 (bot protection)
- **Nykaa**: `https://www.nykaa.com/careers` → 403 (bot protection)
- **Intel**: `https://jobs.intel.com/en` → 403 (bot protection)
- **Bloomberg**: `https://www.bloomberg.com/company/careers/` → 403 (bot protection)
- **Cash App**: `https://cash.app/careers` → 403 (bot protection)
- **Faire**: `https://www.faire.com/careers` → 403 (bot protection)

### 3. Timeouts (May Work on Retry)

- **PolicyBazaar**: `https://www.policybazaar.com/careers/` → Timeout
- **FirstCry**: `https://www.firstcry.com/careers` → Timeout
- **VMware**: `https://careers.vmware.com/` → Timeout
- **Akamai**: `https://www.akamai.com/careers/` → Timeout (duplicate entry)
- **DealHub.io**: `https://dealhub.io/careers` → Timeout

### 4. Server Errors (502)

- **Udaan**: `https://careers.udaan.com/` → HTTP 502 (server error, may be temporary)
- **Bold**: `https://bold.co/careers` → HTTP 502 (server error, may be temporary)

### 5. Other Errors

- **Uber**: `https://www.uber.com/careers/list/` → HTTP 406 (Not Acceptable)
- **Confluent**: `https://careers.confluent.io/jobs` → HTTP 429 (Rate Limited - temporary)
- **Dunzo**: `https://www.dunzo.com/careers` → DNS error
- **Expert Thinking**: `https://expertthinking.com/careers` → DNS error

## Recommendations

### Immediate Fixes Needed

1. **Update 404 URLs**: Search for correct career pages for companies with 404 errors
2. **Remove Duplicates**: 
   - Remove `CRED_Club` (duplicate of `Cred`)
   - Remove `Akamai Technologies` (duplicate of `Akamai`)
3. **Fix DNS Errors**: Update URLs for Dunzo and Expert Thinking

### May Work with Browser Fallback

Companies with 403 errors may work when using the browser fallback feature (already enabled in config).

### Temporary Issues

- 502 errors (Udaan, Bold) may be temporary server issues
- 429 (Confluent) is rate limiting - will work on retry
- Timeouts may work on retry or with longer timeout

## Next Steps

1. Fix the 404 URLs by searching for correct career pages
2. Remove duplicate entries
3. Test again after fixes
4. For 403 errors, rely on browser fallback during actual scraping
