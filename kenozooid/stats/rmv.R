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

# csv file times are in minutes
f$time = f$time * 60

# calculate running average depth
profile$avg_depth = cumsum(profile$depth) / seq(along=profile$depth)

data = merge(f, profile)
n = nrow(data)

# running time
time = data$time[2:n] / 60.0
avg_depth = data$avg_depth[2:n]
avg_rmv = cumsum(diff(-data$pressure)) * tank / time / (avg_depth / 10.0 + 1)

rmv = data.frame(time=time, avg_depth=round(avg_depth, 1), avg_rmv=round(avg_rmv, 1))

print(rmv)

# vim: sw=4:et:ai
