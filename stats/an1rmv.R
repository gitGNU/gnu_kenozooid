# read tank pressure data from an1rmv.csv and calculate RMV during dive

# time [min] and tank pressure readings [bars] columns expected
f = read.csv('stats/an1rmv.csv')
tank = 15

f$time = f$time * 60

# fixme: constant depth is assumed
data = merge(f, profiles)
n = nrow(data)

rmv = diff(-data$pressure) * tank / diff(data$time / 60.0) / (data$depth[2:n] / 10.0 + 1)
print(rmv)
data$rmv = c(0, round(rmv))

print(data)
