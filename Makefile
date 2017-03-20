RSYNC=rsync -zcav \
	--exclude=\*~ --exclude=.\* \
	--delete-excluded --delete-after \
	--no-owner --no-group \
	--progress --stats

DIR_BUILD_DOC_USER=build/homepage/doc/user
DIR_DOC_USER=doc/user

homepage: .homepage-stamp
epydoc: .epydoc-stamp
sphinx: .sphinx-stamp

doc: .homepage-stamp .epydoc-stamp .sphinx-stamp

.homepage-stamp:
	$(RSYNC) doc/homepage build

.epydoc-stamp:
	epydoc --config=doc/epydoc.conf --no-private --simple-term --verbose

.sphinx-stamp:
	mkdir -p $(DIR_BUILD_DOC_USER)
	./bin/kz plot --info --avg-depth examples/backup-ostc-20110728.uddf $(DIR_BUILD_DOC_USER)/dive-2011-06-26.pdf
	./bin/kz plot --info --avg-depth -k 8 examples/backup-ostc-20110728.uddf $(DIR_DOC_USER)/dive-2011-06-26.png
	./bin/kz plot -t cmp --legend --labels Rebreather 'Open Circuit' -k 1,2 examples/logbook.uddf $(DIR_BUILD_DOC_USER)/divemode-compare.pdf
	./bin/kz plot -t cmp --legend --labels Rebreather 'Open Circuit' -k 1,2 examples/logbook.uddf $(DIR_DOC_USER)/divemode-compare.png
	./bin/kz plan deco --rmv 16 -gl 20 -gh 90 -6 'ean27 ean50' 42 25 > $(DIR_DOC_USER)/deco-plan.txt
	sphinx-build doc build/homepage/doc
	sphinx-build -b epub doc doc-tmp-epub
	cp doc-tmp-epub/*.epub build/homepage/doc

doc-upload:
	$(RSYNC) build/homepage/ wrobell@dcmod.org:~/public_html/kenozooid

