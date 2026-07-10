# CareerAgent Collector error codes

Stable error codes allow the Web UI, future desktop client, task queue, alerts, and tests to react to failures without parsing raw exception messages.

| Error code | Stage | Retryable | Meaning | Recommended action |
|---|---|---:|---|---|
| `INPUT_EMPTY` | input validation | No | No URL was provided | Paste a complete creator-profile URL |
| `INVALID_URL_SCHEME` | input validation | No | URL has no HTTP/HTTPS scheme | Copy the complete browser or share URL |
| `UNSUPPORTED_DOMAIN` | input validation | No | Domain is not supported | Use a supported Douyin URL |
| `NOT_PROFILE_URL` | URL parsing | No | A work URL or unrecognized URL was supplied | Open the creator profile and copy its URL |
| `SHORT_LINK_RESOLVE_FAILED` | URL parsing | Yes | Share-link redirect could not be resolved | Check the network or use the full profile URL |
| `NETWORK_TIMEOUT` | network | Yes | Upstream request timed out | Retry after checking the connection |
| `NETWORK_UNAVAILABLE` | network | Yes | DNS, proxy, firewall, or connection failure | Check network and proxy settings |
| `RATE_LIMITED` | fast API | Yes | Request frequency was limited | Wait and reduce collection frequency |
| `LOGIN_REQUIRED` | session | Yes | Login state is absent or expired | Use “重新登录抖音” |
| `SESSION_PROFILE_LOCKED` | browser startup | Yes | Persistent browser profile is in use | Close remaining Chromium processes |
| `HUMAN_VERIFICATION_REQUIRED` | browser fallback | Yes | Human verification is required | Complete verification manually |
| `RISK_CONTROL` | upstream | Yes | Temporary platform risk control | Wait, reduce frequency, or log in again |
| `ACCOUNT_NOT_FOUND` | profile fetch | No | Account does not exist or is unavailable | Verify the profile manually |
| `ACCOUNT_PRIVATE` | profile fetch | No | Content is private or inaccessible | Use an authorized account |
| `NO_PUBLIC_CONTENT` | content fetch | No | No public work is available | Confirm the profile has public content |
| `FILTER_NO_MATCH` | filtering | No | Selected content type has no result | Select “全部作品” or another type |
| `FAST_API_UNAVAILABLE` | fast API | Yes | Fast collection path is unavailable | Browser fallback is attempted automatically |
| `BROWSER_NOT_INSTALLED` | browser startup | Yes | Playwright Chromium is missing | Run the start script again |
| `BROWSER_LAUNCH_FAILED` | browser startup | Yes | Chromium could not start | Close residual processes and retry |
| `PAGE_LOAD_TIMEOUT` | browser fallback | Yes | Creator page did not load in time | Check the network and retry |
| `UPSTREAM_FORMAT_CHANGED` | normalization | Yes | Platform response structure changed | Export diagnostics and update the Provider |
| `DATABASE_LOCKED` | persistence | Yes | SQLite is locked by another process | Keep only one running instance |
| `DATABASE_ERROR` | persistence | Yes | Database read/write failed | Check database and disk state |
| `DISK_FULL` | persistence | Yes | Insufficient disk space | Free disk space and restart |
| `PERMISSION_DENIED` | persistence | No | Runtime directory is not writable | Move the project to a writable directory |
| `INTERNAL_ERROR` | internal | Yes | Unclassified internal error | Save run ID and export a diagnostic package |

Raw technical detail is for diagnosis only. Application logic should depend on the stable error code and retryability fields.
