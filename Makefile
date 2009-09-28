upload-doc:
	rsync --delete-after \
		--delete-excluded \
		-zcav --no-owner --no-group --progress \
		--stats \
		build/sphinx/html/ \
		wrobell@maszyna.it-zone.org:~/public_html/kenozooid

