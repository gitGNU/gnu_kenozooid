upload-doc:
	rsync --delete-after \
		--delete-excluded \
		--exclude=\*~ \
		-zcav --no-owner --no-group --progress \
		--stats \
		build/homepage/ \
		wrobell@maszyna.it-zone.org:~/public_html/kenozooid

