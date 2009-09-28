upload-doc:
	rsync --delete-after \
		--delete-excluded \
		-zcav --no-owner --no-group --progress \
		--stats \
		doc/_build/html/ \
		wrobell@maszyna.it-zone.org:~/public_html/kenozooid

