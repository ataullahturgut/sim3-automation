#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly=TRUE)
if(length(args)<6){
  stop("usage: direction_vlmc_c_104_v1_reference.R <weekly.csv> <parent.csv> <stage> <outdir> <pruning_fun.R> <window>")
}
weekly_path <- args[[1]]
parent_path <- args[[2]]
stage <- args[[3]]
outdir <- args[[4]]
prune_path <- args[[5]]
WINDOW <- as.integer(args[[6]])

if(WINDOW!=104L) stop("WINDOW_MUST_BE_104")
dir.create(outdir,recursive=TRUE,showWarnings=FALSE)
source(prune_path)

ALPHABET <- c("0","1")
ALPHA0 <- 0.05
NUM_SIMU <- 100000L

read_weekly <- function(path){
  d <- read.csv(path,stringsAsFactors=FALSE)
  d$week_start <- as.Date(d$week_start)
  d$sign <- as.integer(d$sign)
  if(any(!d$sign %in% c(0L,1L))) stop("INVALID_SIGN")
  if(any(diff(d$week_start)<=0)) stop("NONINCREASING_WEEK_AXIS")
  d
}

segments <- function(S,k){
  n <- nchar(S)
  if(k<=0L) return(rep("",n+1L))
  if(k>n) return(character())
  substring(S,seq_len(n-k+1L),seq.int(k,n))
}

count_word <- function(S,w){
  if(nchar(w)==0L) return(nchar(S)+1L)
  sum(segments(S,nchar(w))==w)
}

children_present <- function(node,present){
  c0 <- paste0("0",node); c1 <- paste0("1",node)
  (c0 %in% names(present) && isTRUE(present[[c0]])) ||
    (c1 %in% names(present) && isTRUE(present[[c1]]))
}

leaf_nodes <- function(present){
  nodes <- names(present)[present]
  nodes[!vapply(nodes,function(s) children_present(s,present),logical(1))]
}

build_initial_nodes <- function(S){
  n <- nchar(S)
  threshold <- max(2L,round(sqrt(n)/length(ALPHABET)))
  nodes <- character()
  k <- 1L
  repeat{
    seg <- segments(S,k)
    if(length(seg)==0L) break
    tab <- table(seg)
    keep <- names(tab)[tab>=threshold]
    if(length(keep)==0L) break
    nodes <- c(nodes,keep)
    k <- k+1L
  }
  list(nodes=unique(nodes),threshold=threshold)
}

fit_vlmc_c <- function(y){
  S <- paste0(y,collapse="")
  init <- build_initial_nodes(S)
  if(length(init$nodes)==0L){
    return(list(leaves=character(),threshold=init$threshold,initial_depth=0L,
                initial_leaves=0L,final_depth=0L,final_leaves=0L,tests=0L,pruned=0L))
  }

  present <- setNames(rep(TRUE,length(init$nodes)),init$nodes)
  tested <- setNames(rep(FALSE,length(init$nodes)),init$nodes)
  initial_leaves <- leaf_nodes(present)
  max_height <- max(nchar(init$nodes))
  ntests <- 0L; npruned <- 0L

  repeat{
    leaves <- leaf_nodes(present)
    if(length(leaves)==0L) break
    untested <- leaves[!tested[leaves]]
    if(length(untested)==0L) break
    ml <- max(nchar(untested))
    testing <- untested[nchar(untested)==ml]
    q <- 1 - ALPHA0/(length(leaves)*max_height)

    for(node in testing){
      ntests <- ntests+1L
      junk <- capture.output({
        res <- pruneing_fun(node_name=node,obs_seq=S,X=ALPHABET,alpha=q,num_simu=NUM_SIMU)
      })
      if(isTRUE(res$ifpruned)){
        present[[node]] <- FALSE
        npruned <- npruned+1L
      } else {
        tested[[node]] <- TRUE
      }
    }

    leaves_now <- leaf_nodes(present)
    if(length(leaves_now)==0L || all(tested[leaves_now])) break
  }

  leaves <- leaf_nodes(present)
  list(
    leaves=leaves,
    threshold=init$threshold,
    initial_depth=max_height,
    initial_leaves=length(initial_leaves),
    final_depth=if(length(leaves)) max(nchar(leaves)) else 0L,
    final_leaves=length(leaves),
    tests=ntests,
    pruned=npruned
  )
}

active_context <- function(y,leaves){
  if(length(leaves)==0L) return("ROOT")
  S <- paste0(y,collapse="")
  ok <- leaves[vapply(leaves,function(w) endsWith(S,w),logical(1))]
  if(length(ok)==0L) return("ROOT")
  ok[[which.max(nchar(ok))]]
}

transition_probability <- function(y,ctx){
  n <- length(y)
  if(ctx=="ROOT"){
    return(list(p=mean(y),support=n,down=n-sum(y),up=sum(y)))
  }
  k <- nchar(ctx)
  down <- 0L; up <- 0L
  if(k>=n) stop("CONTEXT_TOO_LONG")
  for(i in seq_len(n-k)){
    w <- paste0(y[i:(i+k-1L)],collapse="")
    if(w==ctx){
      nxt <- y[[i+k]]
      if(nxt==1L) up <- up+1L else down <- down+1L
    }
  }
  den <- down+up
  if(den<=0L) stop(paste0("ZERO_CONTEXT_SUPPORT:",ctx))
  list(p=up/den,support=den,down=down,up=up)
}

metrics <- function(z){
  n <- nrow(z); au <- sum(z$actual_up==1L); ad <- n-au
  tp <- sum(z$forecast_up==1L & z$actual_up==1L)
  tn <- sum(z$forecast_up==0L & z$actual_up==0L)
  fp <- sum(z$forecast_up==1L & z$actual_up==0L)
  fn <- sum(z$forecast_up==0L & z$actual_up==1L)
  eps <- 1e-12; pp <- pmin(pmax(z$p_up,eps),1-eps)
  data.frame(
    n=n,accuracy=(tp+tn)/n,
    balanced_accuracy=((tp/au)+(tn/ad))/2,
    brier=mean((z$p_up-z$actual_up)^2),
    log_loss=mean(-(z$actual_up*log(pp)+(1-z$actual_up)*log(1-pp))),
    actual_up=au,actual_down=ad,forecast_up=tp+fp,forecast_down=tn+fn,
    up_sensitivity=tp/au,down_sensitivity=tn/ad,
    tp=tp,tn=tn,fp=fp,fn=fn,
    always_up_accuracy=au/n,
    previous_sign_accuracy=mean(z$previous_up==z$actual_up),
    mean_p_up=mean(z$p_up),min_p_up=min(z$p_up),max_p_up=max(z$p_up),
    stringsAsFactors=FALSE
  )
}

d <- read_weekly(weekly_path)
parent <- read.csv(parent_path,stringsAsFactors=FALSE)
parent$k <- as.integer(parent$k)
parent <- parent[parent$k==104L,,drop=FALSE]
parent$target_week <- as.Date(parent$target_week)

rows <- list()
for(target_idx in seq.int(WINDOW+1L,nrow(d))){
  target <- d$week_start[[target_idx]]
  if(stage=="pre2025" && (target<as.Date("2024-01-01") || target>=as.Date("2025-01-01"))) next
  if(stage=="2025" && (target<as.Date("2025-01-01") || target>=as.Date("2026-01-01"))) next

  idx <- (target_idx-WINDOW):(target_idx-1L)
  y <- d$sign[idx]
  fit <- fit_vlmc_c(y)
  ctx <- active_context(y,fit$leaves)
  tr <- transition_probability(y,ctx)
  rows[[length(rows)+1L]] <- data.frame(
    target_week=as.character(target),
    origin_week=as.character(d$week_start[[target_idx-1L]]),
    p_up=tr$p,forecast_up=as.integer(tr$p>=0.5),
    actual_up=d$sign[[target_idx]],previous_up=d$sign[[target_idx-1L]],
    active_context=ctx,active_context_depth=if(ctx=="ROOT")0L else nchar(ctx),
    active_context_support=tr$support,active_trans_down=tr$down,active_trans_up=tr$up,
    threshold_gen=fit$threshold,initial_depth=fit$initial_depth,
    initial_leaves=fit$initial_leaves,final_depth=fit$final_depth,
    final_leaves=fit$final_leaves,branch_tests=fit$tests,branches_pruned=fit$pruned,
    stringsAsFactors=FALSE
  )
}
fc <- do.call(rbind,rows)
if(is.null(fc)||nrow(fc)==0L) stop("NO_FORECASTS")

par <- merge(fc,parent[,c("target_week","p_up","forecast_up","actual_up","previous_up")],
             by="target_week",suffixes=c("_vlmcc","_vlmc104"),all.x=TRUE)
if(any(is.na(par$p_up_vlmc104))) stop("PARENT_SUPPORT_MISMATCH")
if(any(par$actual_up_vlmcc!=par$actual_up_vlmc104)) stop("ACTUAL_MISMATCH")

m_c <- metrics(data.frame(
  p_up=par$p_up_vlmcc,forecast_up=par$forecast_up_vlmcc,
  actual_up=par$actual_up_vlmcc,previous_up=par$previous_up_vlmcc
))
m_b <- metrics(data.frame(
  p_up=par$p_up_vlmc104,forecast_up=par$forecast_up_vlmc104,
  actual_up=par$actual_up_vlmc104,previous_up=par$previous_up_vlmc104
))
comp <- cbind(data.frame(identity=c("VLMC_C_104","VLMC_BS_104")),rbind(m_c,m_b))
comp$delta_accuracy_vs_vlmc104 <- comp$accuracy-m_b$accuracy[[1]]
comp$delta_balanced_vs_vlmc104 <- comp$balanced_accuracy-m_b$balanced_accuracy[[1]]
comp$delta_brier_vs_vlmc104 <- comp$brier-m_b$brier[[1]]
comp$delta_logloss_vs_vlmc104 <- comp$log_loss-m_b$log_loss[[1]]

prefix <- if(stage=="pre2025")"PRE2025" else "2025"
write.csv(fc,file.path(outdir,paste0("GOLD_CONTROL_DIRECTION_VLMC_C_104_V1_",prefix,"_FORECASTS_2026-09-18.csv")),row.names=FALSE)
write.csv(comp,file.path(outdir,paste0("GOLD_CONTROL_DIRECTION_VLMC_C_104_V1_",prefix,"_COMPARISON_2026-09-18.csv")),row.names=FALSE)
summary <- list(
  identity="DIRECTION_VLMC_C_104_V1_RESEARCH",stage=stage,window=WINDOW,
  alpha0=ALPHA0,num_simu=NUM_SIMU,reference_seed_per_branch=1L,
  threshold_gen_formula="max(2, round(sqrt(n)/|X|))",
  external_reference_commit="8195ee16dedbb3a89c288869ee9c0b856ea2ed4f",
  vlmc_c=as.list(m_c[1,]),vlmc_bs_104=as.list(m_b[1,])
)
dput(summary,file=file.path(outdir,paste0("GOLD_CONTROL_DIRECTION_VLMC_C_104_V1_",prefix,"_SUMMARY_2026-09-18.R")))
writeLines(capture.output(str(summary)),file.path(outdir,paste0("GOLD_CONTROL_DIRECTION_VLMC_C_104_V1_",prefix,"_SUMMARY_2026-09-18.txt")))
cat("VLMC_C_104_V1_PASS",stage,"n=",nrow(fc),"\n")
print(comp)
