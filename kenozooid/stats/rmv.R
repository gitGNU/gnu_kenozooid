#
# read tank pressure data from CSV file (time, pressure)
# and calculate RMV during dive
#

# arguments
# - CSV file with time [min] and pressure [bar]
# - tank size

if (length(kz.args) != 2) {
    stop('Arguments required: CSV file, tank size')
}

f = read.csv(kz.args[1])
tank = as.integer(kz.args[2])
profile = kz.profiles

f$time = f$time * 60
indices = match(f$time, profile$time)
n = length(indices)
indices = cbind(indices[1:n - 1], indices[2:n])

avg_depth = apply(indices, 1, function(p) { mean(profile$depth[p[1]:p[2]]) })

data = merge(f, profile)
n = nrow(data)

time = data$time[2:length(data$time)] / 60.0
rmv = diff(-data$pressure) * tank / diff(data$time / 60.0) / (avg_depth / 10.0 + 1)
avg_rmv = cumsum(rmv) / 1:length(rmv)
rmv = data.frame(time=time, depth=round(avg_depth, 1), rmv=round(rmv),
    avg_rmv=round(avg_rmv))

print(rmv)

# vim: sw=4:et:ai
