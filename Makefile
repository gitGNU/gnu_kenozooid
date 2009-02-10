EPYDOC_ARGS=--docformat restructuredtext --parse-only -v --html --no-frames
build-doc:
	mkdir -p doc/_build/html/api
	rm -f doc/extapi.pyc doc/extapi.pyo
	#gaphorconvert -f png -v -u -d dino-doc/diagrams doc/design/dino.gaphor
	epydoc $(EPYDOC_ARGS) -o doc/_build/html/api -n "Kenozooid Project" kenozooid
	sphinx-build doc doc/_build/html

upload-doc:
	rsync --delete-after \
		--delete-excluded \
		-zcav --no-owner --no-group --progress \
		--stats \
		doc/_build/html/ \
		wrobell@maszyna.it-zone.org:~/public_html/kenozooid

