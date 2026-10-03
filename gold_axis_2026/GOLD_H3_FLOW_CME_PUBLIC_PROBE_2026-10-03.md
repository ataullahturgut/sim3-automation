# FLOW-H3 CME / CONTINUOUS SOURCE PROBE — 2026-10-03

Purpose: test official CME public paths first, then separately test continuous-futures sources that expose both Volume and Open Interest.

## CME public daily_volume XLSX

| Date | HTTP | Bytes | OI text hits | Gold rows |
|---|---:|---:|---:|---:|
| 20220103 | 403 | 602 | 0 | 0 |
| 20240102 | 403 | 602 | 0 | 0 |
| 20250930 | 403 | 602 | 0 | 0 |
| 20260930 | 403 | 602 | 0 | 0 |

## CME Gold product JSON endpoint

| Date | Flag | HTTP | Bytes | monthData_n | totals present |
|---|---|---:|---:|---:|---|
| 20220103 | F | 403 | 602 | None | False |
| 20220103 | P | 403 | 602 | None | False |
| 20240102 | F | 403 | 602 | None | False |
| 20240102 | P | 403 | 602 | None | False |
| 20250930 | F | 403 | 602 | None | False |
| 20250930 | P | 403 | 602 | None | False |
| 20260930 | F | 403 | 602 | None | False |
| 20260930 | P | 403 | 602 | None | False |

## Continuous-futures alternative access probe

| Provider | Dataset | HTTP | Rows | Volume col | OI col |
|---|---|---:|---:|---|---|
| NASDAQ_DATA_LINK | CHRIS/CME_GC1 | 403 | None | None | None |
| QUANDL_LEGACY | CHRIS/CME_GC1 | 403 | None | None | None |
| NASDAQ_DATA_LINK | CHRIS/CME_GC2 | 403 | None | None | None |
| QUANDL_LEGACY | CHRIS/CME_GC2 | 403 | None | None | None |
| NASDAQ_DATA_LINK | CHRIS/CME_GC3 | 403 | None | None | None |
| QUANDL_LEGACY | CHRIS/CME_GC3 | 403 | None | None | None |

### Alternative response heads

#### NASDAQ_DATA_LINK CHRIS/CME_GC1
- HTTP 403, bytes 882
- head: <html style="height:100%"><head><META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW"><meta name="format-detection" content="telephone=no"><meta name="viewport" content="initial-scale=1.0"><meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"><script type="text/javascript" src="/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"></script></head><body style="margin:0px;height:100%"><iframe id="main-iframe" src="/_Incapsula_Resource?CWUDNSAI=23&xinfo=45-2870542-0%200NNN%20RT%281791043877189%2039%29%20q%280%20-1%20-1%201%29%20r%280%20-1%29%20B15%2811%2c3946258%2c0%29%20U18&incident_id=944000050028472903-14640431177400685&edet=15&cinfo=0b000000&rpinfo=0&cip=20.186.239.243&mth=GET" frameborder=0 width="100%" height="100%" marginheight="0px" marginwidth="0px">Request unsuccessful. 

#### QUANDL_LEGACY CHRIS/CME_GC1
- HTTP 403, bytes 885
- head: <html style="height:100%"><head><META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW"><meta name="format-detection" content="telephone=no"><meta name="viewport" content="initial-scale=1.0"><meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"><script type="text/javascript" src="/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"></script></head><body style="margin:0px;height:100%"><iframe id="main-iframe" src="/_Incapsula_Resource?CWUDNSAI=23&xinfo=14-45794816-0%200NNN%20RT%281791043877331%2041%29%20q%280%20-1%20-1%203%29%20r%281%20-1%29%20B15%2811%2c3946292%2c0%29%20U18&incident_id=679000220185235423-280890436001138062&edet=15&cinfo=0b000000&rpinfo=0&cip=20.186.239.243&mth=GET" frameborder=0 width="100%" height="100%" marginheight="0px" marginwidth="0px">Request unsuccessful

#### NASDAQ_DATA_LINK CHRIS/CME_GC2
- HTTP 403, bytes 881
- head: <html style="height:100%"><head><META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW"><meta name="format-detection" content="telephone=no"><meta name="viewport" content="initial-scale=1.0"><meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"><script type="text/javascript" src="/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"></script></head><body style="margin:0px;height:100%"><iframe id="main-iframe" src="/_Incapsula_Resource?CWUDNSAI=23&xinfo=39-1128093-0%200NNN%20RT%281791043877446%2027%29%20q%280%20-1%20-1%20-1%29%20r%280%20-1%29%20B15%2811%2c3946258%2c0%29%20U18&incident_id=944000050028472903-5681430045655399&edet=15&cinfo=0b000000&rpinfo=0&cip=20.186.239.243&mth=GET" frameborder=0 width="100%" height="100%" marginheight="0px" marginwidth="0px">Request unsuccessful. 

#### QUANDL_LEGACY CHRIS/CME_GC2
- HTTP 403, bytes 883
- head: <html style="height:100%"><head><META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW"><meta name="format-detection" content="telephone=no"><meta name="viewport" content="initial-scale=1.0"><meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"><script type="text/javascript" src="/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"></script></head><body style="margin:0px;height:100%"><iframe id="main-iframe" src="/_Incapsula_Resource?CWUDNSAI=23&xinfo=41-10895472-0%200NNN%20RT%281791043877539%2032%29%20q%280%20-1%20-1%202%29%20r%280%20-1%29%20B15%2811%2c3946292%2c0%29%20U18&incident_id=915000040117318053-58428464571810089&edet=15&cinfo=0b000000&rpinfo=0&cip=20.186.239.243&mth=GET" frameborder=0 width="100%" height="100%" marginheight="0px" marginwidth="0px">Request unsuccessful.

#### NASDAQ_DATA_LINK CHRIS/CME_GC3
- HTTP 403, bytes 888
- head: <html style="height:100%"><head><META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW"><meta name="format-detection" content="telephone=no"><meta name="viewport" content="initial-scale=1.0"><meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"><script type="text/javascript" src="/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"></script></head><body style="margin:0px;height:100%"><iframe id="main-iframe" src="/_Incapsula_Resource?CWUDNSAI=23&xinfo=49-181547370-0%200NNN%20RT%281791043877610%2022%29%20q%280%20-1%20-1%202%29%20r%280%20-1%29%20B15%2811%2c3946258%2c0%29%20U18&incident_id=408000050950435209-1157019607808606577&edet=15&cinfo=0b000000&rpinfo=0&cip=20.186.239.243&mth=GET" frameborder=0 width="100%" height="100%" marginheight="0px" marginwidth="0px">Request unsuccessf

#### QUANDL_LEGACY CHRIS/CME_GC3
- HTTP 403, bytes 883
- head: <html style="height:100%"><head><META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW"><meta name="format-detection" content="telephone=no"><meta name="viewport" content="initial-scale=1.0"><meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"><script type="text/javascript" src="/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"></script></head><body style="margin:0px;height:100%"><iframe id="main-iframe" src="/_Incapsula_Resource?CWUDNSAI=23&xinfo=9-15971258-0%200NNN%20RT%281791043877676%2026%29%20q%280%20-1%20-1%20-1%29%20r%280%20-1%29%20B15%2811%2c3946292%2c0%29%20U18&incident_id=679000220185235423-99475028917552521&edet=15&cinfo=0b000000&rpinfo=0&cip=20.186.239.243&mth=GET" frameborder=0 width="100%" height="100%" marginheight="0px" marginwidth="0px">Request unsuccessful.

## Governance interpretation

- Direct CME automated public access returning 403 is not bypassed.
- Nasdaq Data Link / Quandl continuous contracts are not silently treated as the official CME aggregate-product VOI source.
- If an alternative is accessible and includes Volume plus Open Interest, it can only proceed under a separately named FLOW successor after source-semantics and roll/contract mapping are frozen.
- No outcome-based model fitting or threshold selection is performed in this probe.
