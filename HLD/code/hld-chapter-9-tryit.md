A teammate proposes storing user-uploaded videos as binary columns in the main database. Give three concrete reasons this hurts, and the standard alternative.

1. Database bloating increases the size and makes backups slower and expensive
2. indexes and queries become slower because the database is handling large binary data instead of just metadata
3. Limited scalability compared to specialized storage solutions

Standard alternative: Store videos in blob storage (e.g., S3, Azure Blob Storage) and keep only references in the database.



Explain why a CDN helps a user in Australia load a US-hosted image, in terms of both latency and bandwidth. What kind of content does it not help with, and why?

it helps because a CDN caches content in edge locations closer to the user, reducing latency by shortening the distance data must travel. It also reduces bandwidth usage on the origin server by serving cached content to multiple users.


Walk through the pre-signed URL upload flow. What's the specific benefit of the client uploading directly to blob storage instead of through your app servers?

The pre-signed URL upload flow works as follows:
1. The client requests a pre-signed URL from the application server.
2. The application server generates a pre-signed URL with specific permissions and an expiration time and sends it back to the client.
3. The client uses the pre-signed URL to upload the file directly to blob storage.
The specific benefit of the client uploading directly to blob storage instead of through your app servers is that it offloads the file transfer workload from the application servers, reducing server load and improving scalability. The direct upload also minimizes latency and allows for larger file uploads without hitting server limits.

You update your site's logo but users keep seeing the old one for hours. What CDN behavior causes this, and what are two ways to force the new version to appear?
The CDN caches the old version of the logo and serves it to users util it is expired or invalidated . Two ways to force the new version to appear:
1. Invalidate the cached version on the CDN, which forces it to fetch the new version
2. Change the URL of the logo (e.g., by adding a version query parameter or changing the file name), which causes the CDN to treat it as a new resource and fetch the updated version.

For each, say where it lives (database / blob storage / CDN) and why: a user's display name, their uploaded résumé PDF, your site's main stylesheet, a movie file, a movie's title and rating.
display name: database
résumé PDF: blob storage
main stylesheet: CDN
movie file: blob storage
movie title and rating: database

An interviewer asks you to "design X at scale." You sketch a queue and a cache. Why is "I'd use a managed service like SQS / a managed Redis" usually the stronger answer than "I'd run my own"? When would you defend running your own instead?
using a managed service like SQS or Redis is usually stronger because it offloads operational complexity, provides built-in scalability, reliability, and maintenance, and allows the team to focus on core application logic rather than infrastructure management. Managed services often come with SLAs and support that can be critical for production systems. You might defend running your own if you have very specific requirements that managed services cannot meet, such as custom configurations, compliance needs, or cost considerations at extreme scale.

using a managed service like SQS or Redis is stronger because it offloads operational complexity and provides build-in scalability , reliablity and maintenance and allowing teams to focus on core application logic . They come with SLAs and support producing critical production systems. You might defend running your own if you have very specific requirements that managed services cannot meet compliance , customization or cost cosniderations at exteme scale.

What's the difference between a region and an availability zone, and why do you spread database replicas across AZs rather than across regions for failover?

A region is a geographical area that has multiple data centers , while an az is a single data center in a region. spreading replicas across AZs is preferred because it provides low-latency failover within same refion , while spreading across regions can introduce higher latency and potential data transfer costs. AZs are designed to be isolated from failures in other AZs, providing a balance between redundancy and performance.
