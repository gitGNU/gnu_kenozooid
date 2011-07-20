RSYNC=rsync -zcav \
	--exclude=\*~ --exclude=.\* \
	--delete-excluded --delete-after \
	--no-owner --no-group \
	--progress --stats

doc: .doc-stamp

.doc-stamp:
	$(RSYNC) doc/homepage build
	epydoc --config=doc/epydoc.conf --no-private --simple-term --verbose
	sphinx-build doc build/homepage/doc

upload-doc:
	$(RSYNC) build/homepage/ wrobell@maszyna.it-zone.org:~/public_html/kenozooid

