#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(VLMCX))

args <- commandArgs(trailingOnly=TRUE)
if(length(args)<5){
  stop("usage: direction_covlmc_x3_v1_reference.R <panel.csv> <parent.csv> <stage:pre2025|2025> <outdir> <window>")
}
panel_path <- args[[1]]
parent_path <- args[[2]]
stage <- args[[3]]
outdir <- args[[4]]
WINDOW <- as.integer(args[[5]])

if(as.character(packageVersion("VLMCX"))!="1.0") stop("VLMCX_VERSION_MISMATCH")
if(WINDOW!=104L) stop("WINDOW_MUST_BE_104")
dir.create(outdir,recursive=TRUE,showWarnings=FALSE)

ALPHA <- 0.05
MAX_DEPTH <- 5L
N_MIN <- 5L
XCOLS <- c("dgs10","dexchus","gpr")

d <- read.csv(panel_path,stringsAsFactors=FALSE)
d$week_start <- as.Date(d$week_start)
d$last_date <- as.Date(d$last_date)
d$sign <- as.integer(d$sign)
if(any(!d$sign %in% c(0L,1L))) stop("INVALID_SIGN")
if(any(!is.finite(as.matrix(d[,XCOLS])))) stop("NONFINITE_COVARIATE")
if(any(diff(d$week_start)<=0)) stop("NONINCREASING_WEEK_AXIS")

parent <- read.csv(parent_path,stringsAsFactors=FALSE)
parent$k <- as.integer(parent$k)
parent <- parent[parent$k==104L,,drop=FALSE]
parent$target_week <- as.Date(parent$target_week)
if(nrow(parent)==0) stop("PARENT_104_MISSING")

metrics <- function(z){
  n <- nrow(z)
  if(n==0L) return(data.frame(n=0L))
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
    balanced_accuracy=if(au>0&&ad>0)((tp/au)+(tn/ad))/2 else NA_real_,
    brier=mean((z$p_up-z$actual_up)^2),
    log_loss=mean(-(z$actual_up*log(pp)+(1-z$actual_up)*log(1-pp))),
    actual_up=au,actual_down=ad,
    forecast_up=tp+fp,forecast_down=tn+fn,
    up_sensitivity=if(au>0)tp/au else NA_real_,
    down_sensitivity=if(ad>0)tn/ad else NA_real_,
    tp=tp,tn=tn,fp=fp,fn=fn,
    always_up_accuracy=au/n,
    previous_sign_accuracy=mean(z$previous_up==z$actual_up),
    mean_p_up=mean(z$p_up),min_p_up=min(z$p_up),max_p_up=max(z$p_up),
    fit_warning_origins=sum(z$warning_count>0L),
    stringsAsFactors=FALSE
  )
}

prob_up <- function(fit){
  pr <- predict(fit)
  if(length(pr)!=2L) stop("PREDICT_PROBABILITY_LENGTH_NOT_2")
  if(any(!is.finite(pr)) || any(pr<0) || any(pr>1)) stop("INVALID_PREDICTED_PROBABILITY")
  if(abs(sum(pr)-1)>1e-7) stop("PREDICTED_PROBABILITIES_NOT_NORMALIZED")

  b <- fit$baseline.state
  if(length(b)!=1L) stop("BASELINE_STATE_INVALID")
  baseline <- suppressWarnings(as.integer(as.character(b)))
  if(is.na(baseline)) baseline <- as.integer(b)
  states <- sort(unique(as.integer(fit$y)))
  if(!all(states==c(0L,1L))) stop("BINARY_STATE_SPACE_CHANGED")
  order <- c(baseline,setdiff(states,baseline))
  idx <- which(order==1L)
  if(length(idx)!=1L) stop("UP_STATE_MAPPING_FAILED")
  list(p=as.numeric(pr[[idx]]),baseline=baseline)
}

rows <- list()
for(target_idx in seq.int(WINDOW+1L,nrow(d))){
  target <- d$week_start[[target_idx]]
  if(stage=="pre2025" && (target<as.Date("2024-01-01") || target>=as.Date("2025-01-01"))) next
  if(stage=="2025" && (target<as.Date("2025-01-01") || target>=as.Date("2026-01-01"))) next

  idx <- (target_idx-WINDOW):(target_idx-1L)
  y <- d$sign[idx]
  Xraw <- as.matrix(d[idx,XCOLS,drop=FALSE])
  mu <- colMeans(Xraw)
  sig <- apply(Xraw,2,sd)
  if(any(!is.finite(sig)) || any(sig<=0)) stop(paste0("ZERO_OR_INVALID_SD:",target))
  X <- sweep(sweep(Xraw,2,mu,"-"),2,sig,"/")

  warns <- character()
  fit <- withCallingHandlers(
    VLMCX::VLMCX(y,X,alpha.level=ALPHA,max.depth=MAX_DEPTH,n.min=N_MIN,trace=FALSE),
    warning=function(w){
      warns <<- c(warns,conditionMessage(w))
      invokeRestart("muffleWarning")
    }
  )
  pu <- prob_up(fit)

  rows[[length(rows)+1L]] <- data.frame(
    target_week=as.character(target),
    origin_week=as.character(d$week_start[[target_idx-1L]]),
    p_up=pu$p,
    forecast_up=as.integer(pu$p>=0.5),
    actual_up=d$sign[[target_idx]],
    previous_up=d$sign[[target_idx-1L]],
    baseline_state=pu$baseline,
    loglik=as.numeric(LogLik(fit)),
    aic=as.numeric(AIC(fit)),
    bic=as.numeric(BIC(fit)),
    warning_count=length(warns),
    warning_text=paste(unique(warns),collapse=" | "),
    dgs10_mean=mu[["dgs10"]],dgs10_sd=sig[["dgs10"]],
    dexchus_mean=mu[["dexchus"]],dexchus_sd=sig[["dexchus"]],
    gpr_mean=mu[["gpr"]],gpr_sd=sig[["gpr"]],
    stringsAsFactors=FALSE
  )
}

fc <- do.call(rbind,rows)
if(is.null(fc)||nrow(fc)==0) stop("NO_FORECASTS")

par <- merge(
  fc,
  parent[,c("target_week","p_up","forecast_up","actual_up","previous_up")],
  by="target_week",
  suffixes=c("_covlmc","_vlmc104"),
  all.x=TRUE
)
if(any(is.na(par$p_up_vlmc104))) stop("PARENT_SUPPORT_MISMATCH")
if(any(par$actual_up_covlmc!=par$actual_up_vlmc104)) stop("ACTUAL_MISMATCH_WITH_PARENT")

cov_metric_input <- data.frame(
  p_up=par$p_up_covlmc,forecast_up=par$forecast_up_covlmc,
  actual_up=par$actual_up_covlmc,previous_up=par$previous_up_covlmc,
  warning_count=par$warning_count
)
base_metric_input <- data.frame(
  p_up=par$p_up_vlmc104,forecast_up=par$forecast_up_vlmc104,
  actual_up=par$actual_up_vlmc104,previous_up=par$previous_up_vlmc104,
  warning_count=0L
)
m_cov <- metrics(cov_metric_input)
m_base <- metrics(base_metric_input)

comparison <- cbind(
  data.frame(identity=c("COVLMC_X3_104","VLMC_BS_104")),
  rbind(m_cov,m_base)
)
comparison$delta_accuracy_vs_vlmc104 <- comparison$accuracy-m_base$accuracy[[1]]
comparison$delta_balanced_vs_vlmc104 <- comparison$balanced_accuracy-m_base$balanced_accuracy[[1]]
comparison$delta_brier_vs_vlmc104 <- comparison$brier-m_base$brier[[1]]
comparison$delta_logloss_vs_vlmc104 <- comparison$log_loss-m_base$log_loss[[1]]

prefix <- if(stage=="pre2025") "PRE2025" else "2025"
write.csv(fc,file.path(outdir,paste0("GOLD_CONTROL_DIRECTION_COVLMC_X3_V1_",prefix,"_FORECASTS_2026-09-18.csv")),row.names=FALSE)
write.csv(comparison,file.path(outdir,paste0("GOLD_CONTROL_DIRECTION_COVLMC_X3_V1_",prefix,"_COMPARISON_2026-09-18.csv")),row.names=FALSE)

summary <- list(
  identity="DIRECTION_COVLMC_X3_V1_RESEARCH",
  stage=stage,
  R_version=R.version.string,
  VLMCX_version=as.character(packageVersion("VLMCX")),
  window=WINDOW,
  covariates=XCOLS,
  alpha_level=ALPHA,max_depth=MAX_DEPTH,n_min=N_MIN,
  scaling="origin-specific z-score from prior 104 weeks only",
  final_rule="UP iff P(UP)>=0.5",
  covlmc=as.list(m_cov[1,]),
  vlmc_bs_104=as.list(m_base[1,])
)
dput(summary,file=file.path(outdir,paste0("GOLD_CONTROL_DIRECTION_COVLMC_X3_V1_",prefix,"_SUMMARY_2026-09-18.R")))
writeLines(capture.output(str(summary)),file.path(outdir,paste0("GOLD_CONTROL_DIRECTION_COVLMC_X3_V1_",prefix,"_SUMMARY_2026-09-18.txt")))
cat("COVLMC_X3_V1_PASS",stage,"n=",nrow(fc),"\n")
print(comparison)
