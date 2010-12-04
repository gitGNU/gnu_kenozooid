# read tank pressure data from an1rmv.csv and calculate RMV during dive

# time [min] and tank pressure readings [bars] columns expected
f = read.csv('stats/an1rmv.csv')
# todo: pass parameters like: profile to analyze, tank size
tank = 15
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
