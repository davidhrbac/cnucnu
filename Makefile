html: FORCE
	rm -rf html
	epydoc --html --no-private --output html -v cnucnu/
	#find -type f -name "*.html" -print0 | xargs -0 sed -i 's,"encoding=iso8859-1",encoding="utf-8",'

view: html
	xdg-open html/index.html

check-doc:
	epydoc --check cnucnu/

FORCE:
