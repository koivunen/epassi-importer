## Overview
 
Dumps EPassi statistics to local postgrest database periodically

## Requirements

- EPassi credentials
- PostgREST
- Python 3.12+

## Installation

 1. Clone somewhere. Use `uv` for executing.
 2. Install DB: See [test.sql](test.sql)

## Database

See [test.sql](test.sql)

*site_diners_5m_buckets:*

|bucket_time|entry_count|siteid|
|-----------|-----------|------|
|2025-10-28 10:20:00.000|12|-1|
|2025-10-28 10:25:00.000|34|-1|
|2025-10-28 10:30:00.000|5|-1|


## Configuration

.env file

- USERNAME=epassiusername
- PASSWORD=epassipassword
- AUTH_BEARER=postgrest-secret

## Usage

```bash
uv run python main.py
```

For crontab to run every 4 minutes during core business hours:

```bash
CRON_TZ=Europe/Helsinki
19,23,27,31,35,39,43,47,51,55,59 10 * * 1-5 /opt/epassi/run_main.sh || true
3,7,11,15,19,23,27,31,35,39,43,47,51,55,59 11-12 * * 1-5 /opt/epassi/run_main.sh || true
3,7,11,15,19,23,27,31,35,39,43,47             13 * * 1-5 /opt/epassi/run_main.sh || true
```


## TODO / Notes

 - Tests: Add --dry-run and --mock
 - Add session reusing (do not continously login)
 - cleanup
 - better runner than crontab
 - dockerize
 - proper API (access)

## Development Status

Functional (2025-10-28) but unmaintained, for reference only.

## License

MIT

## Similar

 - https://github.com/Adafy/ApiFramework.Plugins.Epassi/blob/main/src/Adafy.ApiFramework.Plugins.Epassi/EpassiApiBase.cs#L21


## Acknowledgements

This research supporting software artifact was supported by Business Finland, under the Veturi program with the Dining Flow project (6547/31/2022). We acknowledge the [Flavoria® multidisciplinary research platform](https://flavoria.fi) and extend our gratitude towards everyone involved in its development, and to our colleagues at UTU NuFo for their continued support.