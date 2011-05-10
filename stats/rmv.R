# read tank pressure data from CSV file (time, pressure)
# and calculate RMV during dive
#
# sample run as
#     $ kz analyze -a stats/rmv.csv -a 15 stats/rmv.R 19 dumps/ostc-dump-18.uddf
#       time    depth      rmv
#     1  240 5.484000 48.43710
#     2  540 6.596774 36.15160
#     3 1020 6.534694 22.67959
#     4 1440 6.632558 12.88351
#


# arguments
# - CSV file with time [min] and pressure [bar]
# - tank size

if (length(args) != 2) {
    stop('Arguments required: CSV file, tank size')
}

f = read.csv(args[1])
tank = as.integer(args[2])
profile = profiles

f$time = f$time * 60
indices = match(f$time, profile$time)
n = length(indices)
indices = cbind(indices[1:n - 1], indices[2:n])

avg_depth = apply(indices, 1, function(p) { mean(profile$depth[p[1]:p[2]]) })

data = merge(f, profile)
n = nrow(data)

time = data$time[2:length(data$time)]
rmv = diff(-data$pressure) * tank / diff(data$time / 60.0) / (avg_depth / 10.0 + 1)
rmv = data.frame(time=time, depth=avg_depth, rmv=rmv)

print(rmv)
