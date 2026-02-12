# CHANGELOG

<!-- version list -->

## v1.12.4 (2026-02-12)


## v1.12.3 (2026-02-12)

### Bug Fixes

- Fix dashboard not loading when no baby selected on first visit
  ([`cd49fd7`](https://github.com/eburairu/baby-app/commit/cd49fd7fc4f02f7ec82bc69b7b8afe70965104e3))


## v1.12.2 (2026-02-12)


## v1.12.1 (2026-02-12)

### Bug Fixes

- Complete Phase 9 - Convert all routers to JSON-only APIs
  ([`8dabbb2`](https://github.com/eburairu/baby-app/commit/8dabbb21445e22a4939f891dc2ea2861d27de9a7))


## v1.12.0 (2026-02-12)

### Features

- Complete htmx to Next.js migration (Phase 9 & 10)
  ([`b387599`](https://github.com/eburairu/baby-app/commit/b3875994c081c7a15dfce442d8895eab51a5dbdf))


## v1.11.0 (2026-02-12)

### Features

- Implement initial application landing page with login/register links and remove unused Python
  version configuration files.
  ([`c7b56a3`](https://github.com/eburairu/baby-app/commit/c7b56a30d3089401bf5c02d05755c027cc584f46))


## v1.10.0 (2026-02-12)

### Features

- Next.jsフロントエンドを実装し、認証機能とマルチステージDockerビルドに統合。
  ([`8967fb4`](https://github.com/eburairu/baby-app/commit/8967fb44845d07ed674943cc2e7a7c6e9139b217))


## v1.9.1 (2026-02-12)

### Bug Fixes

- Correct UserSession import path in permission error handler
  ([`6c1f621`](https://github.com/eburairu/baby-app/commit/6c1f62102bdccc88b9c6d7af17cda5565b19bb99))


## v1.9.0 (2026-02-12)

### Features

- Add global baby selector and improve permission error handling
  ([`f467fb4`](https://github.com/eburairu/baby-app/commit/f467fb44e76a7f52c1d157a35c759a932fd48717))


## v1.8.3 (2026-02-12)

### Bug Fixes

- Add missing GET /sleeps/new endpoint and improve error handling
  ([`b0cd3ff`](https://github.com/eburairu/baby-app/commit/b0cd3ff9272d3a86df0bed1a14e7eb713a2d317f))


## v1.8.2 (2026-02-12)

### Performance Improvements

- Optimize database queries and add performance indexes
  ([`53c9747`](https://github.com/eburairu/baby-app/commit/53c9747427d4e307d150e5cdf9f2ab330de32ff4))


## v1.8.1 (2026-02-12)

### Bug Fixes

- Correctly handle underscore in permission keys during update
  ([`9977e34`](https://github.com/eburairu/baby-app/commit/9977e3436ad90067defada137720815ef7a63001))

### Testing

- Add unit tests for statistics and contraction services
  ([`e024169`](https://github.com/eburairu/baby-app/commit/e0241691d76775081f24131f2b12f50d0584e9a1))


## v1.8.0 (2026-02-12)

### Features

- Implement granular baby visibility control in dashboard and settings
  ([`99b3fd0`](https://github.com/eburairu/baby-app/commit/99b3fd0dcb1c319b7f76c004de5fe8e50f5aa560))

### Testing

- Expand test suite for RBAC and dependency logic to prevent regressions
  ([`347fa12`](https://github.com/eburairu/baby-app/commit/347fa1287dd1a395c024eb5dcfdd7c02cb0abdc9))


## v1.7.1 (2026-02-12)

### Bug Fixes

- Add missing user dependency to get_current_baby
  ([`9188d2a`](https://github.com/eburairu/baby-app/commit/9188d2a3cca24a15c88768a2708b1a56a853bd52))


## v1.7.0 (2026-02-12)

### Features

- Implement RBAC for baby information and record access control
  ([`4ef6aa9`](https://github.com/eburairu/baby-app/commit/4ef6aa964a515adf6a18325acaa2ceae8e9ffda2))


## v1.6.0 (2026-02-12)

### Bug Fixes

- **growth**: Correct Jinja2 min filter usage in growth chart template to prevent Internal Server
  Error
  ([`2059d51`](https://github.com/eburairu/baby-app/commit/2059d518e16df22d9143f97e026451d383b499f8))

### Features

- Display selected baby name badge on all main pages
  ([`cfc4461`](https://github.com/eburairu/baby-app/commit/cfc44617ca1924f3ef17441dcc5aa1f3caf725ad))


## v1.5.5 (2026-02-12)

### Bug Fixes

- Set selected_baby_id cookie in all router responses to persist baby selection
  ([`f407891`](https://github.com/eburairu/baby-app/commit/f407891628acaa8bf7cc80ab4024e7f996f6c9bd))


## v1.5.4 (2026-02-12)

### Bug Fixes

- Centralize Jinja2Templates and add now() to globals to fix schedule creation error
  ([`9e26e01`](https://github.com/eburairu/baby-app/commit/9e26e01175afe074466d3a6cfd77f7eaf32b968d))


## v1.5.3 (2026-02-12)

### Bug Fixes

- Add cookie support to get_current_baby for consistent baby selection across all pages
  ([`dc98c16`](https://github.com/eburairu/baby-app/commit/dc98c16f7f0d25f68dab2a2b7e1ea82e1dcc3d80))


## v1.5.2 (2026-02-12)

### Bug Fixes

- Resolve baby_id selection issue for multi-baby families
  ([`57bcdf8`](https://github.com/eburairu/baby-app/commit/57bcdf834047c1e799ac999a0f203ef279a14d65))

### Build System

- Add Docker support for development environment
  ([`4b4242c`](https://github.com/eburairu/baby-app/commit/4b4242c484c2afd55262ea7654c5d2c1b693c822))


## v1.5.1 (2026-02-12)

### Bug Fixes

- Provide default value for SYSTEM_INVITE_CODE to prevent build failure
  ([`bedb23b`](https://github.com/eburairu/baby-app/commit/bedb23baae1a39436b3e8e2f0de9e29e8805c0b5))


## v1.5.0 (2026-02-12)

### Documentation

- Update setup instructions and environment configuration
  ([`e055f6e`](https://github.com/eburairu/baby-app/commit/e055f6ee4777e106a6a33cd3908ac5f05f15704e))

### Features

- Add editing functionality to diaper, sleep, schedule, and contraction records
  ([`664339a`](https://github.com/eburairu/baby-app/commit/664339ac9b4078d36f970ad99ddb80a8a72ea09b))

- Change timezone from UTC to Asia/Tokyo
  ([`3844f2b`](https://github.com/eburairu/baby-app/commit/3844f2b4eac057e033b73566064e128ef9530f0c))


## v1.4.1 (2026-02-12)

### Bug Fixes

- Refine loading overlay logic to prevent unwanted spinners during periodic updates
  ([`c3a6055`](https://github.com/eburairu/baby-app/commit/c3a605591b225c0ca44af8fb7dc39eccb6e50ce8))


## v1.4.0 (2026-02-12)


## v1.3.1 (2026-02-11)


## v1.3.0 (2026-02-11)

### Features

- Add baby-themed loading overlay
  ([`79a48ca`](https://github.com/eburairu/baby-app/commit/79a48cac9abafac1670ebb1d5883abc55757ff6d))


## v1.2.0 (2026-02-11)


## v1.1.1 (2026-02-11)

### Bug Fixes

- Remove 'unimplemented link' text from dashboard
  ([`b9078c9`](https://github.com/eburairu/baby-app/commit/b9078c90ccf1f9e45bf74809f05453ddec20974a))


## v1.1.0 (2026-02-11)

### Features

- Implement 'Born' button and modal for status transition
  ([`deda0e8`](https://github.com/eburairu/baby-app/commit/deda0e895f692ef998757ca1e1857169b0c2f11f))


## v1.0.1 (2026-02-11)


## v1.0.0 (2026-02-11)

- Initial Release
