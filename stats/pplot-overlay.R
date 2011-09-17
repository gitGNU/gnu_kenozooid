#
# plot dive profiles
#

# arguments
# - CSV file with time [min] and pressure [bar]
# - tank size

library(Hmisc)
library(grid)
library(colorspace)

if (length(args) != 3) {
    stop('Arguments required: ...')
}

args.fout = args[1]
args.sig = args[2] == 'True'
args.fmt = args[3]

args.width = 10
args.height = 5

if (args.fmt == 'pdf') {
    cairo_pdf(args.fout, width=args.width, height=args.height, onefile=TRUE)
} else if (args.fmt == 'png') {
    fimg = png
    args.width = 800
    args.height = 400
    png(args.fout, width=args.width, height=args.height)
} else if (args.fmt == 'svg') {
    svg(args.fout, width=args.width, height=args.height)
}

if (is.null(kz.dives.ui$title))
    par(mar=c(5, 4, 1, 2) + 0.1)

# find max times and max depths within dive profiles
lim = aggregate(kz.profiles[c('time', 'depth')], by=kz.profiles['dive'],
    function(a, b) max(a), max(b))

xl = c(0, max(lim$time) / 60.0)
yl = rev(c(0, max(lim$depth)))
plot(NA, xlim=xl, ylim=yl, xlab='Time [min]', ylab='Depth [m]')

# first the grid
minor.tick(nx=5, ny=2)
grid()

n = nrow(kz.dives)
cols = diverge_hcl(n)

# then plot the profiles
for (i in 1:n) {
    dp = kz.profiles[kz.profiles$dive == i, ]
    lines(dp$time / 60.0, dp$depth, col=cols[i])
}

if (!is.null(kz.dives.ui$label)) {
    lscale = ifelse(n > 10, 0.7, 1.0)
    legend('bottomright', as.vector(kz.dives.ui$label), col=cols, lwd=1,
        inset=c(0.02, 0.05), ncol=ceiling(n / 10), cex=lscale)
}

dev.off()

# vim: sw=4:et:ai
