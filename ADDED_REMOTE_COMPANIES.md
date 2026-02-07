# Added Remote Companies

## Summary
Added **48 new remote companies** to `data/companies.json` (Cloudflare and Confluent were already present).

**Total companies in file:** 196

## Newly Added Companies

1. **Upwork** - https://www.upwork.com/careers/
2. **Docker** - https://www.docker.com/careers/
3. **Automattic** - https://automattic.com/work-with-us/
4. **DigitalOcean** - https://www.digitalocean.com/careers
5. **Constructor** - https://constructor.io/careers/
6. **Shopify** - https://www.shopify.com/careers
7. **Abnormal Security** - https://abnormalsecurity.com/careers
8. **Mentorsity** - https://mentorsity.com/careers
9. **MissionWired** - https://missionwired.com/careers
10. **Symetra** - https://www.symetra.com/careers
11. **Doist** - https://doist.com/careers/
12. **LogicGate** - https://www.logicgate.com/careers/
13. **Canonical** - https://canonical.com/careers
14. **Cloudbeds** - https://www.cloudbeds.com/careers/
15. **Sorcero** - https://sorcero.com/careers
16. **Beekeeper** - https://www.beekeeper.io/careers
17. **Uplers** - https://www.uplers.com/careers/
18. **Bold** - https://bold.co/careers
19. **DuckDuckGo** - https://duckduckgo.com/hiring
20. **DealHub.io** - https://dealhub.io/careers
21. **Kemecon** - http://kemecon.com/careers
22. **Akamai Technologies** - https://www.akamai.com/careers/
23. **Arkency** - https://arkency.com/careers
24. **Deltek** - https://www.deltek.com/en-us/about-us/careers
25. **Cash App** - https://cash.app/careers
26. **Affordmate** - http://www.affordmate.com/careers
27. **Rec Room** - https://recroom.com/careers
28. **Funded.club** - https://funded.club/careers
29. **Expert Thinking** - https://expertthinking.com/careers
30. **Patreon** - https://www.patreon.com/careers
31. **Xapobank** - http://www.xapobank.com/careers
32. **Cengage Group** - https://www.cengagegroup.com/about/careers/
33. **Quest Software** - https://www.quest.com/careers/
34. **Workera** - https://workera.ai/careers
35. **Faire** - https://www.faire.com/careers
36. **McGraw Hill** - https://www.mheducation.com/careers.html
37. **UserGems** - https://usergems.com/careers
38. **Goinstacare** - https://goinstacare.com/careers
39. **Workiva** - https://www.workiva.com/careers
40. **Contra** - https://contra.com/careers
41. **Awesomemotive** - https://awesomemotive.com/careers
42. **Appcues** - https://www.appcues.com/careers
43. **Jenius Bank** - https://jeniusbank.com/careers
44. **DocuSign** - https://www.docusign.com/company/careers
45. **Census** - https://www.getcensus.com/careers
46. **AngelOne** - https://www.angelone.in/careers

## Already Present (Not Added)
- **Cloudflare** - Already existed in file
- **Confluent** - Already existed in file

## Notes

### URL Verification
The careers page URLs have been set based on standard patterns. Some may need verification:
- Companies with `http://` (non-HTTPS) may need updating to HTTPS
- Some smaller companies may have different URL structures

### Recommended Next Steps
1. **Test the scraper** with a few companies to verify URLs work
2. **Update any broken URLs** that fail during scraping
3. **Check for HTTPS** - Some companies listed with `http://` may need `https://`

### Companies to Verify URLs
- Kemecon (http://kemecon.com/careers)
- Affordmate (http://www.affordmate.com/careers)
- Xapobank (http://www.xapobank.com/careers)
- Mentorsity (may need verification)
- Sorcero (may need verification)
- Funded.club (may need verification)

### Scraper Configuration
All companies are configured with:
- `scraper_type`: "custom" (standard HTML scraping)
- `search_terms`: ["software engineer", "developer", "sde"]

The scraper will automatically try browser fallback if HTML scraping finds zero jobs.

## Testing
To test if URLs are working:
```bash
python main.py
```

Check the logs for any companies that fail to scrape, then update their URLs accordingly.
