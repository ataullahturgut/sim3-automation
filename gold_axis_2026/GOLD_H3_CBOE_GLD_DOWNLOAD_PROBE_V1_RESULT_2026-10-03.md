# CBOE GLD HISTORICAL OPTIONS DOWNLOAD PAYLOAD PROBE

## volume_all
- HTTP: 200
- final URL: https://www.cboe.com/us/options/market_statistics/historical_data/download/class/?symbolType=underlying&symbol=GLD&startDate=2023-01-03&endDate=2023-01-10&reportType=volume&volumeType=sum&volumeAggType=daily&exchanges=CBOE&exchanges=BATS&exchanges=C2&exchanges=EDGX
- content-type: text/csv
- content-disposition: attachment; filename="daily_volume_GLD_2023-01-03_2023-01-10.csv"
- bytes: 700
- redirects: []

### Parsed first rows

- Trade Date | Underlying | Product Type | Exchange | Volume
- 2023/01/03 | GLD | S | BATS | 12417
- 2023/01/03 | GLD | S | C2 | 16142
- 2023/01/03 | GLD | S | CBOE | 13099
- 2023/01/03 | GLD | S | EDGX | 5100
- 2023/01/04 | GLD | S | BATS | 15740
- 2023/01/04 | GLD | S | C2 | 22248
- 2023/01/04 | GLD | S | CBOE | 15804
- 2023/01/04 | GLD | S | EDGX | 4667
- 2023/01/05 | GLD | S | BATS | 10397
- 2023/01/05 | GLD | S | C2 | 9878
- 2023/01/05 | GLD | S | CBOE | 9777
- 2023/01/05 | GLD | S | EDGX | 4138
- 2023/01/06 | GLD | S | BATS | 13249
- 2023/01/06 | GLD | S | C2 | 15404
- 2023/01/06 | GLD | S | CBOE | 24873
- 2023/01/06 | GLD | S | EDGX | 6297
- 2023/01/09 | GLD | S | BATS | 7858
- 2023/01/09 | GLD | S | C2 | 12173
- 2023/01/09 | GLD | S | CBOE | 14692
- 2023/01/09 | GLD | S | EDGX | 7878
- 2023/01/10 | GLD | S | BATS | 5191
- 2023/01/10 | GLD | S | C2 | 6379
- 2023/01/10 | GLD | S | CBOE | 11073
- 2023/01/10 | GLD | S | EDGX | 5181

### Text head

Trade Date,Underlying,Product Type,Exchange,Volume
2023/01/03,GLD,S,BATS,12417
2023/01/03,GLD,S,C2,16142
2023/01/03,GLD,S,CBOE,13099
2023/01/03,GLD,S,EDGX,5100
2023/01/04,GLD,S,BATS,15740
2023/01/04,GLD,S,C2,22248
2023/01/04,GLD,S,CBOE,15804
2023/01/04,GLD,S,EDGX,4667
2023/01/05,GLD,S,BATS,10397
2023/01/05,GLD,S,C2,9878
2023/01/05,GLD,S,CBOE,9777
2023/01/05,GLD,S,EDGX,4138
2023/01/06,GLD,S,BATS,13249
2023/01/06,GLD,S,C2,15404
2023/01/06,GLD,S,CBOE,24873
2023/01/06,GLD,S,EDGX,6297
2023/01/09,GLD,S,BATS,7858
2023/01/09,GLD,S,C2,12173
2023/01/09,GLD,S,CBOE,14692
2023/01/09,GLD,S,EDGX,7878
2023/01/10,GLD,S,BATS,5191
2023/01/10,GLD,S,C2,6379
2023/01/10,GLD,S,CBOE,11073
2023/01/10,GLD,S,EDGX,5181


## volume_cboe
- HTTP: 200
- final URL: https://www.cboe.com/us/options/market_statistics/historical_data/download/class/?symbolType=underlying&symbol=GLD&startDate=2023-01-03&endDate=2023-01-10&reportType=volume&volumeType=sum&volumeAggType=daily&exchanges=CBOE
- content-type: text/csv
- content-disposition: attachment; filename="daily_volume_GLD_2023-01-03_2023-01-10.csv"
- bytes: 218
- redirects: []

### Parsed first rows

- Trade Date | Underlying | Product Type | Exchange | Volume
- 2023/01/03 | GLD | S | CBOE | 13099
- 2023/01/04 | GLD | S | CBOE | 15804
- 2023/01/05 | GLD | S | CBOE | 9777
- 2023/01/06 | GLD | S | CBOE | 24873
- 2023/01/09 | GLD | S | CBOE | 14692
- 2023/01/10 | GLD | S | CBOE | 11073

### Text head

Trade Date,Underlying,Product Type,Exchange,Volume
2023/01/03,GLD,S,CBOE,13099
2023/01/04,GLD,S,CBOE,15804
2023/01/05,GLD,S,CBOE,9777
2023/01/06,GLD,S,CBOE,24873
2023/01/09,GLD,S,CBOE,14692
2023/01/10,GLD,S,CBOE,11073


## oi_underlying
- HTTP: 404
- final URL: https://www.cboe.com/us/options/market_statistics/historical_data/download/class/?symbolType=underlying&symbol=GLD&startDate=2023-01-03&endDate=2023-01-10&reportType=oi&volumeType=sum&volumeAggType=daily
- content-type: text/html; charset=utf-8
- content-disposition: None
- bytes: 608537
- redirects: []

### Parsed first rows

- <!DOCTYPE html>
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- <html lang="en-us">
- <head>
-     
-            
- 
- 
- 
- 
- 
-     <script src="https://cdn.cookielaw.org/scripttemplates/otSDKStub.js"  type="text/javascript" charset="UTF-8" data-domain-script="019682b2-f8a4-757a-b22a-a5dc76f8622e" ></script>
-     <script type="text/javascript">
-         function OptanonWrapper() { }
-     </script>
- 

### Text head

<!DOCTYPE html>










<html lang="en-us">
<head>
    
           





    <script src="https://cdn.cookielaw.org/scripttemplates/otSDKStub.js"  type="text/javascript" charset="UTF-8" data-domain-script="019682b2-f8a4-757a-b22a-a5dc76f8622e" ></script>
    <script type="text/javascript">
        function OptanonWrapper() { }
    </script>

    

    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">

    <title>404 Page Not Found</title>

    <meta name="description" content="">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    

    
        
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag() {
        dataLayer.push(arguments);
    }
    gtag("consent", "default", {
        ad_storage: "denied",
        ad_user_data: "denied", 
        ad_personalization: "denied",
        analytics_storage: "denied",
        functionality_storage: "denied",
        personalization_storage: "denied",
        security_storage: "granted",
        wait_for_update: 2000,
    });
    gtag("set", "ads_data_redaction", true);
    gtag("set", "url_passthrough", true);
</script>

        
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-5D4ZVF');</script>
<!-- End Google Tag Manager -->

    

    
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180">
    <link rel="icon" href="/favicon-32x32.png" sizes="32x32">
    <link rel="icon" href="/favicon-16x16.png" sizes="16x16">
    <link rel="manifest" href="/manifest.json">
    <link rel="mask-icon" href="/safari-pinned-tab.svg" color="#3ab449">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=Montserrat:ital,wght@0,400..900;1,400..900&family=Open+Sans:ital,wght@0,300..800;1,300..800&family=Hanken+Grotesk:wght@100..900&family=Ubuntu+Mono:wght@400;700&family=Noto+Sans:ital,wght@0,100..900;1,100..900&family=Noto+Sans+TC:wght@100..900&family=Noto+Sans+SC:wght@100..900&family=Noto+Sans+KR:wght@100..900&family=Noto+Sans+JP:wght@100..900&family=Source+Sans+Pro:wght@400;500;700;800&display=swap" rel="stylesheet">

    <meta name="theme-color" content="#ffffff">

    

    <link rel="stylesheet" href="/_cache/css/19419dc9582858f82e5e2a206f394ee8.css" />
<link rel="stylesheet" href="/_cache/css/6fb805654732c9e735a1aa002561591d.css" />
<link rel="stylesheet" href="/_cache/css/2c108772f0b7f3c0e165f1c7627c4ff6.css" />
<link rel="stylesheet" href="/_cache/css/ace0f44c0ea16e491efb5316f21c95bd.css" />

    <style>
        .font-inter .site--main *:not(th, th *, td, td *, .hero *, .link-group *) {
          font-family: var(--font-family-primary);
        }
    </style>

    
    

    

    <script>
        var CTX = {
            batsEnv: {"environment":"noz","region":"opt","group":"prod_main","text":"BZX Options Production","envType":"prod","subType":"main","mkt":"opt","mktType":"options","isMaster":true,"isSlave":false,"isProduction":true,"isCertification":false,"isDevelopment":false,"isContinuousTrading":false,"isComplexSupported":true,"isMultipleUnderlyingComplexSupported":false,"isStockOptionSupported":false,"isTrading":true,"isFlexSupported":false,"isOptions":true,"isOptionsOnFutures":false,"location":"us","dc":"secaucus","dcType":"primary","timezone":"US/Eastern","intranetDomain":"noz.us.cboe.net","batsMkt":{"region":"opt","tradingSystem":"opt","mkt":"opt","mktType":"options","location":"us","name":"BZX Options","longName":"Cboe BZX Options Exchange","isCommon":false,"isEquities":false,"isFutures":false,"isIndices":false,"isOptions":true,"isOptionsOnFutures":false,"isDerivatives":false,"isQuoteSupported":true,"isFirmLoginMkt":false,"family":"us-options"}},
            cdn_url: 'https://cdn.cboe.com',
            cdn_api_url: 'https://cdn-api.cboe.com',
            publicDomain: 'www.cboe.com',
            publicAjaxDomain: 'www-api.cboe.com',
            recaptchaKey: '6LfM9P8lAAAAAF2Dp5gqsNCh2FZsOVptgpn-NeEW',
            i18nLanguage: {"code":null,"path":""},

            
        };
    </script>

    <script src="/jsi18n/"></script>

    
    
</head>
<body class="   page--">
    

    
        
<!-- Google Tag Manager (body) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-5D4ZVF"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (body) -->


    

    
        <script>
            window.dataLayer = window.dataLayer || [];
            dataLayer.push({
            'adv_rid': '1_02',
            'adv_sid': '0'
            });
        </script>
    

    
    
    
    

    
        
<link rel="preload" as="image" imageSrcSet="https://www.google.com/cse/static/images/2x/googlelogo_grey_46x15dp.png 2x"/><link rel="preload" as="image" href="https://cdn.cboe.com/assets/images/general/meganav_ad-MARKETS-2026-06-2x.png"/><link rel="preload" as="image" href="https://cdn.cboe.com/assets/images/general/meganav_ad-DATA.png"/><link rel="preload" as="image" href="https://cdn.cboe.com/assets/images/general/meganav_ad-SOLUTIONS.png"/><link rel="preload" as="image" href="https://cdn.cboe.com/assets/cboe-com/options-institute/misc/nav-options101.png"/><link rel="preload" as="image" href="https://cdn.cboe.com/assets/cboe-com/options-institute/misc/nav-portal.png"/><link rel="preload" as="image" href="https://cdn.cboe.com/assets/images/general/meganav_ad-ABOUT.png"/><div id="cboe-header-embed"><div class="tw-bg-interface-brand-primary-07"><header class="tw-relative tw-mx-auto tw-flex tw-max-w-screen-xl tw-items-center tw-justify-between tw-bg-interface-brand-primary-07 tw-p-spacing-400 md:tw-px-spacing-600 tw-z-[10000]" data-cboe-embed-root="header" data-mega-nav-open="false"><div class="tw-text-ink-common-inv-01 lg:tw-hidden"><nav><button id="nav-toggle-button" data-cboe-embed="menu-toggle"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-x" aria-hidden="true"><path d="M18 6 6 18"></path><path d="m6 6 12 12"></path></svg><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-menu" aria-hidden="true"><path d="M4 5h16"></path><path d="M4 12h16"></path><path d="M4 19h16"></path></svg></button><ul data-cboe-embed="mobile-nav" class="tw-transition-transform tw-duration-500 tw-ease-in-out md:before:tw-none tw-fixed tw-left-0 tw-z-30 tw-block tw-h-full tw-w-full md:tw-w-1/2 tw-top-[72px] tw-translate-x-0 tw-transform-gpu tw-overflow-auto tw-border-base-primary tw-px-spacing-50 tw-pb-3 tw-bg-interface-brand-primary-07 tw-hidden"><li class="tw-bg-interface-brand-primary-07 tw-font-subheading-sm tw-text-ink-common-inv-01" data-expanded="false"><span class="tw-justify-between tw-px-4 tw-flex tw-cursor-pointer tw-items-center tw-py-3 tw-text-white tw-no-underline lg:tw-p-0 lg:tw-text-[#002753]"><i><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-left tw-h-4 tw-w-4" aria-hidden="true"><path d="m15 18-6-6 6-6"></path></svg></i>Markets<i><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-right tw-h-4 tw-w-4" aria-hidden="true"><path d="m9 18 6-6-6-6"></path></svg></i></span><ul class="tw-hidden"><li class="tw-bg-interface-brand-primary-05 tw-font-detail-lg tw-text-ink-common-inv-01" data-expanded="false"><span class="tw-justify-between tw-px-4 tw-flex tw-cursor-pointer tw-items-center tw-py-3 tw-text-white tw-no-underline lg:tw-p-0 lg:tw-text-[#002753]"><i><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-left tw-h-4 tw-w-4" aria-hidden="true"><path d="m15 18-6-6 6-6"></path></svg></i>Global Markets<i><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-right tw-h-4 tw-w-4" aria-hidden="true"><path d="m9 18 6-6-6-6"></path></svg></i></span><ul class="tw-hidden"><li class="tw-bg-interface-brand-primary-04 tw-font-body-sm tw-text-ink-common-inv-01" data-expanded="false"><a href="/markets" target="_self" class="tw-block tw-bg-[length:20px] tw-bg-[3px_center] tw-bg-no-repeat tw-px-4 tw-py-3 tw-pr-3 tw-text-sm tw-leading-6 tw-text-base-gray-6 tw-underline lg:tw-pl-3 lg:tw-text-[16px] tw-pl-4">Global Markets Overview</a></li><li class="tw-bg-interface-brand-primary-04 tw-font-body-sm tw-text-ink-common-inv-01" data-expanded="false"><a href="/markets/prediction-markets" target="_self" class="tw-block tw-bg-[length:20px] tw-bg-[3px_center] tw-bg-no-repeat tw-px-4 tw-py-3 tw-pr-3 tw-text-sm tw-leading-6 tw-text-base-gray-6 tw-underline lg:tw-pl-3 lg:tw-text-[16px] tw-pl-4">Prediction Markets</a></li><li class="tw-bg-interface-brand-primary-04 tw-font-body-sm tw-text-ink-common-inv-01" data-expanded="false"><span class="tw-justify-between tw-px-4 tw-flex tw-cursor-pointer tw-items-center tw-py-3 tw-text-white tw-no-underline lg:tw-p-0 lg:tw-text-[#002753] tw-pl-4"><i><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-left tw-h-4 tw-w-4" aria-hidden="true"><path d="m15 18-6-6 6-6"></path></svg></i>United States<i><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-right tw-h-4 tw-w-4" aria-hidden="true"><path d="m9 18 6-6-6-6"></path></svg></i></span><ul class="tw-hidden"><li class="tw-bg-interface-brand-primary-01 tw-font-detail-md tw-text-ink-brand-primary" data-expanded="false"><span class="tw-justify-between tw-px-4 tw-flex tw-cursor-pointer tw-items-center tw-py-3 tw-text-white tw-no-underline lg:tw-p-0 lg:tw-text-[#002753] tw-pl-8"><i><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-left tw-h-4 tw-w-4" aria-hidden="true"><path d="m15 18-6-6 6-6"></path></svg></i>Equities<i><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-chevron-right tw-h-4 tw-w-4" aria-hidden="true"><path d="m9 18 6-6-6-6"></path></svg></i></span><ul class="tw-hidden"><li class="tw-bg-interface-common-base-01 tw-font-detail-md tw-text-ink-brand-primary" data-expanded="false"><a href="/markets/us/equities" target="_self" class="tw-block tw-bg-[length:20px] tw-bg-[3px_center] tw-bg-no-repeat tw-px-4 tw-py-3 tw-pr-3 tw-text-sm tw-leading-6 tw-text-base-gray-6 tw-underline lg:tw-pl-3 lg:tw-text-[16px] tw-pl-12">Overview</a></li><li class="tw-bg-interface-comm
