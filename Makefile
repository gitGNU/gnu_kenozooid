RSYNC=rsync -zcav \
	--exclude=\*~ --exclude=.\* \
	--delete-excluded --delete-after \
	--no-owner --no-group \
	--progress --stats

homepage: .homepage-stamp
epydoc: .epydoc-stamp
sphinx: .sphinx-stamp

doc: .homepage-stamp .epydoc-stamp .sphinx-stamp

.homepage-stamp:
	$(RSYNC) doc/homepage build

.epydoc-stamp:
	epydoc --config=doc/epydoc.conf --no-private --simple-term --verbose

.sphinx-stamp:
	mkdir -p build/homepage/doc/user
	./bin/kz plot --info --avg-depth examples/backup-ostc-20110728.uddf doc/user/dive-2011-06-26.pdf
	./bin/kz plot --info --avg-depth -k 8 examples/backup-ostc-20110728.uddf doc/user/dive-2011-06-26.png
	./bin/kz plot -t cmp --legend --labels Rebreather 'Open Circuit' -k 1,2 examples/logbook.uddf doc/user/divemode-compare.pdf
	./bin/kz plot -t cmp --legend --labels Rebreather 'Open Circuit' -k 1,2 examples/logbook.uddf doc/user/divemode-compare.png
	./bin/kz plan deco --rmv 16 -gl 20 -gh 90 -6 'ean27 ean50' 42 25 > build/homepage/doc/user/deco-plan.txt
	sphinx-build doc build/homepage/doc
	sphinx-build -b epub doc doc-tmp-epub
	cp doc-tmp-epub/*.epub build/homepage/doc
	cp doc/user/*.pdf build/homepage/doc/user/

upload-doc:
	$(RSYNC) build/homepage/ wrobell@wrobell.it-zone.org:~/public_html/kenozooid

