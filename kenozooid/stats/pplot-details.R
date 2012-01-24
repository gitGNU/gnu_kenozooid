
# plot dive profiles
#

library(Hmisc)
library(grid)

# annotate points with labels without overlapping
# x is sorted, overlapping labels are moved down
annotate <- function(x, y, labels, cex=par('cex'), font=par('font')) {
    offset.x = strwidth('m') * 0.3 * cex
    offset.y = strheight('x') * 0.2 * cex
    labels.w = strwidth(labels, cex=cex, font=font) + 2 * offset.x
    labels.h = strheight(labels, cex=cex, font=font) + 2 * offset.y

    x = x + offset.x # add off parameter?
    y = y - offset.y - labels.h # add adj parameter?

    if (length(labels) > 1) {
        last = c(x[1], y[1], x[1] + labels.w[1], y[1] + labels.h[1]) # last obstacle
        for (i in 2:length(labels)) {
            k = i - 1
            if (x[i] <= last[3] # sorted x -> this check is enough
                    && (last[4] <= y[i] && y[i] <= last[2]
                        || last[4] <= y[i] + labels.h[i]
                        && y[i] + labels.h[i] <= last[2])) {

                # move the label down, but leave its x position intact
                y[i] = y[k] - labels.h[k] - offset.y
                # expand last obstacle in case of 3 and more overlapping labels
                last = c(min(x[i], last[1]), max(y[i], last[2]),
                    max(x[i] + labels.w[i], last[3]),
                    min(y[i] + labels.h[i], last[4]))
            } else
                # no overlapping label, just move on to next one
                last = c(x[i], y[i], x[i] + labels.w[i], y[i] + labels.h[i])
        }
    }

    xs = x + labels.w
    ys = y + labels.h
    labels.x = x + offset.x
    labels.y = y + offset.y

    rect(x, y, xs, ys, col=rgb(1, 1, 1, 0.7), bg='white', border=NA)
    text(labels.x, labels.y, labels, adj=c(0, 0), cex=cex, font=font)
}

if (length(kz.args) != 4) {
    stop('Arguments required: output file, output file format, mod flag,
        signature flag')
}

kz.args.fout = kz.args[1]
kz.args.fmt = kz.args[2]
kz.args.sig = '--sig' %in% kz.args
kz.args.mod = '--mod' %in% kz.args

kz.args.width = 10
kz.args.height = 5

if (kz.args.fmt == 'pdf') {
    cairo_pdf(kz.args.fout, width=kz.args.width, height=kz.args.height, onefile=TRUE)
} else if (kz.args.fmt == 'png') {
    fimg = png
    kz.args.width = 900
    kz.args.height = 450
    png(kz.args.fout, width=kz.args.width, height=kz.args.height, res=96)
} else if (kz.args.fmt == 'svg') {
    svg(kz.args.fout, width=kz.args.width, height=kz.args.height)
}

if (is.null(kz.dives.ui$title))
    par(mar=c(5, 4, 1, 2) + 0.1)

for (i in 1:nrow(kz.dives)) {
    dive = kz.dives[i,]
    dive.title = if (is.null(kz.dives.ui$title)) NA else kz.dives.ui[i, 'title']
    dive.info = if (is.null(kz.dives.ui$info)) NA else kz.dives.ui[i, 'info']
    dive.info_avg_depth = if (is.null(kz.dives.ui$avg_depth)) NA else kz.dives.ui[i, 'avg_depth']

    dp = kz.profiles[kz.profiles$dive == i, ]

    dive_time = dp$time / 60.0
    # minus for decent, plus for ascent
    dp$speed = c(0, -round(diff(dp$depth) / diff(dive_time)))
    # skip speed for first and last samples as first and last samples are
    # usually injected due to dive computers not starting and not ending
    # dives at 0m
    dp$speed[2] = 0
    dp$speed[length(dp$speed)] = 0

    xlim = range(dive_time)
    ylim = rev(range(dp$depth))

    # set ylim to include mod of each gas, but skip mod of a gas which is
    # deeper more than 3m comparing to the maximum depth of the dive
    if (kz.args.mod
            && max(dp$mod_low, na.rm=TRUE) - 3 < ylim[1])
        ylim = rev(range(ylim, dp$mod_high, na.rm=TRUE))

    plot(NA, xlim=xlim, ylim=ylim,
        xlab='Time [min]', ylab='Depth [m]')

    # deco info
    if (any(!is.na(dp$deco_time))) {
        deco_depth = approxfun(dp$time, dp$deco_depth,
            method='constant', f=0)(dp$time)

        n = length(dp$time)
        dc = rep(rgb(0.90, 0.90, 1.0), n - 1)
        dc[which(dp$deco_alarm)] = rgb(1.0, 0.50, 0.50)
        rect(dive_time[1:n - 1], deco_depth[1:n - 1], dive_time[2:n], rep(0, n - 1),
            col=dc, border=dc)
    }

    # mod for used gases
    # - if no gas info, then no mod
    # - mod for 1.4 and 1.6 is shown
    if (kz.args.mod) {
        i_mod = which(!is.na(dp$mod_low))
        if (length(i_mod) > 0) {
            k = length(i_mod)
            dt = c(dive_time[i_mod], dive_time[length(dive_time)])
            mod_low = dp$mod_low[i_mod]
            mod_high = dp$mod_high[i_mod]
            x1 = c(dt[1], dt[2:k])
            x2 = c(dt[2:k], dt[k + 1])
            y1 = c(mod_low[1:k - 1], mod_low[k])
            y2 = c(mod_high[1], mod_high[2:k])
            rect(x1, y1, x2, y2, col=rgb(1, 0, 0, 0.1), border=NA)
            segments(x1, y1, x2, y1, col=rgb(1, 0, 0, 0.5))
            segments(x1, y2, x2, y2, col=rgb(1, 0, 0, 0.5))
        }
    }

    # then the grid
    minor.tick(nx=5, ny=2)
    grid()

    # plot dive average depth line
    if (!is.na(dive.info_avg_depth)) {
        duration = dive$duration / 60.0
        lines(c(0, duration), c(dive$avg_depth, dive$avg_depth),
                col='green')
        text(duration, dive$avg_depth, dive.info_avg_depth, cex=0.6,
            font=2, pos=4, offset=0.1)
    }

    # and finally plot the dive profile
    lines(dive_time, dp$depth, col='blue')

    # annotations
    labels = data.frame(depth=c(), time=c(), label=c(), pch=c())

    # setpoint change
    i_sp = which(!is.na(dp$setpoint))
    if (length(i_sp) > 0)
        labels = rbind(labels,
            data.frame(
                depth=dp$depth[i_sp],
                time=dive_time[i_sp],
                label=sprintf('SP %.2f', dp$setpoint[i_sp] / 100000.0),
                pch=21
            )
        )

    # gas switch
    i_gas = which(!is.na(dp$gas_name))
    if (length(i_gas) > 0)
        labels = rbind(labels,
            data.frame(
                depth=dp$depth[i_gas],
                time=dive_time[i_gas],
                label=dp$gas_name[i_gas],
                pch=23
            )
        )

    max_descent = min(dp$speed)
    max_ascent = max(dp$speed)
    # find firt maximum descent rate speed (> 20m/min)
    # and last maximum ascent rate speed (> 10m/min)
    i_speed = c(head(which(dp$speed < -20 & dp$speed == max_descent), 1),
        tail(which(dp$speed > 10 & dp$speed == max_ascent), 1))
    if (length(i_speed) > 0)
        labels = rbind(labels,
            data.frame(
                depth=dp$depth[i_speed],
                time=dive_time[i_speed],
                label=sprintf('%+dm/min', dp$speed[i_speed]),
                pch=ifelse(dp$speed[i_speed] > 0, 24, 25)
            )
        )

    if (nrow(labels)) {
        labels = labels[order(labels$time), ]
        points(labels$time, labels$depth, pch=labels$pch, cex=0.5,
            col='blue', bg='white')
        annotate(labels$time, labels$depth, labels$label,
            font=2, cex=0.6)
    }

    if (!is.na(dive.title))
        title(sprintf('Dive %s', dive.title))

    if (!is.na(dive.info)) {
        info = textGrob(dive.info, gp=gpar(cex=0.7, font=2))
        pushViewport(viewport(0.9, 0.3,
            width=grobWidth(info) + unit(0.02, 'npc'),
            height=grobHeight(info) + unit(0.03, 'npc'),
            just=c('right', 'bottom')
        ))
        grid.rect(gp=gpar(alpha=0.8))
        grid.draw(info)
        popViewport()
    }

    if (kz.args.sig)
        grid.text(sprintf('generated by kenozooid ver. %s', kz.version),
            x=0.99, y=0.01, just=c('right', 'bottom'),
            gp=gpar(cex=0.6, fontface='italic'))
}

dev.off()

# vim: sw=4:et:ai
