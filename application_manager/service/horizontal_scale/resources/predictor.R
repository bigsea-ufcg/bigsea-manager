verbose = F
suppressMessages(require(forecast))
suppressMessages(require(stats))
suppressMessages(require(scales))
suppressMessages(require(plyr))
suppressMessages(require(dplyr))
suppressMessages(require(Rmisc))
suppressMessages(require(reshape))

args <- commandArgs(trailingOnly = TRUE)

file = args[1]
predict_horizon = as.numeric(args[2])

create_predict            <- function(ddf, mean, h) {

    graph <- data.frame(cpu_value=double(),
                        mem_value=double(),
                        type=character())

    cpu_predicts_df <- data.frame(meanf=double(),
                                  naive=double(),
                                  rwf=double(),
                                  drift=double());
    mem_predicts_df <- data.frame(meanf=double(),
                                  naive=double(),
                                  rwf=double(),
                                  drift=double())


    ts.cpu <- ts(ddf$cpu)
    ts.mem <- ts(ddf$mem)
    if(mean) {
        ###cpu###
        cpu_meanf_value=as.numeric(head(meanf(ts.cpu, h, level = 0.95)$mean))
        cpu_naive_value=as.numeric(head(naive(ts.cpu, h, level = 0.95)$mean))
        cpu_rwf_value=as.numeric(head(rwf(ts.cpu, h, level = 0.95)$mean))
        cpu_drift_value=as.numeric(head(rwf(ts.cpu, h, drift=TRUE, level = 0.95)$mean))
        ###mem###
        mem_meanf_value=as.numeric(head(meanf(ts.mem, h, level = 0.95)$mean))
        mem_naive_value=as.numeric(head(naive(ts.mem, h, level = 0.95)$mean))
        mem_rwf_value=as.numeric(head(rwf(ts.mem, h, level = 0.95)$mean))
        mem_drift_value=as.numeric(head(rwf(ts.mem, h, drift=TRUE, level = 0.95)$mean))
    } else {
        ###cpu###
        cpu_meanf_value=as.numeric(head(meanf(ts.cpu, h, level = 0.95)$upper))
        cpu_naive_value=as.numeric(head(naive(ts.cpu, h, level = 0.95)$upper))
        cpu_rwf_value=as.numeric(head(rwf(ts.cpu, h, level = 0.95)$upper))
        cpu_drift_value=as.numeric(head(rwf(ts.cpu, h, drift=TRUE, level = 0.95)$upper))
        ###mem###
        mem_meanf_value=as.numeric(head(meanf(ts.mem, h, level = 0.95)$upper))
        mem_naive_value=as.numeric(head(naive(ts.mem, h, level = 0.95)$upper))
        mem_rwf_value=as.numeric(head(rwf(ts.mem, h, level = 0.95)$upper))
        mem_drift_value=as.numeric(head(rwf(ts.mem, h, drift=TRUE, level = 0.95)$upper))
    }


    cpu_predicts_df <- data.frame(meanf=cpu_meanf_value[h],
                         naive=cpu_naive_value[h],
                         rwf=cpu_rwf_value[h],
                         drift=cpu_drift_value[h])
    mem_predicts_df <- data.frame(meanf=min(1,mem_meanf_value[h]),
                         naive=min(1,mem_naive_value[h]),
                         rwf=min(1,mem_rwf_value[h]),
                         drift=min(1,mem_drift_value[h]))

    meanf_df <- data.frame(cpu_value=cpu_predicts_df$meanf[1],
                         mem_value=mem_predicts_df$meanf[1],
                         type='meanf')
    naive_df <- data.frame(cpu_value=cpu_predicts_df$naive[1],
                         mem_value=mem_predicts_df$naive[1],
                         type='naive')
    rwf_df   <- data.frame(cpu_value=cpu_predicts_df$rwf[1],
                         mem_value=mem_predicts_df$rwf[1],
                         type='rwf')
    drift_df <- data.frame(cpu_value=cpu_predicts_df$drift[1],
                         mem_value=mem_predicts_df$drift[1],
                         type='drift')

    graph <- rbind(graph, meanf_df, naive_df, rwf_df, drift_df)

    return(graph)
}

get_num_machines          <- function(cpu, mem, host_cpu, host_mem) {

  free_cores       <- host_cpu * (1 - cpu) * 4
  free_mem         <- host_mem * (1 - mem) * 1

  hadoop_cores     <- 2
  hadoop_mem       <- 4

  limit_cores      <- (host_cpu * 4) - 2 #(1 / (VCPUS * host$cpu))
  limit_mem        <- host_mem - (host_mem * 0.1)

  num_maq_cores    <- floor(min(limit_cores, free_cores)/hadoop_cores)
  num_maq_mem      <- floor(min(limit_mem, free_mem)/hadoop_mem)

  num_maq          <- max(0,min(num_maq_cores,num_maq_mem))

  return(num_maq)
}

create_num_maq_df         <- function(ddf, host_cpu, host_mem, h) {

  num_maq <- data.frame(num_maq=integer(),
                        type=character())

    cpu_meanf_value = ddf$cpu_value[1]
    cpu_naive_value = ddf$cpu_value[2]
    cpu_rwf_value   = ddf$cpu_value[3]
    cpu_drift_value = ddf$cpu_value[4]
    mem_meanf_value = ddf$mem_value[1]
    mem_naive_value = ddf$mem_value[2]
    mem_rwf_value   = ddf$mem_value[3]
    mem_drift_value = ddf$mem_value[4]

    meanf_maq       = get_num_machines(cpu_meanf_value, mem_meanf_value,
                                       host_cpu, host_mem)
    naive_maq       = get_num_machines(cpu_naive_value, mem_naive_value,
                                       host_cpu, host_mem)
    rwf_maq         = get_num_machines(cpu_rwf_value, mem_rwf_value, host_cpu,
                                       host_mem)
    drift_maq       = get_num_machines(cpu_drift_value, mem_drift_value,
                                       host_cpu, host_mem)

    meanf_maq_df    = data.frame(num_maq=meanf_maq,
                                 type='meanf')
    naive_maq_df    = data.frame(num_maq=naive_maq,
                                 type='naive')
    rwf_maq_df      = data.frame(num_maq=rwf_maq,
                               type='rwf')
    drift_maq_df    = data.frame(num_maq=drift_maq,
                                 type='drift')

    num_maq         = rbind(num_maq, meanf_maq_df, naive_maq_df,
                            rwf_maq_df, drift_maq_df)

    return(num_maq)
}

instance                  <- read.csv(file, header=FALSE, sep=';',
                                      col.names=c("cpu_util","mem_util",
                                                  "cpu_tot","mem_tot","index"))
host_cpu                  <- instance$cpu_tot[1]
host_mem                  <- instance$mem_tot[1]

instance.by_index         <- group_by(instance, index)

instance.max              <- dplyr::summarise(instance.by_index,
                                              cpu = max(cpu_util),
                                              mem = max(mem_util))

instance.last             <- tail(instance.max, 10)
predict                   <- create_predict(instance.last, TRUE,
                                            predict_horizon)

num_maq                   <- create_num_maq_df(predict, host_cpu, host_mem,
                                               predict_horizon)

cat(min(num_maq$num_maq))
