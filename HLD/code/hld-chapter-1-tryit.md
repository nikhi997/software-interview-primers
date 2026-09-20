A photo-sharing app expects 500 million photo views per day and 5 million uploads per day. Compute reads/sec and writes/sec. What's the read:write ratio?

reads= 500 * 10^6 /day
reads =5000/sec
writes = 50/sec

reads:writes= 100:1

Each photo averages 2 MB. How much new storage per day? Per year?

storage/day = 110TB
/year = 3.65 PB


At what point (which of the four failure points above) does the single-box design first break for this photo app — and why is it a different failure point than for the URL shortener?

database outgrows one box

In one sentence each: name the cost we paid when we split the database onto its own box, and the benefit we got.

we will add the network hop so it will add some latency . we benefit from single point of failure and scaling independently .
