#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(VLMC))

args <- commandArgs(trailingOnly=TRUE)
if (length(args) < 4) {
  stop("usage: direction_vlmc_bs_family_v2_reference.R <input.csv> <stage:pre2025|2025> <output_dir> <calibration.csv|AUTO>")
}
input_csv <- args[[1]]
stage <- args[[2]]
out_dir <- args[[3]]
calibration_arg <- args[[4]]

dir.create(out_dir, recursive=TRUE, showWarnings=FALSE)

K0 <- 0.30
K_GRID <- seq(0.40, 2.50, by=0.02)
B <- 1000L
BURN_IN <- 10000L
SEED <- 1521L
WINDOWS <- c(26L,52L,104L)

if (as.character(packageVersion("VLMC")) != "1.4.4") {
  stop(paste0("VLMC_VERSION_MISMATCH:", packageVersion("VLMC")))
}

d <- read.csv(input_csv, stringsAsFactors=FALSE)
required <- c("week_start","weekly_return","sign")
if (!all(required %in% names(d))) stop("INPUT_SCHEMA_MISSING")
d$week_start <- as.Date(d$week_start)
d$sign <- as.integer(d$sign)
if (any(!d$sign %in% c(0L,1L))) stop("INVALID_SIGN")
if (any(diff(d$week_start) <= 0)) stop("NON_INCREASING_WEEK_AXIS")
if (any((d$weekly_return > 0) != (d$sign == 1L))) stop("RETURN_SIGN_MISMATCH")

as_binary_factor <- function(x) factor(as.integer(x), levels=c(0,1))

fit_vlmc <- function(x, cutoff) {
  VLMC::vlmc(as_binary_factor(x),
             cutoff.prune=cutoff,
             threshold.gen=2,
             y=TRUE,
             quiet=TRUE)
}

predict_next_class_reference <- function(model, train_plus_actual) {
  n <- length(train_plus_actual)-1L
  p <- as.integer(model$size[["ord.MC"]])
  if (p == 0L) {
    nd <- as_binary_factor(c(0L, train_plus_actual[n+1L]))
    pr <- predict(model, nd, type="class")
    ans <- pr[[2L]]
  } else {
    idx <- (n-p+1L):(n+1L)
    nd <- as_binary_factor(train_plus_actual[idx])
    pr <- predict(model, nd, type="class")
    ans <- pr[[p+1L]]
  }
  as.integer(as.character(ans))
}

predict_next_prob_up <- function(model, train) {
  p <- as.integer(model$size[["ord.MC"]])
  if (p == 0L) {
    nd <- as_binary_factor(c(0L,0L))
    probs <- predict(model, nd, type="probs")
    row <- probs[2L,]
  } else {
    hist <- tail(as.integer(train), p)
    nd <- as_binary_factor(c(hist,0L))
    probs <- predict(model, nd, type="probs")
    row <- probs[p+1L,]
  }
  if (!("1" %in% names(row))) stop("UP_PROBABILITY_COLUMN_MISSING")
  pu <- as.numeric(row[["1"]])
  if (!is.finite(pu) || pu < 0 || pu > 1) stop("INVALID_P_UP")
  pu
}

calibrate_k <- function(train, k) {
  if (length(train) != k) stop("CALIBRATION_WINDOW_MISMATCH")
  initial <- fit_vlmc(train, K0)
  set.seed(SEED)
  matches <- integer(length(K_GRID))

  for (b in seq_len(B)) {
    xs <- as.integer(simulate(initial,
                              nsim=k+1L,
                              n.start=BURN_IN,
                              integer.return=TRUE,
                              keep.RSeed=TRUE))
    actual <- xs[k+1L]

    for (j in seq_along(K_GRID)) {
      m <- fit_vlmc(xs[seq_len(k)], K_GRID[[j]])
      pred <- predict_next_class_reference(m, xs)
      if (!is.na(pred) && pred == actual) matches[[j]] <- matches[[j]] + 1L
    }
  }

  losses <- 1 - matches/B
  best <- which.max(matches) # first/smallest K on ascending exact tie
  data.frame(
    k=k,
    k0=K0,
    k_star=K_GRID[[best]],
    bootstrap_matches=matches[[best]],
    bootstrap_loss=losses[[best]],
    k_tie_count=sum(matches == matches[[best]]),
    initial_order=as.integer(initial$size[["ord.MC"]]),
    initial_context=as.integer(initial$size[["context"]]),
    initial_leaves=as.integer(initial$size[["nr.leaves"]]),
    B=B,
    burn_in=BURN_IN,
    seed=SEED,
    stringsAsFactors=FALSE
  )
}

metric_block <- function(z) {
  n <- nrow(z)
  if (n == 0L) return(data.frame(n=0L))
  au <- sum(z$actual_up==1L); ad <- n-au
  tp <- sum(z$forecast_up==1L & z$actual_up==1L)
  tn <- sum(z$forecast_up==0L & z$actual_up==0L)
  fp <- sum(z$forecast_up==1L & z$actual_up==0L)
  fn <- sum(z$forecast_up==0L & z$actual_up==1L)
  eps <- 1e-12
  pp <- pmin(pmax(z$p_up,eps),1-eps)
  data.frame(
    n=n,
    accuracy=(tp+tn)/n,
    balanced_accuracy=if (au>0 && ad>0) ((tp/au)+(tn/ad))/2 else NA_real_,
    brier=mean((z$p_up-z$actual_up)^2),
    log_loss=mean(-(z$actual_up*log(pp)+(1-z$actual_up)*log(1-pp))),
    actual_up=au,actual_down=ad,
    forecast_up=tp+fp,forecast_down=tn+fn,
    up_sensitivity=if(au>0) tp/au else NA_real_,
    down_sensitivity=if(ad>0) tn/ad else NA_real_,
    tp=tp,tn=tn,fp=fp,fn=fn,
    always_up_accuracy=au/n,
    previous_sign_accuracy=mean(z$previous_up==z$actual_up),
    mean_p_up=mean(z$p_up),
    min_p_up=min(z$p_up),
    max_p_up=max(z$p_up),
    stringsAsFactors=FALSE
  )
}

if (stage == "pre2025") {
  calibrations <- do.call(rbind,lapply(WINDOWS,function(k) calibrate_k(d$sign[seq_len(k)],k)))
  write.csv(calibrations,file.path(out_dir,"GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_CALIBRATION_2026-09-18.csv"),row.names=FALSE)

} else if (stage == "2025") {
  if (calibration_arg == "AUTO") stop("2025_REQUIRES_FROZEN_CALIBRATION")
  calibrations <- read.csv(calibration_arg,stringsAsFactors=FALSE)
  if (!all(WINDOWS %in% calibrations$k)) stop("CALIBRATION_WINDOWS_MISSING")
} else stop("INVALID_STAGE")

forecasts <- list()
for (k in WINDOWS) {
  cal <- calibrations[calibrations$k==k,]
  Kstar <- cal$k_star[[1L]]
  for (target_idx in (k+1L):nrow(d)) {
    target_date <- d$week_start[[target_idx]]
    if (stage=="pre2025" && target_date >= as.Date("2025-01-01")) next
    if (stage=="2025" && (target_date < as.Date("2025-01-01") || target_date >= as.Date("2026-01-01"))) next

    train <- d$sign[(target_idx-k):(target_idx-1L)]
    m <- fit_vlmc(train,Kstar)
    pu <- predict_next_prob_up(m,train)
    forecasts[[length(forecasts)+1L]] <- data.frame(
      k=k,
      target_week=as.character(target_date),
      origin_week=as.character(d$week_start[[target_idx-1L]]),
      k_star=Kstar,
      p_up=pu,
      forecast_up=as.integer(pu>=0.5),
      actual_up=d$sign[[target_idx]],
      previous_up=d$sign[[target_idx-1L]],
      final_order=as.integer(m$size[["ord.MC"]]),
      final_context=as.integer(m$size[["context"]]),
      final_leaves=as.integer(m$size[["nr.leaves"]]),
      stringsAsFactors=FALSE
    )
  }
}
fc <- do.call(rbind,forecasts)
if (is.null(fc) || nrow(fc)==0) stop("NO_FORECASTS")

forecast_name <- if(stage=="pre2025") "GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_PRE2025_FORECASTS_2026-09-18.csv" else "GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_2025_FORECASTS_2026-09-18.csv"
write.csv(fc,file.path(out_dir,forecast_name),row.names=FALSE)

by_variant <- do.call(rbind,lapply(WINDOWS,function(k){
  z <- fc[fc$k==k,,drop=FALSE]
  if(stage=="pre2025"){
    years <- sort(unique(as.integer(substr(z$target_week,1,4))))
    do.call(rbind,lapply(years,function(y){
      zz <- z[substr(z$target_week,1,4)==as.character(y),,drop=FALSE]
      cbind(data.frame(k=k,period=as.character(y)),metric_block(zz))
    }))
  } else {
    cbind(data.frame(k=k,period="2025"),metric_block(z))
  }
}))

if(stage=="pre2025"){
  first_common <- max(sapply(WINDOWS,function(k) min(as.Date(fc$target_week[fc$k==k & substr(fc$target_week,1,4)=="2024"]))))
  common <- do.call(rbind,lapply(WINDOWS,function(k){
    z <- fc[fc$k==k & as.Date(fc$target_week)>=first_common & substr(fc$target_week,1,4)=="2024",,drop=FALSE]
    cbind(data.frame(k=k,period=paste0("2024_common_from_",first_common)),metric_block(z))
  }))
  metrics <- rbind(by_variant,common)
} else metrics <- by_variant

write.csv(metrics,file.path(out_dir,paste0("GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_",toupper(stage),"_METRICS_2026-09-18.csv")),row.names=FALSE)

summary <- list(
  identity="DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH",
  stage=stage,
  R_version=R.version.string,
  VLMC_version=as.character(packageVersion("VLMC")),
  weekly_input="sum of governed daily simple percentage returns; sign=1 iff weekly sum > 0",
  windows=WINDOWS,
  K0=K0,
  K_grid=c(min(K_GRID),max(K_GRID),0.02),
  B=B,burn_in=BURN_IN,seed=SEED,
  bootstrap_classifier="VLMC::predict(type='class')",
  final_rule="UP iff P(UP)>=0.5",
  calibration=calibrations,
  metrics=metrics
)
dput(summary,file=file.path(out_dir,paste0("GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_",toupper(stage),"_SUMMARY_2026-09-18.R")))
writeLines(capture.output(str(summary)),file.path(out_dir,paste0("GOLD_CONTROL_DIRECTION_VLMC_BS_FAMILY_V2_",toupper(stage),"_SUMMARY_2026-09-18.txt")))

cat("VLMC_BS_FAMILY_V2_STAGE_PASS",stage,"\n")
print(calibrations)
print(metrics)
