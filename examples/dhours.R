#
# example R script to use with Kenozooid
#
# print total hours of diving
#

secs = sum(kz.dives$duration)
print(sprintf('Total dive hours %.1f', secs / 3600))

# vim: sw=4:et:ai
